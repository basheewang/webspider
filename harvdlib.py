#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: harvdlib.py

# import fileinput
import http
import http.cookiejar
import json
import os
import time
import urllib
from optparse import OptionParser
from itertools import islice
import requests


# For debug purpose.
def saveFile(data, s, coding='utf8'):
    # save_path = 'temp.out'
    f_obj = open('temp_' + s + '.html', 'wb')
    f_obj.write(bytes(data, coding))
    f_obj.close()


# Main function
def getdata(url, title):
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
    print('Try to extract book json contents...', end=" ")
    json_contents = urllib.request.urlopen(url).read().\
        decode('utf8', 'ignore')
    print('Done!')
    bpj = json.loads(json_contents)
    # img_url = []
    total_page = len(bpj['sequences'][0]['canvases'])
    print("There are total ", total_page, "pictures need to be downloaded.")
    page_no = len(str(len(bpj['sequences'][0]['canvases'])))
    wait_time = 5
    if not os.path.exists(os.path.join(os.path.curdir, title)):
        os.mkdir(os.path.join(os.path.curdir, title))

    # for idx, img in islice(enumerate(bpj['sequences'][0]['canvases']), 0, 30):
    for idx, img in enumerate(bpj['sequences'][0]['canvases']):
        # img_url.append(img['images'][0]['resource']['@id'])
        pic_url = img['images'][0]['resource']['@id']
        fn = os.path.join(
            os.path.curdir, title,
            '{:0{no}d}'.format(idx + 1, no=page_no) + '_' + pic_url.split('/')[-1])
        print(
            "\t[" + '{:0{no}d}'.format(idx + 1, no=page_no) +
            "/" + str(total_page) + "] Download",
            pic_url, end=' ')

        if os.path.isfile(fn):
            print('File existed, ignored!')
            continue
        raw = requests.get(pic_url)
        if int(raw.headers['Content-length']) > 10000:
            with open(fn, 'wb') as outfile:
                outfile.write(raw.content)
            print('Downloaded!')
        else:
            print('File too small, skipped!')

        print("Wait", wait_time, "seconds...")
        # for i in range(wait_time)[::-1]:
        #     time.sleep(1)
        #     print("%d\r" % (i))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from guoxue123")
    parser.add_option("-t", "--title", default='temp', dest="title",
                      help="The url of a book from guoxue123")
    (options, args) = parser.parse_args()
    getdata(options.url, options.title)
