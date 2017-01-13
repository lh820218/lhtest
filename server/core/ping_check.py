#!/usr/bin/python
#coding:utf8
'''
Created on 2017年1月3日

@author: lihui1
'''

import re,os

def pingServer(vip):
    result=os.popen('ping -c 1 -w 1 %s' % vip)
    search_result=re.search('\d+%',result.read())
    if search_result.group() == '100%':
        ping_num=0
        while ping_num<=3:
            result=os.popen('ping -c 1 -w 1 %s' % vip)
            search_result=re.search('\d+%',result.read())
            if search_result.group() == '100%':
                ping_num+=1
                continue
            else:
                return 1
        return 0
    else:
        return 1