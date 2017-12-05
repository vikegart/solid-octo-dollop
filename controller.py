from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth

from parser import Parser, ParserRunningError, ParserNotRunningError


class Controller:
    app = Flask(__name__)
    auth = HTTPBasicAuth()

    @staticmethod
    @app.errorhandler(ParserRunningError)
    def parser_running_error_handler(_):
        return "You can't do this action, when parser is running", 400

    @staticmethod
    @app.errorhandler(ParserNotRunningError)
    def parser_running_error_handler(_):
        return "You can't do this action, when parser isn't running", 400

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
        return '{}/{}'.format(*Parser.get_status())

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
