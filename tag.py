#! /usr/bin/env python
# _*_ coding:utf-8 _*_
###########python2
import requests
import json
import sys,datetime
import requests
import MySQLdb.cursors
import MySQLdb as mdb
import time
import re
#from json import JSONDecodeError
import logging
import requests
import time
import hmac
import hashlib
import base64
import urllib
import json
import sys
import MySQLdb.cursors
import MySQLdb as mdb
import re
#from json import JSONDecodeError
import logging
import requests
import time
import datetime

session = requests.session()
def is_not_null_and_blank_str(content):
    """
    非空字符串
    :param content: 字符串
    :return: 非空 - True，空 - False

    >>> is_not_null_and_blank_str('')
    False
    >>> is_not_null_and_blank_str(' ')
    False
    >>> is_not_null_and_blank_str('  ')
    False
    >>> is_not_null_and_blank_str('123')
    True
    """
    if content and content.strip():
        return True
    else:
        return False

def get(data,webhook,header={}):
    """
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
    param = urllib.urlencode(data)
    # response = self.session.post(hook, data=data).json()
    webhook = webhook + "?" + param
    print webhook
    try:
        response = session.get(webhook,headers=header)
    except requests.exceptions.HTTPError as exc:
        logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        logging.error("消息发送失败，HTTP connection error!")
        raise
    except requests.exceptions.Timeout:
        logging.error("消息发送失败，Timeout error!")
        raise
    except requests.exceptions.RequestException:
        logging.error("消息发送失败, Request Exception!")
        raise
    else:
        try:
            result = response.json()
        except:
            logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
            return {'errcode': 500, 'errmsg': '服务器响应异常'}
        else:
            return result

def post(data,webhook):
    """
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
    #data = json.dumps(data)
    try:
        #print (data)
        #print (webhook)
        response = session.post(webhook, data=data)
        #print (response.text)
    except requests.exceptions.HTTPError as exc:
        logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        logging.error("消息发送失败，HTTP connection error!")
        raise
    except requests.exceptions.Timeout:
        logging.error("消息发送失败，Timeout error!")
        raise
    except requests.exceptions.RequestException:
        logging.error("消息发送失败, Request Exception!")
        raise
    else:
        try:
            result = response.json()
        except:
            logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
            return {'errcode': 500, 'errmsg': '服务器响应异常'}
        else:
            return result

#获取标签信息
def get_tags_info(page=1):
    """
    markdown类型
    :return: 返回消息发送结果
    """
    url = "https://console.ops.com/tam/api/v1/base/external/cost/unit/list"
    data = {
        "page": page,
        "size":100,
    }
    md5_key = "for_external_string"
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    string = md5_key + date_str
    checkcode = hashlib.md5(string).hexdigest()
    headers = {"VERIFICATION": checkcode}
    logging.debug("获取员工信息：%s" % data)
    return get(data,url,header=headers)

#更新标签
def insertorupdate(conn,i):
    # dbucloudlist = []
    cursor = conn.cursor()
    taglist = i.get('tag_account').get('tag')
    operator = i.get('operator')
    business_user =i.get('business_user')   #业务负责人
    yunweiname = ''
    for i in operator:
        name =i.get('name')   #运维负责人
        email = i.get('email')   #运维负责人
        yunweiname = yunweiname+name+email
    for i in taglist:
        tag_key = i.get('tag_key')   #tag
        tag_describe = i.get('tag_describe')    #bline
        sql = "insert into authorization_tags(tag, bline,bususername, name) values(%s,%s,%s,%s) " \
              "on duplicate key update tag=VALUES(tag),bline=VALUES(bline),bususername=VALUES(bususername),name=VALUES(name)"
        values = (tag_key, tag_describe,business_user, yunweiname)
        # try:
            # print 'update product sql start'
            # 执行sql语句
        n = cursor.execute(sql, values)
        # print n
        # 提交到数据库执行
        conn.commit()
            #print ('update impl success')
        # except Exception as e:
        #     print e
        #     # Rollback in case there is any error
        #     conn.rollback()
        #     print 'update impl fail,rollback'


class DingtalkChatbot(object):
    """
    钉钉工作通知，给同一用户发相同内容消息一天仅允许一次。给同一用户发消息一天不得超过50次。
    """
    def __init__(self):
        """
        机器人初始化
        """
        super(DingtalkChatbot, self).__init__()
        self.times = 0
        self.start_time = time.time()
        self.webhook = "https://aal.com/message/ding_notice"
        self.baiduhook = "https://al.com/cmpts/msgchl/notice/send"

    def send_text(self, webhook,msg, is_at_all=False, at_mobiles=[]):
        """
        text类型
        :param msg: 消息内容
        :param is_at_all: @所有人时：true，否则为false
        :param at_mobiles: 被@人的手机号（字符串）
        :return: 返回消息发送结果
        """
        data = {"msgtype": "text"}
        if is_not_null_and_blank_str(msg):
            data["text"] = {"content": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        # if at_mobiles:
        #     at_mobiles = list(map(str, at_mobiles))

        data["at"] = {"atMobiles": at_mobiles, "isAtAll": is_at_all}
        logging.debug('text类型：%s' % data)
        return post(json.dumps(data),webhook)

# def getmysqlconn():
#     config = {
#         'host': '9.9.9.9',
#         'port': 3306,
#         'user': 'avds',
#         'passwd': '.INIT@vds',
#         'db': 'avds',
#         'charset': 'utf8',
#         'cursorclass': MySQLdb.cursors.DictCursor
#     }
#     conn = mdb.connect(**config)
#     return conn

def getmysqlconn():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'avds',
        'passwd': '.INIT@avs',
        'db': 'avds',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.DictCursor
    }
    conn = mdb.connect(**config)
    return conn

