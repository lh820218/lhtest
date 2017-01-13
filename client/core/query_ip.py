#!/usr/bin/python
#coding:utf8

import socket
import fcntl
import struct
import commands

#指定设备名获取IP
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

#获取VIP地址
def get_vip_address():
    command="%s ad sh|sed -n '/127.0.0.1/{n;p;}'|grep '^ *inet [0-9]\{1,3\}\.'|awk '{print $2}'|awk -F'/' '{print $1}'" % ('/sbin/ip')
    exec_result=commands.getstatusoutput(command)
    lo_vip=exec_result[1]
    if exec_result[0] == 0 and not lo_vip:
        command="%s ad sh|grep '/32'|awk '{print $2}'|awk -F'/' '{print $1}'" % ('/sbin/ip')
        exec_result=commands.getstatusoutput(command)
        vip=exec_result[1]
    else:
        command="%s ad sh|grep -v %s|grep '/32'|awk '{print $2}'|awk -F'/' '{print $1}'" % ('/sbin/ip',lo_vip)
        exec_result=commands.getstatusoutput(command)
        vip=exec_result[1]
    if not vip:
        return 0
    else:
        return vip

#获取业务网IP
def get_data_ip():
    command="%s -a|awk -F'.' '{print $3"'"."'"$4}'|sort -nr |uniq -c|awk '{if ($1>1) print $2}'" % 'sogou-host'
    exec_result=commands.getstatusoutput(command)
    if exec_result[0]==0:
        command="%s -a|grep %s" %("sogou-host",exec_result[1])
        exec_result=commands.getstatusoutput(command)
        if exec_result[0]==0:
            host=exec_result[1].split('\n')
            if int(host[0].replace('.','')) > int(host[1].replace('.','')):
                return host[0]
            else:
                return host[1]
    
