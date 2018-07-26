# import sys
import urllib.request
from bs4 import BeautifulSoup
import re

urls = ['http://writesprite.com/Pg-1-%E6%96%87%E5%AD%B8%E5%8F%B2'] + \
    ['http://writesprite.com/pagelist.php?catid=1&catname=%E6%96%87%E5%AD%B8%E5%8F%B2&s=' +
     str(i + 1) + '0' for i in range(47)]

outfile = open('ooooo' + '.txt', 'w', encoding='utf8')

for url in urls:
    print('Get page: ' + url + '...')
    bc = urllib.request.urlopen(url).read().decode('utf8', 'ignore')
    bcsoup = BeautifulSoup(bc, 'html.parser')

    url_pre = url[:len(url)-url[::-1].find('/')]

    for link in bcsoup.findAll('a'):
        if re.compile(r'detial.*').search(link['href']):
            print('\tGeting data for ' + link.text.replace('\u3000', '') + '...')
            conts = urllib.request.urlopen(
                url_pre + link['href']).read().decode('utf8', 'ignore')
            contsoup = BeautifulSoup(conts, 'html.parser')
            cont_text = contsoup.find('div', attrs={'class': 'l_side'})
            print(cont_text.text.replace('\u3000', ''), file=outfile)

outfile.close()
