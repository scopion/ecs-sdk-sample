# -*- encoding: utf-8 -*-
# !/usr/bin/env python
# =========================================================================
# Copyright 2012-present Yunify, Inc.
# -------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================
import random
import re
import threading
import hmac
import uuid
import requests
import sys,datetime
import time
import base64
import json as jsmod
from hashlib import sha1, sha256
import MySQLdb.cursors
import MySQLdb as mdb

try:
    import httplib
except:
    import http.client as httplib
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'
ISO8601_MS = '%Y-%m-%dT%H:%M:%S.%fZ'
try:
    import urllib.parse as urllib

    is_python3 = True
except:
    import urllib

    is_python3 = False


def json_dump(obj, indent=None):
    """ Dump an object to json string, only basic types are supported.
        @return json string or `None` if failed

        >>> json_dump({'int': 1, 'none': None, 'str': 'string'})
        '{"int":1,"none":null,"str":"string"}'
    """
    try:
        jstr = jsmod.dumps(obj, separators=(',', ':'),
                           indent=indent, sort_keys=True)
    except:
        jstr = None
    return jstr


def json_load(json):
    """ Load from json string and create a new python object
        @return object or `None` if failed

        >>> json_load('{"int":1,"none":null,"str":"string"}')
        {u'int': 1, u'none': None, u'str': u'string'}
    """
    try:
        obj = jsmod.loads(json)
    except:
        obj = None
    return obj


def get_utf8_value(value):
    if sys.version < "3":
        if isinstance(value, unicode):
            return value.encode('utf-8')
        if not isinstance(value, str):
            value = str(value)
        return value
    else:
        return str(value)


def parse_ts(ts):
    """ Return as timestamp
    """
    ts = ts.strip()
    try:
        ts_s = time.strptime(ts, ISO8601)
        return time.mktime(ts_s)
    except ValueError:
        try:
            ts_s = time.strptime(ts, ISO8601_MS)
            return time.mktime(ts_s)
        except ValueError:
            return 0


def get_ts(ts=None):
    """ Get formatted time
    """
    if not ts:
        ts = time.gmtime()
    return time.strftime(ISO8601, ts)


class InvalidAction(Exception):
    pass


class InvalidParameterError(Exception):
    """ Error when invalid parameter found in request
    """
    pass


