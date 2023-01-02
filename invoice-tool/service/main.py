from flask import Flask, Blueprint
from flask_restx import Api
from base.config import Config
from service.resources.invoices import api as invoices_namespace


def create_app():
    config = Config().get_config()
    url_prefix = config['UrlPrefix']
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    blueprint = Blueprint('api', __name__, url_prefix=url_prefix)
    api = Api(
        app= app,
        title='Nordpool Invoice Downloader Endpoints',
        version='1.0',
        # doc='/doc',
        description='Provides Endpoints exclusively for downloading the invoices from Nordpool.',
        terms_url='',
    )
    api.init_app(blueprint)
    app.register_blueprint(blueprint)
    api.add_namespace(ns=invoices_namespace, path='/')
    return app


flask_app = create_app()
