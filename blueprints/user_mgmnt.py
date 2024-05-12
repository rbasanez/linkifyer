import uuid
from flask import Blueprint, request, session, render_template, redirect, url_for
from models.logger import logger
from models.user import user


# Function to extract page title from path
def get_page_title(path):
    try: return path.split('.')[1]
    except: return path


bp = Blueprint('user', __name__)

@bp.route("/account", methods=["GET"])
def account():
    return render_template('account.html', page_title=get_page_title(request.endpoint))

# Route for registration
@bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    session.clear()
    user.clear()
    username = request.form.get('username', type=str, default=None)
    password = request.form.get('password', type=str, default=None)
    if request.method == "POST":
        status, message = user.find_by_username(username)
        if status and message is not None and message.get('user_id') is not None:
            error = 'username already exists'
        else:
            password = user.hash_password(password)
            user.populate(username=username, password=password)
            if user.push():
                return redirect(url_for('login'))
            else:
                error = 'something went wrong, you better check the logs'
    return render_template('register.html', page_title=get_page_title(request.endpoint), error=error, username=username)


@bp.route("/update/username", methods=["POST"])
def update_username():
    error = None
    username = request.form.get('username', type=str, default=None)
    
    status, message = user.find_by_username(username)
    
    if status and message is not None and message.get('user_id') is not None:
        error = 'username already exists'
    else:
        user.populate(username=username)
        if user.push():
            session['username'] = username
            logger.info(session)
            return 'success'
        else:
            error = 'internal error'
    return error

@bp.route("/update/password", methods=["POST"])
def update_password():
    error = None
    password = request.form.get('password', type=str, default=None)
    print(session)
    print(user.__dict__)
    
    # status, message = user.find_by_username(password)
    
    # if status and message is not None and message.get('user_id') is not None:
    #     error = 'username already exists'
    # else:
    #     user.populate(username=username)
    #     if user.push():
    #         session['username'] = username
    #         logger.info(session)
    #         return 'success'
    #     else:
    #         error = 'internal error'
    return ""