class RequestChecker(object):
    def err_occur(self, error_msg):
        raise InvalidParameterError(error_msg)

    def is_integer(self, value):
        try:
            int(value)
        except:
            return False
        return True

    def check_integer_params(self, directive, params):
        """ Specified params should be `int` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `int` type.
        """
        for param in params:
            if param not in directive:
                continue
            val = directive[param]
            if self.is_integer(val):
                directive[param] = int(val)
            else:
                self.err_occur(
                    "parameter [%s] should be integer in directive [%s]" % (param, directive))

    def check_list_params(self, directive, params):
        """ Specified params should be `list` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `list` type.
        """
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                self.err_occur(
                    "parameter [%s] should be list in directive [%s]" % (param, directive))

    def check_required_params(self, directive, params):
        """ Specified params should be in directive
        @param directive: the directive to check
        @param params: the params that should be in directive.
        """
        for param in params:
            if param not in directive:
                self.err_occur(
                    "[%s] should be specified in directive [%s]" % (param, directive))

    def check_datetime_params(self, directive, params):
        """ Specified params should be `date` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `date` type.
        """
        for param in params:
            if param not in directive:
                continue
            if not parse_ts(directive[param]):
                self.err_occur(
                    "[%s] should be 'YYYY-MM-DDThh:mm:ssZ' in directive [%s]" % (param, directive))

    def check_params(self, directive, required_params=None,
                     integer_params=None, list_params=None, datetime_params=None):
        """ Check parameters in directive
        @param directive: the directive to check, should be `dict` type.
        @param required_params: a list of parameter that should be in directive.
        @param integer_params: a list of parameter that should be `integer` type
                               if it exists in directive.
        @param list_params: a list of parameter that should be `list` type
                            if it exists in directive.
        @param datetime_params: a list of parameter that should be `date` type
                                if it exists in directive.
        """
        if not isinstance(directive, dict):
            self.err_occur('[%s] should be dict type' % directive)
            return False

        if required_params:
            self.check_required_params(directive, required_params)
        if integer_params:
            self.check_integer_params(directive, integer_params)
        if list_params:
            self.check_list_params(directive, list_params)
        if datetime_params:
            self.check_datetime_params(directive, datetime_params)
        return True

    def check_sg_rules(self, rules):
        return all(self.check_params(rule,
                                     required_params=['priority', 'protocol'],
                                     integer_params=['priority', 'direction'],
                                     list_params=[]
                                     ) for rule in rules)

    # def check_router_statics(self, statics):
    #     def check_router_static(static):
    #         required_params = ['static_type']
    #         integer_params = []
    #         static_type = static.get('static_type')
    #         if static_type == RouterStaticFactory.TYPE_PORT_FORWARDING:
    #             # src port, dst ip, dst port
    #             required_params.extend(['val1', 'val2', 'val3'])
    #             integer_params = []
    #         elif static_type == RouterStaticFactory.TYPE_VPN:
    #             # vpn type
    #             required_params.extend(['val1'])
    #         elif static_type == RouterStaticFactory.TYPE_TUNNEL:
    #             required_params.extend(['vxnet_id', 'val1'])
    #         elif static_type == RouterStaticFactory.TYPE_FILTERING:
    #             integer_params = []
    #         else:
    #             integer_params = []
    #
    #         return self.check_params(static, required_params, integer_params)
    #
    #     return all(check_router_static(static) for static in statics)

    def check_lb_listener_port(self, port):
        if port in [25, 80, 443] or 1024 <= port <= 65535:
            return
        self.err_occur(
            'illegal port[%s], valid ones are [25, 80, 443, 1024~65535]' % port)

    def check_lb_listener_healthy_check_method(self, method):
        # valid methods: "tcp", "http|/url", "http|/url|host"
        if method == 'tcp' or re.match('http\|\/[^|]*(\|.+)?', method):
            return
        self.err_occur('illegal healthy check method[%s]' % method)

    def check_lb_listener_healthy_check_option(self, options):
        # options format string: inter | timeout | fall | rise
        items = options.split('|')
        if len(items) != 4:
            self.err_occur('illegal healthy check options[%s]' % options)

        inter, timeout, fall, rise = [int(item) for item in items]
        if not 2 <= inter <= 60:
            self.err_occur(
                'illegal inter[%s], should be between 2 and 60' % inter)
        if not 5 <= timeout <= 300:
            self.err_occur(
                'illegal timeout[%s], should be between 5 and 300' % timeout)
        if not 2 <= fall <= 10:
            self.err_occur(
                'illegal fall[%s], should be between 2 and 10' % fall)
        if not 2 <= rise <= 10:
            self.err_occur(
                'illegal rise[%s], should be between 2 and 10' % rise)

    def check_lb_backend_port(self, port):
        if 1 <= port <= 65535:
            return
        self.err_occur(
            'illegal port[%s], should be between 1 and 65535' % port)

    def check_lb_backend_weight(self, weight):
        if 1 <= weight <= 100:
            return
        self.err_occur(
            'illegal weight[%s], should be between 1 and 100' % weight)

    def check_lb_listeners(self, listeners):
        required_params = ['listener_protocol',
                           'listener_port', 'backend_protocol']
        integer_params = ['forwardfor', 'listener_port']
        for listener in listeners:
            self.check_params(listener,
                              required_params=required_params,
                              integer_params=integer_params,
                              )
            self.check_lb_listener_port(listener['listener_port'])
            if 'healthy_check_method' in listener:
                self.check_lb_listener_healthy_check_method(
                    listener['healthy_check_method'])
            if 'healthy_check_option' in listener:
                self.check_lb_listener_healthy_check_option(
                    listener['healthy_check_option'])

    def check_lb_backends(self, backends):
        required_params = ['resource_id', 'port']
        integer_params = ['weight', 'port']
        for backend in backends:
            self.check_params(backend,
                              required_params=required_params,
                              integer_params=integer_params,
                              )
            self.check_lb_backend_port(backend['port'])
            if 'weight' in backend:
                self.check_lb_backend_weight(backend['weight'])


