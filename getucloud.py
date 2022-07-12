#-*- encoding: utf-8 -*-
#!/usr/bin/env python
import MySQLdb as mdb
import hashlib, json, httplib
import urlparse
import urllib
import sys,datetime
import requests
import MySQLdb.cursors
import time

class UCLOUDException(Exception):
    def __str__(self):
        return "Error"


def _verfy_ac(private_key, params):
    items = params.items()
    items.sort()

    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + str(value)

    params_data = params_data+private_key
    
    '''use sha1 to encode keys'''
    hash_new = hashlib.sha1()
    hash_new.update(params_data)
    hash_value = hash_new.hexdigest()
    return hash_value


class UConnection(object):
    def __init__(self, base_url):
        self.base_url = base_url
        o = urlparse.urlsplit(base_url)
        if o.scheme == 'https':
            self.conn = httplib.HTTPSConnection(o.netloc)
        else:
            self.conn = httplib.HTTPConnection(o.netloc)

    def __del__(self):
        self.conn.close()

    def get(self, resouse, params):
        # type: (object, object) -> object
        resouse += "?" + urllib.urlencode(params)
        #打印url
        #print("%s%s" % (self.base_url, resouse))
        self.conn.request("GET", resouse)
        response = json.loads(self.conn.getresponse().read())
        return response

    def post(self, uri, params):
        #打印url
        #print("%s%s %s" % (self.base_url, uri, params))
        headers = {"Content-Type": "application/json"}
        self.conn.request("POST", uri, json.JSONEncoder().encode(params), headers)
        response = json.loads(self.conn.getresponse().read())
        return response


class UcloudApiClient(object):
    # 添加 设置 数据中心和  zone 参数
    def __init__(self, base_url, public_key, private_key):
        self.g_params = {}
        self.g_params['PublicKey'] = public_key
        self.private_key = private_key
        self.conn = UConnection(base_url)

    def get(self, uri, params):
        # type: (object, object) -> object
        # print params
        _params = dict(self.g_params, **params)

#        if project_id : 
#            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, _params)
        return self.conn.get(uri, _params)

    def post(self, uri, params):
        _params = dict(self.g_params, **params)

#        if project_id :
#            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, _params)
        return self.conn.post(uri, _params)


def getmysqlconn():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'avds',
        'passwd': '.INIT@avds',
        'db': 'avds',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.DictCursor
    }
    conn = mdb.connect(**config)
    return conn


def insertorupdate(conn,instanceId,instanceName,tags,privateIpAddress,publicIpAddress,OSNEnvironment,OSName,regionId,updateTime,status,arn):
    cursor = conn.cursor()
    # SQL update sql
    sql = """insert into cloudhost(instanceId,instanceName,tags,privateIpAddress,publicIpAddress,OSNEnvironment,OSName,regionId,updateTime,status,arn) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update instanceName=VALUES(instanceName),tags=VALUES(tags),privateIpAddress=VALUES(privateIpAddress),publicIpAddress=VALUES(publicIpAddress),OSNEnvironment=VALUES(OSNEnvironment),OSName=VALUES(OSName),regionId=VALUES(regionId),updateTime=VALUES(updateTime),status=VALUES(status),arn=VALUES(arn)"""

    values = (instanceId,instanceName,tags,privateIpAddress,publicIpAddress,OSNEnvironment,OSName,regionId,updateTime,status,arn)
    try:
        #print 'update sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        print n
        # 提交到数据库执行
        conn.commit()
        #print 'update success'
    except Exception as e:
        # Rollback in case there is any error
        print e
        conn.rollback()
        #print 'update fail,rollback'


def insertorupcount(conn,arn,type,departmentname,instancenum):
    # dbucloudlist = []
    cursor = conn.cursor()
    # SQL update sql
    sql = """insert into authorization_arners(arn,type,departmentname,instancenum) values(%s,%s,%s,%s) on duplicate key update arn=VALUES(arn),type=VALUES(type),departmentname=VALUES(departmentname),instancenum=VALUES(instancenum)"""

    values = (arn,type,departmentname,instancenum)
    try:
        #print 'update sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        #print n
        # 提交到数据库执行
        conn.commit()
        #print 'update success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'update fail,rollback'

def getarninfo(conn,arn):
    cursor = conn.cursor()
    sql = """SELECT business_ids,opsuserid,bususerid FROM authorization_arners where arn=%s """
    values = (arn)
    try:
        cursor.execute(sql,values)
        results = cursor.fetchall()
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'select fail,rollback'
    return results


