import requests
import time

def downloader(url, file):
    start = time.time()
    size = 0
    response = requests.get(url, stream=True)
    chunk_size = 1024
    content_size = int(response.headers['content-length'])
    print(content_size)
    if response.status_code == 200:
        print('[文件大小]:%0.2f MB' % (content_size / chunk_size / 1024))
        with open(file, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                print('\r'+'[下载进度]：%s%.2f%%' % ('>'*int(size*50/content_size),float(size/content_size*100) ), end='')
    end =time.time()
    print('\n'+'全部下载完成！用时%.f秒' % (end-start))
if __name__ == "__main__":
    url = 'https://js.a.kspkg.com/bs2/fes/kwai-android-generic-gifmakerrelease-6.11.9.12260_544f8d.apk'
    downloader(url, '快手.apk')
