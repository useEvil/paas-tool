import time
import urllib
import httplib
import logging
import calendar
import datetime as date
import simplejson as json
import webhelpers.paginate as paginate

from re import findall
from operator import itemgetter, attrgetter
from pyramid.view import view_config

from paas.models import Application, Deploy
#from paas.authorization import AuthorizationControl
from paas.helpers import *

USER = {'id': 'PaaS Tool'}
Log = logging.getLogger(__name__)

@view_config(route_name='rest_app_listing', renderer='json', request_method='GET')
#@AuthorizationControl('administer')
def listing(request):
    Log.debug('listing')
    """ json data for deploys """
    params       = request.params
    currentPage  = int(params.get('page') or 1)
    itemsPerPage = int(params.get('rp') or 30)
    sortName     = params.get('sortname') or 'dealEndDate'
    sortOrder    = params.get('sortorder') or 'desc'
    query        = params.get('query')
    type         = params.get('qtype') or ''
    qrange       = params.get('range') or ''
    if query:
        appObjs = Application().getList()
        page    = paginate.Page(appObjs, page=currentPage, items_per_page=itemsPerPage)
        total   = page.item_count
    else:
        offset  = (currentPage - 1) * itemsPerPage
        appObjs = Application().getSet(itemsPerPage, offset)
        total   = Application().getTotal()
        page    = paginate.Page(appObjs, page=1, items_per_page=itemsPerPage)
    result      = { }
    result['rows']  = [ ]
    result['page']  = currentPage
    result['total'] = total
    for item in page.items:
        row = {'id': item.id, 'cell': ['<a style="color: blue;text-decoration: underline;" href="/view/%s" class="release" id="view_%s" title="View">%s</a>'%(item.id, item.id, item.id)]}
        row['cell'].append('<span title="%s">%s</span>'%(item.project, item.project))
        row['cell'].append(item.environment)
        row['cell'].append('<span title="%s">%s</span>'%(item.version, item.version))
        row['cell'].append(item.createdDate.strftime(getSettings('date.long')))
        if item.approvedBy:
            row['cell'].append(item.approvedBy)
        else:
            row['cell'].append('<a href="#" id="approve_%s" class="approve_release">Approve</a>'%(item.id))
        row['cell'].append(item.createdBy)
        row['cell'].append('<a style="color: blue;text-decoration: underline;" href="%s/Ticket/Display.html?id=%d" class="release" id="rt_%d" title="RT %d" target="_rt">%d</a>'%(getSettings('rt.domain'), item.rt, item.rt, item.rt, item.rt))
        row['cell'].append(item.release_type.label)
        row['cell'].append(item.release_status.label)
        result['rows'].append(row)
    return result

@view_config(route_name='rest_projects', renderer='json', request_method='GET')
#@AuthorizationControl('authorize')
def projects(request):
    uri = '%s%s/site'%(getSettings('dui.domain'), getSettings('dui.path'))
    Log.debug('==== uri [%s]'%(uri))
    content = getHttpRequest(uri)
    try: projects = findall('<a href="/admin/default/design/[^"]+">([^<]+)</a>', content)
    except Exception: print "No projects found"
    Log.debug('==== projects [%s]'%(projects))
    return projects

@view_config(route_name='rest_environments', renderer='json', request_method='GET')
#@AuthorizationControl('authorize')
def environments(request):
    project = request.matchdict['project']
    Log.debug('==== project [%s]'%(project))
    uri = '%s%s/design/%s'%(getSettings('dui.domain'), getSettings('dui.path'), project)
    Log.debug('==== uri [%s]'%(uri))
    content = getHttpRequest(uri)
    try: envs = findall("<h4>[^<]+<b>([^<]+)</b>", content)
    except Exception: print "No environments found"
    Log.debug('==== envs [%s]'%(envs))
    return envs

