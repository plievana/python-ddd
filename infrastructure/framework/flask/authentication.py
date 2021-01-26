import base64
from http import HTTPStatus
from flask import request, Response, abort, g

from application.response import json_response
from infrastructure.framework.flask.base import RouteController


class UnauthenticatedException(Exception):
    """ Use this exception when authentication fails """
    pass


class ForbiddenException(Exception):
    """ Use this exception when permission check fails """
    pass


def authenticate(method):
    def wrapper(self):
        assert isinstance(self, RouteController), '@authenticate must be used with RouteController or derived classes'
        assert self._authentication_service is not None,\
            'You are using @authenticate for route {} but AuthenticationService not injected into {}'\
            .format(request.path, type(self).__name__)
        
        user = self._authentication_service.authenticate()
        g.user_id = user.id
        return method(self)
    return wrapper


class BasicAuthenticationService:
    def __init__(self, users_repository):
        self._users_repository = users_repository
    
    def authenticate(self):
        if request.headers.get('Authorization') is None:
            abort(Response(json_response({
                'title': 'Authentication failed',
                'description': 'Authorization header is missing'
            }), status=HTTPStatus.UNAUTHORIZED))

        try:
            auth_type, credentials = request.headers['Authorization'].split(' ')
        except Exception:
            abort(Response(json_response({
                'title': 'Authentication failed',
                'description': "Wrong Authentication header"
            })))

        if auth_type.lower() != 'basic':
            abort(Response(json_response({
                'title': 'Authentication failed',
                'description': "Expected 'Authorization: Basic <credentials>' header"
            }), status=HTTPStatus.UNAUTHORIZED))

        try:
            decoded_credentials = base64.b64decode(credentials)
            login, password = decoded_credentials.decode().split(':')
        except Exception as e:
            abort(Response(json_response({
                'title': 'Authentication failed',
                'description': f'Invalid credentials ({e})'
            }), status=HTTPStatus.UNAUTHORIZED))

        user = self._users_repository.get_user_by_login_and_password(login, password)

        if user is None:
            abort(Response(json_response({
                'title': 'Authentication failed',
                'description': 'Invalid credentials'
            }), status=HTTPStatus.UNAUTHORIZED))

        return user