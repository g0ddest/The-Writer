from app import app, connection, models

from flask import Flask, session, render_template, Markup, request, redirect, escape, abort
from jinja2 import evalcontextfilter
import markdown as md
from mongokit import Connection
from bson.objectid import ObjectId
import hashlib
from functools import wraps
import datetime
import os
import time

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

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

works_location = u'%s/works' % CURRENT_DIR

Markdown(app)

DEBUG = True

def make_me_shine(cursor):
    result = [ ]
    for rec in cursor:
        if ',' in rec['path']:
            parents = rec['path'].split(',')
            for rec1 in result:
                if str(rec1['_id']) == parents[len(parents)-1]:
                    result.insert(result.index(rec1)+1, rec)
                    break
        else:
            result.append(rec)  
    return result

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
        owning_user = connection.User.find_one({'login': kwargs['username']})
        if owning_user:
            work = connection.Work.find_one({'$and': [
                                                    {'owner.$id': owning_user._id},
                                                    {'name': kwargs['work']}
                                                ]})
            if work:
                if work['access'] == "public":
                    kwargs['work'] = work
                    kwargs['username'] = owning_user
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
    return decorated_function

def chapter_rights_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        owning_user = connection.User.find_one({'login': kwargs['username']})
        if owning_user:
            work = connection.Work.find_one({'$and': [
                                            {'owner.$id': owning_user._id},
                                            {'name': kwargs['work']}
                                        ]})
            if work:
                have_this_inner = False
                for inner in work['chapters']:
                    if inner['name'] == kwargs['file']:
                        have_this_inner = True
                if have_this_inner:
                    if work['access'] == "public":
                        kwargs['username'] = owning_user
                        kwargs['work'] = work
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

def process_comments(f):
    @wraps(f)
    def wrapper_function(*args, **kwargs):
        chapter_id = 0
        if 'file' in kwargs:
            for ch in kwargs['work'].chapters:
                if ch['name']==kwargs['file']: chapter_id=ch['id']
        if request.method == "GET":
            result_set = [ ]
            cond_string = '^%s_%s' % (kwargs['work']._id, str(chapter_id))
            comm_request = connection.Comment_tree.find({'path': {'$regex': cond_string} })
            sorted_array = make_me_shine(comm_request)
            counter = 0
            for rec in sorted_array:
                indent = 10 * rec['path'].count(',')
                comm_data = connection.Comments.find_one({'comment_id': rec['_id']})
                created = comm_data['created'].strftime('%Y, %b %d, %H:%M')
                result_set.append({
                        'id': comm_data['comment_id'],
                        'author': comm_data['author'].login,
                        'created': created,
                        'value': comm_data['text'],
                        'counter': counter,
                        'indent': indent
                })
                counter += 1
            kwargs['comments'] = result_set
            return f(*args, **kwargs)
        else:
            comm_id = ObjectId()
            if request.form['ansref'] == 'new':
                path = u'%s_%s' % (kwargs['work']._id, str(chapter_id))
            else:
                ans_id = ObjectId(request.form['ansref'])
                answered_comm = connection.Comment_tree.find_one({'_id': ans_id})
                path = u'%s,%s' % (answered_comm['path'], request.form['ansref'])
            connection.Comment_tree({
                '_id': comm_id,
                'path': path
            }).save()
            connection.Comments({
                'comment_id': comm_id,
                'text': request.form['commtext'],
                'author': kwargs['username'],
                'created': datetime.datetime.now(),
                'updated': datetime.datetime.now()
            }).save()
            return 'Fine'
    return wrapper_function

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/about/')
def about():
    return 'The about page'

@app.route('/register/', methods=['GET', 'POST'])
@guest_required
def register():
    if request.method == 'POST':
        if request.form['username'] and request.form['name'] and request.form['password']:
            mdfive = hashlib.md5()
            mdfive.update(request.form['password'])
            #TODO: Potential injection. Parse data, please
            user = connection.User.find_one({'login': request.form['username']})
            if user:
                return 'Not a unique username'
            else:
                connection.User({
                    'login': request.form['username'],
                    'password': mdfive.hexdigest(),
                    'name': request.form['name']
                }).save()
                return "User added!"
        else:
            return 'Please, fill all fields'
    return '''
        <form action="" method="post">
            <p><input placeholder="Name" type=text name=name>
            <p><input placeholder="Login" type=text name=username>
            <p><input placeholder="Password" type=text name=password>
            <p><input type=submit value=Register>
        </form>
    '''


