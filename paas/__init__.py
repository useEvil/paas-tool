from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    session_factory = UnencryptedCookieSessionFactoryConfig('abetterplacetoshop')
    config = Configurator(settings=settings, session_factory=session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('app_create', '/app/create')
    config.add_route('app_view', '/app/view/{id}')
    config.add_route('app_edit', '/app/edit/{id}')
    config.add_route('deploy_create', '/deploy/create')
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
    config.add_route('rest_projects', '/REST/paas/projects')
    config.add_route('rest_builds', '/REST/paas/builds/{project}')
    config.add_route('rest_environments', '/REST/paas/environments/{project}')
    config.scan()
    return config.make_wsgi_app()

