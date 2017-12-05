from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth

from parser import Parser, ParserBadRequestError


class Controller:
    app = Flask(__name__)
    auth = HTTPBasicAuth()

    @staticmethod
    @app.errorhandler(ParserBadRequestError)
    def error_handler(error):
        return 'Error: {}'.format(error), 400

    @staticmethod
    @auth.get_password
    def get_pw(username):
        if username == 'admin':
            return 'admin'
        return None

    @staticmethod
    @app.route('/')
    @auth.login_required
    def index():
        return '{}/{}'.format(Parser.current, Parser.count)

    @staticmethod
    @app.route('/stop')
    @auth.login_required
    def stop():
        Parser.stop_parsing()
        return 'Ok'

    @staticmethod
    @app.route('/start')
    @auth.login_required
    def start():
        Parser.start_parsing(request.args.get('url'), int(request.args.get('count')))
        return 'Ok'

    @staticmethod
    @app.route('/result')
    @auth.login_required
    def result():
        return '<br/>'.join(Parser.parsed)

    @staticmethod
    @app.route('/clear')
    @auth.login_required
    def clear():
        Parser.clear()
        return 'Ok'

    @classmethod
    def run(cls, **kwargs):
        cls.app.run(**kwargs)
