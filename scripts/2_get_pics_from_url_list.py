import os
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor

url_file_list = ['../raw_data/sexy/IMAGES/urls_sexy.txt',
                 '../raw_data/porn/IMAGES/urls_porn.txt',
                 '../raw_data/neutral/IMAGES/urls_neutral.txt',
                 '../raw_data/hentai/IMAGES/urls_hentai.txt',
                 '../raw_data/drawings/IMAGES/urls_drawings.txt']

def printE(s):
    print('\033[31m ' + s + ' \033[0m')

def printI(s):
    print('\033[32m ' + s + ' \033[0m')

def printV(s):
    print('\033[33m ' + s + ' \033[0m')

def is_valid_jpg(jpg_file):
    with open(jpg_file, 'rb') as f:
        f.seek(-2, 2)
        buf = f.read()
        f.close()
        return buf == b'\xff\xd9'  # 判定jpg是否包含结束字段

def is_valid_png(png_file):
    with open(png_file, 'rb') as f:
        f.seek(-2, 2)
        buf = f.read()
        return buf == b'\x60\x82'

def check_and_download(m):
    url = m['url']
    path = m['path']

    parent_path = os.path.dirname(path)
    md5_val = hashlib.md5(url.encode('utf8')).hexdigest()

    png_file = parent_path + '/' + md5_val + '.png'
    jpeg_file = parent_path + '/' + md5_val + '.jpeg'

    if(os.path.exists(png_file) or os.path.exists(jpeg_file)):
        printI("have download %s" % url)
    else:
        DownloadFile(path, url)

def DownloadFile(path, url, time=5):
    md5_val = hashlib.md5(url.encode('utf8')).hexdigest()
    jpeg_full_name = path + '/' + md5_val + '.jpeg'
    png_full_name = path + '/' + md5_val + '.png'

    if os.path.exists(jpeg_full_name):
        printI('file exist %s ' % jpeg_full_name)
        if is_valid_jpg(jpeg_full_name) is False:
            os.remove(jpeg_full_name)
            printI('remove pic %s ' % jpeg_full_name)
        else:
            return
    elif os.path.exists(png_full_name):
        printI('file exist %s ' % png_full_name)
        if is_valid_png(png_full_name) is False:
            os.remove(png_full_name)
            printI('remove pic %s ' % png_full_name)
        else:
            return

    try:
        s = requests.session()
        s.keep_alive = False
        r = s.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        headers = r.headers
        if 'Content-Type' in headers:
            dtype = headers['Content-Type']
            if dtype == 'image/jpeg' or dtype == 'image/png':
                pic_full_name = path + '/' + md5_val + '.' + dtype.split('/')[1]
                printI('pic_name : %s, url : %s' % (pic_full_name, url))
                with open(pic_full_name, 'wb') as f:
                    f.write(r.content)
            else:
                cmdline = 'echo ' + 'path : ' + path + ', url : ' + url + ', type : ' + dtype + ' >> ' + path + '/typeerror.txt'
                os.system(cmdline)

    except Exception as e:
        printE('DownloadFile error : %s ' % e)
        if time > 0:
            time -= 1
            printE("DownloadFile faild %s " % url)
            DownloadFile(path, url, time)
        else:
            printE('file: %s downlaod alway faild' % url)
            cmdline = 'echo ' + url + ' >> ' + path + '/errorurl.txt'
            os.system(cmdline)


def main():
    download_list = []
    for url_file in url_file_list:
        fb = open(url_file, 'r')
        lines = fb.readlines()
        for line in lines:
            download_path = os.path.dirname(url_file)
            d = dict()
            d['path'] = download_path
            d['url'] = line.strip()
            download_list.append(d)

    print(len(download_list), download_path)
    with ThreadPoolExecutor(5) as executor1:
        executor1.map(check_and_download, download_list)


if __name__ == '__main__':
    main()
