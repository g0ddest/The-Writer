from flask import Flask, session, render_template, Markup, request, redirect, escape, abort

from flask.ext.login import login_user, logout_user, current_user, login_required
from mongokit import Connection

app = Flask(__name__)
app.config.from_object('config')
app.debug = app.config['DEBUG']
app.secret_key = app.config['SECRET_KEY']
connection = Connection( app.config['DB_HOST'], app.config['DB_PORT'] )
db = connection[ app.config['DB_NAME'] ]
from app import Writer
