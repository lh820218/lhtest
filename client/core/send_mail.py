#!/usr/bin/python
#coding:utf8
'''
Created on 2016年12月21日

@author: lihui1
'''
import requests

def sendmail(ff,to,subject,body):
        values ={
        'uid':'liyang190030@sogou-inc.com',
        'fr_name':'dba',
        'fr_addr':ff,
        'title':subject,
        'body':body,
        'mode':'html',
        'maillist':to}
        mail_url="http://mail.portal.sogou/portal/tools/send_mail.php?"
        requests.post(mail_url,data=values)
#         with open('/search/data/opbin/rds/rds_backup_statistics/log/sendmail.log','w') as a:
#             a.write('%s' % result)