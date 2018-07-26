#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: guoxue123.py

import fileinput
import http
import http.cookiejar
import re
import time
import urllib
from optparse import OptionParser

from bs4 import BeautifulSoup


# For debug purpose.
def saveFile(data, s, coding='utf8'):
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
        decode('utf8', 'ignore')
    contsoup = BeautifulSoup(book_contents, 'html.parser')
    # contsoup.find('h2', attrs={'class': 'wikiitemtitle'}).span.decompose()
    if 'wiki.pl' in url:
        contsoup.find('h2').span.decompose()
    title = contsoup.find('h2').text
    book_contents_url = []
    if 'wiki.pl' in url:
        content = contsoup.find('div', attrs={'class': 'ctext'})
        for link in content.find_all('a'):
            # print(link)
            book_contents_url.append((url[:url.find('g/') + 2] + link['href'],
                                      link.text.replace('\u3000', ' ')))
    else:
        pattern = url.split(' / '.strip())[3]
        book_contents_url = \
            [(url[:url.find('g/') + 2] + hl['href'], hl.text)
             for hl in contsoup.find_all(
                'a', attrs={'class': None})
                if re.compile(pattern + '/\d').search(hl['href'])]

    print('Book contents extraction done, there are total',
          len(book_contents_url), 'chapters.')

    outfile = open(title + '.md', 'w', encoding='utf-8')

    print('Now begin to extract each chapter contents:')
    for ch in book_contents_url:

        # wait_time = 10
        # print("Wait", wait_time, "seconds...")
        # for i in range(wait_time)[::-1]:
        #     time.sleep(1)
        #     print("%d\r" % (i), end='')

        print('\tExtracting data for:', ch[1], '...')
        chapter_contents = urllib.request.urlopen(
            ch[0]).read().decode('utf8', 'ignore')
        csoup = BeautifulSoup(chapter_contents, 'html.parser')
        if 'wiki.pl' in url:
            csoup.find(
                'h2', attrs={'class': 'wikisectiontitle'}).span.decompose()
            chp_title = csoup.find(
                'h2', attrs={'class': 'wikisectiontitle'}).text
        else:
            chp_title = '\n'.join([h2.text for h2 in csoup.find_all('h2')])
        print('\n# ' + chp_title + ' #\n', file=outfile)

        chapter_text = ''
        for td in csoup.find_all('td', attrs={'class': 'ctext', 'style': None}):
            try:
                td.div.decompose()
                td.p.decompose()
            except:
                None
            # for tc in td.children:
            #     print(tc)
            chapter_text += ''.join([str(t) for t in td.contents]) + '\n'
        # chapter_text = '\n\n'.join([td.text for td in csoup.find_all(
        #     'td', attrs={'class': 'ctext', 'style': None})])
        # chapter = csoup.find('td', attrs={'width': '87%'})
        # chapter = csoup.find('table', attrs={'border': '1'})
        # chapter_text = ''.join(['# ' + tt + ' #'.replace('\u3000', '')
        #                         .replace('\n', '').replace(u'\xa0', u'')
        #                         if tt.parent.get('class') == ['s3']
        #                         else
        #                         '[' + tt + ']{.KaiTi}'.replace(
        #     '\u3000', '').replace('\n', '\n\n')
        #     .replace(u'\xa0', u'').replace(u'\x20', u'')
        #     if tt.parent.get('class') == ['q']
        #     else tt.replace('\u3000', '')
        #     .replace('\n', '\n\n').replace(u'\xa0', u'')
        #     .replace(u'\x20', u'')
        #     for tt in csoup.find_all(text=True)])
        print('\t\tDone! Now writing to output file:', title + '.md')
        print(chapter_text, file=outfile)
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