class HmacKeys(object):
    """ Key based Auth handler helper.
    """
    host = None
    qy_access_key_id = None
    qy_secret_access_key = None
    _hmac = None
    _hmac_256 = None

    def __init__(self, host, qy_access_key_id, qy_secret_access_key):
        self.host = host
        self.update_provider(qy_access_key_id, qy_secret_access_key)

    def update_provider(self, qy_access_key_id, qy_secret_access_key):
        self.qy_access_key_id = qy_access_key_id
        self.qy_secret_access_key = qy_secret_access_key
        if is_python3:
            qy_secret_access_key = qy_secret_access_key.encode()
        self._hmac = hmac.new(qy_secret_access_key, digestmod=sha1)
        if sha256:
            self._hmac_256 = hmac.new(qy_secret_access_key, digestmod=sha256)
        else:
            self._hmac_256 = None

    def algorithm(self):
        if self._hmac_256:
            return 'HmacSHA256'
        else:
            return 'HmacSHA1'

    def digest(self, string_to_digest):
        if self._hmac_256:
            _hmac = self._hmac_256.copy()
        else:
            _hmac = self._hmac.copy()
        if is_python3:
            string_to_digest = string_to_digest.encode()
        _hmac.update(string_to_digest)
        return _hmac.digest()

    def sign_string(self, string_to_sign):
        to_sign = self.digest(string_to_sign)
        return base64.b64encode(to_sign).strip()


class QuerySignatureAuthHandler(HmacKeys):
    """ Provides Query Signature Authentication.
    """

    SignatureVersion = 1
    APIVersion = 1

    def _calc_signature(self, params, verb, path):
        """ calc signature for request
        """
        string_to_sign = '%s\n%s\n' % (verb, path)
        params['signature_method'] = self.algorithm()
        keys = sorted(params.keys())
        pairs = []
        for key in keys:
            val = get_utf8_value(params[key])
            if is_python3:
                key = key.encode()
            pairs.append(urllib.quote(key, safe='') + '=' +
                         urllib.quote(val, safe='-_~'))
        qs = '&'.join(pairs)
        string_to_sign += qs
        # print "string to sign:[%s]" % string_to_sign
        b64 = self.sign_string(string_to_sign)
        return (qs, b64)

    def add_auth(self, req, **kwargs):
        """ add authorize information for request
        """
        req.params['access_key_id'] = self.qy_access_key_id
        req.params['signature_version'] = self.SignatureVersion
        req.params['version'] = self.APIVersion
        time_stamp = get_ts()
        req.params['time_stamp'] = time_stamp
        qs, signature = self._calc_signature(req.params, req.method,
                                             req.auth_path)
        # print 'query_string: %s Signature: %s' % (qs, signature)
        if req.method == 'POST':
            # req and retried req should not have signature
            params = req.params.copy()
            params["signature"] = signature
            req.body = urllib.urlencode(params)
            req.header = {
                'Content-Length': str(len(req.body)),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/plain',
                'Connection': 'Keep-Alive'
            }
        else:
            req.body = ''
            # if this is a retried req, the qs from the previous try will
            # already be there, we need to get rid of that and rebuild it
            req.path = req.path.split('?')[0]
            req.path = (req.path + '?' + qs +
                        '&signature=' + urllib.quote_plus(signature))


class HTTPRequest(object):
    def __init__(self, method, protocol, header, host, port, path,
                 params, auth_path=None, body=""):
        """
        Represents an HTTP request.

        @param method - The HTTP method name, 'GET', 'POST', 'PUT' etc.
        @param protocol - 'http' or 'https'
        @param header - http request header
        @param host - the host to make the connection to
        @param port - the port to use when connect to host
        @param path - URL path that is being accessed.
        @param auth_path - The part of the URL path used when creating the
                         authentication string.
        @param params - HTTP url query parameters, {'name':'value'}.
        @param body - Body of the HTTP request. If not present, will be None or
                     empty string ('').
        """
        self.method = method
        self.protocol = protocol
        self.header = header
        self.host = host
        self.port = port
        self.path = path
        self.auth_path = auth_path or path
        self.params = params
        self.body = body

    def __str__(self):
        return (('method:(%s) protocol:(%s) header(%s) host(%s) port(%s) path(%s) '
                 'params(%s) body(%s)') % (self.method, self.protocol, self.header,
                                           self.host, str(self.port),
                                           self.path, self.params,
                                           self.body))

    def authorize(self, connection, **kwargs):
        # add authorize information to request
        if connection._auth_handler:
            connection._auth_handler.add_auth(self, **kwargs)


