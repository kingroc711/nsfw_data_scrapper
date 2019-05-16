import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from scripts.a_get_pics_from_web_page import GetPicsFromWebPage as PP


class GetPicsFromURLList:

    def checkAndDownload(self, m):
        url = m['url']
        path = m['path']

        parent_path = os.path.dirname(path)
        md5_val = hashlib.md5(url.encode('utf8')).hexdigest()

        png_file = parent_path + '/' + md5_val + '.png'
        jpeg_file = parent_path + '/' + md5_val + '.jpeg'

        pp = PP()

        if (os.path.exists(png_file) or os.path.exists(jpeg_file)):
            pp.printI("had download %s, file name md5 : %s" % (url, md5_val))
            return
        else:
            md5_val = hashlib.md5(url.encode('utf8')).hexdigest()
            jpeg_full_name = path + '/' + md5_val + '.jpeg'
            png_full_name = path + '/' + md5_val + '.png'

            if os.path.exists(jpeg_full_name):
                pp.printI('file exist %s ' % jpeg_full_name)
                if pp.isValidJPEG(jpeg_full_name) is False:
                    os.remove(jpeg_full_name)
                    pp.printI('remove pic %s ' % jpeg_full_name)
                else:
                    return
            elif os.path.exists(png_full_name):
                pp.printI('file exist %s ' % png_full_name)
                if pp.isValidPNG(png_full_name) is False:
                    os.remove(png_full_name)
                    pp.printI('remove pic %s ' % png_full_name)
                else:
                    return

            pp.downloadFile(path, url)

    def downloader(self, download_list):
        with ThreadPoolExecutor(1) as executor:
            executor.map(self.checkAndDownload, download_list)


def main():
    url_file_list = ['../raw_data/sexy/IMAGES/urls_sexy.txt',
                     '../raw_data/porn/IMAGES/urls_porn.txt',
                     '../raw_data/neutral/IMAGES/urls_neutral.txt',
                     '../raw_data/hentai/IMAGES/urls_hentai.txt',
                     '../raw_data/drawings/IMAGES/urls_drawings.txt']

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

    d = GetPicsFromURLList()
    d.downloader(download_list)


if __name__ == '__main__':
    main()
