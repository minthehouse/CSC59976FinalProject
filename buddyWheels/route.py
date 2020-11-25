import os
import secrets
from PIL import Image
import datetime
from flask import render_template, url_for, flash, redirect, request, abort
from buddyWheels import app, db, bcrypt, mail
#from buddyWheels.forms import RegistrationForm, LoginForm
from buddyWheels.models import User
from flask_login import login_user, current_user, logout_user, login_required, AnonymousUserMixin
from flask_mail import Message


@app.route("/")
def default():
    return redirect(url_for('home'))


@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')