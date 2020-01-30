import os
import math
import json 
import datetime

# external
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Sequence,
    Float,
)
import jwt

import warnings
# https://github.com/marshmallow-code/flask-marshmallow/issues/53
with warnings.catch_warnings():
     from flask_marshmallow import Marshmallow

def debug(msg):
    print('\n\n\n'+msg+'\n\n\n')


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\xfa\xfe\xc5\x8d \xaf\xbe\xb8`\xbfz\xbc\x96Z\x9b\xc1\x9b]\xefB\x1a\x1b\xe7\xf4'


db = SQLAlchemy(app)

ma = Marshmallow(app)

socketio = SocketIO(app, cors_allowed_origins='*')


# Distance Calculator
def distance(origin, destination):
    """Find distance between two given points
    params: (['latitudeA', 'longitudeA'], ['latitudeB', 'longitudeB'])
    """

    # Usage: distance([40.689202777778, -74.044219444444],
    #             [38.889069444444, -77.034502777778])
    #       or
    # distance([latitudeA, longitudeA],
    #             [latitudeB, longitudeB])
    # return: distance in meters, round by 2

    # Conversions:
    # d_km = d_km/1000
    # d_miles = d_km*0.621371

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return round(d*1000, 2)  # in meters




# JWT ENCODE/DECODE FUNCTIONS

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token='auth_header'):
    """
    Decodes the auth token
    :param: auth_token
    :return: integer (user_id)|string (error)
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


# Function that gives user id, username, email and admin_status from JWT Token

def user_info(token):
    # pass auth_header and else is done here :)
    """return type: dict
    """
    auth_token = token.split(" ")[0]
    resp = decode_auth_token(auth_token)
    if not isinstance(resp, str):
        user = Users.query.filter_by(id=resp).first()
        return {
            'id':user.id,
            'email':user.email,
            'username':user.username,
            'admin':user.admin_status
        }
    return 'AuthFail'


### Models

class Users(db.Model):
    # pk is email
    """API call will interact with Users table
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(100))
    email = Column(String(60), unique=True)
    admin_status = Column(Boolean, nullable=False, default=0)
 
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class Events(db.Model):
    # pk is id
    # one-to-many with Attendence
    """API call will interact with Events table
    """
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime)
    admin_name = Column(String(50))
    attendence = db.relationship(
        'Attendence', backref='event', lazy=True)
    # These are the required fields in post request
    otp = Column(String(6), nullable=False, unique=True) #900,000 Events supported without flushing data
    event_name = Column(String(100))
    event_description = Column(String(2000), nullable=True)
    ending_time_delta = Column(Integer) #Treated in Minutes
    location_range = Column(Integer)  # Treated in meters
    # needs users lat and long also
    # an option to allow or disallow broadcast to users


class Attendence(db.Model):
    # pk is id
    """SocketIO will interact with Attendence table
    """
    __tablename__ = "attendences"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))

    event_otp = Column(String(6), nullable=False) #before inserting check if otp does exsists in events table
    
    email = Column(String(60))
    datetime = Column(DateTime)
    status = Column(Boolean) #presence column, for location ambiguity, server handled



### Scehmas

# Users schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'email', 'admin_status')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Attendence Schema
class AttendenceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'event_id', 'email', 'datetime', 'status')

attendence_schema = AttendenceSchema()
attendences_schema = AttendenceSchema(many=True)


# Events Schema
class EventSchema(ma.Schema):
    class Meta:
        fields = ('id', 'creation_date', 'admin_name', 'otp', 'event_name', \
            'event_description', 'ending_time_delta', 'location_range')

event_schema = EventSchema()
events_schema = EventSchema(many=True)


### API Endpoints

# user signup
@app.route('/user/signup', methods=['POST'])
def user_signup():

    username=request.json['username']
    password = request.json['password']
    email=request.json['email']

    new_user = Users(username, password, email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


# user login
@app.route('/user/login', methods=['POST'])
def user_login():

    email=request.json['email']
    password=request.json['password']
    
    try:
        user = Users.query.filter_by(email=request.json['email']).first()

        if password == user.password:
            auth_token = encode_auth_token(user.id)
            return jsonify({
                'status':'success',
                'message':'Successfully logged in',
                'auth_token':auth_token.decode()
            })
    except Exception as e:
        # print('\n\n\n', Users.query.filter_by(email=request.json['email']).first().password, '\n\n\n')
        # print('\n\n\n', password, e , '\n\n\n')
        return jsonify({
            'status': 'fail',
            'message': 'Wrong Credentials! Check Again.'
        })


# This is for testing, it may not be needed
@app.route('/user/logged', methods=['POST'])
def user_logged():
    """return: id, memail, name, admin_status for logged in user | Failure message if authorization fails
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[0]
    else:
        auth_token = ''
    if auth_token:
        resp = decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = Users.query.filter_by(id=resp).first()
            return jsonify({
                'status': 'success',
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.username,
                    'admin_status': user.admin_status
                }
            })
        return jsonify({
            'status':'Fail',
            'message':resp
        })
    else:
        return jsonify({
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        })



# users view
@app.route('/users', methods=['GET'])
def user_view():
    # workleft: change this method to post and firstly check admin stat
    """return: detail of all registered users
    """
    all_users = Users.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

# user view
@app.route('/users/<id>', methods=['GET'])
def single_user_view(id):
    # workleft: change this method to post and firstly check admin stat
    """return: detail of user for provided <id>
    """
    user = Users.query.get(id)
    return jsonify({
        'id':id,
        'email':user.email,
        'username':user.username,
        'password':user.password
    })



# create event
@app.route('/event/create', methods=['POST'])
def create_event():
    """Endpoint to create an Event
    Required: Authorized and admin
    return: event detail | auth fail
    """

    auth_header = request.headers.get('Authorization')
    user_details = user_info(auth_header)
    admin_status_ = user_details.get('admin')

    if user_details != 'AuthFail' and admin_status_:
        creation_date_ = datetime.datetime.now()
        admin_name_ = user_details.get("username")

        otp_ = request.json['otp']
        event_name_ = request.json['event_name']
        event_description_ = request.json['event_description']
        ending_time_delta_ = request.json['ending_time_delta']
        location_range_ = request.json['location_range']
        
        new_event = Events(creation_date= creation_date_, admin_name=admin_name_, \
                otp=otp_, event_name=event_name_, event_description=event_description_, \
                ending_time_delta=ending_time_delta_, location_range=location_range_)

        db.session.add(new_event)
        db.session.commit()

        return event_schema.jsonify(new_event)
        
    else:
        return jsonify({
            'status':'Fail',
            'message':'Authentication Failure'
        })


# API is not needed here. For Testing Purposes.
@app.route('/attendence', methods=['POST'])
def attendence_post():
    # If status is 0 then treat it as not present and specify reason
    # out of raidus distance

    #check if event already exsists then don't let it

    event_otp_ = request.json['event_otp']
    
    email_ = user_info(request.headers.get('Authorization')).get("email")
    datetime_ = datetime.datetime.now()
    # workleft: In api take latitude and longitude of user and then
    # compare it with admins lat and long and judge on distance param
    status_ = 1 # code logic needed here

    event_id_ = Events.query.filter_by(otp = event_otp_).first().id
    new_attendence = Attendence(event_id=event_id_, event_otp=event_otp_, email=email_, \
        datetime=datetime_, status=status_)
    
    db.session.add(new_attendence)
    db.session.commit()

    return jsonify({
        "event_otp":event_otp_,
        "email":email_,
        "datetime":datetime_,
        "status":status_
    })



@socketio.on('join', namespace='/rooms_namespace')
def on_join(data):
    debug(str(data))
    debug(str(type(data)))
    data = json.loads(data)
    #verify if attendence is success
    #then get them join in that room name with otp added
    #now broadcast to that room

    status = data['status']
    if status!='Success':
        return ''
    
    room = '-'.join(data['event_name'].split(' ')) + '-' + str(data['otp'])
    username = data["username"] #add this to payLoad (clientside)
    join_room(room)
    mymessage = {
        'username':data['username']
    }
-
    emit('join_room', json.dumps(mymessage), room=room)



@socketio.on('admin_stats', namespace='/admin_namespace')
def made_for_admin():
    #admin_stats is mapped with admin_listen
    pass



@socketio.on('attendence_request', namespace='/attendence_namespace')
def take_attendence_from_user(json_):
    #attendence_request is mapped with attendence_result at now
    """This will mark attendence if valid or return failure reason
    at the namespace 'attendence_namespace' and this is done privately for
    the user.
    It also broadcasts the attendence result to
    """

    otp_ = json_['otp']
    token_ = json_['token']


    user_detail = user_info(token_)
    if user_detail != 'AuthFail':
        
        email_ = user_info(token_).get("email")
        datetime_ = datetime.datetime.now()
        # workleft: In client payLoad take latitude and longitude of user and then
        # compare it with admins lat and long and judge on distance param
        status_ = 1 # code logic needed here
        try:
            event_id_ = Events.query.filter_by(otp=otp_).first().id

        except Exception as e:
            event_id_ = -1

        if event_id_>=0:

            new_attendence = Attendence(event_id=event_id_, event_otp=otp_, email=email_, \
                datetime=datetime_, status=status_)
            db.session.add(new_attendence)
            
            if status_==0:
                payLoad = {
                    'Status':'Fail',
                    'Reason':'You are far away from Event Location'
                }
            elif status_==1:
                payLoad = {
                    'Status':'Success',
                    'Reason': 'Attendence updated'
                }
                db.session.commit()
            else:
                payLoad = {
                    'Status':'Fail',
                    'Reason': 'Server Error'
                }
        else:
            payLoad = {
                'Status':'Fail',
                'Reason': 'No such Event'
            }
        
    else:
        payLoad = {
            'Status':'Fail',
            'Reason': 'AuthFail'
        }

    emit('attendence_result', json.dumps(payLoad)) #json is emited now, privately
    try:
        if status_:
            # negative otp means ignore it, wrong entry
            # here recheck for otp is not needed, so can be removed
            try:
                event = Events.query.filter_by(otp=otp_).first()
                event_name_ = event.event_name
                admin_name_ = event.admin_name
                attendence_status = 'Success' # This param is for admin only
            except:
                event_name_ = ''
                admin_name_ = ''
                otp_ = -1
                attendence_status = 'Failure' # This param is for admin only
            
            payLoad = {
                'email':user_info(token_).get("email"),
                'username':user_info(token_).get("username"),
                'datetime':str(datetime_),
                'status': attendence_status,
                'event_name':event_name_,
                'admin_name':admin_name_,
                'otp':otp_
            }
            emit('admin_listen', json.dumps(payLoad), namespace='/admin_namespace')
        else:
            raise ValueError('Status failure')
    except:
        payLoad = {
            'email':'',
            'username':'',
            'datetime':str(datetime.datetime.now()),
            'status': 'Failure',
            'event_name':'',
            'admin_name':'',
            'otp':-1
        }
        emit('admin_listen', json.dumps(payLoad), namespace='/admin_namespace')



if __name__ == '__main__':
    socketio.run(app)



## Do this:
# when a new event is created, event-name (slug) is added in events db. Now when attende sends otp we take it and check if it matches with any \
# event and event attendence is going on. Then we take attendence and emit this info to admin namespace.
# also, attende attendence is sended to one more route that attendence is emited to that particular event room (if allowed for so by admin).

# attendence is emitted to: 1) attendence namespace, from their attendence is done and emited to admin.
# 2) broadcaster namespace, from there to specific room name if allowed by admin.

# admin_namespace -> to emit to the admin_namespace :emits to the client side namespace then  (SERVER SIDE NOT NEEDED)
# attendence_namespace-> attendence (to emit client attendence) :emits to the client side admin_namespace then
# broadcaster_namespace -> attendence comes to this namespace also, from here it's sended to particular room



### SocketsIO how and what
# User can only emit
## the attendence is marked
#event otp is required, and the token for that very user


# Browser will Broadcast 1)attendences  (otp cann't be broadcasted)
## When user enters the otp, it takes them to a dashbaord with that otp
##and their we broadcast the attendences



#### To be continued

# Create API endpoints for admin to mark someones attendence
# Endpoint to generate csv file for a paticular event with attendes details
# Time check, before attendence verify it's in allowed time limit. Or frontend takes care of this and don't send vague requests \
#or server takes request don't add to db and sends a message Attendence is closed now.
#fetch creation_date and time_delta then before adding see if valid.

### Implementing the socketIO
# user emits a signal to us with otp then we process and commit it.

# An API to give a few otp examples which are available


##### To be done
# so much cleaning and filtering and purifying
# use bcrypt to genrate and store passwords in hashes only-
    # signup, create and commit in database
    # login, check
# check for already registered users:-> not possible as we email is pk
# make use of make_response, to add status code as well along with jsonify return
# replace flask-jwt with flask-jwt-extended
# from passlib.hash import pbkdf2_sha256 as sha256
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTE2Mzc2NDksImlhdCI6MTU4MDEwMTY0NCwic3ViIjoxfQ.QkM-DsJR0yuVbSL-ElkQeHG0xYPpF_BrA-lJhi8MZqk
# clean dtetime.datetime.now()
# In Events table, admin name is used, can be either made unique during /
#registration or make it admin email. Ask?
# imporovements in model can be done, like create a function that takes id or email \
#and gives all other details. then use this in all other functions
# check if resp isinstance of str or not