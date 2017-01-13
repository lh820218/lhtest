#!/usr/bin/python
#coding:utf8
'''
Created on 2016年12月30日

@author: lihui1
'''

from core import client_api
from core.db_connect import redis_op as redis_op
from core import query_ip
from core import vip_operation
from core import record_log
import sys,time,pickle
import threading

class ClientMonitor(object):
    def __init__(self):
        try:
            self.data_ip=query_ip.get_data_ip()
            self.vip=vip_operation.read_redis_get_vip(self.data_ip)
        except:
            record_log.log('get data_ip or vip error,please check!')
            sys.exit(1)
        
    def format_msg(self,key,value):
        msg = {key: value}
        return pickle.dumps(msg)
    
    def config_update(self,update_key,configs):
        configs=pickle.dumps(configs)
        redis_op.set(update_key,configs)
        
    
    def get_configs(self):
        count = 1 
        while count<30:
            configs = redis_op.get("config:%s" % self.data_ip)
            if configs:
                return pickle.loads(configs) 
            else:
                count +=1
                time.sleep(1)
    
    def handle(self):
        self.configs = self.get_configs()
        if self.configs['services']: 
            #{'services': {'linux_memory': [30, 'get_memory_info', 0], 'linux_cpu': [30, 'get_cpu_status', 0]}}
            while True:
                for service_name,val in self.configs['services'].items():
                    interval,plugin_name,last_check = val
                    next_run_time = interval - (time.time() - last_check)
                    if time.time() - last_check >= interval:
                        t = threading.Thread(target=self.task_run,args=[service_name,plugin_name,])
                        t.start()
                        self.configs['services'][service_name][2] = time.time()
                        self.config_update("config:%s" % self.data_ip,self.configs)
                    else:
                        time.sleep(10)
        else:
            record_log.log('---nothing to monitor,configs dict is empty---')
    
    def task_run(self,service_name,plugin_name):
        plugin_func = getattr(client_api,plugin_name)
        result = plugin_func(self.data_ip,self.vip)
        if service_name != 'linux_vip':
            msg = self.format_msg('report_service_data', 
                                {'ip': self.data_ip,
                                 'service_name':service_name,
                                 'data': result,
                                                })
            self.redis.public(msg)
   
    def run(self):
        self.handle()
if __name__ == '__main__':
    c = ClientMonitor()
    c.run()
    
    
    