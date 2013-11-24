from flask import Flask
from flask import render_template
from flask import Markup
from jinja2 import evalcontextfilter, escape
import markdown as md

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

app = Flask(__name__)

Markdown(app)

DEBUG = True
app.debug = DEBUG

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/about')
def about():
    return 'The about page'

@app.route('/user/<username>')
def user_info(username):
    return 'information about ' + username

@app.route('/work/<username>/<work>/<file>', methods=['GET'])
def work(username, work, file):
    return render_template('work.html', title='Work', text=api_work_get(username, work, file))

# ------------------------
# api for web application

@app.route('/api/work/<username>/<work>/<file>', methods=['GET'])
def api_work_get(username, work, file):
    with open('e:/projects/Writer/works/%s/%s/%s.md' % (username, work, file)) as f:
        return f.read()

@app.route('/api/work/<int:id>', methods=['POST'])
def api_work_post(id):
    return 'information about ' + str(id)

if __name__ == '__main__':
    app.run()