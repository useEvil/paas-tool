"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import os
import socket
import base64
import logging
import urllib
import urllib2
import sys

from re import findall
from string import Template

from paas.models import Application, Deploy
from paas.helpers import *

Log = logging.getLogger(__name__)

class CloudZilla(object):
    """CloudZilla API Library"""
    def login(self, userId=None, userPass=None):
        Log.debug('login')
        """ sends data to CloudZilla System """
        if not userId and not userPass: return
        uri    = '%s%s/'%(getSettings('cloud.domain'), getSettings('cloud.path'))
        data = {'user': userId, 'pass': userPass}
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        try:
            code, content = self._sendToCloudZilla(uri, data)
            if code == 401:
                print 'Login Info Incorrect'
                sys.exit()
            elif code == 200:
                print 'Login Correct'
                return
        except urllib2.URLError, e:
            print 'Failed to login'
            Log.error(e)
            sys.exit()

    def create(self, params=None, userId=None, userEmail=None):
        Log.debug('create')
        """ sends data to CloudZilla System """
        if not userId: userId = params['login']
        type = Application().getById(params['type'])
        uri  = '%s%s/ticket/new'%(getSettings('cloud.domain'), getSettings('cloud.path'))
        body = Template("""Project:
                                $project

                             Environment:
                                $environment

                             Release Date:
                                $releaseDate

                             Version:
                                $version

                             Rollback:
                                $rollback

                             Properties:
                                $properties

                             Notes:
                                $notes
                             """)
        ticket = Template("""id: ticket/new
Queue: $q_name
Requestor: $req_email
Subject: $subject
Cc: $cc_email
Owner: $owner
Status: $status
Priority: $priority
Starts: $starts
Text: $content""")
        data = dict({
            'q_name': 'General',
            'status': 'new',
            'req_email': userEmail,
            'cc_email': params['mailer'],
            'subject': '%s (%s) to [%s]'%(type.label, params['project'], params['environment'].upper()),
            'owner': '',
            'priority': '',
            'starts': params['releaseDate'],
            'content': body.safe_substitute(params)
        })
        data = {'user': userId, 'pass': params['password'], 'content': ticket.safe_substitute(data)}
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        try:
            code, content = self._sendToCloudZilla(uri, data)
            try: rt_id = findall("Ticket (\d+) created", content)[0]
            except IndexError: print 'Unknown CloudZilla ID'; sys.exit()
            Log.debug('==== rt_id [%s]'%(rt_id))
            return rt_id
        except urllib2.URLError, e:
            print 'Failed to create'
            Log.error(e)
            sys.exit()

    def comment(self, params=None, userId=None, userEmail=None):
        Log.debug('comment')
        """ sends data to CloudZilla System """
        if not userId: userId = params['login']
        uri    = '%s%s/ticket/%d/comment'%(getSettings('cloud.domain'), getSettings('cloud.path'), params['releaseCloudZilla'])
        ticket = Template("""id: $rt_id
Action: Comment
Text: $content""")
        data = dict({
            'rt_id': params['releaseCloudZilla'],
            'content': params['comment']
        })
        data = {'user': userId, 'pass': params['password'], 'content': string.safe_substitute(data)}
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        try:
            code, content = self._sendToCloudZilla(uri, data)
            try: rt_id = findall("Ticket (\d+) created", content)[0]
            except IndexError: print 'Unknown CloudZilla ID'; sys.exit()
            Log.debug('==== rt_id [%s]'%(rt_id))
            return rt_id
        except urllib2.URLError, e:
            print 'Failed to comment'
            Log.error(e)
            sys.exit()

    def approve(self, releaseCloudZilla=None, userId=None):
        Log.debug('approve')
        """ sends data to CloudZilla System """
        if not releaseCloudZilla and not userId: return
        uri    = '%s%s/ticket/%d/comment'%(getSettings('cloud.domain'), getSettings('cloud.path'), releaseCloudZilla)
        ticket = Template("""id: $rt_id
Action: Comment
Text: $content""")
        data = dict({
            'rt_id': releaseCloudZilla,
            'content': 'Approved by %s'%(userId)
        })
        data = {'user': userId, 'content': ticket.safe_substitute(data)}
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        try:
            code, content = self._sendToCloudZilla(uri, data)
            try: result = findall('Message recorded', content)[0]
            except IndexError: print 'Message Not Authorized'; sys.exit()
        except urllib2.URLError, e:
            print 'Failed to approve'
            Log.error(e)
            sys.exit()

    def resolved(self, releaseCloudZilla=None, userId=None):
        Log.debug('resolved')
        """ sends data to CloudZilla System """
        if not releaseCloudZilla and not userId: return
        uri    = '%s%s/ticket/%d/comment'%(getSettings('cloud.domain'), getSettings('cloud.path'), releaseCloudZilla)
        ticket = Template("""id: $rt_id
Action: Comment
Status: resolved
Text: $content""")
        data = dict({
            'rt_id': params['releaseCloudZilla'],
            'content': 'Resolved by %s'%(userId)
        })
        data = {'user': userId, 'content': ticket.safe_substitute(data)}
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        try:
            code, content = self._sendToCloudZilla(uri, data)
            try: result = findall("Message recorded", content)[0]
            except IndexError: print 'Message Not Resolved'; sys.exit()
            return
        except urllib2.URLError, e:
            print 'Failed to resolve'
            Log.error(e)
            sys.exit()

    def _sendToCloudZilla(self, uri=None, data=None):
        if not uri and not data: return
        Log.debug('_sendToCloudZilla')
        """ sends data to CloudZilla System """
        Log.debug('==== data [%s]'%(data))
        Log.debug('==== uri [%s]'%(uri))
        pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pass_mgr.add_password(None, uri, data['user'], data['pass'])
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(pass_mgr)))
        data  = urllib.urlencode(data)
        login = urllib2.Request(uri, data)
        try:
            response = urllib2.urlopen(login)
            code     = response.code
            content  = response.read()
#            Log.debug('==== response code [%s]'%(code))
#            Log.debug('==== response read [%s]'%(content))
        except urllib2.URLError, e:
            print 'Failed to get Authenticated Session'
            Log.error(e)
            sys.exit()
        return code, content
