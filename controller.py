from flask import Flask, jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth

from parser import Parser, ParserError


class Controller:
    app = Flask(__name__)
    auth = HTTPBasicAuth()

    @staticmethod
    @app.errorhandler(ParserError)
    def parser_running_error_handler(e):
        return jsonify(error=dict(
                           code=e.code,
                           message=e.message)
                       ), e.code

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
        current, end = Parser.get_status()
        return jsonify(current=current, end=end)

    @staticmethod
    @app.route('/stop')
    @auth.login_required
    def stop():
        Parser.stop_parsing()
        return '', 200

    @staticmethod
    @app.route('/start')
    @auth.login_required
    def start():
        Parser.start_parsing(request.args.get('url'), int(request.args.get('count')))
        return '', 200

    @staticmethod
    @app.route('/result')
    @auth.login_required
    def result():
        return jsonify(parsed=list(Parser.parsed))

    @staticmethod
    @app.route('/clear')
    @auth.login_required
    def clear():
        Parser.clear()
        return '', 200

    @classmethod
    def run(cls, **kwargs):
        cls.app.run(**kwargs)
