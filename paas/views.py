from pyramid.view import view_config

from paas.models import DBSession, MyModel, Application, Deploy
#from paas.authorization import AuthorizationControl
from paas.helpers import *

@view_config(route_name='index', renderer='templates/index.pt')
#@AuthorizationControl('index')
def index(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one':one, 'project':'paas'}

@view_config(route_name='app_view', renderer='templates/view.pt')
#@AuthorizationControl('index')
def view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one':one, 'project':'paas'}

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one': one, 'project': 'paas'}