class HTTPResponse(httplib.HTTPResponse):
    def __init__(self, *args, **kwargs):
        httplib.HTTPResponse.__init__(self, *args, **kwargs)
        self._cached_response = ""

    def read(self, amt=None):
        """Read the response.

        If this method is called without amt argument, the response body
        will be cached. Subsequent calls without arguments will return
        the cached response.
        """
        if amt is None:
            if not self._cached_response:
                self._cached_response = httplib.HTTPResponse.read(self)
            return self._cached_response
        else:
            return httplib.HTTPResponse.read(self, amt)


class ConnectionQueue(object):
    """ Http connection queue
    """

    def __init__(self, timeout=60):
        self.queue = []
        self.timeout = timeout

    def size(self):
        return len(self.queue)

    def get_conn(self):
        # get a valid connection or `None`
        for _ in range(len(self.queue)):
            (conn, _) = self.queue.pop(0)
            if self._is_conn_ready(conn):
                return conn
            else:
                self.put_conn(conn)

    def put_conn(self, conn):
        self.queue.append((conn, time.time()))

    def clear(self):
        # clear expired connections
        while self.queue and self._is_conn_expired(self.queue[0]):
            self.queue.pop(0)

    def _is_conn_expired(self, conn_info):
        (_, time_stamp) = conn_info
        return (time.time() - time_stamp) > self.timeout

    def _is_conn_ready(self, conn):
        # sometimes the response may not be remove
        # after read at lasttime's connection
        response = getattr(conn, '_HTTPConnection__response', None)
        return (response is None) or response.isclosed()


class ConnectionPool(object):
    """ Http connection pool for multiple hosts.
        It's thread-safe
    """

    CLEAR_INTERVAL = 5.0

    def __init__(self, timeout=60):
        self.timeout = timeout
        self.last_clear_time = time.time()
        self.lock = threading.Lock()
        self.pool = {}

    def size(self):
        with self.lock:
            return sum([conn.size() for conn in self.pool.values()])

    def put_conn(self, host, port, conn):
        # put connection into host's connection pool
        with self.lock:
            key = (host, port)
            queue = self.pool.setdefault(key, ConnectionQueue(self.timeout))
            queue.put_conn(conn)

    def get_conn(self, host, port):
        # get connection from host's connection pool
        # return a valid connection or `None`
        self._clear()
        with self.lock:
            key = (host, port)
            if key in self.pool:
                return self.pool[key].get_conn()

    def _clear(self):
        # clear expired connections of all hosts
        with self.lock:
            curr_time = time.time()
            if self.last_clear_time + self.CLEAR_INTERVAL > curr_time:
                return
            key_to_delete = []
            for key in self.pool:
                self.pool[key].clear()
                if self.pool[key].size() == 0:
                    key_to_delete.append(key)
            for key in key_to_delete:
                del self.pool[key]
            self.last_clear_time = curr_time


class HttpConnection(object):
    """
    Connection control to restful service
    """

    def __init__(self, qy_access_key_id, qy_secret_access_key, host=None,
                 port=443, protocol="https", pool=None, expires=None,
                 http_socket_timeout=10, debug=False):
        """
        @param qy_access_key_id - the access key id
        @param qy_secret_access_key - the secret access key
        @param host - the host to make the connection to
        @param port - the port to use when connect to host
        @param protocol - the protocol to access to web server, "http" or "https"
        @param pool - the connection pool
        """
        self.host = host
        self.port = port
        self.qy_access_key_id = qy_access_key_id
        self.qy_secret_access_key = qy_secret_access_key
        self.http_socket_timeout = http_socket_timeout
        self._conn = pool if pool else ConnectionPool()
        self.expires = expires
        self.protocol = protocol
        self.secure = protocol.lower() == "https"
        self.debug = debug
        self._auth_handler = None
        self._proxy_host = None
        self._proxy_port = None
        self._proxy_headers = None
        self._proxy_protocol = None

    def _get_conn(self, host, port):
        """ Get connection from pool
        """
        conn = self._conn.get_conn(host, port)
        return conn or self._new_conn(host, port)

    def _set_conn(self, conn):
        """ Set valid connection into pool
        """
        self._conn.put_conn(conn.host, conn.port, conn)

    def _new_conn(self, host, port):
        """ Create new connection
        """
        if self.secure:
            conn = httplib.HTTPSConnection(
                host, port, timeout=self.http_socket_timeout)
        else:
            conn = httplib.HTTPConnection(
                host, port, timeout=self.http_socket_timeout)
        # Use self-defined Response class
        conn.response_class = HTTPResponse
        return conn

    def build_http_request(self, method, path, params, auth_path, headers,
                           host, data):
        raise NotImplementedError(
            "The build_http_request method must be implemented")

    def send(self, method, path, params=None, headers=None, host=None,
             auth_path=None, data=""):

        if not params:
            params = {}

        if not headers:
            headers = {}

        if not host:
            host = self.host

        # Build the http request
        request = self.build_http_request(method, path, params, auth_path,
                                          headers, host, data)
        request.authorize(self)

        conn_host = host
        conn_port = self.port
        request_path = request.path

        #: proxy
        if self._proxy_protocol:
            conn_host = self._proxy_host
            conn_port = self._proxy_port

        #: proxy - http
        if self._proxy_protocol == "http":
            request_path = "%s://%s%s" % (self.protocol, host, request_path)

        #: get connection
        conn = self._get_conn(conn_host, conn_port)

        #: proxy - https
        if self._proxy_protocol == "https":
            conn.set_tunnel(host, self.port, self._proxy_headers)

        # Send the request
        conn.request(method, request_path, request.body, request.header)

        # Receive the response
        response = conn.getresponse()

        # Reuse the connection
        if response.status < 500:
            self._set_conn(conn)

        return response


