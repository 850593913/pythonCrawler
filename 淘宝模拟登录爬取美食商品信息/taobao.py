from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import re
from config import *
import pymongo
import os
from hashlib import md5

option = webdriver.ChromeOptions()
option.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2}) #不加载图片
option.add_experimental_option('excludeSwitches', ['enable-automation']) #开发者模式
option.add_argument('--headless') #无窗口模式
browser = webdriver.Chrome(chrome_options=option)
browser.maximize_window() #窗口最大化
wait = WebDriverWait(browser, 10)

#创建数据库
client = pymongo.MongoClient(MONGO_URL)
db = client[TAOBAO_DB]

#登录
def login(username, password):
    print('正在登录', username+' '+password)
    browser.get('https://login.taobao.com/member/login.jhtml')
    #密码登录
    password_login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_QRCodeLogin > div.login-links > a.forget-pwd.J_Quick2Static')))
    password_login.click()
    #微博登录
    weibo_login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_OtherLogin > a.weibo-login')))
    weibo_login.click()
    #用户名
    username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(2) > div > input')))
    username_input.send_keys(username)
    #密码
    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(3) > div > input')))
    password_input.send_keys(password)
    #登录按钮
    login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a > span')))
    login_button.click()

#查找
def search(searchword):
    print('正在搜索', searchword)
    search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
    search_input.send_keys(searchword)
    search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
    search_button.click()
    page_count = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
    total = int(re.search('.*?(\d+).*?', page_count.text).group(1)) #总页数
    print(total)

#翻页
def get_next_page(pagenumber):
    print('正在翻页')
    try:
        page_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        page_input.clear()
        page_input.send_keys(pagenumber)
        page_button =  wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        page_button.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active'), str(pagenumber)))
        print('第'+str(pagenumber)+'页')
    except:
        get_next_page(pagenumber)

#获得产品信息
def get_product():
    print('产品信息')
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist')))
    doc = pq(browser.page_source)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'title': item.find('.title').text(),
            'price': item.find('.price').text(),
            'location': item.find('.location').text(),
            'deal': item.find('.deal-cnt').text(),
            'image': item.find('.pic .J_ItemPic').attr('src'),
        }
        print(product)
        save_to_mongo(product)

#保存到数据库
def save_to_mongo(result):
    if db[TAOBAO_TABLE].insert(result):
        print('成功存储', result)
        return True
    return False

if __name__ == "__main__":
    login('自己的账号', '自己的密码')
    search(SEARCHWORD)
    get_product()
    for pagenumber in range(2, PAGENUMBER):
        get_next_page(pagenumber)
        get_product()

        

    