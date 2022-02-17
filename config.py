import os
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec


base_dir = os.path.dirname(os.path.abspath(__file__))

security_definitions = {
    "basicAuth": {
        "type": "basic"
    }
}

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(base_dir, 'base.db')
    TEST_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Зачем эта настройка: https://flask-sqlalchemy-russian.readthedocs.io/ru/latest/config.html#id2
    DEBUG = True
    PORT = 5000
    SECRET_KEY = "My secret key =)"
    RESTFUL_JSON = {
        'ensure_ascii': False,
    }
    APISPEC_SPEC= APISpec(
        title='Notes Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        securityDefinitions=security_definitions,
        security=[],
        openapi_version='2.0.0'
    )
    APISPEC_SWAGGER_URL= '/swagger'  # URI API Doc JSON
    APISPEC_SWAGGER_UI_URL = '/swagger-ui'  # URI UI of API Doc
    LANGUAGES = ['en', 'ru']