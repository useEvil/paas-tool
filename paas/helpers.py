"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import cookielib
import socket
import base64
import cgi
import os
import calendar
import datetime as date

from logging import getLogger
from re import findall
from socket import setdefaulttimeout
from urllib import urlencode
from urllib2 import Request, urlopen, build_opener, install_opener, URLError, HTTPCookieProcessor
from string import Template

from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound

log     = getLogger(__name__)
AGENT   = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

def objectAsDict(obj, dict={}):
    for elem in obj.__dict__.keys():
        if elem.startswith("_"):
            continue
        else:
            dict[elem] = obj.__dict__[elem]
    return dict

def escapeValue(obj, elem=None):
    if elem:
        return cgi.escape(obj.__dict__[elem])
    else:
        return cgi.escape(obj)

def escapeValues(dict={}, elements=[]):
    for elem in elements:
        log.debug('==== elem [%s]'%(elem))
        dict[elem] = escape_value(dict[elem])
    return dict

def price(n):
    if n is None: return "$0.00"
    n = str("%.2f" % float(n))
    negative = False
    n = str(n)
    if '.' in n:
        dollars, cents = n.split('.')
    else:
        dollars, cents = n, None
    if dollars.find("-") >= 0:
      negative = True
      dollars = dollars.replace("-","")
    r = []
    for i, c in enumerate(reversed(str(dollars))):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    out = "$" + ''.join(r)
    if cents:
        out += '.' + cents[0:2]
    if negative:
        out = '<span style="color: red;">-' + out + '</span>'
    return out

def number(n):
    if n is None: return '0'
    negative = False
    n = str(n)
    if '.' in n:
        number, decimal = n.split('.')
    else:
        number, decimal = n, None
    if number.find("-") >= 0:
      negative = True
      number = number.replace("-","")
      
    r = []
    for i, c in enumerate(reversed(str(number))):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    out = ''.join(r)
    if decimal:
        out += '.' + decimal[0:2]
    if negative:
        out = '<span style="color: red;">-' + out + '</span>'
    return out

def hasUserId(session=None):
    if session:
        return getSessionData(session, 'userId')
    return None

def hasRole(session=None, role=None):
    if session:
        permissions = getSessionData(session, 'permissions')
        return permissions and role in permissions and role.title() or None
    return None

def useAuth():
    return getSettings('auth.enable') == 'True'

def mode():
    return getSettings('mode')

def enabledOptions():
    return [ {'value': 0, 'label': 'Disabled'}, {'value': 1, 'label': 'Enabled'} ]

def environmentOptions():
    return [ {'value': 0, 'label': 'Dev'}, {'value': 1, 'label': 'QA'}, {'value': 2, 'label': 'Stage'}, {'value': 3, 'label': 'Production'} ]

def makeTestStyleOverride(low=0,high=100, m=10):
    """for the test list view"""
    return "left:%dpx;width:%dpx;" % (low * m, (high - low) * m)

def invalidateCache(type='tests'):
    port  = getSettings('invalidate.%s.port'%type)
    path  = getSettings('invalidate.%s.path'%type)
    hosts = str.split(getSettings('invalidate.%s.hosts'%type), ";")
    hosts = map(lambda x: str.strip(x), hosts)
    failures = []
    for host in hosts:
        url = 'http://%s:%s%s'%(host, port, path)
        log.warn('==== invalidating:url [%s]'%(url))
        for num in range(1):
            log.debug("%d %s " % (num, url))
            try:
                ## we dont care about the response
                urlopen(url)
            except URLError, e:
                failures.append(url)
                log.error(e)
    return {'status': (len(failures) is 0) and 200 or 500, 'message': (len(failures) is 0) and failures or 'Successfully Invalidated Cache'}

def sessionTestStyles(rule=None):
    if not rule:
        return None
    attrs = makeTestStyleOverride(rule.sessionLow, rule.sessionHigh)
    return attrs

def sessionTestClass(rule=None, base_class=""):
    if not rule:
        return {}
    brand_style = rule.isBrand('br') and 'brand2' or 'brand1'
    if not rule.enabled:
        brand_style += ' disabled'
    attrs = "%s %s" % (base_class, brand_style)
    return attrs

def getUser(session=None):
    if session:
        userId = hasUserId(session)
        user   = getSessionData(session, 'meta')
        perms  = getSessionData(session, 'permissions')
        return dict({'id': userId, 'permissions': perms, 'meta': user})
    return None

def getStartEnd(start=None, end=None, type='short'):
    if start:
        start = date.datetime.strptime(start, getSettings('date.short'))
        if not end:
            end = start + date.timedelta(days=DAYS)
    if end:
        end = date.datetime.strptime(end, getSettings('date.short'))+date.timedelta(days=1)
        if not start:
            start = end - date.timedelta(days=DAYS)
    start = start.strftime(getSettings('date.%s'%type))
    end   = end.strftime(getSettings('date.%s'%type))
    return start, end

def getSessionData(session=None, key=None):
    if session.has_key(key):
      return session[key]
    return ''

def getSettings(key=None):
    return get_current_registry().settings[key]

def getHttpRequest(uri=None, data=None):
    if data:
        data = urlencode(data)
    setdefaulttimeout(3)
    req   = Request(uri, data, AGENT)
    response = urlopen(req)
    try: content = response.read()
    except Exception, e: print "Failed to content: "%(e.reason)
    return content
