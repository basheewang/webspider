#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: harvdlib.py

# import fileinput
import http
import http.cookiejar
import json
import os
# import time
import urllib
from optparse import OptionParser
from itertools import islice
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import hashlib


# Check duplicated files
def checkfile(title):
    # Generate md5 file
    print('Now generate md5.csv file, please wait...')
    md5file = open(os.path.curdir + os.sep + title + os.sep + 'md5.csv','w')
    mymd5 = {}
    dup_file = []
    print('File_Name,MD5_Value', file=md5file)
    for f in [os.path.curdir + os.sep + title + os.sep + f for f
              in os.listdir(os.path.curdir + os.sep + title) if f.endswith('.jpg')]:
        if generate_md5(f) in list(mymd5.values()):
            dupfile = list(mymd5.keys())[list(mymd5.values()).index(generate_md5(f))]
            print(f, 'has same md5 value as: ', dupfile)
            dup_file.append(f)
            dup_file.append(dupfile)
        mymd5[f]= generate_md5(f)
        print(f.split('\\')[-1], generate_md5(f), sep=',', file=md5file)
    print('MD5 file generated as: ', md5file.name)
    md5file.close()

    if len(dup_file) > 0:
        for f in list(set(dup_file)):
            os.remove(f)
            print(f, ' has been deleted!')
        print('There are total ', str(len(dup_file)), ' files deleted!')
        print('Now rerun the command to downloaded.')


# For generate md5
def generate_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

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
    # wait_time = 5
    if not os.path.exists(os.path.join(os.path.curdir, title)):
        os.mkdir(os.path.join(os.path.curdir, title))

    timeout_list=[]
    # for idx, img in islice(enumerate(bpj['sequences'][0]['canvases']), 0, 30):
    for idx, img in enumerate(bpj['sequences'][0]['canvases']):
        # img_url.append(img['images'][0]['resource']['@id'])
        pic_url = img['images'][0]['resource']['@id']
        fn = os.path.join(
            os.path.curdir, title,
            '{:0{no}d}'.format(idx + 1, no=page_no) + '_' + pic_url.split('/')[-1])
        print(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "\t[" + '{:0{no}d}'.format(idx + 1, no=page_no) +
            "/" + str(total_page) + "]",
            pic_url, end=' ')

        if os.path.isfile(fn):
            print('File existed, ignored!')
            continue
        try:
            raw = requests.get(pic_url, timeout=5)
            if int(raw.headers['Content-length']) > 10000:
                with open(fn, 'wb') as outfile:
                    outfile.write(raw.content)
                    print('Downloaded!')
            else:
                print('File too small, skipped!')
        except:
            print('\n\t\tTime out! continue to next image.')
            timeout_list.append((pic_url,fn))

        # print("Wait", wait_time, "seconds...")
        # for i in range(wait_time)[::-1]:
        #     time.sleep(1)
        #     print("%d\r" % (i))

    print('There are',len(timeout_list), 'images time out, Now getting them:')
    i = 0
    while len(timeout_list) > 0:
        for pic_url in timeout_list:
            i += 1
            print('[' + str(i) + '/' + str(len(timeout_list)) + '] Retrieving',
                  pic_url[0], '...', end=' ')
            try:
                raw = requests.get(pic_url[0], timeout=5)
                timeout_list.remove(pic_url)
            except:
                print('\n\t\tTime out! continue to next image.')
                # timeout_list.append(pic_url)
            if int(raw.headers['Content-length']) > 10000:
                with open(pic_url[1], 'wb') as outfile:
                    outfile.write(raw.content)
                    print(pic_url[1].split('\\')[-1] + ' Downloaded!')
            else:
                print('File too small, skipped!')

    checkfile(title)
                
        
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from Harvard University Library")
    parser.add_option("-t", "--title", default='temp', dest="title",
                      help="The folder you want to save in.")
    parser.add_option("-l", "--listurl", default='', dest="listurl",
                      help="The url of a list of vols form a book.")
    parser.add_option("-s", "--startvol", default=1, dest="startvol",
                      help="The url of a list of vols form a book.")
    (options, args) = parser.parse_args()
    if len(options.listurl) > 10:
        vol_list = []
        vol_url = ''
        vol_cont = urllib.request.urlopen(
            options.listurl).read().decode('utf8', 'ignore')
        vol_soup = BeautifulSoup(vol_cont, 'html.parser')
        for url in vol_soup.find('table').findAll('a'):
            vol_list.append(url['href'])
        vol = len(vol_list)
        print("There are total", vol, "volumes for this book.")
        # for idx, url in enumerate(vol_list):
        for idx, url in islice(enumerate(vol_list), int(options.startvol) - 1, vol):
            try:
                print("Now working on the Vol.", idx + 1, "...")
                json_cont = urllib.request.urlopen(
                    url).read().decode('utf8', 'ignore')
            except urllib.error.HTTPError:
                # if ValueError == "HTTP Error 404: Not Found":
                continue
    
            for script in BeautifulSoup(json_cont, 'html.parser').findAll('script'):
                if 'window.harvard_md_server' in script.text:
                    # voljson = json.loads(script.text)
                    vol_url = re.compile(
                        r'"loadedManifest": "(.*)",').search(script.text).group(1)
                    break
            getdata(vol_url, options.title + '_' +
                    '{:0{no}d}'.format(idx + 1, no=len(str(vol))))
    else:
        getdata(options.url, options.title)

