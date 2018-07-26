import re
import sys

infile = open(sys.argv[1], 'r', encoding='utf-8')
outname = sys.argv[1].split('.')[0] + '_new' + '.md'
outfile = open(outname, 'w', encoding='utf8')

i = 0
ii = 0
pflag = False

for line in infile.readlines():
    i += 1
    # print(line)
    if re.compile('【').search(line):
        ii += 1
        pflag = True
        print(line, file=outfile)
    elif re.compile(r'[·○#]|凡.篇|曰：|云：|──').search(line):
        print(line, file=outfile)
    elif pflag is True and len(line) > 1:
        newline = re.sub(r'([，。？！；：]”?)', r'\1 ', line)
        for p in newline.split(' '):
            if len(p) > 1:
                print(ii, p, file=outfile)
    elif len(line) == 1:
        print(line, file=outfile)
    else:
        print(line, file=outfile)
        pflag = False
