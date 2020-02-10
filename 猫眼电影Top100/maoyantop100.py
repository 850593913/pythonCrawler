import requests
import re
import json
import datetime
from multiprocessing.pool import Pool
def get_one_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def main(page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Referer': ''
    }
    url = 'https://maoyan.com/board/4?offset='
    html = get_one_page(url+str(page), headers)
    for item in parse_html(html):
        print(item)
        write_to_file(item)


def parse_html(html):
    pattern = re.compile('<dd>.*?>(\d+)</i>.*?title="(.*?)".*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>', re.S)
    result = re.findall(pattern, html)
    for item in result:
        yield{
            'index': item[0],
            'title': item[1],
            'actor': item[2].strip()[3:],
            'time': item[3].strip()[5:],
            'score': item[4]+item[5],
        }

def write_to_file(content):
    with open('test.txt', 'a') as f:
            f.write(json.dumps(content, ensure_ascii=False)+'\n')
            f.close()

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    p = Pool()
    p.map(main, [i*10 for i in range(10)])
    endtime = datetime.datetime.now()
    print(endtime-starttime)
