from flask import Flask, session, render_template, Markup, request, redirect, escape, abort

from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.mongoengine import MongoEngine

#http://flask-mongoengine.readthedocs.org/en/latest/

app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)
from app import models, users

