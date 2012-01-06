import datetime as date
import paas.helpers as h

from pyramid.view import view_config

from paas.models import DBSession, MyModel, Application, Deploy
from paas.authorization import AuthorizationControl

@view_config(route_name='index', renderer='templates/index.pt')
#@AuthorizationControl('index')
def index(request):
    now    = date.datetime.today().strftime(h.getSettings('date.long'))
    user   = h.getUser(request.session)
    userId = user and user['meta']['id'] or ''
    return {'date': now, 'h': h, 'user': user, 'id': userId}

@view_config(route_name='app_view', renderer='templates/view.pt')
#@AuthorizationControl('index')
def view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one': one, 'project': 'paas'}

@view_config(route_name='app_create', renderer='templates/create.pt')
#@AuthorizationControl('index')
def create(request):
    now    = date.datetime.today().strftime(h.getSettings('date.long'))
    user   = h.getUser(request.session)
    userId = user and user['meta']['id'] or ''
    return {'date': now, 'h': h, 'user': user, 'id': userId}

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one': one, 'project': 'paas'}
