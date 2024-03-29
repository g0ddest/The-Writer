from app import app, connection
from mongokit import Document
import datetime

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

@connection.register
class User(Document):
    __database__ = app.config['DB_NAME']
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

@connection.register
class Work(Document):
    __database__ = app.config['DB_NAME']
    __collection__ = "works"
    structure = {
        'owner': User,
        'name': unicode,
        'title': unicode,
        'description': unicode,
        'vcs': bool,
        'access': unicode, #?!?
        'created': datetime.datetime,
        'modified': datetime.datetime,
        'chapters': [
            {
                'name': unicode,
                'title': unicode,
                'created': datetime.datetime,
                'updated': datetime.datetime
            }
        ]
    }
    default_values = {
        'created': datetime.datetime.now()
    }
    validators = { }
    indexes = [ ]
    required_fields = ['title']
    use_dot_notation = True
    use_autorefs = True
    
    def __repr__(self):
        return '<Work %r>' % (self.title)

connection.register([User, Work])

#create indexes:
for document_name, obj in connection._registered_documents.iteritems():
    obj.generate_index(connection[app.config['DB_NAME']][obj._obj_class.__collection__])
