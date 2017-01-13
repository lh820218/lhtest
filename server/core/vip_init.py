#!/usr/bin/python
#coding:utf8
'''
Created on 2016年12月28日

@author: lihui1
'''
import global_settings
from core import db_connect
import pickle
from core.get_dns_info import get_domain_a
import ping_check
import record_log
from db_connect import redis_op

def vip_init():
    rds_vip=[hostip for hostip in db_connect.mysql_op.mysql_op('select write_domain,masters from mysql_clusters_online where stat=1',op_type='read',Result_Status='Tuple')]
    for vip_info in rds_vip:
        vip=get_domain_a(vip_info[0])
        if not vip:
            record_log.log('service domain get A record FAILED,domain is %s' % vip_info[0])
        vip_value=pickle.dumps({})
        vip_list=redis_op.get('vip_list')
        if vip_list:
            vip_list=pickle.loads(vip_list)
            vip_list.append(vip)
        else:
            vip_list=[]
            vip_list.append(vip)
        vip_list=pickle.dumps(vip_list)
        redis_op.set('vip_list',vip_list)
        db_connect.redis_op.set('vip_info:%s' % vip,vip_value)
        for data_ip in vip_info[1].split(','):
            db_connect.redis_op.set('host:%s' % data_ip,vip)