def updatecms_host(conn,instanceId,instanceName,privateIpAddress,publicIpAddress,device_type,host_position,OSName,regionId,updateTime,status,arn,tags,busid,opsuserid,bususerid,createTime):
    cursor = conn.cursor()
    # SQL update sql
    sql = """insert into cms_hosts(instanceId,instanceName,privateIpAddress,publicIpAddress,device_type,host_position,OSName,regionId,updateTime,status,arn,tags,busid,opsuserid,bususerid,createTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update instanceName=VALUES(instanceName),privateIpAddress=VALUES(privateIpAddress),publicIpAddress=VALUES(publicIpAddress),device_type=VALUES(device_type),host_position=VALUES(host_position),OSName=VALUES(OSName),regionId=VALUES(regionId),serialNumber=VALUES(serialNumber),updateTime=VALUES(updateTime),status=VALUES(status),arn=VALUES(arn),tags=VALUES(tags),busid=VALUES(busid),opsuserid=VALUES(opsuserid),bususerid=VALUES(bususerid),createTime=VALUES(createTime)"""
    values = (instanceId,instanceName,privateIpAddress,publicIpAddress,device_type,host_position,OSName,regionId,updateTime,status,arn,tags,busid,opsuserid,bususerid,createTime)
    try:
        #print 'update sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        print n
        # 提交到数据库执行
        conn.commit()
        #print 'update success'
    except Exception as e:
        # Rollback in case there is any error
        print e
        conn.rollback()


def delcloudhost(conn):
    sql = "delete from cloudhost WHERE OSNEnvironment ='ucloud' and DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d')"
    cursor = conn.cursor()
    try:
        #print 'del sql start'
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        #print 'del success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'del fail,rollback'

def delcms_host(conn):
    sql = "delete from cms_hosts WHERE host_position='ucloud' and DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d')"
    cursor = conn.cursor()
    try:
        #print 'del sql start'
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        #print 'del success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'del fail,rollback'


#配置公私钥"""
public_key  = "sZgGYg=="
private_key = "a21cc514"
base_url    = "https://api.ucloud.cn"
#listregion = ['cn-bj1','cn-bj2','us-ca','cn-sh2','hk']
#{u'Zone': u'th-bkk-02', u'Region': u'th-bkk', u'RegionId': 10026, u'BitMaps': u'', u'IsDefault': False, u'RegionName': u'th-bkk-02'}


#调用
if __name__=='__main__':
    arg_length = len(sys.argv)
    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    listregion = []
    regions = ApiClient.get("/", {"Action":"GetRegion"}).get('Regions');
    for r in regions:
        listregion.append(r.get('Region'))
    print listregion
    conn = getmysqlconn()
    host_position = 'ucloud'
    #获取ProjectList
    listprojectidresponse = ApiClient.get("/", {"Action":"GetProjectList"});
    # print listprojectidresponse
    listprojectset = listprojectidresponse.get('ProjectSet')
    #print listprojectset
    #循环projectid
    for projectidindex in listprojectset:
        #获取单个projectid
        print projectidindex
        projectid = projectidindex.get('ProjectId')
        ProjectName = projectidindex.get('ProjectName')
        arninfo = getarninfo(conn,projectid)
        for p in arninfo:
            busid = p.get('business_ids')
            opsuserid = p.get('opsuserid')
            bususerid = p.get('bususerid')
        instancenum = 0
        #循环regionid
        for regionid in set(listregion):
            Parameters = {
                "Action": "DescribeUHostInstance",
                "ProjectId": projectid,  # 项目ID 请在Dashbord 上获
                "Region": regionid,
            }
            #获取此项目此地区机器表
            response = ApiClient.get("/", Parameters)
            count = response.get('TotalCount')
            if count:
                print  count
                print 'ecs exist'
                instancenum = instancenum + count
                listhost = response.get('UHostSet')
                # 循环获取单个机器信息
                for i in listhost:
                    instanceId = i.get('UHostId').encode("utf-8")
                    instanceName = i.get('Name').encode("utf-8")
                    privateIpAddress = i.get('IPSet')[0].get('IP').encode("utf-8")
                    publicIpAddress = i.get('IPSet')[1].get('IP').encode("utf-8")
                    device_type ='ip'
                    OSName = i.get('OsName').encode("utf-8")
                    regionId = i.get('Zone').encode("utf-8")
                    updateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status = i.get('State').encode("utf-8")
                    tags = i.get('Remark').encode("utf-8")
                    arn = projectid
                    createtimeStamp = i.get('CreateTime')
                    timeArray = time.localtime(createtimeStamp)
                    createTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    updatecms_host(conn,instanceId,instanceName,privateIpAddress,publicIpAddress,device_type,host_position,OSName,regionId,updateTime,status,arn,tags,busid,opsuserid,bususerid,createTime)
                    insertorupdate(conn,instanceId,instanceName,tags,privateIpAddress,publicIpAddress,host_position,OSName,regionId,updateTime,status,arn)
            else:
                pass
            print projectid + '  done in ' + regionid
        print projectid + '  done'
        insertorupcount(conn,projectid,host_position,ProjectName,instancenum)

    print 'all project done'
    delcloudhost(conn)
    delcms_host(conn)
    conn.close()
    print 'job done'













