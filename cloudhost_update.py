# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import time
import socket
import MySQLdb

'''
mysql> desc ip_base;
+--------------+--------------+------+-----+---------+-------+
| Field        | Type         | Null | Key | Default | Extra |
+--------------+--------------+------+-----+---------+-------+
| cdate        | datetime     | YES  |     | NULL    |       |
| ip           | varchar(32)  | NO   | PRI | NULL    |       |
| isrecord     | int(1)       | YES  |     | 0       |       |
| bline        | varchar(128) | YES  |     | NULL    |       |
| location     | varchar(64)  | YES  |     | NULL    |       |
| iptype       | int(1)       | YES  |     | 1       |       |
| hashostids   | int(1)       | YES  |     | 0       |       |
| hasdbids     | int(1)       | YES  |     | 0       |       |
| hasbashids   | int(1)       | YES  |     | 0       |       |
| hassyslogids | int(1)       | YES  |     | 0       |       |
| hasnetids    | int(1)       | YES  |     | 0       |       |
+--------------+--------------+------+-----+---------+-------+
'''

nows = time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
ipns = "/opt/yuncloud/cloudhost_list/%s.txt" %nows[:10]
ahts = "/opt/yuncloud/cloudhost_list/all_host.txt"
aips = "/opt/yuncloud/cloudhost_list/all_ip.txt"

class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
        self.conn = MySQLdb.connect(host='114.114.114.114', user='114', passwd='114', db='114', charset='utf8')
        self.conn.autocommit(True)

    def cursor(self):
        try:
            self.conn.ping()
            curs = self.conn.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            curs = self.conn.cursor()
        return curs

    def close(self):
        if self.conn:
            self.conn.close()


def getCloudHostToFile():
    ipfs = open(ipns, 'w')
    conn = MySQLdb.connect(host='127.0.0.1', user='114', passwd='114.114@114', db='114', charset='utf8') 
    curs = conn.cursor()
    curs.execute("SELECT updateTime, publicIpAddress, eipAddress, departmentname, OSNEnvironment FROM cloudhost, accountcontacters WHERE cloudhost.arn=accountcontacters.arn AND (publicIpAddress!='' OR eipAddress!='') AND (OSNEnvironment='ucloud' OR OSNEnvironment='青云' OR OSNEnvironment='阿里云')")
    rets = curs.fetchall()
    for rows in rets:
        if rows[2] != '':
            ipfs.write("%s\t%s\t%s\t%s\n" %(str(rows[0]), rows[2], rows[3], rows[4]))
        else:
            ipfs.write("%s\t%s\t%s\t%s\n" %(str(rows[0]), rows[1], rows[3], rows[4]))
    ipfs.close()
    curs.close()
    conn.close()


def updateCloudHostToDB(conn):
    curs = conn.cursor()
    ipfs = open(ipns, 'r')
    for line in ipfs:
        item = line.strip('\n').split('\t')
        if len(item) != 4:
            continue
        ip = item[1] 
        iptype = 2
        bline = item[2]
        curs.execute("INSERT IGNORE INTO ip_base (cdate, ip, isrecord, bline, location, iptype, hashostids, hasdbids, hasbashids, hassyslogids, hasnetids) VALUES (%s, %s, 2, %s, %s, %s, 2, 2, 2, 2, 2) ON DUPLICATE KEY UPDATE cdate=%s, bline=%s", (item[0], ip, bline, item[3], iptype, nows, bline,))
        print("INSERT IGNORE INTO ip_base (cdate, ip, isrecord, bline, location, iptype, hashostids, hasdbids, hasbashids, hassyslogids, hasnetids) VALUES ('%s', '%s', 2, '%s', '%s', %s, 2, 2, 2, 2, 2) ON DUPLICATE KEY UPDATE cdate='%s', bline='%s';" %(item[0], ip, bline, item[3], iptype, nows, bline))
    curs.execute("DELETE FROM ip_base WHERE isrecord=2 AND cdate<DATE_SUB(now(), interval 8 day);")
    ipfs.close()
    curs.close()


def getAllAssetToFile(conn):
    curs = conn.cursor()
    htfs = open(ahts, 'w')
    curs.execute("SELECT host, bline FROM host_base WHERE class=2")
    rets = curs.fetchall()
    for rows in rets:
        htfs.write("%s\t%s\n" %(str(rows[0]), rows[1]))
    htfs.close()

    ipfs = open(aips, 'w')
    curs.execute("SELECT ip, bline FROM ip_base WHERE iptype=1")
    rets = curs.fetchall()
    for rows in rets:
        ipfs.write("%s\t%s\n" %(str(rows[0]), rows[1]))
    ipfs.close()

    curs.close()


if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    getCloudHostToFile()
    conn = mydb()
    updateCloudHostToDB(conn)
    getAllAssetToFile(conn)
    conn.close()

