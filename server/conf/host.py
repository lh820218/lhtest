#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月10日

@author: lihui1
'''

import global_settings
import templates
from core import db_connect

rds=templates.LinuxTemple()
rds.hosts=[dip for hostip in db_connect.mysql_op.mysql_op('select masters from mysql_clusters_online where stat=1',op_type='read',Result_Status='Tuple') 
           for ip in hostip for dip in ip.split(',')]

monitor_group=[rds,]
