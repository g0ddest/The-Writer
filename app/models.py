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
        'bitbucket': {
            'oauth_token': basestring,
            'oauth_token_secret': basestring
        },
        'vkontakte': {
            'uid': int
        },
        'google': {
            'id': unicode
        },
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
    use_schemaless = True
    def __repr__(self):
        return '<User %r>' % (self.login)
    
    @classmethod
    def get_or_create_from_bitbucket(_, data):
        user = connection.User.find_one({'bitbucket.oauth_token': data['oauth_token'],
                          'bitbucket.oauth_token_secret': data['oauth_token_secret']
                          })
        if not user:
            user = connection.User({
                    'bitbucket': {
                        'oauth_token': data['oauth_token'],
                        'oauth_token_secret': data['oauth_token_secret']
                    },
                    'name': data['display_name'],
                    'login': data['username']
            })
            user.save()
        return user

    @classmethod
    def get_or_create_from_vkontakte(_, data):
        user = connection.User.find_one({'vkontakte.uid': data['uid']})
        if not user:
            user = connection.User({
                    'vkontakte': { 'uid': data['uid'], },
                    'name': data['first_name'] + u'' + data['last_name'],
                    'login': u'vk' + str(data['uid'])
            })
            user.save()
        return user

    @classmethod
    def get_or_create_from_google(_, data):
        user = connection.User.find_one({'google.id': data['id']})
        if not user:
            user = connection.User({
                    'google': { 'id': data['id'], },
                    'name': data['name'],
                    'login': u'google' + data['id']
            })
            user.save()
        return user

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
