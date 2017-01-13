#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月3日

@author: lihui1
'''

from service import linux

class BaseTemp(object):
    def __init__(self):
        self.name=''
        self.group=''
        self.hosts=[]
        self.service=[]

class LinuxTemple(BaseTemp):
    def __init__(self):
        super(LinuxTemple,self).__init__()
        self.group_name='linux_server'
        self.name='LinuxTemple'
        self.services=[
                      linux.vip_check,
                      ]
        
