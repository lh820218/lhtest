#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月14日

@author: lihui1
'''

import logging
from send_mail import sendmail as sendmail

def log(message):
    logging.basicConfig(level=logging.DEBUG,  
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/tmp/test.log',
                        filemode='a')  
    logging.debug(message)
    
    
def reslut_record(op_status,data_ip,vip):
    if op_status==0:
        log('host %s Cluster information abnormal' % data_ip)
        subject='cluster information abnormal,vip %s' % vip
        body='vip:%s,data_ip:%s,this is Cluster information abnormal,please check cluster information' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
    elif op_status==1:
        log('keepalived is restart success,host is %s' % data_ip)
        subject='cluster keepalived is restart success,vip:%s' % vip
        body='vip:%s,data_ip:%s,this is cluster keepalived is restart success' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
    elif op_status==2:
        log('slave %s exec system command failed' % data_ip)
        subject='slave %s exec system command failed' % data_ip
        body='vip:%s,data_ip:%s,slave exec system command failed,pleases check slave exec log' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
    elif op_status==3:
        log('master %s exec system command failed' % data_ip)
        subject='master %s exec system command failed' % data_ip
        body='vip:%s,data_ip:%s,master exec system command failed,pleases check master exec log' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
    elif op_status==4:
        log('VIP is %s,master is %s,waitting slave the exec result timeout,read result information in the redis' % (vip,data_ip))
        subject='waitting slave the exec result timeout,vip:%s' % vip
        body='VIP is %s,master is %s,waitting slave the exec result timeout,read result information in the redis' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)