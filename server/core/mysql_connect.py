#!/usr/bin/python
# coding:utf8
import MySQLdb
import sys
reload(sys)
#sys.setdefalutencoding("utf-8")
import variables

class Db_conn():
    def __init__(self):
        self.db_type='mysql'
        self.db_user=variables.mysql_user
        self.db_pass=variables.mysql_pass
        self.db_port=variables.mysql_port
        self.db_name=variables.mysql_db
        self.db_host=variables.mysql_host
    def mysql_op(self,sql,op_type='read',Result_Status='Dict'):
        if op_type=='read':
            try:
                dblink = MySQLdb.connect(host=self.db_host,user=self.db_user,passwd=self.db_pass,port=self.db_port,db=self.db_name,connect_timeout=5,charset='utf8')
            except Exception as e:
                print e
            if Result_Status == 'Tuple':   #返回元组作为结果集
                cursor = dblink.cursor()
            elif Result_Status=='Dict':    #返回字典作为结果集
                cursor = dblink.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
            except Exception as e:
                print e
                return 0
            cursor.close()
            dblink.close()
            return result
        if op_type=='write':
            try:
                dblink = MySQLdb.connect(host=self.db_host,user=self.db_user,passwd=self.db_pass,port=self.db_port,db=self.db_name,connect_timeout=5,charset='utf8')
            except Exception as e:
                print e
            try:
                cursor = dblink.cursor()
                n=cursor.execute(sql)
            except Exception as e:
                print e
                return 0
            dblink.commit()
            cursor.close()
            dblink.close()
            return n