import os

url_file_list = ['../raw_data/drawings/IMAGES/urls_drawings.txt',
                 '../raw_data/hentai/IMAGES/urls_hentai.txt',
                 '../raw_data/neutral/IMAGES/urls_neutral.txt',
                 '../raw_data/porn/IMAGES/urls_porn.txt',
                 '../raw_data/sexy/IMAGES/urls_sexy.txt']

def main():
    for l in url_file_list:
        print(l)
        print(os.path.dirname(l))
        print(os.path.abspath(l))

if __name__ == '__main__':
    main()