#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: gushiwen.py

from selenium import webdriver
import selenium
from optparse import OptionParser
from bs4 import BeautifulSoup
import urllib.parse
import re


# For debug purpose.
def saveFile(data, s, coding='utf8'):
    # save_path = 'temp.out'
    f_obj = open('temp_' + s + '.html', 'wb')
    f_obj.write(bytes(data, coding))
    f_obj.close()


def convert2url(title, author=''):
    gsw_url = 'https://so.gushiwen.org/search.aspx?value='
    query = ''
    if len(author) > 0:
        query = urllib.parse.quote(title) + '%2B' + \
            urllib.parse.quote(author)
    else:
        query = urllib.parse.quote(title)

    return gsw_url + query


def getcontent(url, number):
    pc = webdriver.Chrome()
    pc.set_page_load_timeout(10)
    pc.get(url)
    try:
        print("Extract poems related to", title,
              'and', author, 'as author')
    except NameError:
        print("Extract poems related to", title)

    # pc.find_element_by_id("btnShangxibee5c2e9ddfe").click()
    # pc.find_element_by_id("btnZhushibee5c2e9ddfe").click()
    # pc.find_element_by_id("btnYiwenbee5c2e9ddfe").click()

    ppc = pc.page_source
    ppc_soup = BeautifulSoup(ppc, "html.parser")
    so_url = 'https://so.gushiwen.org'  # /shiwenv_ccee5691ba93.aspx
    all_links = [a['href'] for a in
                 ppc_soup.findAll('a', attrs={'target': '_blank'})
                 if 'shiwenv' in a['href']]

    CRED = '\033[91m'
    CEND = '\033[0m'
    all_poem = []
    total_page = 0
    try:
        total_page = ppc_soup.find('label', attrs={'id': 'sumPage'}).text
    except AttributeError:
        print(CRED + "No poems found, please check your keywords!" + CEND)
        return all_poem
    if int(total_page) > 1:
        print("Poems which contains", title,
              "have more than 10, will extract the first 2 pages only!")
        p2_pre = 'https://so.gushiwen.org/search.aspx?type=title&page=2&'
        p2_url = p2_pre + url.split('?')[-1]
        try:
            pc.get(p2_url)
            p2pc_soup = BeautifulSoup(pc.page_source, "html.parser")
            all_links2 = [a['href'] for a in
                          p2pc_soup.findAll('a', attrs={'target': '_blank'})
                          if 'shiwenv' in a['href']]
            for l2 in all_links2:
                all_links.append(l2)
        except selenium.common.exceptions.TimeoutException:
            None
    poem_links = [so_url + url for url in all_links[:number]]

    j = 1
    for link in poem_links:
        print("To extract", j, "out of", len(poem_links), "...", end=' ')
        try:
            pc.get(link)
        except selenium.common.exceptions.TimeoutException:
            continue
        poem_id = link.split('/')[-1].split('_')[-1].split('.')[0]
        content_only = [False, False, False]
        i = 0
        for btn in ['btnShangxi', 'btnZhushi', 'btnYiwen']:
            try:
                pc.find_element_by_id(btn + poem_id).click()
            except selenium.common.exceptions.ElementNotInteractableException:
                content_only[i] = True
            i += 1
        if False not in content_only:
            print("Skipped for poem which has contents only!")
            j += 1
            continue
        poem = pc.page_source
        poem_soup = BeautifulSoup(poem, "html.parser")
        poem_title = poem_soup.find('h1').text
        poem_author = poem_soup.find('p', attrs={'class': 'source'}).text
        print(poem_title, poem_author + "\n", end='')
        if False in content_only:
            poem_cont = poem_soup.find(
                'div', attrs={'class': 'contson'}).findAll('p')[:-1]
            # continue
        else:
            poem_cont = poem_soup.find(
                'div', attrs={'class': 'contson'})
        all_poem.append(['\n## ' + poem_title + ' ##\n',
                         '**' + poem_author + '**\n', poem_cont])
        # print('Hi')
        j += 1

    pc.quit()

    return all_poem


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from Harvard University Library")
    parser.add_option("-t", "--title", default='一些诗词', dest="title",
                      help="The document title of the md file.")
    parser.add_option("-n", "--number", default=None, dest="number",
                      help="The number of poems want to get if more than 10.")
    parser.add_option("-f", "--file", default='mypoem', dest="file",
                      help="The file which contains title and author of the poem.")
    parser.add_option("-o", "--output", default='poem.md', dest="output",
                      help="The output markdown file name.")
    (options, args) = parser.parse_args()

    myallpoem = []
    myfile = open(options.output, 'a')
    print("Now write to markdown file", options.output, "...")
    print('% ' + options.title, file=myfile)
    for line in open(options.file, 'r').readlines():
        try:
            title = re.split(r'\s+', line.strip())[0].strip()
            author = re.split(r'\s+', line.strip())[1].strip()
            if options.number is None:
                mypoem = getcontent(convert2url(title, author),
                                    options.number)
            else:
                mypoem = getcontent(convert2url(title, author),
                                    int(options.number))
        except IndexError:
            title = line.strip()
            if options.number is None:
                mypoem = getcontent(convert2url(title), options.number)
            else:
                mypoem = getcontent(convert2url(title), int(options.number))
        print('\n# 关于', title, '的诗词 #\n', file=myfile)
        myallpoem.append(mypoem)
        for line in mypoem:
            for ele in line:
                if isinstance(ele, list):
                    for e in ele:
                        print(e, file=myfile)
                else:
                    print(ele, file=myfile)

    myfile.close()
    print('Done!')
