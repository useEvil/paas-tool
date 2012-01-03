from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('app_view', '/app/view/{id}')
    config.add_route('app_edit', '/app/edit/{id}')
    config.add_route('deploy_view', '/deploy/view/{id}')
    config.add_route('deploy_edit', '/deploy/edit/{id}')
    config.add_route('home', '/home')
    config.add_route('rest_app_listing', '/REST/app/listing')
    config.add_route('rest_app_create', '/REST/app/create')
    config.add_route('rest_app_update', '/REST/app/update/{id}')
    config.add_route('rest_app_delete', '/REST/app/delete/{id}')
    config.add_route('rest_deploy_create', '/REST/deploy/create')
    config.add_route('rest_deploy_update', '/REST/deploy/update/{id}')
    config.add_route('rest_deploy_delete', '/REST/deploy/delete/{id}')
    config.scan()
    return config.make_wsgi_app()

