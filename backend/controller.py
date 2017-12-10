from flask import Flask, jsonify, render_template
from flask import request
from flask_httpauth import HTTPBasicAuth

from parser import ParserError, Parser

SUCCESS_STATUS = 'success'
ERROR_STATUS = 'error'


class Controller:
    app = Flask(__name__,
                static_folder="../frontend/dist/static",
                template_folder="../frontend/dist")
    auth = HTTPBasicAuth()

    @staticmethod
    @app.errorhandler(ParserError)
    def parser_running_error_handler(e):
        return jsonify(status=ERROR_STATUS,
                       error=dict(
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
        return render_template('index.html')

    @staticmethod
    @app.route('/api/status')
    @auth.login_required
    def status():
        current, end = Parser.get_status()
        return jsonify(status=SUCCESS_STATUS, current=current, end=end)

    @staticmethod
    @app.route('/api/stop')
    @auth.login_required
    def stop():
        Parser.stop_parsing()
        return jsonify(status=SUCCESS_STATUS)

    @staticmethod
    @app.route('/api/start')
    @auth.login_required
    def start():
        Parser.start_parsing(request.args.get('url'), int(request.args.get('count')))
        return jsonify(status=SUCCESS_STATUS)

    @staticmethod
    @app.route('/api/result')
    @auth.login_required
    def result():
        return jsonify(status=SUCCESS_STATUS, result=Parser.get_result())

    @staticmethod
    @app.route('/api/clear')
    @auth.login_required
    def clear():
        Parser.clear_result()
        return jsonify(status=SUCCESS_STATUS)

    @classmethod
    def run(cls, **kwargs):
        cls.app.run(**kwargs)
