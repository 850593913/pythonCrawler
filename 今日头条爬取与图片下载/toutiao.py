import requests
from urllib.parse import urlencode
import time
import json
import re
from bs4 import BeautifulSoup
from config import *
import pymongo
from requests.exceptions import RequestException
import os
from hashlib import md5
from multiprocessing.pool import Pool

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
        'Referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'X-requested-with': 'XMLHttpRequest',
}
cookies = {
    'Cookie': 'tt_webid=6791062722623079950; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6791062722623079950; csrftoken=7ed4855309c9f8acfe2fca089394e3eb; ttcid=3ca8c4efb62c42898288ebf3353aa95837; tt_scid=Q5VL4jazZsu1nbDW1EbLuQ1zzY2UMC.GNwJzY6EvJ6rMZH9NMQ1bE5hsAsC8LsNnf840; __tasessionId=7xccw36gb1581235049180; s_v_web_id=k6eqkrr9_si1p4Jht_LrHN_4Nq5_Ah71_rJlM5e12E7HP'
    # 'Cookie': ''
}

#请求主页
def get_page_index(offset, keyword):
    data = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': int(time.time()),
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)

    try:
        response = requests.get(url,headers=headers, cookies=cookies)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    
#解析主页
def parse_page_index(html):
    data = json.loads(html).get('data')
    return data

#请求详情页
def get_page_detail(url, headers):
    try:
        response = requests.get(url,headers=headers, cookies=cookies)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

#解析详情页
def parse_page_detail(url, html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    pattern = re.compile('JSON.parse\("(.*?)"\),', re.S)
    result = re.search(pattern, html)
    if result:
        text = result.group(1).replace(r'\"', r'"').replace(r'\\', r'')
        sub_images = json.loads(text).get('sub_images')
        images = [item.get('url') for item in sub_images]
        for image in images:
            download_images(image)
        return {
            'title': title,
            'url': url,
            'images': images,
        }

#保存到数据库
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('成功存储', result)
        return True
    return False

#请求图片
def download_images(url):
    print('正在下载', url)
    try:
        response = requests.get(url,headers=headers, cookies=cookies)
        if response.status_code == 200:
            save_images(response.content)
        return None
    except RequestException:
        return None

#保存图片
def save_images(content):
    file = '{0}\{1}.{2}'.format(os.getcwd()+'\images', md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file):
        with open(file, 'wb') as f:
            f.write(content)
            f.close()
def main(offset):
    html = get_page_index(offset, KEYWORD)
    print(html)
    for item in parse_page_index(html):
        url = item.get('article_url')
        if url:
            html = get_page_detail(url, headers)
            result = parse_page_detail(url, html)
            if result:
                save_to_mongo(result) 


if __name__ == '__main__':
    p = Pool()
    p.map(main, [i*20 for i in range(3)])