class APIConnection(HttpConnection):
    """ Public connection to qingcloud service
    """
    req_checker = RequestChecker()

    def __init__(self, qy_access_key_id, qy_secret_access_key, zone,
                 host="api.qingcloud.com", port=443, protocol="https",
                 pool=None, expires=None,
                 retry_time=2, http_socket_timeout=60, debug=False):
        """
        @param qy_access_key_id - the access key id
        @param qy_secret_access_key - the secret access key
        @param zone - the zone id to access
        @param host - the host to make the connection to
        @param port - the port to use when connect to host
        @param protocol - the protocol to access to web server, "http" or "https"
        @param pool - the connection pool
        @param retry_time - the retry_time when message send fail
        """
        # Set default zone
        self.zone = zone
        # Set retry times
        self.retry_time = retry_time

        super(APIConnection, self).__init__(
            qy_access_key_id, qy_secret_access_key, host, port, protocol,
            pool, expires, http_socket_timeout, debug)

        self._auth_handler = QuerySignatureAuthHandler(self.host,
                                                       self.qy_access_key_id, self.qy_secret_access_key)

        # other apis
        # TODO: seperate functions in this class into each function class
        # self.actions = [
        #     NicAction(self),
        #     AlarmPolicy(self),
        #     S2Action(self),
        # ]

    def send_request(self, action, body, url="/iaas/", verb="GET"):
        """ Send request
        """
        request = body
        request['action'] = action
        request.setdefault('zone', self.zone)
        if self.debug:
            print(json_dump(request))
            sys.stdout.flush()
        if self.expires:
            request['expires'] = self.expires

        retry_time = 0
        while retry_time < self.retry_time:
            # Use binary exponential backoff to desynchronize client requests
            next_sleep = random.random() * (2 ** retry_time)
            try:
                response = self.send(verb, url, request)
                if response.status == 200:
                    resp_str = response.read()
                    if type(resp_str) != str:
                        resp_str = resp_str.decode()
                    if self.debug:
                        print(resp_str)
                        sys.stdout.flush()
                    return json_load(resp_str) if resp_str else ""
            except:
                if retry_time < self.retry_time - 1:
                    self._get_conn(self.host, self.port)
                else:
                    raise

            time.sleep(next_sleep)
            retry_time += 1

    def _gen_req_id(self):
        return uuid.uuid4().hex

    def build_http_request(self, verb, url, base_params, auth_path=None,
                           headers=None, host=None, data=""):
        params = {}
        for key, values in base_params.items():
            if values is None:
                continue
            if isinstance(values, list):
                for i in range(1, len(values) + 1):
                    if isinstance(values[i - 1], dict):
                        for sk, sv in values[i - 1].items():
                            if isinstance(sv, dict) or isinstance(sv, list):
                                sv = json_dump(sv)
                            params['%s.%d.%s' % (key, i, sk)] = sv
                    else:
                        params['%s.%d' % (key, i)] = values[i - 1]
            else:
                params[key] = values

        # add req_id
        params.setdefault('req_id', self._gen_req_id())

        return HTTPRequest(verb, self.protocol, headers, self.host, self.port,
                           url, params)



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
#