@view_config(route_name='rest_builds', renderer='json', request_method='GET')
#@AuthorizationControl('authorize')
def builds(request):
    project = request.matchdict['project']
    Log.debug('==== project [%s]'%(project))
    uri = '%s%s/peek/%s/bin/application.conf'%(getSettings('dui.domain'), getSettings('dui.path'), project)
    Log.debug('==== uri [%s]'%(uri))
    content = getHttpRequest(uri)
    try: type = findall('BUILD_REMOTE_LOC=\$REMOTE_SVR/builds/(\w+)', content)[0]
    except IndexError: print "No app type found"; return
    Log.debug('==== type [%s]'%(type))
    uri = '%s%s/%s/%s/'%(getSettings('builds.domain'), getSettings('builds.path'), type, project)
    Log.debug('==== uri [%s]'%(uri))
    content = getHttpRequest(uri)
    Log.debug('==== content [%s]'%(content))
    try:
        builds = findall('<a href="(\w+)-(\w*)-([b]\d+)-(.+)[.]\w+">', content)
        sorted(builds, key=itemgetter(2), reverse=True)
    except Exception: print "No builds found"
    if not builds:
        try:
            builds = findall('<a href="(\w+)-([b]\d+)-(.+)[.]\w+">', content)
            sorted(builds, key=itemgetter(1), reverse=True)
        except Exception: print "No builds found"

    Log.debug('==== len(builds) [%s]'%(len(builds)))
    Log.debug('==== builds [%s]'%(builds))
    return builds
    length = len(builds)
    if length > 10:
        return builds[length-10:length]
    else:
        return builds

@view_config(route_name='rest_app_create', renderer='json', request_method='GET')
#@AuthorizationControl('administer')
def create(request):
    USER['id'] = hasUserId(request.session)
    params = request.params
    Log.debug("REST: create test: %s"%(params['testName']))
    _create_rule_from_params(params)
    try:
        _create_rule_from_params(params)
        Log.debug("Creating test: %s"%(params['testName']))
    except Exception, e:
        Log.error(e.message)
        return { 'status': 404, 'message': 'Failed to Create Test' }
    return { 'status': 200, 'message': 'Successfully Created Test' }

@view_config(route_name='rest_app_update', renderer='json', request_method='GET')
#@AuthorizationControl('administer')
def update(request):
    USER['id'] = hasUserId(request.session)
    id     = request.matchdict['id']
    params = request.params
    Log.debug("REST: update test: %s"%(id))
    rule = SessionTest().getById(id)
    _update_rule_from_params(rule, params)
    try:
        rule = SessionTest().getById(id)
        _update_rule_from_params(rule, params)
        Log.debug("Updating Data for test: %s"%(id))
    except Exception, e:
        Log.error(e.message)
        return { 'status': 404, 'message': 'Failed to Update Test' }
    return { 'status': 200, 'message': 'Successfully Updated Test' }

@view_config(route_name='rest_app_delete', renderer='json', request_method='GET')
#@AuthorizationControl('administer')
def delete(request):
    USER['id'] = hasUserId(request.session)
    id = request.matchdict['id']
    Log.debug("REST: delete test: %s"%(id))
    try:
        rule = SessionTest().delete(id)
        Log.debug("Deleting Data for test: %s"%(id))
    except Exception, e:
        Log.error(e.message)
        return { 'status': 404, 'message': 'Failed to Delete Test' }
    return { 'status': 200, 'message': 'Successfully Deleted Test' }

#@view_config(route_name='app_status', renderer='json', request_method='GET')
#@AuthorizationControl('administer')
def status(request):
    USER['id'] = hasUserId(request.session)
    id     = request.matchdict['id']
    status = request.matchdict['status']
    Log.debug("REST: update test status: %s to %s"%(id, status))
    try:
        rule = SessionTest().getById(id)
        rule.enabled = status
        Log.debug("Updating Status for test: %s to %s"%(id, status))
    except Exception, e:
        Log.error(e.message)
        return { 'status': 404, 'message': 'Failed to Update Test Status to: %s'%(status == 1 and 'Enabled' or 'Disabled') }
    return { 'status': 200, 'message': 'Successfully Updated Test Status to: %s'%(status == 1 and 'Enabled' or 'Disabled') }


## internal functions ##
def _str_to_date(strdate):
    """return a datetime obj from a string"""
    ruledate = None
    try:
        ruledate = date.datetime.strptime(strdate, getSettings('date.short'))
    except ValueError:
        raise
    return ruledate

def _check_for_add(self, value, list):
    if not list: return 1
    for obj in list:
        if obj.id == value: return 0
    return 1

def _check_for_delete(self, obj, list):
    if not list: return 1
    for value in list:
        if obj.id == value['id']: return 0
    return 1
