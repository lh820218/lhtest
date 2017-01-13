#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月14日

@author: lihui1
'''

import socket
import record_log

def get_domain_a(domain):
    try:
        result=socket.getaddrinfo(domain,None)
        ip=result[0][4][0]
        if ip:
            return ip
        else:
            message='get domain(%s) in A is not exists' % (domain)
            record_log.log(message)
            return 0
    except Exception as e:
        record_log.log(e)
        return 0
