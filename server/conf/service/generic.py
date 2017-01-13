#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月3日

@author: lihui1
'''
class BaseService(object):
    def __init__(self):
        self.plugin_name='plugin name'
        self.name='service name'
        self.interval=300
        self.last_time=0

