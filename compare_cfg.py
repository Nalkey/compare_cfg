#!/usr/bin/env python3
# coding: utf-8

import difflib
import os
import time
import webbrowser

__Author__ = 'Yuanhao Wu'
__version__ = '1.0'
__time__ = '2017-03-21'
__email__ = 'yuanhao.wu@ericsson.com'


def readfile(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as fd:
            lines = fd.read().splitlines()
            text = []
            start_char = 0
            locked = 0
            # lines为字符串的数组，需要对每行进行处理，去掉头部时间戳
            for line in lines:
                # 因为log每行时间戳长度固定，为了加速，不用每行都判断gsh的起始位置
                if locked == 0 and 'gsh ' in line:
                    start_char = line.find('gsh ')
                    locked = 1
                # 为了避免/r/n和/n的问题，直接rstrip()并替换上\n
                line = line.rstrip()[start_char:] + '\n'
                text.append(line)
            return text
    except IOError as e:
        print('Open File ERROR: {}'.format(e))
        exit(-1)


def go():
    # start_time = time.time()
    try:
        file1 = '{}\\cfg1.log'.format(os.path.split(os.path.realpath(__file__))[0])
        file2 = '{}\\cfg2.log'.format(os.path.split(os.path.realpath(__file__))[0])
        if file1 == '' or file2 == '':
            raise NameError('InputError')
    except Exception as e:
        print('''Error: {}
        Usage: compare_cfg.py filename1 filename2'''.format(e))
        exit(-1)

    cfg1 = readfile(file1)
    cfg2 = readfile(file2)

    # 结果会分屏，每边65列适合HP Probook 640的屏幕宽度
    d = difflib.HtmlDiff(wrapcolumn=65)
    result = '{}\\result{}.html'.format(os.path.split(os.path.realpath(__file__))[0],
                                        time.strftime('%y%m%d%H%M'))
    try:
        with open(result, 'w', encoding='utf-8') as fd:
            fd.write(d.make_file(cfg1, cfg2))
    except Exception as e:
        print('Write File ERROR: {}'.format(e))

    webbrowser.open_new_tab(result)
    # print('{:.1f}'.format(time.time() - start_time))
    # exit(0)
