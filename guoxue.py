#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: guoxue123.py

import http.cookiejar
import urllib
from bs4 import BeautifulSoup
from optparse import OptionParser
import re
import fileinput


# For debug purpose.
def saveFile(data, s, coding='gbk'):
    # save_path = 'temp.out'
    f_obj = open('temp_' + s + '.html', 'wb')
    f_obj.write(bytes(data, coding))
    f_obj.close()


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
    print('Try to extract book contents...')
    book_contents = urllib.request.urlopen(url).read().\
        decode('gb18030', 'ignore')
    contsoup = BeautifulSoup(book_contents, 'html.parser')
    title = contsoup.find('table').find_all('span')[-1].text.strip()
    book_contents_url = {}
    for link in contsoup.find_all('a'):
        # print(link)
        if re.compile('\d\d?\d?\d?\.htm').match(link['href']):
            book_contents_url[url.replace('index.htm', '') + link['href']] = \
                link.text.replace('\u3000', ' ')
    print('Book contents extraction done, there are total',
          len(book_contents_url), 'chapters.')

    outfile = open(title + '.md', 'w', encoding='utf-8')

    print('Now begin to extract each chapter contents:')
    for k in sorted(book_contents_url.keys()):
        print('\tExtracting data for:', book_contents_url[k], '...')
        chapter_contents = urllib.request.urlopen(k).read().\
            decode('gb18030', 'ignore')
        csoup = BeautifulSoup(chapter_contents, 'html.parser')
        ccsoup = BeautifulSoup(str(csoup).replace(
            "<br/>", "\n"), 'html.parser')
        # chapter = csoup.find('td', attrs={'width': '87%'})
        # chapter = csoup.find('table', attrs={'border': '1'})
        chapter_text = ''.join(['# ' + tt + ' #'.replace('\u3000', '')
                                .replace('\n', '').replace(u'\xa0', u'')
                                if tt.parent.get('class') == ['s3']
                                else
                                '[' + tt + ']{.KaiTi}'.replace(
                                    '\u3000', ' ').replace('\n', '\n\n')
                                .replace(u'\xa0', u'').replace(u'\x20', u'')
                                if tt.parent.get('class') == ['h']
                                else
                                '[' + tt + ']{.FS}'.replace(
                                    '\u3000', ' ').replace('\n', '\n\n')
                                .replace(u'\xa0', u'').replace(u'\x20', u'')
                                if tt.parent.get('class') == ['q']
                                else tt.replace('\u3000', ' ')
                                .replace('\n', '\n\n').replace(u'\xa0', u'')
                                .replace(u'\x20', u'')
                                for tt in ccsoup.find_all(text=True)])
        print(chapter_text, file=outfile)
        print('\t\tDone!', end=' ')
        if ccsoup.find('img'):
            print('**IMG found**', end=' ')
        print('Now writing to output file:', title + '.md')
        # print(chapter_text)
    outfile.close()
    print("Extract completed!")

    print("Now post-processing the file...", end="")
    for line in fileinput.input(title + '.md', inplace=True):
        if not (re.search(r'目录页', line) or
                re.search(r'html', line) or
                re.search(r'Powered', line) or
                re.search(r'guoxue123', line) or
                re.search(r'Copyright', line) or
                re.search(r'国学导航', line) or
                re.search(r'首页', line)
                ):
            print(line, end='')
    print('All done!')


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from guoxue123")
    (options, args) = parser.parse_args()
    getdata(options.url)
