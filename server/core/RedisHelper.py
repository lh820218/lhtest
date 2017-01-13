#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月1日

@author: lihui1
'''
import redis
import time
import variables
import pickle

class RedisHelper():
    def __init__(self):
        self.__conn=redis.Redis(host=variables.redis_host,password=variables.redis_password)
#订阅频道
        self.sub=variables.redis_channel
#发布频道
        self.pub=variables.redis_channel

#redis 发布功能  
    def public(self,msg):
        self.__conn.publish(self.pub,msg)
        return True
    
    def set(self,key,value):
        self.__conn.set(key,value)
        
    def get(self,key):
        value=self.__conn.get(key)
        return value
    
    def redis_delete(self,key):
        self.__conn.delete(key)
        
#加锁，如果redis存在key='lock.'+key，返回失败，否则成功；
    def redis_lock(self,key,timeout):
        key='lock.'+key
        result=self.__conn.setnx(key,1)
        self.key_expire(key, timeout)
        return result,key

#redis订阅功能
    def subscribe(self):
        pub=self.__conn.pubsub()
        pub.subscribe(self.sub)
        pub.parse_response()
        return pub
    
    def ping(self):
        if self.__conn.ping():
            return True
        else:
            return False
    
    def key_expire(self,key,timeout):
        if timeout:
            result=self.__conn.expire(key,int(timeout))
            if result:
                return 1
            else:
                return 0
        
    #单线程读写redis
    def redis_single_thread_read_write(self,redis_op,data_ip,result,key,value,timeout):
        if result:
            result[data_ip]=value
            result=pickle.dumps(result)
            self.set(key,result)
            self.key_expire(key,timeout)
        else:
            result={}
            result[data_ip]=value
            result=pickle.dumps(result)
            self.set(key,result)
            self.key_expire(key,timeout)

# 
# redis_op=RedisHelper()
# 
# while True:
#     a=redis_op.subscribe()
#     print a.parse_response()
