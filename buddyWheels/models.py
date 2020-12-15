from buddyWheels import db, login_manager, app
import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import request
import json
from yelpapi import YelpAPI



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstName = db.Column(db.String(20), unique=True, nullable=False)
    lastName = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class FavoritePlaces(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_info = db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)
    business_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"FavoritePlaces('{self.business_name}', '{self.address}', '{self.rating}')"


'''
class yelp_api():
    
    API_KEY = 'APPkzjieslVnhZkXzIBZUkjk5LEohlL9JgzKiyIkaSdo8nHluBI9aJSwnYopRg8_dEq9wlKGW65AHZK4IODId2KCQ_XLJp18-Wne7fnUxWKWus99NY8_SZyBkkLRX3Yx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search?attributes=wheelchair_accessible'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}
    
    destination = request.form.get('destination', False)

    #define the parameters
    PARAMETERS = {'term': destination,
                'limit': 10,
                'radius': 10000,
                'location': 'ny'}
    def search(self):

        response = requests.get(url = ENDPOINT, params = PARAMETERS, headers = HEADERS)
        #name_response = response['business']['name']
        # convert the JSON string to a dictionary
        business_data = response.json()
        #names = business_data['businesses']
        
        return render_template('search.html', title='Search', business_data=business_data )


'''