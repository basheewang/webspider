# import sys
import urllib.request
from bs4 import BeautifulSoup
import re

urls = [
    'https://chs.ebaomonthly.com/window/reading/chlit/ch1/chi1_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch2/chi2_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch3/chi3_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch4/chi4_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch5/ch5_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch6/ch6_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch7/ch7_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch8/ch8_cont.htm',
    'https://chs.ebaomonthly.com/window/reading/chlit/ch9/ch9_cont.htm',
]

outfile = open('kkkkk' + '.md', 'w', encoding='utf-8')

for url in urls:
    print('Get page: ' + url + '...')
    bc = urllib.request.urlopen(url).read().decode('big5', 'ignore')
    bcsoup = BeautifulSoup(bc, 'html.parser')

    url_pre = url[:len(url)-url[::-1].find('/')]

    for link in bcsoup.findAll('a'):
        if re.compile(r'ch.?\d+_\d+\.htm').search(link['href']):
            print('\tGeting data for ' + link.text.replace('\u3000', ' ') + '...')
            conts = urllib.request.urlopen(
                url_pre + link['href']).read().decode('big5', 'ignore')
            contsoup = BeautifulSoup(conts, 'html.parser')
            print(contsoup.text.replace('\u3000', ' '), file=outfile)

outfile.close()
