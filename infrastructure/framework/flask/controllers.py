import flask
from http import HTTPStatus

from flask import Response, g

from application.commands import AddItemCommand
from application.queries import GetItemsQuery
from application.response import json_response
from application.settings import APPLICATION_NAME
from infrastructure.framework.flask.base import RouteController
from infrastructure.framework.flask.authentication import authenticate


class InfoController(RouteController):

    def on_get(self):
        doc = {
            'framework': 'Flask {}'.format(flask.__version__),
            'application': APPLICATION_NAME,
        }
        body = json_response(doc)
        status = HTTPStatus.OK
        return body, status


class ItemsController(RouteController):
    def on_get(self):
        query = GetItemsQuery()
        if not query.is_valid():
            # TODO: Add error details
            return '', HTTPStatus.BAD_REQUEST

        result = self._query_bus.execute(query)
        body = json_response(result)
        status = HTTPStatus.OK
        return body, status

    @authenticate
    def on_post(self):
        command = AddItemCommand({
            **flask.request.json,
            'seller_id': g.user_id
        }, strict=False)
        command_name = type(command).__name__

        import pdb;pdb.set_trace()
        if not command.is_valid():
            flask.abort(Response(json_response({'title': 'Invalid Command',
                                                'description': f'{command_name} validation failed due to {command.validation_errors()}'}),
                                 status=HTTPStatus.BAD_REQUEST))

        try:
            result = self._command_bus.execute(command)
            return json_response(result), HTTPStatus.OK
        except Exception as e:
            flask.abort(Response(json_response({'title': f'Failed to execute {command_name}',
                                                'description': str(e)}),
                                 status=HTTPStatus.BAD_REQUEST))
