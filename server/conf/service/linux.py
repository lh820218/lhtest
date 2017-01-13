#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月3日

@author: lihui1
'''
import generic

class vip_check(generic.BaseService):
    def __init__(self):
        super(vip_check,self).__init__()
        self.plugin_name='get_vip_status'
        self.name='linux_vip'
        self.interval=300    #service_name
        self.trigger={
                      #'func':operation_vip_restart,  #在master上创建
                      'vip_num':2
                      }
        
