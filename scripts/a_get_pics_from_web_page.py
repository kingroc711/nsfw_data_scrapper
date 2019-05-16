import os
import urllib.request
import socket
import json
from urllib.error import URLError, HTTPError
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor
import threading


class GetPicsFromWebPage(object):
    def printE(self, s):
        print('\033[31m ' + s + ' \033[0m')

    def printI(self, s):
        print('\033[32m ' + s + ' \033[0m')

    def printV(self, s):
        print('\033[33m ' + s + ' \033[0m')

    def getJsonData(self, url, time=5):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

        headers = {'User-Agent': user_agent}

        req = urllib.request.Request(url, headers=headers)

        try:
            response = urllib.request.urlopen(req, timeout=5)
            json_txt = response.read().decode("utf8")
            return json_txt
        except (HTTPError, URLError, socket.timeout, socket.gaierror) as e:
            print('getJsonData exception %s' % e)
            if time > 0:
                time -= 1
                return self.getJsonData(url, time)
            else:
                cmdline = 'echo ' + url + ' >> ./errorjson.txt'
                os.system(cmdline)
                return None

    def getDownloadPicUrl(self, string):
        jsonObj = json.loads(string)
        pic_list = []
        after = None
        if 'data' in jsonObj:
            data = jsonObj['data']
            if 'after' in data:
                after = data['after']
            if 'children' in data:
                chinldren = data['children']
                for child in chinldren:
                    data = child['data']
                    pic_url = data['url']
                    # print('is_video %s  pic url %s' % (data['is_video'], pic_url))
                    if data['is_video'] is False:
                        pic_list.append(pic_url)
        return after, pic_list

    def isValidJPEG(self, jpg_file):
        with open(jpg_file, 'rb') as f:
            f.seek(-2, 2)
            buf = f.read()
            f.close()
            return buf == b'\xff\xd9'  # 判定jpg是否包含结束字段

    def isValidPNG(self, png_file):
        with open(png_file, 'rb') as f:
            f.seek(-2, 2)
            buf = f.read()
            return buf == b'\x60\x82'

    def downloadFile(self, path, url, time=5):
        md5_val = hashlib.md5(url.encode('utf8')).hexdigest()
        jpeg_full_name = path + '/' + md5_val + '.jpeg'
        png_full_name = path + '/' + md5_val + '.png'

        if os.path.exists(jpeg_full_name):
            self.printI('file exist %s ' % jpeg_full_name)
            if self.isValidJPEG(jpeg_full_name) is False:
                os.remove(jpeg_full_name)
                self.printI('remove pic %s ' % jpeg_full_name)
            else:
                return
        elif os.path.exists(png_full_name):
            self.printI('file exist %s ' % png_full_name)
            if self.isValidPNG(png_full_name) is False:
                os.remove(png_full_name)
                self.printI('remove pic %s ' % png_full_name)
            else:
                return

        try:
            s = requests.session()
            s.keep_alive = False
            r = s.get(url, headers={
                'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
            headers = r.headers
            if 'Content-Type' in headers:
                dtype = headers['Content-Type']
                if dtype == 'image/jpeg' or dtype == 'image/png':
                    pic_full_name = path + '/' + md5_val + '.' + dtype.split('/')[1]
                    self.printI('pic_name : %s, url : %s' % (pic_full_name, url))
                    with open(pic_full_name, 'wb') as f:
                        f.write(r.content)
                else:
                    cmdline = 'echo ' + 'path : ' + path + ', url : ' + url + ', type : ' + dtype + ' >> ' + path + '/typeerror.txt'
                    os.system(cmdline)

        except Exception as e:
            self.printE('downloadFile error : %s ' % e)
            if time > 0:
                time -= 1
                self.printE("downloadFile faild %s " % url)
                self.downloadFile(path, url, time)
            else:
                self.printE('file: %s downlaod alway faild' % url)
                cmdline = 'echo ' + url + ' >> ' + path + '/errorurl.txt'
                os.system(cmdline)

    def downloadPics(self, path, url_list):
        for url in url_list:
            self.downloadFile(path, url)

    def downloaderCall(self, m):
        org_url = m['url']
        download_path = m['path']
        url = org_url

        self.printV('%s, download path %s, url : %s ' % (threading.current_thread().getName(), download_path, url))

        while True:
            jsonString = self.getJsonData(url)
            if jsonString is None:
                self.printE(url + '   no no no no no no no no no no no no no  work ')
                break
            else:
                self.printI(url + '   work work work work work work work work work good ')

                after, pic_list = self.getDownloadPicUrl(jsonString)
                # print(downloadPath, pic_list)
                self.downloadPics(download_path, pic_list)
                if after is None:
                    self.printE('url %s after is None' % org_url)
                    break
                else:
                    afterUrl = org_url + "&after=" + after
                    # print('after url : ' + afterUrl)
                    url = afterUrl

    def downloader(self, download_list):
        print(download_list)
        with ThreadPoolExecutor(10) as executor1:
            executor1.map(self.downloaderCall, download_list)


def main():
    curPath = os.path.abspath('.')
    parentPath = os.path.abspath('..')
    raw_data = parentPath + '/raw_data/'
    source_urls = curPath + '/source_urls/'

    fileList = os.listdir(source_urls)
    download_list = []
    for fileName in fileList:
        downloadPath = raw_data + fileName.split('.')[0]
        fileFullName = os.path.join(source_urls, fileName)
        print(fileFullName)
        fb = open(fileFullName, 'r')
        lines = fb.readlines()
        for line in lines:
            d = dict()
            d['path'] = downloadPath
            d['url'] = line.strip()
            download_list.append(d)

    d = GetPicsFromWebPage()
    d.downloader(download_list)


if __name__ == '__main__':
    main()
