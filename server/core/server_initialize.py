#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月3日

@author: lihui1
'''
import global_settings
import db_connect
from conf.host import monitor_group
import pickle,time

def build_config(client_ip):
    applied_services = []
    configs={
             'services':{},
             }
    for group in monitor_group:
        for host_ip in group.hosts:
            if host_ip==client_ip:
                applied_services.extend(group.services)
        applied_services=set(applied_services)
        
    for service_class in applied_services: #serialize instance to dict 
        service_ins = service_class()
        #print service_ins.name, service_ins.interval,service_ins.plugin_name
        configs['services'][service_ins.name] = [service_ins.interval,service_ins.plugin_name, 0]
    return configs

def flush_all_host_configs_into_redis(): 
    applied_host=[]
    for group in monitor_group:
        applied_host.extend(group.hosts)
        applied_host=set(applied_host)
    for host_ip in applied_host:
        configs=build_config(host_ip)
        redis_key='config:%s' % host_ip
        redis_op=db_connect.redis_op
        redis_op.set(redis_key,pickle.dumps(configs))
