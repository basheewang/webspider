#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: mlp.py


'''
Extract data from http://www.4399er.com/xzt/xmblmh/
'''

import http.cookiejar
import urllib
from bs4 import BeautifulSoup
from optparse import OptionParser
import re
# import fileinput
import os
import time
import requests


# For debug purpose.
def saveFile(data, s, coding='gbk'):
    # save_path = 'temp.out'
    f_obj = open('temp_' + s + '.html', 'wb')
    f_obj.write(bytes(data, coding))
    f_obj.close()


def getbooklist():
    cj = http.cookiejar.LWPCookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)
    opener.addheaders = [
        ("User-agent",
         "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
         "(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"),
        ("Connection", "keep-alive"),
        ("Host", "login.taobao.com"),
        ("Referer", "https://login.taobao.com/member/login.jhtml")
    ]

    # To get all books
    total_url = 'http://www.4399er.com/xzt/xmblmh/'
    pre_url = 'http://www.4399er.com'
    books = urllib.request.urlopen(total_url).read().\
        decode('utf8', 'ignore')
    booksoup = BeautifulSoup(books, 'html.parser')
    print("Now begin to extrace books url...")
    book_list = []
    for link in booksoup.find_all('a', attrs={'class': 'tit'}):
        book_list.append(pre_url + link['href'])
        # print(pre_url + link['href'])

    print("There are total", len(book_list), 'books!')
    return book_list


def getdata(url):
    cj = http.cookiejar.LWPCookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)
    opener.addheaders = [
        ("User-agent",
         "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
         "(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"),
        ("Connection", "keep-alive"),
        ("Host", "login.taobao.com"),
        ("Referer", "https://login.taobao.com/member/login.jhtml")
    ]

    # To get all books
    # total_url = 'http://www.4399er.com/xzt/xmblmh/'
    # books = urllib.request.urlopen(total_url).read().\
    #     decode('utf8', 'ignore')
    # booksoup = BeautifulSoup(books, 'html.parser')
    # print("Now begin to extrace books url...")
    # for link in booksoup.find_all('a'):
    #     print(link['href'])

    print('Try to extract book contents...')
    book_contents = urllib.request.urlopen(url).read().\
        decode('utf8', 'ignore')
    contsoup = BeautifulSoup(book_contents, 'html.parser')
    title = contsoup.find('title').text.strip().split('-')[0]
    title = title.replace(' ', '_').replace('&', '_')
    # replace('：', '_').replace(':', '_').
    if not os.path.exists(title):
        os.makedirs(title)
        print('Folder:', title, 'was created!')
    else:
        print('Folder:', title, 'already existed!')

    j = 1

    try:
        book_contents_url = [url]
        total_page = re.compile(
            '(\d+)').search(contsoup.find('span', attrs={'class': 'zong'}).text).group(1)
        url_pre = url[:-5]

        for i in range(int(total_page) - 1):
            book_contents_url.append(url_pre + '-' + str(i + 2) + '.html')

        print('Book contents extraction done, there are total',
              len(book_contents_url), 'pages.')

        # outfile = open(title + '.md', 'w', encoding='utf-8')

        print('Now begin to download pictures:')

        for k in book_contents_url:
            print('\tExtracting data for:', k, '...')
            chapter_contents = urllib.request.urlopen(k).read().\
                decode('utf8', 'ignore')
            csoup = BeautifulSoup(chapter_contents, 'html.parser')
            for pic in csoup.find_all('img'):
                pic_url = pic['src']
                fn = os.path.join(os.path.curdir, title, '%03d' %
                                  j + '_' + pic_url.split('/')[-1])
                print("\t\t[" + '%03d' % j + "]Download", pic_url, end=' ')

                if os.path.isfile(fn):
                    print()
                    j += 1
                    continue
                raw = requests.get(pic_url)
                if int(raw.headers['Content-length']) > 10000:
                    with open(fn, 'wb') as outfile:
                        outfile.write(raw.content)
                        # os.system("wget -O {0} {1}".format(fn, pic_url))
                        os.system(
                            "convert {0} -resize 200% -quality 100 -density 300 {1}".
                            format(fn, fn))
                        print('[The picture file was Enlarged!]', end=' ')
                        os.system(
                            "convert {0} -unsharp 1.5x1.0+1.5+0.02 {1}".format(fn, fn))
                        print('[Sharpened!]')
                else:
                    print('\t\t\tToo small, skipped!')
                    continue

                time.sleep(3)
                # urllib.request.urlretrieve(pic_url, fn)
                j += 1
            print('\tDone!')
    except AttributeError:
        for pic in contsoup.find_all('img'):
            pic_url = pic['src']
            fn = os.path.join(os.path.curdir, title, '%03d' %
                              j + '_' + pic_url.split('/')[-1])
            print("\t\t[" + '%03d' % j + "]Download", pic_url, end=' ')

            raw = requests.get(pic_url)
            if int(raw.headers['Content-length']) > 10000:
                with open(fn, 'wb') as outfile:
                    outfile.write(raw.content)
                    # os.system("wget -O {0} {1}".format(fn, pic_url))
                    os.system(
                        "convert {0} -resize 200% -quality 100 -density 300 {1}".
                        format(fn, fn))
                    print('[The picture file was Enlarged!]', end=' ')
                    os.system(
                        "convert {0} -unsharp 1.5x1.0+1.5+0.02 {1}".format(fn, fn))
                    print('[Sharpened!]')
            else:
                print('\t\t\tToo small, skipped!')
                continue

            time.sleep(3)
            # urllib.request.urlretrieve(pic_url, fn)
            j += 1
        print('\tDone!')

    # outfile.close()
    print("Extract completed!")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from guoxue123")
    (options, args) = parser.parse_args()

    book_lists = getbooklist()
    for url in book_lists[119:]:
        getdata(url)
