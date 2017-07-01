#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import sys
import socket
import time
import getpass
import os
import subprocess
import difflib
import webbrowser
import tkinter
from tkinter.filedialog import *

__Author__ = 'Yuanhao Wu'
__version__ = '1.1'
__time__ = '2017-03-21'
__email__ = 'yuanhao.wu@ericsson.com'


def choose():
    # 调用Tk()的任何方法都会显示根窗口，特意定义master并用withdraw隐藏根窗口
    master = tkinter.Tk()
    master.withdraw()
    choices = askopenfilenames()
    return choices


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
                if locked == 1:
                    # 为了避免/r/n和/n的问题，直接rstrip()并替换上\n
                    line = line.rstrip()[start_char:] + '\n'
                    text.append(line)
                else:
                    if 'gsh ' in line:
                        start_char = line.find('gsh ')
                        locked = 1
            return text
    except IOError as e:
        print('Open File ERROR: {}'.format(e))
        exit(-1)


def go():
    # start_time = time.time()
    '''try:
        file1 = '{}\\cfg1.log'.format(os.path.split(os.path.realpath(__file__))[0])
        file2 = '{}\\cfg2.log'.format(os.path.split(os.path.realpath(__file__))[0])
    '''

    try:
        file1, file2 = choose()
        if file1 == '' or file2 == '':
            raise NameError('InputError')
    except Exception as e:
        print('Error: {}'
              'Usage: compare_cfg.py filename1 filename2'.format(e))
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

start_time = time.time()*1000 #the start time
#define the function of sending logs
def sendlog(startTime,toolID):
    userName = getpass.getuser()  # to get the user
    hostIP = socket.gethostbyname(socket.gethostname())  # to get the host IP
    logPath = "C:/Users/" + userName + "/AppData/Roaming/"
    logFileName = str(sys.argv[0][sys.argv[0].rfind(os.sep) + 1:]).split(".")[0].split("/")[-1] + "python.log"
    # print str(sys.argv[0][sys.argv[0].rfind(os.sep)+1:]).split(".")[0].split("/")[-1]

    remoteIP = "10.185.59.51"
    remotePort = 9991
    endTime = time.time() * 1000
    log = "[{" + chr(34) + "eid" + chr(34) + ":" + chr(34) + str(userName) + chr(34) + "," + chr(34) + "toolUID" + chr(
        34) + ":" + chr(34) + str(toolID) + chr(34) + "," + chr(34) + "startTime" + chr(34) + ":" + str(
        startTime) + "," + chr(34) + "endTime" + chr(34) + ":" + str(endTime) + "," + chr(34) + "ipAddr" + chr(
        34) + ":" + chr(34) + str(hostIP) + chr(34) + "}]"
    pingTest = subprocess.call('ping -n 2 %s'% remoteIP, stdout=open('nul', 'w'), stderr=subprocess.STDOUT)
    if pingTest==1:
        f = open(logPath + logFileName, "a+b")
        f.write(log + "\n")
        f.close()
    elif pingTest==0:
        s_tm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # define the socket using TCP
        s_tm.connect((remoteIP, remotePort))  # connect to server
        s_tm.sendall(("[{" + chr(34) + "eid" + chr(34) + ":" + chr(34) + str(userName) + chr(34) + "," + chr(34) + "toolUID" + chr(
        34) + ":" + chr(34) + "1759320e-e845-451d-b315-19c8614c7a69" + chr(34) + "," + chr(34) + "startTime" + chr(34) + ":" + str(
        startTime) + "," + chr(34) + "endTime" + chr(34) + ":" + str(endTime) + "," + chr(34) + "ipAddr" + chr(
        34) + ":" + chr(34) + str(hostIP) + chr(34) + "}]").encode(encoding='utf-8'))  # send to logs
        s_tm.close()  # close the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # define the socket using TCP
        s.connect((remoteIP, remotePort))  # connect to server
        s.sendall(log.encode(encoding='utf-8'))  # send to logs
        s.close()  # close the socket
        is_file = os.path.isfile(logPath + logFileName)
        if is_file:
            f_log = open(logPath + logFileName, "r+b")
            for line in f_log.readlines():
                old_log = line.strip("\n")
                s_log = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_log.connect((remoteIP, remotePort))
                s_log.sendall(old_log.encode(encoding='utf-8'))
                s_log.close()
            f_log.close()
            os.remove(logPath + logFileName)

########################
# Main function starts #
########################

go()

########################
# Main function stops  #
########################

toolID = "d0eaa59e-219f-4a86-93da-b1fbb5eb5969"  # your toolID from Lighthouse
sendlog(start_time,toolID)
