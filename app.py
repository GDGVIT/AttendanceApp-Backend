import os
import math
import json 
import datetime

# external
import jwt
from flask import (
    Flask,
    request,
    jsonify,
    make_response,
)
from flask_socketio import (
    SocketIO, 
    send, 
    emit, 
    join_room, 
    leave_room,
)
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
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from os import environ



def debug(msg):
    print('\n\n\n'+msg+'\n\n\n')


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = environ.get('STRIPE_API_KEY')


db = SQLAlchemy(app)

ma = Marshmallow(app)

socketio = SocketIO(app, cors_allowed_origins='*')


# Distance Calculator
def distance(origin, destination):

    """
    Find distance between two given coordinates
    :param arg1: ['latitudeA', 'longitudeA']
    :param arg2: ['latitudeB', 'longitudeB']
    :type arg1: list
    :type arg2: list
    :return: distance in meters, round by 2
    :type: Integer
    """

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
    :param arg1: User ID
    :type arg1: Integer
    :return: JWT Token
    :rtype: string
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
    :param arg1: JWT Token
    :type arg1: String
    :return: User ID | Exception
    :rtype: Integer |  String
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

    """
    Give User Details by simplying passing JWT Token
    :param arg1: JWT Token
    :type arg1: String
    :return: User Detail | 'AuthFail'
    :rtype: Dict | String
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
    return 'AuthFail' #This should have been changed to dict type


### Models

class Users(db.Model):

    # pk is email
    """
    API call will interact with Users table
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
    """
    API call will interact with Events table
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
    """
    SocketIO will interact with Attendence table
    """
    __tablename__ = "attendences"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))

    event_otp = Column(String(6), nullable=False) #before inserting check if otp does exsists in events table
    
    email = Column(String(60))
    datetime = Column(DateTime)
    status = Column(Boolean) #presence column, for location ambiguity, server handled



### Scehmas
## Maybe I never needed Schemas :?

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

    email_check = Users.query.filter_by(email=email).first()

    if email_check:
        return jsonify({
            'username':'',
            'password':'',
            'email':'',
            'admin_status':0,
            'jwt':'',
            'status':'User Already Exsists'
        })

    new_user = Users(username, password, email)
    db.session.add(new_user)
    db.session.commit()

    user = Users.query.filter_by(email=request.json['email']).first()
    auth_token = encode_auth_token(user.id)

    return jsonify({
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':auth_token.decode(),
        'status':"User Created Successfully"
    })


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
        return jsonify({
            'status': 'fail',
            'message': 'Wrong Credentials! Check Again.'
        })


# This is for testing, it may not be needed
@app.route('/user/logged', methods=['POST'])
def user_logged():

    """
    return: id, memail, name, admin_status for logged in user | Failure message if authorization fails
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

    # Pass JWT Token in Header
    """
    return: detail of all registered users
    """
    auth_header = request.headers.get('Authorization')
    user_detail = user_info(auth_header)

    if user_detail != 'AuthFail':

        if user_detail.get('admin'): # NoneType | 0| 1
            all_users = Users.query.all()
            result = users_schema.dump(all_users)
            payLoad = result
            return make_response(jsonify(payLoad), 200)
    
        elif user_detail.get('admin') == 0:
            payLoad = {
                'Status':'Fail',
                'Reason':'Not Admin'
            }
            return make_response(jsonify(payLoad), 403)
    
    else:
        payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)


# user view
@app.route('/users/<id>', methods=['GET'])
def single_user_view(id):

    # Pass JWT Token in Header
    """
    return: detail of user for provided <id>
    """
    auth_header = request.headers.get('Authorization')
    user_detail = user_info(auth_header)

    if user_detail != 'AuthFail':

        if user_detail.get('admin'): # NoneType | 0| 1
            user = Users.query.get(id)
            payLoad = {
                'id':id,
                'email':user.email,
                'username':user.username,
                'password':user.password
            }
            return make_response(jsonify(payLoad), 200)
    
        elif user_detail.get('admin') == 0:
            payLoad = {
                'Status':'Fail',
                'Reason':'Not Admin'
            }
            return make_response(jsonify(payLoad), 403)
    
    else:
        payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)





# create event
@app.route('/event/create', methods=['POST'])
def create_event():

    """
    Endpoint to create an Event
    Required: Authorized and admin
    return: event detail | auth fail
    """

    auth_header = request.headers.get('Authorization')
    user_details = user_info(auth_header)
    try:
        admin_status_ = user_details.get('admin')
    except:
        admin_status = 0

    if user_details != 'AuthFail' and admin_status_:
        creation_date_ = datetime.datetime.now()
        admin_name_ = user_details.get("username")

        otp_ = request.json['otp']
        event_name_ = request.json['event_name']
        event_description_ = request.json['event_description']
        ending_time_delta_ = request.json['ending_time_delta']
        location_range_ = request.json['location_range']

        otp_check = Events.query.filter_by(otp=otp_).first()

        if otp_check: #exsists
            payLoad = {
                'Status': 'Fail',
                'Reason': 'OTP has expired' #used otp
            }
            return make_response(jsonify(payLoad), 400)
        
        else:  
            new_event = Events(creation_date= creation_date_, admin_name=admin_name_, \
                    otp=otp_, event_name=event_name_, event_description=event_description_, \
                    ending_time_delta=ending_time_delta_, location_range=location_range_)

            db.session.add(new_event)
            db.session.commit()

            payLoad = event_schema.jsonify(new_event)
            return make_response(payLoad, 200) # Object of type Response is not JSON serializable
        
    else:
        payLoad = {
            'status':'Fail',
            'message':'Authentication Failure'
        }
        return make_response(jsonify(payLoad), 401)


