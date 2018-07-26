#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: guoxue123.py

from optparse import OptionParser
import re
import ipdb


def getLineLen(filename):
    infile = open(filename, 'r', encoding='utf8')
    i = 0
    for line in infile.readlines():
        # ipdb.set_trace()
        i += 1
        if re.compile(r'^## ').search(line):
            print('Name found! -->', line)
        elif re.compile(r'^$').search(line):
            None
        else:
            if len(line) <= 10:
                print(i, ':', 'A title found')
            else:
                print(i, ':', len(line))
        if i >= 100:
            break


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", default='', dest="url",
                      help="The url of a book from guoxue123")
    parser.add_option("-f", "--input", default='', dest="infile",
                      help="Input file name")
    (options, args) = parser.parse_args()
    getLineLen(options.infile)
