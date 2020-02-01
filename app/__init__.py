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
    print('\n\n\n'+str(msg)+'\n\n\n'+'\n\nType:\t'+str(type(msg))+'\n\n')


# app = Flask(__name__)
# basedir = os.path.abspath(os.path.dirname(__file__))

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
#     os.path.join(basedir, 'db.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = environ.get('STRIPE_API_KEY')


# db = SQLAlchemy(app)

# ma = Marshmallow(app)

from .models import *
socketio = SocketIO(app, cors_allowed_origins='*')



