import requests
from urllib.parse import urlencode
import json
import time
import random
import jieba
from PIL import Image  #打开图片用的
import numpy #把图片转为n维数组
import matplotlib.pyplot as plt   #显示图片用的
from wordcloud import WordCloud 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
    'Referer': 'https://item.jd.com/1263013576.html'

}
cookies = {
    'Cookie': '__ysuid=1555768594247eoc; cna=8TY6FdCfhAICAXF1+OnYAlDc; UM_distinctid=16e5561ac0f176-0a109840cb946b-345b417d-1fa400-16e5561ac1032c; timerun_8099666=10783; __ayft=1581323543639; __aysid=1581323543640G3p; __ayscnt=1; _m_h5_tk=c000252ce0654b344b0976e17e2c0981_1581328761239; _m_h5_tk_enc=eb3e203f4ea569e82d1cf5c4d0ff7de5; P_ck_ctl=53164927ADEC88E00FF297EA2B4BFC5E; _m_h5_c=67d1e6213e85378826350accf292040b_1581332183814%3Bdcc9cc073c64b9e399951efd9be8832b; youku_history_word=[%22%E9%95%BF%E5%AE%89%E5%8D%81%E4%BA%8C%E6%97%B6%E8%BE%B0%22]; __arycid=dd-3-00; __arcms=dd-3-00; modalObj={"UUID":"1"}; __arpvid=1581323728764X2Bcgf-1581323728842; __aypstp=4; __ayspstp=4; __ayvstp=11; __aysvstp=11; isg=BDEx_b5Yy4Gob2QWZH3-PxmfVb3LHqWQMsNMhhNG6vg3OlGMW2peYNteXM5c8j3I',
}

def get_one_page(url, headers, page):
    data = {
        'callback': 'fetchJSON_comment98vv9131',
        'productId': '1263013576',
        'score': '0',
        'sortType': '5',
        'page': page,
        'pageSize': '10',
        'isShadowSku': '0',
        'fold': '1',
    }
    try:
        response = requests.get(url+urlencode(data), headers=headers)
        # print(response.status_code)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def parse_one_page(response):
    string = response[26:-2]
    # print(json)
    data = json.loads(string)
    # print(data.get('comments'))
    comments = data.get('comments')
    for comment in comments:
        print(comment.get('content'))
        save_to_file(comment.get('content')+'\n')

def save_to_file(content):
    with open('comments.txt', 'a') as f:
        f.write(content)
        f.close()

def cut_word():
    with open('comments.txt') as f:
        comment = f.read()
        wordlist = jieba.cut(comment, cut_all=True)
        wl = " ".join(wordlist)
        # print(wl)
        return wl

def create_word_cloud():
    #设置词云形状图片
    coloring = numpy.array(Image.open('wawa.jpg'))
    #词云配置
    wc = WordCloud(background_color='white',mask=coloring, max_words=2000, scale=10,
                   max_font_size=50, random_state=42, font_path='Alibaba-PuHuiTi-Bold.ttf')
    print(1)
    #生成词云
    wc.generate(cut_word())
    #在只设置mask的情况下，你将会得到一个拥有图片形状的词云
    plt.imshow(wc, interpolation='bilinear') #以线性插值方式显示图片
    plt.axis('off') #关闭坐标轴
    # plt.figure()
    plt.show() 

if __name__ == "__main__":
    # url = 'https://club.jd.com/comment/productPageComments.action?'
    # for page in range(5):
    #     response = get_one_page(url, headers, page)
    #     parse_one_page(response)efws
    #     time.sleep(random.random()*5)
    # cut_word()
    # print(cut_word())
    create_word_cloud()