import os
from threading import Thread
import urllib.request
import socket
import json
from urllib.error import URLError, HTTPError
import hashlib
import requests

class MonitorThread(Thread):

    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args
        print('Thread : ' + str(self.args) + ', ' + self.name + ' start')

    def run(self):
        proxy_support = urllib.request.ProxyHandler({'sock5': 'localhost:1080'})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        #data = urllib.request.urlopen(self.name).read()
        json = urllib.request.urlopen(self.name).read().decode("utf8")
        print(json)

def printE(s):
    print('\033[31m ' + s + ' \033[0m!')

def printI(s):
    print('\033[32m ' + s + ' \033[0m')

def URLTools(url, time=5):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

    headers = {'User-Agent': user_agent}

    req = urllib.request.Request(url, headers=headers)

    try:
        response = urllib.request.urlopen(req, timeout=5)
        json_txt = response.read().decode("utf8")
        return json_txt
    except (HTTPError, URLError, socket.timeout, socket.gaierror) as e:
        print('exception %s' % e)
        if(time > 0):
            time -= 1
            print("URLTools %s " % url)
            return URLTools(url, time)
        else:
            cmdline = 'echo ' + url + ' >> ' + source_urls + '/errorurl.txt'
            os.system(cmdline)

def getDownloadPicUrl(string):
    jsonObj = json.loads(string)
    pic_list = []
    if 'data' in jsonObj:
        data = jsonObj['data']
        after = None
        if 'after' in data:
            after = data['after']
            #print('after %s ' % after)
        if 'children' in data:
            chinldren = data['children']
            for child in chinldren:
                data = child['data']
                pic_url = data['url']
                #print('is_video %s  pic url %s' % (data['is_video'], pic_url))
                if data['is_video'] is False:
                    pic_list.append(pic_url)
    return after, pic_list

def is_valid_jpg(jpg_file):
    with open(jpg_file, 'rb') as f:
        f.seek(-2, 2)
        buf = f.read()
        f.close()
        return buf ==  b'\xff\xd9'  # 判定jpg是否包含结束字段

def DownloadFile(path, url, time=5):
    md5_val = hashlib.md5(url.encode('utf8')).hexdigest()

    pic_full_name = path + '/' + md5_val + '.' + 'jpeg'
    if os.path.exists(pic_full_name):
        printI('file exist %s ' % pic_full_name)
        if is_valid_jpg(pic_full_name) is False:
            os.remove(pic_full_name)
            printI('remove pic %s ' % pic_full_name)
        else:
            return

    try:
        s = requests.session()
        s.keep_alive = False
        r = s.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        headers = r.headers
        if 'Content-Type' in headers:
            dtype = headers['Content-Type']
            if dtype == 'image/jpeg':
                printI('pic_name : %s, url : %s' % (pic_full_name, url))
                with open(pic_full_name, 'wb') as f:
                    f.write(r.content)

    except Exception as e:
        printE('error : %s ' % e)
        if time > 0:
            time -= 1
            printE("DownloadFile faild %s " % url)
            DownloadFile(path, url, time)
        else:
            printE('file: %s downlaod alway faild' % url)
            cmdline = 'echo ' + url + ' >> ' + path + '/errorurl.txt'
            os.system(cmdline)

def DownloadPics(path, url_list):
    for url in url_list:
        DownloadFile(path, url)

curPath = os.path.abspath('.')
parentPath = os.path.abspath('..')

raw_data = parentPath + '/raw_data/'
source_urls = curPath + '/source_urls/'

fileList = os.listdir(source_urls)
for fileName in fileList:
    downloadPath = raw_data + fileName.split('.')[0]
    fileFullName = os.path.join(source_urls, fileName)
    print(fileFullName)
    fb = open(fileFullName, 'r')
    lines = fb.readlines()
    for line in lines:
        org_url = line.strip()
        url = org_url
        while True:
            jsonString = URLTools(url)
            if jsonString is None:
                printE(url + '   no no no no no no no no no no no no no  work ')
            else:
                printI(url + '   work work work work work work work work work good ')

                after, pic_list = getDownloadPicUrl(jsonString)
                #print(downloadPath, pic_list)
                DownloadPics(downloadPath, pic_list)
                if after is None:
                    printE('url %s after is None' % org_url)
                    break;
                else:
                    afterUrl = org_url + "&after=" + after
                    #print('after url : ' + afterUrl)
                    url = afterUrl