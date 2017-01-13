#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月14日

@author: lihui1
'''
import global_settings
import query_ip
import pickle
import vip_operation
from core import record_log
import db_connect
import sys
import time
import record_log
import send_mail
from send_mail import sendmail as sendmail
from db_connect import redis_op as redis_op

def lock_key_rw(data,key,timeou=20):
    while True:
        result,lock_key=redis_op.redis_lock(key,20)
        if result:
            know_problems_host_list=redis_op.get(key)
            if know_problems_host_list:
                know_problems_host_list=pickle.loads(know_problems_host_list)
                know_problems_host_list.append(data)
                know_problems_host_list=pickle.dumps(know_problems_host_list)
                redis_op.set(key,know_problems_host_list)
            else:
                value=[data,]
                know_problems_host_list=pickle.dumps(value)
                redis_op.set(key,know_problems_host_list)
            break
        else:
            continue
    redis_op.redis_delete(lock_key)

def fun_main(data_ip,vip):    
    #判断VIP挂载情况
    status=vip_operation.update_vip_mount_info(vip,data_ip)
#     if status==0:
#         subject='this is key:"vip_info:%s is not exists' % vip
#         body='this is key:"vip_info:%s is not exists,host data_ip is %s' % (vip,data_ip)
#         sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
#         redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
#         record_log.log('please check data in the redis,beacause this is key:"vip_info:%s" is not exists' % vip)
#         sys.exit(1)
    if status==2:
        subject='warings:vip mount information faile,%s' % vip
        body='vip:%s,data_ip:%s,vip check failed' % (vip,data_ip)
        sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
        #redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
        record_log.log('warings----vip mount information faile,host data_ip %s,vip %s' % (data_ip,vip))
        sys.exit(1)
    
    #取得是否脑裂的状态，当前这个VIP的KEY，还有VIP在每个节点上的挂载状态
    try:
        status,vip_info_key,vip_status=vip_operation.vip_health_check(vip)
    except Exception as e:
        record_log(e)
    
    #判断当前主机是否正在被处理中，如果是，则程序全部退出,know_problems
    alarm_host_list=redis_op.get('know_problems_host')
    if alarm_host_list:
        alarm_host_list=pickle.loads(alarm_host_list)
        if data_ip in alarm_host_list:
            record_log.log('host %s is exists know_problems,skip this check' % data_ip)
            sys.exit(1)
    
    #如果脑裂
    if status==2:
        #检查VIP是否已经无法ping通
        status=vip_operation.check_trouble_vip(vip)
        #如果VIP网络连通性正常
        if not status:
            #发邮件报警
            #db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
            subject='this is cluster split-brain，vip:%s' % vip
            body='vip:%s,data_ip:%s,this is cluster split-brain,please check cluster status' % (vip,data_ip)
            sendmail('dba@sogou-inc.com','lihui210694@sogou-inc.com',subject,body)
        #如果已经无法ping通
        else:
            try:
                lock_key_rw(data_ip,'know_problems_host')
                op_status=vip_operation.mysql_role_restart_keepalived(data_ip,vip)
                record_log.reslut_record(op_status,data_ip,vip)
            except Exception as e:
                record_log.log(e)
    #如果没有脑裂
    elif status==1:
        status=vip_operation.check_trouble_vip(vip)
        if not status:
            record_log.log('VIP is %s,cluster state is normal' % (vip))
        else:
            try:
                lock_key_rw(data_ip,'know_problems_host')
                op_status=vip_operation.mysql_role_restart_keepalived(data_ip,vip)
                record_log.reslut_record(op_status,data_ip,vip)
            except Exception as e:
                record_log.log(e)
    elif status==0:
        print 'this is a alerm,send information admin mobile'
        key='check_vip_inum:%s' % vip
        lock_key_rw(1,key)
        check_inum=redis_op.get(key)
        if len(check_inum==2):
            #db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
            redis_op.redis_delete(key)
        else:
            sys.exit(0)
    return 1