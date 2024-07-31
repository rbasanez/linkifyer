from datetime import datetime, timezone # type: ignore
from flask import Flask, json, jsonify, request, render_template, url_for, flash, redirect
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, func
from sqlalchemy_serializer import SerializerMixin
from pathlib import Path # type: ignore
from urllib.parse import quote  # type: ignore
from modules.forms import GetLinkForm, LoginForm, RegisterForm, FetchUrlForm
from modules.hash import hash_password, validate_passwords
from modules.item import Item
from modules.logger import logger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{Path(__file__).resolve().parent}/database.db'
app.config['SECRET_KEY'] = 'b01800a69ae34b80972910eb5ce7a284'

db = SQLAlchemy(app)


class Users (db.Model, UserMixin):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), nullable=False, unique=True)
    password   = db.Column(db.String(50), nullable=False)
    fname      = db.Column(db.String(50), nullable=True)
    lname      = db.Column(db.String(50), nullable=True)
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Items (db.Model, SerializerMixin):
    id          = db.Column(db.Integer, primary_key=True)
    hash        = db.Column(db.String(50), nullable=False, unique=True)
    user_id     = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False,)
    url         = db.Column(db.Text(), nullable=False)
    host        = db.Column(db.Text(), nullable=False)
    schema      = db.Column(db.Text(), nullable=False)
    title       = db.Column(db.Text(), nullable=True)
    tags        = db.Column(db.Text(), nullable=True)
    actors      = db.Column(db.Text(), nullable=True)
    collections = db.Column(db.Text(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    poster      = db.Column(db.Text(), nullable=True)
    icon        = db.Column(db.Text(), nullable=True)
    favorite    = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, default=func.now())

item = Item()

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
    link = None
    item.clear()
    form = GetLinkForm()
    return render_template('home.html', page_title='home', link=link, form=form, item=item)

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
            item_found = Items.query.filter_by(user_id=current_user.id, hash=form.hash.data).first()
            if item_found:
                for k, v in form.data.items():
                    setattr(item_found, k, v)
            else:
                items = Items(user_id=current_user.id, **form_data)
                db.session.add(items)
            db.session.commit()
            return redirect(url_for('library'))
        else:
            item_found = Items.query.filter_by(id=id).first()
            for k, v in item_found.to_dict().items():
                if v and hasattr(form, k):
                    form[k].data = v
    except Exception as err:
        flash(quote(str(err)), 'danger')
    return render_template('edit.html', page_title='edit', form=form, item=item_found)

@app.route('/fetch', methods=['GET', 'POST'])
@login_required
def fetch():
    link = request.args.get('link', None)
    where = request.args.get('w', 'library')
    form = FetchUrlForm()
    try:
        if form.validate_on_submit():
            item.poster = form.poster.data
            form.poster.data = item.save_poster(current_user.id)
            item.icon = form.icon.data
            form.icon.data = item.save_icon(current_user.id)
            form_data = {k: v for k, v in form.data.items() if k != 'csrf_token'}
            item_found = Items.query.filter_by(user_id=current_user.id, hash=form.hash.data).first()
            if item_found:
                for k, v in form.data.items():
                    setattr(item_found, k, v)
            else:
                items = Items(user_id=current_user.id, **form_data)
                db.session.add(items)
            db.session.commit()
            return redirect(url_for(where))
        else:
            item.clear()
            item.start(link)
            for k, v in item.__dict__.items():
                if v: form[k].data = v
    except Exception as err:
        flash(quote(str(err)), 'danger')
    
    return render_template('fetch.html', page_title='fetch', link=link, form=form, item=item)

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

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('User logged out', 'info')
    return redirect(url_for('login'))

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

@app.route('/destroy')
def destroy():
    db.session.query(Users).delete()
    db.session.commit()
    return "data destroyed"


@app.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    form = GetLinkForm()
    return render_template('library.html', page_title='library', form=form)


@app.route('/items/<id>', methods=['GET'])
def items(id):
    items = dict()
    if id == 'all':
        items = Items.query.filter_by(user_id=current_user.id).order_by(text("last_update desc")).all()
    return jsonify([item.to_dict() for item in items])



@app.route('/delete', methods=['GET'])
@app.route('/delete/<item_id>', methods=['GET'])
@login_required
def delete(item_id):
    item = Items.query.filter_by(id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    return str(1)









import subprocess
import sys
import os

def open_chrome_incognito(url):
    chrome_path = ""
    
    # Determine the platform and set the path to Chrome accordingly
    if sys.platform == "win32":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif sys.platform == "darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif sys.platform == "linux" or sys.platform == "linux2":
        chrome_path = "/usr/bin/google-chrome"
    else:
        raise Exception("Unsupported operating system")
    
    if not os.path.exists(chrome_path):
        raise Exception(f"Google Chrome not found at {chrome_path}")
    
    # Open Chrome in incognito mode
    subprocess.run([chrome_path, "--incognito", url])




if __name__ == "__main__":
    open_chrome_incognito("http://127.0.0.1:5000")
    app.run(debug=True)








exit()