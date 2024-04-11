import os
import uuid
import re
import logging
import argparse
from pathlib import Path
from models.logger import logger, logging
from models.user import User
from models.item import Item
from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_session import Session
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Parsing command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default='localhost', help='Host address (default: localhost)')
parser.add_argument('--port', type=int, default=9191, help='Port number (default: 9191)')
parser.add_argument('--prefix', type=str, default='', help='Site Prefix (default: /)')
parser.add_argument('--https', action='store_true', help='Enable HTTPS (default: HTTP)')
parser.add_argument('--incognito', action='store_true', help='Open browser in incognito mode')
parser.add_argument("--dev", action="store_true", help="Run in development mode (debug=True)")
args = parser.parse_args()

protocol = "https" if args.https else "http"

if args.dev:
    logging.getLogger().setLevel(logging.DEBUG)

# Class to store application information
class App:
    def __init__(self) -> None:
        app_path = Path(__file__).resolve()
        self.name = app_path.name
        self.path = app_path.parent
        self.scheme = protocol
        self.host = args.host
        self.port = args.port
        self.prefix = args.prefix

# Initializing App instance
app_info = App()
app_info.name = 'linkifyer'

# Initializing database and models

user = User()
user.db_start()
item = Item()
item.db_start()

# Function to validate session
def validate_session():
    return session.get("session_id") is not None

# Function to extract page title from path
def get_page_title(path):
    try: return path.split('.')[1]
    except: return path

# Function to start the Flask application
def start():
    # Create a Flask application instance
    app = Flask(__name__)
    app.secret_key = '83592b9b85b2442eb9aedf4ff60fa24e'
    app.config.from_object(__name__)
    app.config['PREFERRED_URL_SCHEME'] = app_info.scheme
    app.config["APPLICATION_ROOT"] = app_info.prefix
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False
    app.config['SESSION_FILE_DIR'] = app_info.path / 'session_data'
    Session(app)

    # Function to run before each request
    @app.before_request
    def before_request_func():
        logger.debug('%s -> %s %s %s', request.remote_addr, request.method, request.scheme, request.path)
        if re.search('/about|/login|/register|/logout|/static', request.path) == None:
            if not validate_session():
                logger.warning('%s %s', request.remote_addr, 'auth required')
                return redirect(url_for('login'))

    # Function to run after each request
    @app.after_request
    def after_request_func(response):
        log_level = logging.DEBUG  # Default to DEBUG level
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        logger.log(log_level, '%s <- %s %s %s %s', request.remote_addr, request.method, response.status, request.scheme, request.path)
        return response
    
    # Route for home page
    @app.route("/")
    def home():
        error = None
        return render_template('home.html', page_title=get_page_title(request.endpoint), error=error)
    
    # Route for login page
    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        username = request.form.get('username', type=str, default=None)
        password = request.form.get('password', type=str, default=None)
        if request.method == "POST":
            user.populate(username=username)
            if user.find():
                if user.validate(password):
                    for k, v in user.__dict__.items():
                        if k != "password": session[k] = v
                    session["session_id"] = str(uuid.uuid4())
                    logger.info(session)
                    return redirect(url_for('home'))
                else:
                    error = "password and username don't match"
                    session.clear()
                    user.clear()
            else:
                error = 'username not found, you should try to register'
                session.clear()
                user.clear()
        return render_template('login.html', page_title=get_page_title(request.endpoint), error=error, username=username)
    
    # Route for logout
    @app.route("/logout", methods=["GET"])
    def logout():
        user.clear()
        session.clear()
        return redirect(url_for('login'))

    # Route for registration
    @app.route("/register", methods=["GET", "POST"])
    def register():
        error = None
        user.clear()
        username = request.form.get('username', type=str, default=None)
        password = request.form.get('password', type=str, default=None)
        if request.method == "POST":
            user.populate(username=username, password=password)
            if user.find():
                error = 'username already exists'
            else:
                if user.push():
                    return redirect(url_for('login'))
                else:
                    error = 'something went wrong, you better check the logs'
        return render_template('register.html', page_title=get_page_title(request.endpoint), error=error, username=username)
    
    # Route for search
    @app.route('/search', methods=['GET'])
    def search():
        error = None
        if request.method == 'GET':
            url = request.args.get('url')
            item.clear()
            item.user_id = session['user_id']
            item.request_url(url)
            item.get_hash()
            item.get_title()
            item.get_poster()
            item.get_icon()
            item.get_tags()
            item.get_description()
            # item.generate_tags()
        return render_template('search.html', page_title=get_page_title(request.endpoint), item=item.__dict__, error=error)
    
    # Route for deleting an item
    @app.route('/delete/<string:user_id>/<string:item_hash>', methods=['GET'])
    def delete(user_id, item_hash):
        item.delete_item(user_id, item_hash)
        return redirect(url_for('library'))

    # Route for saving an item
    @app.route('/save', methods=['POST'])
    def save():
        item.title = request.form.get('title', type=str, default=None)
        item.tags = request.form.get('tags', type=str, default=None)
        item.description = request.form.get('description', type=str, default=None)
        item.save_poster()
        item.save_icon()
        item.save_data()
        return str(item.save_data())
    
    @app.route('/favorite', methods=['GET'])
    def favorite():
        item_id = request.args.get('item_id', None)
        success, result = item.toggle_favorite(item_id)
        return str(result)
    
    # Route for library
    @app.route('/library', methods=['GET'])
    def library():
        error = None
        return render_template('library.html', page_title=get_page_title(request.endpoint), error=error)

    # Route for library
    @app.route('/AllItems', methods=['GET'])
    def all_items():
        item.user_id = session['user_id']
        success, result = item.get_all_items()
        print(result)
        return jsonify(result)

    # Error handler for 404 Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('home'))

    # Function to handle simple WSGI requests
    def simple(env, resp):
        resp('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']
    
    # Wrapping the application with DispatcherMiddleware
    app.wsgi_app = DispatcherMiddleware(simple, {app_info.prefix: app.wsgi_app})

    return app

if __name__ == '__main__':
    # Start the Flask application
    app = start()
    

    url = f"{app_info.scheme}://{args.host}:{args.port}{app_info.prefix}"
    # Open browser in incognito mode if specified
    if args.incognito:
        url = f"{app_info.scheme}://{args.host}:{args.port}"
        os.system(f'start chrome.exe -incognito --new-window "{url}"')

    try:
        if args.dev:
            # Run the application in development mode
            app.run(debug=True, host=app_info.host, port=app_info.port)

        else:
            # Run the application using Waitress server
            from waitress import serve as waitress_serve
            waitress_serve(app, host=app_info.host, port=app_info.port, url_scheme=app_info.scheme, threads=100)

    except Exception as err:
        logger.error(err)
        exit(3)