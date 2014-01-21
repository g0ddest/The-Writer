from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, EqualTo

from app import connection

import hashlib
from pymongo.errors import DuplicateKeyError

class LoginForm(Form):
    login = TextField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False
        mdfive = hashlib.md5()
        mdfive.update(self.password.data)
        user = connection.User.find_one({'$and': [
                        {'login': self.login.data},
                        {'password': mdfive.hexdigest()}
                    ]})
        if user:
            self.user = user
            return True
        else:
            self.login.errors.append('Try again')
            return False

class RegisterForm(Form):
    login = TextField('Login', validators=[DataRequired()])
    name = TextField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Repeat Password', [
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    def validate(self):
        if not Form.validate(self):
            return False
        mdfive = hashlib.md5()
        mdfive.update(self.password.data)
        try:
            connection.User({
                'login': self.login.data,
                'password': mdfive.hexdigest(),
                'name': self.name.data
            }).save()
        except DuplicateKeyError as e:
            self.login.errors.append('Not a unique login.')
            return False
        return True