def getinstancelist(conn):
    listinstance = []
#    sql = 'select id  from ops_hole where level =2 and business_id=16'
    sql = "select instanceId,instanceName,tags,regionId,times  from cloudhost where tagcheck='false' and arn='acs:ram::16428:role/-security'"
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    #print results
    #print results.__class__
    for p in results:
        #print p
        listinstance.append(p)
        #print holelist
    # except Exception as e:
    #     print e
    #     # Rollback in case there is any error
    #     print 'select instance dict fail,rollback'
    return listinstance

def gettaglist(conn):
    listinstance = []
    sql = "select tag  from authorization_tags"
    cursor = conn.cursor()
    # try:
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    for p in results:
        tag = p.get('tag')
        listinstance.append(tag)
    # except Exception as e:
    #     print e
    return listinstance

def settime(conn,instanceid):
#    sql = 'select id  from ops_hole where level =2 and business_id=16'
    sql = "update cloudhost set times = times + 1 where instanceId=%s"
    val = [instanceid]
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    n=cursor.execute(sql,val)
    # 提交到数据库执行
    conn.commit()
    #print holelist
    return n
    # except Exception as e:
    #     print e
        # Rollback in case there is any error
        #print 'update times dict fail,rollback'

def settagcheck(conn,instanceid):
    sql = "update cloudhost set tagcheck = 'true' where instanceId=%s"
    val = [instanceid]
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    n=cursor.execute(sql,val)
    # 提交到数据库执行
    conn.commit()
    #print holelist
    return n
    # except Exception as e:
    #     # Rollback in case there is any error
    #     conn.rollback()
    #     print e




if __name__ == '__main__':
    try:
        #测试地址
        # baiduurl = 'https://yalou.com/robot/send?access_token=V1JXTUxkeU1Fa3Q2QUJThQeVNaUE5LM2dyWDZ1U3Q0Y2JMS252dg'
        # baidusecret = 'SECf6ab7674f9d4a4d3b5661'
        #生产
        # baiduurl = 'https://ych.com/robot/send?access_token=MjN0T3hvUlmU5Y0pOVk4wOFFDSlVjWHBYZC9zSndSNisvdjdidA'
        # baidusecret = 'SEC2a66c1c70b32bdc87992'
        # timestamp = long(round(time.time() * 1000))
        # secret_enc = bytes(baidusecret).encode('utf-8')
        # string_to_sign = '{}\n{}'.format(timestamp, baidusecret)
        # string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        # hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        # sign = urllib.quote_plus(base64.b64encode(hmac_code))
        # webhook = baiduurl + "&timestamp=" + str(timestamp) + "&sign=" + sign
        # xiaoding = DingtalkChatbot()
        #
        conn = getmysqlconn()
        ###########规则更新及入库
        count = 100
        page = 1
        while (count == 100):
            response = get_tags_info(page=page)
            #print response
            list = response['data']
            count = len(list)
            for i in list:
                print i
                insertorupdate(conn, i)
            page = page + 1
        total = response['total']

        '''
        #####获取第一次对比结果，将对比不通过的再次对比
        instancelist = getinstancelist(conn)
        tagoklist = set(gettaglist(conn))
        for i in instancelist:
            if i.get('tags'):
                tags = eval(i.get('tags').encode("utf-8"))
                print tags
                instanceid = i.get('instanceId').encode("utf-8")
                if tags:
                    for t in tags:
                        if t in tagoklist:
                            r =settagcheck(conn,instanceid)
                            print r
                            break

        ########最后的结果
        instancelist = getinstancelist(conn)
        msg = ''
        msgp = ''
        for i in instancelist:
            print i
            instanceid=i.get('instanceId').encode("utf-8")
            n = settime(conn,instanceid)
            print n
            instancename=i.get('instanceName').encode("utf-8")
            regionId=i.get('regionId').encode("utf-8")
            if i.get('tags'):
                tag = i.get('tags').encode("utf-8")
            else:
                tag = '空'
            times = i.get('times')
            if 14>times>=7:
                tt='\n通知次数达到7次，无人处理，建议运维管理老师对服务器进行关机处理，一周后删除'
            elif times>=14:
                tt = '\n通知次数达到14次，无人处理，建议运维管理老师对服务器进行备份，然后删除'
            else:
                tt=''
            msgp='服务器id：'+instanceid+'，服务器名：'+instancename+'，所在地区：'+regionId+'，标签为：'+tag+tt+ '\n'
            msg = msg + msgp
        if msg:
            print msg
            title='安全通知：\n以下服务器标签不在规则列表中，请security账号的老师认领并修改标签!!!\n'
            response = xiaoding.send_text(webhook,title+msg, is_at_all=True)
            print response
        else:
            msg = '今日未发现不合规标签'
            esponse = xiaoding.send_text(webhook, msg, is_at_all=True)
            print esponse
        '''
    except Exception as e:
        baiduurl = 'https://yanlou.com/robot/send?access_token=OHpuTno4L0WVlUMlRRS3B0elNwSTN6R0hBM0lrVVpJcUNIKw'
        baidusecret = 'SEC23f478b04d4d120a79e9'
        timestamp = long(round(time.time() * 1000))
        secret_enc = bytes(baidusecret).encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, baidusecret)
        string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)
        webhook = baiduurl + "&timestamp=" + str(timestamp) + "&sign=" + sign
        xiaoding = DingtalkChatbot()

        xiaoding.send_text(webhook,'tag'+str(e) + '@101515154', at_mobiles=['12415481'])






