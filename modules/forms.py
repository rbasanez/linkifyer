from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, EqualTo
from markupsafe import Markup

class GetLinkForm(FlaskForm):
    url = StringField(None, validators=[DataRequired()], render_kw={'class':'form-control form-control-sm','placeholder':'Get Link'})
    pass

class LoginForm(FlaskForm):
    username = StringField(None, validators=[DataRequired()], render_kw={'class':'form-control form-control-sm','placeholder':'Username'})
    password = PasswordField(None, validators=[DataRequired()], render_kw={'class':'form-control form-control-sm','placeholder':'Password'})

class RegisterForm(FlaskForm):
    username = StringField(None,
        validators=[DataRequired()],
        render_kw={'class':'form-control','placeholder':'Username'}
    )
    password = PasswordField(None,
        validators=[DataRequired()],
        render_kw={'class':'form-control','placeholder':'Password'}
    )
    confirm = PasswordField(None,
        validators=[DataRequired(message='Password is required.'), EqualTo('password', message='Passwords must match')],
        render_kw={'class':'form-control','placeholder':'Confirm password'}
    )
    submit = SubmitField('Register', render_kw={'class':'btn app-btn'},)
    pass

class FetchUrlForm(FlaskForm):
    hash = HiddenField(None, validators=[DataRequired()])
    poster_url = HiddenField(None, validators=[DataRequired()])
    poster_path = HiddenField(None, validators=[DataRequired()])
    icon_url = HiddenField(None, validators=[DataRequired()])
    icon_path = HiddenField(None, validators=[DataRequired()])
    host = HiddenField(None, validators=[DataRequired()])
    url = HiddenField(None, validators=[DataRequired()])
    title = StringField(None, validators=[], render_kw={'class':'form-control', 'placeholder':'Enter title manually'})
    tags = StringField(None, validators=[], render_kw={'class':'form-control border-0', 'placeholder':'Enter tag(s) manually'})
    models = StringField(None, validators=[], render_kw={'class':'form-control border-0', 'placeholder':'Enter models(s) manually'})
    collections = StringField(None, validators=[], render_kw={'class':'form-control border-0', 'placeholder':'Enter collection(s) manually'})
    description = TextAreaField(None, validators=[], render_kw={'class':'form-control', 'style':'resize: none;', 'placeholder':'Enter description manually'})