# API is not needed here. For Testing Purposes.
@app.route('/attendence', methods=['POST'])
def attendence_post():

    # If status is 0 then treat it as not present and specify reason
    # out of raidus distance

    # event exsists -done
    # user authorized -done

    event_otp_ = request.json.get('event_otp')
    datetime_ = datetime.datetime.now()
    try:
        email_ = user_info(request.headers.get('Authorization')).get("email")
    except: # User Doesn't exsist.
        email_ = ''
        payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)

    # workleft: In api take latitude and longitude of user and then
    # compare it with admins lat and long and judge on distance param
    status_ = 1 # code logic needed here
    try:
        event_id_ = Events.query.filter_by(otp = event_otp_).first().id
        new_attendence = Attendence(event_id=event_id_, event_otp=event_otp_, email=email_, \
            datetime=datetime_, status=status_)
        db.session.add(new_attendence)
        db.session.commit()
        payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":status_
        }
        return make_response(jsonify(payLoad), 200)

    except: # No such event
        event_id_ = -1
        payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)





@socketio.on('join', namespace='/rooms_namespace')
def on_join(data):

    """
    verify if attendence is success 
    then get them join in that room name with otp added
    now broadcast to that room
    """
    try:
        data = json.loads(data) # now it's dict form, before it was string
    except:
        data = {}

    status = data.get('status')
    if status!='Success':
        return ''
    
    room = '-'.join(data.get('event_name').split(' ')) + '-' + str(data['otp'])
    username = data.get("username") #add this to payLoad (clientside)
    join_room(room)
    mymessage = {
        'username':data.get('username')
    }

    emit('join_room', json.dumps(mymessage), room=room)



@socketio.on('admin_stats', namespace='/admin_namespace')
def made_for_admin():

    """
    To tell flask-SocketIO that there exsists a namespace named admin_namespace
    then we can use it in functions written below. Or else error will be thrown.
    """
    #admin_stats is mapped with admin_listen
    pass



@socketio.on('attendence_request', namespace='/attendence_namespace')
def take_attendence_from_user(json_):
    
    #attendence_request is mapped with attendence_result at now
    """
    This will mark attendence if valid or return failure reason
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
        # Make change after making change in events model
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



""" To help someone who will work on this in future, To help the frontend person: (This may not be exactly True)

when a new event is created, event-name (slug) is added in events db. Now when attende sends otp we take it and check if it matches with any
event and event attendence is going on. Then we take attendence and emit this info to admin namespace.
also, attende attendence is sended to one more route that attendence is emited to that particular event room (if allowed for so by admin).

attendence is emitted to:
1) attendence namespace, from their attendence is done and emited to admin.
2) broadcaster namespace, from there to specific room name if allowed by admin.

admin_namespace -> to emit to the admin_namespace :emits to the client side namespace then  (SERVER SIDE NOT NEEDED)
attendence_namespace-> attendence (to emit client attendence) :emits to the client side admin_namespace then
broadcaster_namespace -> attendence comes to this namespace also, from here it's sended to particular room """



#### To be continued

# Create API endpoints for admin to mark someones attendence
# Endpoint to generate csv file for a paticular event with attendes details
# Time check, before attendence verify it's in allowed time limit. Or frontend takes care of this and don't send vague requests \
#or server takes request don't add to db and sends a message Attendence is closed now.
#fetch creation_date and time_delta then before adding see if valid.
# An API to give a few otp examples which are available


##### To be done
# so much cleaning and filtering and purifying
# use bcrypt to genrate and store passwords in hashes only-
    # signup, create and commit in database
    # login, check
# make use of make_response, to add status code as well along with jsonify return

# from passlib.hash import pbkdf2_sha256 as sha256
# jwt token expiry thing api


# In Events table, admin name is used, can be either made unique during /
#registration or make it admin email. Ask?
# add field admin_email in events model
# add admin_email field in sockets attendence_namespace payLoad for admin

## model changes
# add field admin_email in events model

## Not doing (left for future if someone works):
# replace flask-jwt with flask-jwt-extended
# empty password is allowed :) Yes, Auth is just to keep users track
# only single ip connection allowed for 1 user
# clean datetime.datetime.now()
# check bugs for sockets