from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth

from parser import Parser


class Controller:
    app = Flask(__name__)
    auth = HTTPBasicAuth()

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
        if Parser.parser_running():
            return '{}/{}'.format(Parser.current, Parser.count)
        else:
            return 'Parser isn\'t running'

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
        if Parser.parser_running():
            return 'Parser is already running'

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
        return '\n'.join(Parser.parsed)

    @classmethod
    def run(cls, **kwargs):
        cls.app.run(**kwargs)