def insertorupdate(conn,instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,OSNEnvironment,OSName,regionId,serialNumber,updateTime,status,arn):
    # dbucloudlist = []
    cursor = conn.cursor()
    # SQL update sql
    sql = """insert into cloudhost(instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,OSNEnvironment,OSName,regionId,serialNumber,updateTime,status,arn) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update instanceName=VALUES(instanceName),privateIpAddress=VALUES(privateIpAddress),publicIpAddress=VALUES(publicIpAddress),eipAddress=VALUES(eipAddress),OSNEnvironment=VALUES(OSNEnvironment),OSName=VALUES(OSName),regionId=VALUES(regionId),serialNumber=VALUES(serialNumber),updateTime=VALUES(updateTime),status=VALUES(status),arn=VALUES(arn)"""

    values = (instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,OSNEnvironment,OSName,regionId,serialNumber,updateTime,status,arn)
    try:
        print 'update sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        print n
        # 提交到数据库执行
        conn.commit()
        print 'update success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'update fail,rollback'

def delinstance(conn):
    sql = "delete from cloudhost where DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d');"
    cursor = conn.cursor()
    try:
        print 'del sql start'
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        print 'del success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'del fail,rollback'

def updatesum(conn,sum,arn):
    sql =  "UPDATE accountcontacters SET instancenum = "+str(sum)+" WHERE arn ='" + arn +"'"
    print sql
    cursor = conn.cursor()
    try:
        print 'updatenum sql start'
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        print 'update success'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'update fail,rollback'

# 配置公私钥"""
qy_access_key_id = 'IPMNJWMPPORFK'
qy_secret_access_key = 'i8Fo1HyiU2eJnuUJb'
zone = 'pek1'


#zonelist = ['pek1', 'pek2', 'sh1a', 'gd1', 'pek3a']
zonelist = ['pek2', 'sh1a', 'gd1', 'pek3a']
# pek1 is deleted,resouce moved to pek3a
projectlist = ['aaaaa','vvvvvv','ggggg' ]

if __name__ == '__main__':
    arg_length = len(sys.argv)
    ApiClient = APIConnection(qy_access_key_id, qy_secret_access_key, zone)
    # 登录系统
    # loginresult = session.post(loginurl, logindata)
    # print loginresult
    
    #conn = getmysqlconn()
    for j in projectlist:
        sum = 0
        for i in zonelist:
            getitembody = {'zone': i, 'resource_groups.n': j}
            ItemsResponse = ApiClient.send_request(action='DescribeResourceGroupItems', body=getitembody)
            print ItemsResponse
            count = ItemsResponse.get('total_count')
            print count.__class__
            sum = sum + count
            if count:
                itemlist = ItemsResponse.get('resource_group_item_set')
                print itemlist
                for k in itemlist:
                    print k
                    instanceId = k.get('resource_id').encode("utf-8")
                    instancelist = instanceId.split(' ')
                    desinstancebody = {'instances': instancelist, 'zone': i, 'sub_channel': 'resource_sharing'}
                    InstancesResponse = ApiClient.send_request(action='DescribeInstances', body=desinstancebody).get(
                        'instance_set')
                    print InstancesResponse
                    instanceName = InstancesResponse[0].get('instance_name').encode("utf-8")
                    privateIpAddress = InstancesResponse[0].get('vxnets')[0].get('private_ip').encode("utf-8")
                    publicIpAddress = ''
                    if InstancesResponse[0].get('eips'):
                        eipAddress = InstancesResponse[0].get('eips')[0].get('eip_addr').encode("utf-8")
                    OSNEnvironment = '青云'
                    OSName = InstancesResponse[0].get('image').get('os_family').encode("utf-8")
                    regionId = i
                    serialNumber = ""
                    updateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status = InstancesResponse[0].get('status').encode("utf-8")
                    arn = j

                    #insertorupdate(conn,instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,OSNEnvironment,OSName,regionId,serialNumber,updateTime,status,arn)
                print arn + '  done in ' + regionId
            else:
                pass
            print 'projecct' + j + 'done in ' + i
        print sum
        #updatesum(conn,sum,j)
        print 'project' + j + ' done'
    print ' all done'
    #delinstance(conn)
    conn.close()
    print 'job done'