@app.route('/me/')
@login_required
def current_user_info():
    return u'user: ' + session['username'] + u' id: ' + session['user_id']


@app.route('/work/<username>/',  methods=['GET'])
def user_info(username):
    user = connection.User.find_one({'login': username})
    if user:
        #TODO: add permissions (do not show private)
        return \
            render_template(
                'user.html',
                title='User',
                works=connection.Work.find({'owner.$id': user._id}),
                username=user['login'],
                is_current_user=str(user['_id']) == str(session['user_id']) if 'user_id' in session and 'username' in session else False
            )
    else:
        return 'we have no user with this login'


@app.route('/login/', methods=['GET', 'POST'])
@guest_required
def login():
    if request.method == 'POST':
        mdfive = hashlib.md5()
        mdfive.update(request.form['password'])
        #TODO: Potential injection. Parse data, please
        user = connection.User.find_one({'$and': [{'login': request.form['username']}, {'password': mdfive.hexdigest()}]})
        if user:
            session['username'] = user['login']
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


@app.route('/logout/')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect('/')


@app.route('/work/<username>/', methods=['POST'])
@login_required
def work_add(username):
    if 'name' in request.form and 'title' in request.form and 'access' in request.form and 'description' in request.form:
        user = connection.User.find_one({'login': username})
        if user:
            existing = connection.Work.find_one({'$and': [{'name': request.form['name']}, {'owner': user}]})
            if not existing:
                connection.Work({
                    'owner': user,
                    'name': request.form['name'],
                    'title': request.form['title'],
                    'description': request.form['description'],
                    #TODO: change on next milestone
                    'vcs': False,
                    #TODO: check is only in [public, private]
                    'access': request.form['access'],
                    'created': datetime.datetime.now(),
                    'modified': datetime.datetime.now(),
                    'chapters': []
                }).save()
                return redirect('/work/%s' % username)
            else:
                return "There is such name"
        else:
            return "No such user"
    else:
        return "Fill all the fields"

@app.route('/work/<username>/<work>/+/', methods=['GET', 'POST'])
@work_rights_required
def add_chapter(username, work):
    #TODO: check shared rights
    if(str(username['_id']) == str(session['user_id'])
       if 'user_id' in session and 'username' in session else False):
        if request.method == "GET":
            return render_template("add_chapter.html", work=work)
        else:
            if not os.path.isdir("%s/%s" % (works_location, username['login'])):
                os.makedirs("%s/%s" % (works_location, username['login']))
            if not os.path.isdir("%s/%s/%s" % (works_location, username['login'], work['name'])):
                os.makedirs("%s/%s/%s" % (works_location, username['login'], work['name']))
            args = (works_location, username['login'], work['name'], request.form["name"])
            with open("%s/%s/%s/%s.md" % args, 'w') as file:
                file.write(request.form["text"].encode('utf-8'))
            
            work.modified = datetime.datetime.now()
            ch_id = len(work.chapters) + 1
            work.chapters.append({
                'id': ch_id,
                'name': request.form["name"],
                'title': request.form["title"],
                'created': datetime.datetime.now(),
                'updated': datetime.datetime.now()
            })
            work.save()
            return "ok"
    else:
        return "You have no permission"

@app.route('/work/<username>/<work>/', methods=['GET', 'POST'])
@work_rights_required
@process_comments
def work_description(username, work, comments=None):
    return \
            render_template(
                'chapters.html',
                username=username['login'],
                work=work,
                is_current_user=str(username['_id']) == str(session['user_id']) if 'user_id' in session and 'username' in session else False,
                comments=comments)
    

@app.route('/work/<username>/<work>/<file>/', methods=['GET', 'POST'])
@chapter_rights_required
@process_comments
def work(username, work, file, comments=None):
    return \
            render_template(
                'work.html',
                title='Work',
                text='\n\r%s' % api_work_get(username['login'], work['name'], file),
                is_current_user=str(username['_id']) == str(session['user_id']) if 'user_id' in session and 'username' in session else False,
                username=username['login'],
                comments=comments)


# ------------------------
# api for web application

@app.route('/api/work/<username>/<work>/<file>/', methods=['GET'])
def api_work_get(username, work, file):
    #TODO: add permission check
    with open('%s/%s/%s/%s.md' % (works_location, username, work, file)) as f:
        return f.read().decode('utf-8')


@app.route('/api/work/<int:id>/', methods=['POST'])
def api_work_post(id):
    return 'information about ' + str(id)
