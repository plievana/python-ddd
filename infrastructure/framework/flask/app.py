from flask import Flask
from composition_root import FlaskContainer


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule('/', 'index', FlaskContainer.info_controller_factory().on_get)
    app.add_url_rule('/items', 'get_items', FlaskContainer.items_controller_factory().on_get, methods=['GET'])
    app.add_url_rule('/items', 'post_item', FlaskContainer.items_controller_factory().on_post, methods=['POST'])
    return app

