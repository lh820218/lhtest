#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月14日

@author: lihui1
'''
import global_settings
import RedisHelper
import query_ip
import pickle
import time
import db_connect
import random
import commands
import record_log
import sys

#更新vip挂载信息，写入redis的key vip_info:vip
def update_vip_mount_info(vip,data_ip):
    key='vip_info:%s' % vip
    vip_mount_info=exec_system_commands('ip ad sh|grep "%s/32"' % vip)
    result,lock_key=db_connect.redis_op.redis_lock(key,30)
    if result:
        if db_connect.redis_op.exists(key):
            result=db_connect.redis_op.get(key)
            result=pickle.loads(result)
            print result
        else:
            result=0
        if vip_mount_info:
            #1表示挂载了VIP，0表示未挂载VIP
            db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,1,100)
            record_log.log('%s is exists vip %s' % (data_ip,vip))
        else:
            db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,0,100)
            record_log.log('%s is not exists vip %s' % (data_ip,vip))
        db_connect.redis_op.redis_delete(lock_key)
        inum=0
        while True:
            time.sleep(1)
            result=db_connect.redis_op.get(key)
            result=pickle.loads(result)
            if len(result)==2:
                break
            else:
                if inum <=20:
                    inum+=1
                    continue
                else:
                    return 2
        return 1
    
#根据业务IP，找到对应的VIP关系
def read_redis_get_vip(data_ip):
    vip_host_key='host:' + data_ip
    vip=db_connect.redis_op.get(vip_host_key)
    return vip

#从redis中读取VIP状态
def read_redis_vip_info(vip):
    vip_info_key="vip_info:"+vip
    vip_status=db_connect.redis_op.get(vip_info_key)
    vip_status=pickle.loads(vip_status)
    return vip_info_key,vip_status
    
#检查vip是否出现脑裂,1表示脑裂，0表示没有脑裂
def vip_health_check(vip):
    vip_info_key,vip_status=read_redis_vip_info(vip)
    if vip_status:
        inum=0
        for key in vip_status:
            value=vip_status[key]
            if value==1:
                inum=inum+1
        #表示两台机器都存在VIP，脑裂
        if inum==2:
            record_log.log('this is cluster appears fissure %s' % vip)
            return 2,vip_info_key,vip_status
        #表示两台机器只有一台挂载VIP
        elif inum==1:
            record_log.log('this is cluster VIP no problems %s' % vip)
            return 1,vip_info_key,vip_status
        #表示VIP无挂载，报警
        elif inum==0:
            record_log.log('this is cluster keepalived faile,please check this is cluster keepalived,host is %s' % vip)
            return 0,vip_info_key,vip_status


#检查VIP是否存在无法ping通的REDIS列表中
def check_trouble_vip(vip):
    try:
        trouble_vip_list=db_connect.redis_op.get('trouble_vip')
        if trouble_vip_list:
            trouble_vip_list=pickle.loads(trouble_vip_list)
            if vip in trouble_vip_list:
                return 1
            else:
                return 0
    except Exception as e:
        record_log.log(e)
        return 0


#检查MYSQL状态
def check_mysql_status(data_ip,vip):
    try:
        result=db_connect.mysql_op.mysql_op('show processlist')
        session_num=len(result)
    except Exception as e:
        record_log.log(e)  
        return 0
    while True:
        try:
            result=db_connect.mysql_op.mysql_op('show slave status')
            result=result[0]
        except Exception as e:
            record_log.log(e)
            return 0
        if result['Slave_IO_Running']=='Yes' and result['Slave_IO_Running']=='Yes':    
            read_binlog=result['Master_Log_File']
            exec_binlog=result['Relay_Master_Log_File']
            read_binlog_pos=result['Read_Master_Log_Pos']
            exec_binlog_pos=result['Exec_Master_Log_Pos']
            behind_seconds=result['Seconds_Behind_Master']
        #如果binlog正在读取和正在回放的文件名一致,则返回落后秒数；否则,判断落后时间，如果是0重新获取，如果非0，则返回
            if read_binlog==exec_binlog:
                behind_sedond_time=behind_seconds
            else:
                if int(behind_seconds)==0:
                    continue
                else:
                    behind_sedond_time=behind_seconds
            sync_status=1
            break
        else:
            status='Flase'
            behind_sedond_time='N'
            sync_status=0
            break
    key='alarm:%s' % vip
    value=[session_num,behind_sedond_time,sync_status]
#     if not sync_status:
#         
#         sys.exit(1)
    while True:
        result,lock_key=db_connect.redis_op.redis_lock(key,20)
        if result:
            record_log.log('host %s get lock %s' %(data_ip,lock_key))
            result=db_connect.redis_op.get(key)
            if result:
                result=pickle.loads(result)
                db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,30)
            else:
                db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,0,key,value,30)
            db_connect.redis_op.redis_delete(lock_key)
            break
        else:
            continue
    return key
    
#判断当前MYSQL的角色,是主还是从
def mysql_is_role(data_ip,vip):
    redis_key=check_mysql_status(data_ip,vip)
    key='cluster_info:%s' % vip
    retry_num=0
    while True:
        if db_connect.redis_op.ping():
            mysql_info=db_connect.redis_op.get(redis_key)
            mysql_info=pickle.loads(mysql_info)
            #判断两个同步节点是否正常，如果不等于2，循环判断几次,如果都取不到长度为2的数据,就判断集群同步有问题
            if len(mysql_info)==2:
                #判断两个主机的同步信息状态是否都为1,如果有一个不是1,表示集群同步有问题
                sync_info_inum=0
                for host_key in mysql_info:
                    sync_info_inum+=mysql_info[host_key][2]
                if sync_info_inum==2:
                    key_list=mysql_info.keys()
                    #取得集群中另外一台机器的数据IP
                    key_list.remove(data_ip)
                    while True:
                        #获得锁
                        result,lock_key=db_connect.redis_op.redis_lock(key,10)
                        if result:
                            #判读落后时间,切两个主机的同步延时必须有一个为0
                            if mysql_info[key_list[0]][1] > mysql_info[data_ip][1] and mysql_info[data_ip][1]==0:
                                value=['M',0]
                                result=db_connect.redis_op.get(key)
                                if result:
                                    result=pickle.loads(result)
                                    db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,120)
                                else:
                                    db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,0,key,value,120)
                            elif mysql_info[key_list[0]][1] < mysql_info[data_ip][1] and mysql_info[key_list[0]][1]==0:
                                value=['S',0]
                                result=db_connect.redis_op.get(key)
                                if result:
                                    result=pickle.loads(result)
                                    db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,120)
                                else:
                                    db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,0,key,value,120)
                            elif mysql_info[key_list[0]][1] == mysql_info[data_ip][1]:
                                result=db_connect.redis_op.get(key)
                                if result:
                                    result=pickle.loads(result)
                                    #判断取回的数据长度为1时,切本机的数据IP不再这个结果中
                                    if len(result)==1 and data_ip not in result:
                                        if result[key_list[0]][0]=='M':
                                            value=['S',0]
                                            db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,120)
                                        elif result[key_list[0]][0]=='S':
                                            value=['M',0]
                                            db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,120)
                                else:
                                    value=['M',0]
                                    db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,0,key,value,45)
                            break
                        else:
                            time.sleep(random.random())
                            continue
                else:
                #当主从数据库任何一台处于非同步状态时返回0
                    return 0
            #当集群信息只有一个的时候，休眠，等待再次从REDIS中取回数据，检查列表长度
            else:
                time.sleep(random.random())
                if retry_num<=20:
                    retry_num+=1
                    record_log.log('waiting cluster info length is two,host is %s,retry is number %s ' % (data_ip,retry_num))
                    continue
                else:
                    return 1
        #当redis的连接串失效时，重建连接，并执行下次迭代
        else:
            db_connect.redis_op=db_connect.redis_conn()
            continue
        db_connect.redis_op.redis_delete(lock_key)
        return key

#判断重启对象的角色,先stop从库,并且stop成功,在重启主库
def mysql_role_restart_keepalived(data_ip,vip):
    retry_exec_command=1
    wait_slave_info=1
    wait_slave_exec_command=1
    key=mysql_is_role(data_ip,vip)
    time.sleep(random.random())
    while True:
        if key and key !=1:
            result=db_connect.redis_op.get(key)
            result=pickle.loads(result)
            host_list=result.keys()
            if len(host_list)==2:
                if result[data_ip][0]=='S':
                    if not result[data_ip][1]:
                        exec_time_status=check_operation_time()
                        if exec_time_status:
                            exec_status=exec_system_commands('/etc/init.d/mysqld stop')     
                            if exec_status:
                                value=['S',1]
                                db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,45)
                                clear_redis_info('know_problems_host',data_ip)
                                record_log.log('update exec system command result in the redis,host is %s,role_result %s,exec system result %s' % (data_ip,result[data_ip][0],value))
                            else:
                                if retry_exec_command<=3:
                                    retry_exec_command+=1
                                    record_log.log('retry shut keepalived,slave host is %s %d' % (data_ip,retry_exec_command))
                                    continue
                                else:
                                    clear_redis_info('know_problems_host',data_ip)
                                    return 2
                elif result[data_ip][0]=='M':
                    host_list.remove(data_ip)
                #判断从库执行命令的结果,命令执行成功后,才执行M的操作
                    if result[host_list[0]][1]:
                        exec_status=exec_system_commands('/etc/init.d/mysqld restart')
                        if exec_status:
                            value=['M',1]
                            db_connect.redis_op.redis_single_thread_read_write(db_connect.redis_op,data_ip,result,key,value,45)
                            clear_redis_info('know_problems_host',data_ip)
                            clear_redis_info('trouble_vip',vip)
                            db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
                            record_log.log('update exec system command result in the redis,%s %s %s' % (data_ip,result[data_ip][0],value))
                        else:
                            if retry_exec_command<=3:
                                time.sleep(random.random())
                                retry_exec_command+=1
                                record_log.log('retry shut keepalived,slave host is %s %d' % (data_ip,retry_exec_command))
                                continue
                            else:
                                clear_redis_info('know_problems_host',data_ip)
                                db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
                                return 3
                    else:
                        if wait_slave_exec_command<=3:
                            time.sleep(random.random())
                            wait_slave_exec_command+=1
                            record_log.log('waiting slave exec shut command,host is %s %d' % (data_ip,wait_slave_exec_command))
                            continue
                        else:
                            clear_redis_info('know_problems_host',data_ip)
                            db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
                            return 4 
            else:
                if wait_slave_info<=5:
                    time.sleep(random.random())
                    wait_slave_info+=1
                    record_log.log('waiting get slave infomation,host is %s,retry is number %d' % (data_ip,wait_slave_info))
                    continue
            return 1
        elif key==1:
            clear_redis_info('know_problems_host',data_ip)
            db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
            return 0
        elif key==0:
            clear_redis_info('know_problems_host',data_ip)
            db_connect.redis_op.set('vip_info:%s' % vip,pickle.dumps({}))
            return 5
        
#检查操作时间是否>=50秒，
def check_operation_time():
    if time.strftime('%S')>=50:
        return 1
    else:
        return 0

def exec_system_commands(command):
    status=commands.getstatusoutput(command)
    if status[0]==0:
        return 1
    else:
        return 0

def clear_redis_info(key,value):
    while True:
        result,lock_key=db_connect.redis_op.redis_lock(key,20)
        if result:
            know_problems_host_list=db_connect.redis_op.get(key)
            if know_problems_host_list:
                know_problems_host_list=pickle.loads(know_problems_host_list)
                know_problems_host_list.remove(value)
                know_problems_host_list=pickle.dumps(know_problems_host_list)
                db_connect.redis_op.set(key,know_problems_host_list)
                db_connect.redis_op.redis_delete(lock_key)
                break
        else:
            continue
    return 1