from app import app, connection
from mongokit import Document

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

class User(Document):
    __database__ = app.config['DATABASE']
    __collection__ = "users"
    structure = {
        'login': unicode,
        'password': basestring, #TODO binary
        'name': unicode,
    }
    validators = {
        'login': max_length(50),
        'name': max_length(120),
    }
    indexes = [
        {
            'fields': ['login'],
            'unique': True,
        },
    ]
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.login)

connection.register([User])

