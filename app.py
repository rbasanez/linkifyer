import argparse
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup

import os
from flask import Flask, json, jsonify, request, render_template, url_for, flash, redirect
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy.sql import text, func
from sqlalchemy_serializer import SerializerMixin
from pathlib import Path
from urllib.parse import quote
from modules.forms import GetLinkForm, LoginForm, RegisterForm, FetchUrlForm
from modules.hash import hash_password, validate_passwords
from modules.link_data import LinkData
from modules.logger import logger
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from modules.site_actions import *
from modules.item_actions import *


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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{Path(__file__).resolve().parent}/database.db'
app.config['SECRET_KEY'] = 'b01800a69ae34b80972910eb5ce7a284'
app.config["APPLICATION_ROOT"] = args.prefix

db = SQLAlchemy(app)

class Users (db.Model, UserMixin):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), nullable=False, unique=True)
    password   = db.Column(db.String(50), nullable=False)
    fname      = db.Column(db.String(50), nullable=True)
    lname      = db.Column(db.String(50), nullable=True)
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Links (db.Model, SerializerMixin):
    id          = db.Column(db.Integer, primary_key=True)
    hash        = db.Column(db.String(50), nullable=False, unique=True)
    user_id     = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    host        = db.Column(db.Text(), nullable=False)
    url         = db.Column(db.Text(), nullable=False)
    title       = db.Column(db.Text(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    models      = db.Column(db.Text(), nullable=True)
    tags        = db.Column(db.Text(), nullable=True)
    collections = db.Column(db.Text(), nullable=True)
    poster_path = db.Column(db.Text(), nullable=True)
    icon_path   = db.Column(db.Text(), nullable=True)
    favorite    = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, default=func.now())

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = GetLinkForm()
    return render_template('home.html', page_title='home', form=form)
@app.route('/library', methods=['GET', 'POST'])

@login_required
def library():
    form = GetLinkForm()
    return render_template('library.html', page_title='library', form=form)

@app.route('/fetch', methods=['GET', 'POST'])
@login_required
def fetch():
    user_id = current_user.id
    url = request.args.get('url', None)
    where = request.args.get('w', 'library')
    form = FetchUrlForm()
    if form.validate_on_submit():
        link_data = Links.query.filter_by(user_id=current_user.id, hash=form.hash.data).first()
        
        if link_data:
            for key, value in form.data.items():
                if hasattr(link_data, key):
                    setattr(link_data, key, value)
        else:
            form_data = {k: v for k, v in form.data.items() if k != 'csrf_token' and hasattr(link_data, k)}
            link_data = Links(user_id=current_user.id, **form_data)
            db.session.add(link_data)
        db.session.commit()
        
        # save poster
        save_image(form.poster_url.data, form.poster_path.data, fileType='poster')
        # save icon
        save_image(form.icon_url.data, form.icon_path.data, fileType='icon')
        return redirect(url_for(where))
    else:
        logger.info(f'processing url: <{url}>')
        link_data = LinkData()
        link_data.start(url, user_id)
        link_data.get_title()
        link_data.get_description()
        link_data.get_models()
        link_data.get_tags()
        link_data.get_collections()
        link_data.get_icon()
        link_data.get_poster()
        for key, value in vars(link_data).items():
            if key and hasattr(form, key): form[key].data = value
    # # save poster
    # save_image(link_data.poster_url, link_data.poster_path, fileType='poster')
    # # save icon
    # save_image(link_data.icon_url, link_data.icon_path, fileType='icon')

    # table_columns = list(Links().to_dict().keys())
    # table_data = {key: value for key, value in vars(link_data).items() if key in table_columns}

    # table_links = Links.query.filter_by(user_id=link_data.user_id, hash=link_data.hash).first()
    # if table_links:
    #     for key, value in table_data.items():
    #         setattr(table_links, key, value)
    # else:
    #     table_links = Links(**table_data)
    #     db.session.add(table_links)
    # db.session.commit()
    

    return render_template('fetch.html', page_title='fetch', link=url, form=form, item=link_data)

@app.route('/edit', methods=['GET','POST'])
@app.route('/edit/<id>', methods=['GET','POST'])
@login_required
def edit(id):
    form = None
    item_found = None
    try:
        form = FetchUrlForm()
        if form.validate_on_submit():
            form_data = {k: v for k, v in form.data.items() if k != 'csrf_token'}
            item_found = Links.query.filter_by(user_id=current_user.id, hash=form.hash.data).first()
            if item_found:
                for k, v in form.data.items():
                    setattr(item_found, k, v)
            else:
                items = Links(user_id=current_user.id, **form_data)
                db.session.add(items)
            db.session.commit()
            return redirect(url_for('library'))
        else:
            item_found = Links.query.filter_by(id=id).first()
            for k, v in item_found.to_dict().items():
                if v and hasattr(form, k):
                    form[k].data = v
    except Exception as err:
        flash(quote(str(err)), 'danger')
    return render_template('edit.html', page_title='edit', form=form, item=item_found)

@app.route('/items/<id>', methods=['GET'])
def items(id):
    items = dict()
    if id == 'all':
        items = Links.query.filter_by(user_id=current_user.id).order_by(text("last_update desc")).all()
    return jsonify([item.to_dict() for item in items])


@app.route('/delete', methods=['GET'])
@app.route('/delete/<item_id>', methods=['GET'])
@login_required
def delete(item_id):
    table_links = Links.query.filter_by(id=item_id).first()
    db.session.delete(table_links)
    db.session.commit()
    return str(1)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = None
    password = None
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data.lower()
        password=form.password.data
        user = Users.query.filter_by(username=username).first()
        if user:
            if validate_passwords(password, user.password):
                login_user(user)
                return redirect(request.args.get('next', url_for('home')))
            else:
                form.password.errors=[f'username and password doesn\'t match']
        else:
            form.username.errors=[f'username not found']
    form.password.data = ''
    return render_template('login.html', page_title='login', username=username, password=password, form=form, login_required=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = None
    password = None
    form = RegisterForm()
    if form.validate_on_submit():
        username=form.username.data.lower()
        password=hash_password(form.password.data)
        user = Users.query.filter_by(username=username).first()
        if user is None:
            user = Users(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            form.username.errors=[f'username already exists!']
    form.password.data = ''
    return render_template('register.html', page_title='register', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('User logged out', 'info')
    return redirect(url_for('login'))



# Function to handle simple WSGI requests
def simple(env, resp):
    resp('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'404 Not Found']

app.wsgi_app = DispatcherMiddleware(simple, {args.prefix: app.wsgi_app})

if __name__ == "__main__":
    url = f"{protocol}://{args.host}:{args.port}{args.prefix}"
    # Open browser in incognito mode if specified
    if args.incognito:
        url = f"{protocol}://{args.host}:{args.port}"
        os.system(f'start chrome.exe -incognito --new-window "{url}"')

    try:
        if args.dev:
            # Run the application in development mode
            app.run(debug=True, host=args.host, port=args.port)

        else:
            # Run the application using Waitress server
            from waitress import serve as waitress_serve
            logger.info(url)
            waitress_serve(app, host=args.host, port=args.port, url_scheme=protocol, threads=100)

    except Exception as err:
        logger.error(err)
        exit(3)