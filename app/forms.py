from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

from app import connection

import hashlib

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
