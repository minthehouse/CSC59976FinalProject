import os
import secrets
from PIL import Image
import datetime
from flask import render_template, url_for, flash, redirect, request, abort
from buddyWheels import app, db, bcrypt, mail
from buddyWheels.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
from buddyWheels.models import User
from flask_login import login_user, current_user, logout_user, login_required, AnonymousUserMixin
from flask_mail import Message
import requests
import json
from yelpapi import YelpAPI
import googlemaps
from datetime import datetime



@app.route("/")
def default():
    return redirect(url_for('home'))


@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/search", methods=['GET', 'POST'])
def search():
    API_KEY = 'APPkzjieslVnhZkXzIBZUkjk5LEohlL9JgzKiyIkaSdo8nHluBI9aJSwnYopRg8_dEq9wlKGW65AHZK4IODId2KCQ_XLJp18-Wne7fnUxWKWus99NY8_SZyBkkLRX3Yx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search?attributes=wheelchair_accessible'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}
    
    destination = request.form.get('destination', False)
    zipcode = request.form.get('zipcode', False)
    #define the parameters
    PARAMETERS = {'term': destination+zipcode,
                'limit': 10,
                'radius': 10000,
                'location': 'ny'}
    response = requests.get(url = ENDPOINT, params = PARAMETERS, headers = HEADERS)
    #name_response = response['business']['name']
    # convert the JSON string to a dictionary
    business_data = response.json()
    #names = business_data['businesses']
    
    return render_template('search.html', title='Search', business_data=business_data )

@app.route("/search/<business_id>")
def business(business_id):
    API_KEY = 'APPkzjieslVnhZkXzIBZUkjk5LEohlL9JgzKiyIkaSdo8nHluBI9aJSwnYopRg8_dEq9wlKGW65AHZK4IODId2KCQ_XLJp18-Wne7fnUxWKWus99NY8_SZyBkkLRX3Yx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/{}'.format(business_id)
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}

    response = requests.get(url=ENDPOINT, headers=HEADERS)
    business_info = response.json()
    

    return render_template('business.html', title='Business', business_info=business_info)


@app.route("/detail")
def detail():
    API_KEY = 'APPkzjieslVnhZkXzIBZUkjk5LEohlL9JgzKiyIkaSdo8nHluBI9aJSwnYopRg8_dEq9wlKGW65AHZK4IODId2KCQ_XLJp18-Wne7fnUxWKWus99NY8_SZyBkkLRX3Yx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search?attributes=wheelchair_accessible'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}

    gmaps = googlemaps.Client(key = 'AIzaSyCcCcw-1jwiB-59cdvWO0aSp4Is78MDt-s')
    geocode_result = gmaps.geocode('1520 amsterdam ave, New york, NY')
    now = datetime.now()
    directions_result = gmaps.directions("1520 amsterdam ave, NY", "1600 Convent Ave, NY",mode = "driving", departure_time=now)
    

    destination = request.form.get('destination', False)
    return render_template('detail.html', title='Detail', direction_result = directions_result)
    






@app.route("/services")
def services():
    return render_template('services.html', title='Services')

@app.route("/contact_us")
def contact():
    return render_template('contact.html', title='Contact')

@app.route("/su")
def su():
    return render_template('su.html', title='SuperUser')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        msg = f'''Congratulations! Your account has been successfully created
You are now able to log in.'''
        flash(msg, 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



