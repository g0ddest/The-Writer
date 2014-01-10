from flask import Flask, session, render_template, Markup, request, redirect, escape, abort
from jinja2 import evalcontextfilter
import markdown as md
from mongokit import Connection
import hashlib
from functools import wraps

mdfive = hashlib.md5()


class Markdown(object):
    def __init__(self, app, auto_escape=False, **markdown_options):
        self.auto_escape = auto_escape
        self._instance = md.Markdown(**markdown_options)
        app.jinja_env.filters.setdefault(
            'markdown', self.__build_filter(self.auto_escape))

    def __call__(self, stream):
        return Markup(self._instance.convert(stream))

    def __build_filter(self, app_auto_escape):
        @evalcontextfilter
        def markdown_filter(eval_ctx, stream):
            __filter = self
            if app_auto_escape and eval_ctx.autoescape:
                return Markup(__filter(escape(stream)))
            else:
                return Markup(__filter(stream))
        return markdown_filter

    def extend(self, configs=None):
        def decorator(ext_cls):
            return self.register_extension(ext_cls, configs)
        return decorator

    def register_extension(self, ext_cls, configs=None):
        instance = ext_cls()
        self._instance.registerExtensions([instance], configs)
        return ext_cls


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection()

# Define collections

collection = connection['writer']
users = collection.users
works = collection.works

Markdown(app)

DEBUG = True
app.debug = DEBUG
app.secret_key = '$M*tQFTpH@u*vUGjiWzBKxLLCGm43n'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session and 'user_id' in session:
            return f(*args, **kwargs)
        else:
            #TODO: write some message
            return redirect('/')
    return decorated_function


def guest_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session and 'user_id' in session:
            #TODO: write some message
            return redirect('/')
        else:
            return f(*args, **kwargs)
    return decorated_function


def work_rights_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        owning_user = users.find_one({'login': kwargs['username']})
        if owning_user:
            work = works.find_one({'$and': [{'owner': str(owning_user['_id'])}, {'name': kwargs['work']}]})
            if work:
                have_this_inner = False
                for inner in work['contains']:
                    if inner['name'] == kwargs['file']:
                        have_this_inner = True
                if have_this_inner:
                    if work['access'] == "public":
                        return f(*args, **kwargs)
                    else:
                        #TODO: make access control
                        #TODO: write some message
                        return redirect('/')
                else:
                    #TODO: write some message
                    return redirect('/')
            else:
                #TODO: write some message
                return redirect('/')
        else:
            #TODO: write some message
            return redirect('/')
    return decorated_function


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/about')
def about():
    return 'The about page'


@app.route('/me/')
@login_required
def current_user_info():
    return 'user: ' + session['username'] + ' id: ' + session['user_id']


@app.route('/user/<username>')
def user_info(username):
    return 'information about ' + username


@app.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    if request.method == 'POST':
        mdfive.update(request.form['password'])
        #TODO: Potential injection. Parse data, please
        user = users.find_one({'login': request.form['username'], 'password': mdfive.hexdigest()})
        if user:
            session['username'] = request.form['username']
            session['user_id'] = str(user['_id'])
            return 'Logged in!'
        else:
            abort(401)
        #return redirect('/')
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=text name=password>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect('/')


@app.route('/work/<username>/<work>/<file>', methods=['GET'])
@work_rights_required
def work(username, work, file):
    return render_template('work.html', title='Work', text=api_work_get(username, work, file))

# ------------------------
# api for web application


@app.route('/api/work/<username>/<work>/<file>', methods=['GET'])
def api_work_get(username, work, file):
    with open('d:/projects/Writer/works/%s/%s/%s.md' % (username, work, file)) as f:
        return f.read()


@app.route('/api/work/<int:id>', methods=['POST'])
def api_work_post(id):
    return 'information about ' + str(id)

if __name__ == '__main__':
    app.run()