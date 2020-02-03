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
from flask_bcrypt import Bcrypt
from os import environ


def debug(msg):
    print('\n\n\n'+str(msg)+'\n\n\n'+'\n\nType:\t'+str(type(msg))+'\n\n')


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = environ.get('STRIPE_API_KEY')


db = SQLAlchemy(app)

ma = Marshmallow(app)

bcrypt = Bcrypt(app)

socketio = SocketIO(app, cors_allowed_origins='*')


class Users(db.Model):

    # pk is email
    """
    API call will interact with Users table
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(100)) #bcrypt storage needs 60 size
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
    admin_email = Column(String(60))
    attendence = db.relationship(
        'Attendence', backref='event', lazy=True)
    # These are the required fields in post request
    otp = Column(String(6), nullable=False, unique=True) #900,000 Events supported without flushing data (Don't know but I passed more lol)
    event_name = Column(String(100))
    event_description = Column(String(2000), nullable=True)
    ending_time_delta = Column(Integer) #Treated in Minutes
    location_range = Column(Integer)  # Treated in meters
    latitude = Column(Float)
    longitude = Column(Float)
    broadcast_choice = Column(Boolean)  # an option to allow or disallow broadcast to users


class Attendence(db.Model):

    # pk is id
    """
    SocketIO will interact with Attendence table
    """
    __tablename__ = "attendences"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))

    event_otp = Column(String(6), nullable=False)
    
    email = Column(String(60))
    datetime = Column(DateTime)
    status = Column(Boolean) #presence column for location ambiguity (server handled)