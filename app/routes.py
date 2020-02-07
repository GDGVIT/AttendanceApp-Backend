from .__init__ import *

from .MyFunctions import *
from .schemas import *
from .sockets import *
from flask import send_from_directory

# internal
import io
import csv
from datetime import timedelta


@app.route('/', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def testing_purpose():
    return "<h1> Hi </h1>"

# user signup
@app.route('/user/signup', methods=['POST'])
@cross_origin(supports_credentials=True)
def user_signup():

    username=request.json['username']
    password = request.json['password']
    password = bcrypt.generate_password_hash(password).decode() # hashed, better than SHA1
    email=request.json['email']

    email_check = Users.query.filter_by(email=email).first()

    if email_check:
        payLoad = {
            'username':'',
            'password':'',
            'email':'',
            'admin_status':0,
            'jwt':'',
            'status':'User Already Exsists'
        }
        return make_response(jsonify(payLoad), 208)

    new_user = Users(username, password, email)
    db.session.add(new_user)
    db.session.commit()

    user = Users.query.filter_by(email=request.json['email']).first()
    auth_token = encode_auth_token(user.id)

    try:
        TokenValue = auth_token.decode()
    except Exception as e: # TypeError object has no attribute Token
        payLoad = {
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':'',
        'status':"Failed to generate Token"
        }
        return make_response(jsonify(payLoad), 500)

    payLoad = {
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':TokenValue,
        'status':"User Created Successfully"
    }
    return make_response(jsonify(payLoad), 200)


# user login
@app.route('/user/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def user_login():

    email=request.json['email']
    password=request.json['password']

    # ReCapchav3 code
    try:
        captcha_response = request.json['g-recaptcha-response']

        if not is_human(captcha_response):
            payLoad = {
                'status': 'fail',
                'message': 'sorry-bots-are-not-allowed',
                'auth_token':'',
                'admin_status':0
            }
            return make_response(jsonify(payLoad), 400)
    except Exception as e:
        debug(e)

    email_exsist = Users.query.filter_by(email=email).first()

    try:
        if email_exsist==None:
            payLoad = {
                'status': 'fail',
                'message': 'User-does-not-exsist',
                'auth_token':'',
                'admin_status':0
            }
            return make_response(jsonify(payLoad), 404)

        user = Users.query.filter_by(email=request.json['email']).first()

        if bcrypt.check_password_hash(user.password, password):   #password == user.password
            auth_token = encode_auth_token(user.id)
            admin_status_ = Users.query.filter_by(email=email).first().admin_status
            payLoad = {
                'status':'success',
                'message':'Successfully-logged-in',
                'auth_token':auth_token.decode(),
                'admin_status':admin_status_
            }
            return make_response(jsonify(payLoad), 200)
        else:
            payLoad = {
                'status': 'fail',
                'message': 'Wrong-Credentials! Check-Again.',
                'auth_token':'',
                'admin_status':0
            }
            return make_response(jsonify(payLoad), 401)
    except Exception as e:
        payLoad = {
            'status': 'fail',
            'message': 'Wrong-Credentials! Check-Again.',
            'auth_token':'',
            'admin_status':0
        }
        return make_response(jsonify(payLoad), 401)


# This is for testing, it may not be needed
@app.route('/user/logged', methods=['GET'])
@cross_origin(supports_credentials=True)
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
            payLoad = {
                'status': 'success',
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.username,
                    'admin_status': user.admin_status
                }
            }
            return make_response(jsonify(payLoad), 200)
        payLoad = {
            'status':'Fail',
            'message':resp
        }
        return make_response(jsonify(payLoad), 400)
    else:
        payLoad = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(payLoad), 400)



# users view (Admin)
@app.route('/users', methods=['GET'])
@cross_origin(supports_credentials=True)
def user_view():

    # Pass JWT Token in Header
    """
    return: detail of all registered users
    """
    try:
        auth_header = request.headers.get('Authorization')
        user_detail = user_info(auth_header)
    except:
        payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

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


# user view (Admin)
@app.route('/users/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def single_user_view(id):

    # Pass JWT Token in Header
    """
    return: detail of user for provided <id>
    """
    try:
        auth_header = request.headers.get('Authorization')
        user_detail = user_info(auth_header)
    except:
        payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

    if user_detail != 'AuthFail':

        try:
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
        except:
            payLoad = {
                'Status':'Fail',
                'Reason':'User Not Found'
            }
            return make_response(jsonify(payLoad), 404)
    
    else:
        payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)





# create event
@app.route('/event/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def create_event():

    """
    Endpoint to create an Event
    Required: Authorized and admin
    return: event detail | auth fail
    """

    auth_header = request.headers.get('Authorization')
    try:
        user_details = user_info(auth_header)
    except: # Token Failure
        payLoad = {
            'status':'Fail',
            'message':'Failed to get Secrets'
        }
        return make_response(jsonify(payLoad), 500)
    try:
        admin_status_ = user_details.get('admin')
    except:
        admin_status = 0

    if user_details != 'AuthFail' and admin_status_:
        creation_date_ = datetime.datetime.now()
        admin_email_ = user_details.get("email")

        otp_ = request.json.get('otp')

        if len(otp_)!=6:
            payLoad = {
                'Status': 'Fail',
                'Reason': 'OTP Size Constraint'
            }
            return make_response(jsonify(payLoad), 406)

        try:
            event_name_ = request.json['event_name']
            event_description_ = request.json['event_description']
            ending_time_delta_ = request.json['ending_time_delta']
            location_range_ = request.json.get('location_range')
            latitude_ = request.json.get('latitude')
            longitude_ = request.json.get('longitude')
            broadcast_choice_ = request.json.get('broadcast_choice')
        except:
            payLoad = {
                'Status': 'Fail',
                'Reason': 'Fill All Required Details'
            }
            return make_response(jsonify(payLoad), 400)

        if location_range_==None or latitude_==None or longitude_==None: # Measure to protect issues
            latitude_ = -1.1
            longitude_ = -1.1
            location_range_ = -1

        otp_check = Events.query.filter_by(otp=otp_).first()

        if otp_check: #exsists
            payLoad = {
                'Status': 'Fail',
                'Reason': 'OTP has expired' #used otp
            }
            return make_response(jsonify(payLoad), 400)
        
        else:  
            new_event = Events(creation_date= creation_date_, admin_email=admin_email_, \
                    otp=otp_, event_name=event_name_, event_description=event_description_, \
                    ending_time_delta=ending_time_delta_, location_range=location_range_, \
                    latitude=latitude_, longitude=longitude_, broadcast_choice=broadcast_choice_)

            db.session.add(new_event)
            db.session.commit()

            payLoad = event_schema.jsonify(new_event)
            return make_response(payLoad, 200) # Object of type Response is not JSON serializable
        
    else:
        payLoad = {
            'status':'Fail',
            'message':'Not Admin'
        }
        return make_response(jsonify(payLoad), 401)


# API is not needed here. For Testing Purposes.
@app.route('/attendence', methods=['POST'])
@cross_origin(supports_credentials=True)
def attendence_post():

    # If status is 0 then treat it as not present and specify reason
    # out of raidus distance

    # event exsists -done
    # user authorized -done
    # InValid Time -done
    datetime_ = datetime.datetime.now()

    event_otp_ = request.json.get('event_otp')
    try:
        event_check = Events.query.filter_by(otp=event_otp_).first()
        if event_check == None:
            raise ValueError('No such Event Exsists')
    except: # Event doesn't exsists
        payLoad = {
            "event_otp":event_otp_,
            "email":'', # Suppose if email failure, then again a new check. So better not returning it.
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)

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

    try: # Integer, else error thrown from distance function
        user_latitude = request.json.get('latitude')
        user_longitude = request.json.get('longitude')
        assert type(user_latitude)==type(float()) or type(user_latitude)==type(int())
        assert type(user_longitude)==type(float()) or type(user_longitude)==type(int())
    except:
        user_latitude = None
        user_longitude = None

    admin_latitude = Events.query.filter_by(otp = event_otp_).first().latitude
    admin_longitude = Events.query.filter_by(otp = event_otp_).first().longitude
    location_range_ = Events.query.filter_by(otp = event_otp_).first().location_range

    if location_range_==-1 or admin_latitude==-1.1 or admin_longitude==-1.1: # Lat and Long failed to come or Distance Range not given
        distance_ = 10
        location_range_ = 0
    else:
        if user_latitude==None or user_longitude==None:
            location_range_=-1
            distance_ = 10
            location_range_ = 0
        else:
            distance_ = distance([user_latitude, user_longitude], [admin_latitude, admin_longitude])

    if distance_>location_range_:
        status_ = 0
    else:
        status_ = 1 

    try:
        event_query = Events.query.filter_by(otp=event_otp_).first()

        admin_datetime = event_query.creation_date
        ending_time_delta_ = event_query.ending_time_delta
        datetime_check = admin_datetime + timedelta(minutes=ending_time_delta_)

        if datetime_ > datetime_check:
            payLoad = {
                "event_otp":event_otp_,
                "email":email_,
                "datetime":datetime_,
                "status":0
            }
            return make_response(jsonify(payLoad), 423) # Attendence is locked down

        # Checking if user has already given attendance
        event_attendences = Attendence.query.filter_by(event_otp=event_otp_).all()
        for user in event_attendences:
            if user.email == email_ and user.status in ['t', 'True', True, '1', 1]:
                payLoad = {
                    "event_otp":event_otp_,
                    "email":email_,
                    "datetime":datetime_,
                    "status":0
                }
                return make_response(jsonify(payLoad), 400)
            
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

    except Exception as e: # No such event
        debug(e)
        event_id_ = -1
        payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)


# Routes for Admin
# To post Attandence (Doesn't matter if failed attendance given or not) \
# because anyhow we are allowing user to put as many attendences on as they wish
# on our sockets
@app.route('/attendence/update/<email>', methods=['POST'])
@cross_origin(supports_credentials=True)
def attendence_update(email):

    # otp, email
    # here we ignore whether event is going on or closed
    auth_header = request.headers.get('Authorization')
    user_detail = user_info(auth_header)

    if user_detail != 'AuthFail':

        try:
            if user_detail.get('admin'):
                event_otp_ = request.json['otp']
                email_ = email
                
                otp_check = Events.query.filter_by(otp=event_otp_).first()
                if otp_check == None:
                    raise ValueError('No such Event')

                email_check = Users.query.filter_by(email=email_).first()
                if email_check == None:
                    raise ValueError('No User with Given Email')
                
                event_id_ = Events.query.filter_by(otp = event_otp_).first().id
                datetime_ = datetime.datetime.now()
                status_ = 1

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
        
            elif user_detail.get('admin') == 0:
                payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)
        
        except:
            payLoad = {
                'Status':'Fail',
                'Reason':'ReCheck OTP and Email'
            }
            return make_response(jsonify(payLoad), 404)

    else:
        payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)


# Download CSV file for Event Attendenes (Event Report Generation)
@app.route('/download/<otp>')
@cross_origin(supports_credentials=True)
def report_generation(otp):

    try:
        event_list = Attendence.query.filter_by(event_otp=otp).all()
        event_name = Events.query.filter_by(otp=otp).first().event_name
        event_name = event_name.replace(' ', '-')

        csv_list = [['id',
            'email',
            'datetime',
            'status',
            ]]

        for each in event_list:
            
            csv_list.append([each.id, 
                each.email, 
                each.datetime,
                each.status,
                ])

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csv_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(event_name)
        output.headers["Content-type"] = "text/csv"
        return output
    except: # Incorrect Event-OTP
        payLoad = {
            'Message': 'Incorrect Event OTP'
        }
        return make_response(jsonify(payLoad), 400)


# Events Info API (Admin)

@app.route('/events/info', methods=['GET'])
@cross_origin(supports_credentials=True)
def events_info():

    # Pass JWT Token in Header
    """
    :return: detail of all Events
    """
    try:
        auth_header = request.headers.get('Authorization')
        user_detail = user_info(auth_header)
    except:
        payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

    if user_detail != 'AuthFail':

        if user_detail.get('admin'): # NoneType | 0| 1
            all_events = Events.query.all() # Here Error if no Event
            result = events_schema.dump(all_events)
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


# Event Info API (Admin)

@app.route('/events/info/<otp>', methods=['GET'])
@cross_origin(supports_credentials=True)
def event_info(otp):

    # Pass JWT Token in Header
    """
    return: detail of event for provided <otp>
    """
    try:
        auth_header = request.headers.get('Authorization')
        user_detail = user_info(auth_header)
    except:
        payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)
    
    if user_detail != 'AuthFail':

        try:
            if user_detail.get('admin'): # NoneType | 0| 1
                event = Events.query.filter_by(otp=otp).first() # Here No Error if Event not present
                
                if event==None:
                    payLoad = {
                        'Status':'Fail',
                        'Reason':'Event Not Found'
                    }
                    return make_response(jsonify(payLoad), 404)

                result = event_schema.dump(event)
                payLoad = result
                return make_response(jsonify(payLoad), 200)
        
            elif user_detail.get('admin') == 0:
                payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)
        except:
            payLoad = {
                'Status':'Fail',
                'Reason':'Server Error'
            }
            return make_response(jsonify(payLoad), 500)
    
    else:
        payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)


# Random Valid OTP Generator

@app.route('/random/otp', methods=['GET'])
@cross_origin(supports_credentials=True)
def random_otp():

    # Pass JWT Token in Header
    """
    :return: detail of all Events
    """
    try:
        auth_header = request.headers.get('Authorization')
        user_detail = user_info(auth_header)
    except:
        payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)
    
    try:
        if user_detail != 'AuthFail':

            if user_detail.get('admin'): # NoneType | 0| 1
                all_events = Events.query.all() # Here Error if no Event
                used_otps = set()
                for otp_ in all_events:
                    used_otps.add(str(otp_.otp))
                
                total_otps = set()
                available_otps = set()
                for otp_ in range(0, 999999+1):
                    otp = str(otp_)
                    if len(otp)!=6:
                        diff = 6-len(otp)
                        otp = '0'*diff + otp
                    total_otps.add(otp)

                    available_otps = total_otps - used_otps
                    if len(available_otps) == 3:
                        break
                payLoad = {
                        "otp1": available_otps.pop(),
                        "otp2": available_otps.pop(),
                        "otp3": available_otps.pop()
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
    except:
            payLoad = {
                'Status':'Fail',
                'Reason':'Server Failure'
            }
            return make_response(jsonify(payLoad), 500)


# Google Auth Route
@app.route("/login/google")
@cross_origin(supports_credentials=True)
def login():

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


# code will come here (Backend only)
@app.route("/login/google/callback")
@cross_origin(supports_credentials=True)
def callback():

    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        #unique_id = userinfo_response.json()["sub"]
        #picture = userinfo_response.json()["picture"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    users_password = users_email    ##token_hex(6) # We can keep password as Email also

    email_check = Users.query.filter_by(email=users_email).first()

    if email_check:
        payLoad = {
            'username':'',
            'password':'',
            'email':'',
            'admin_status':0,
            'jwt':'',
            'status':'User Already Exsists'
        }
        return make_response(jsonify(payLoad), 208)

    new_user = Users(username=users_name, password=users_password, email=users_email)
    db.session.add(new_user)
    db.session.commit()

    user = Users.query.filter_by(email=users_email).first()
    auth_token = encode_auth_token(user.id)

    try:
        TokenValue = auth_token.decode()
    except Exception as e: # TypeError object has no attribute Token
        payLoad = {
        'username':users_name,
        'password':users_password,
        'email':users_email,
        'admin_status':0,
        'jwt':'',
        'status':"Failed to generate Token |  User is Created Successfully"
        }
        return make_response(jsonify(payLoad), 500)

    payLoad = {
        'username':users_name,
        'password':users_password,
        'email':users_email,
        'admin_status':0,
        'jwt':TokenValue,
        'status':"User Created Successfully"
    }
    return make_response(jsonify(payLoad), 200)


@app.route("/.well-known/acme-challenge/aokcL2OopAazPQc_2ih2E8kvf6DQf3cYGxtJh6Gk4S8")
@cross_origin(supports_credentials=True)
def cert_purpose():
    return send_from_directory(root, 'aokcL2OopAazPQc_2ih2E8kvf6DQf3cYGxtJh6Gk4S8.rxo3TnizjGMpXaT9kXo-AxrZB5G956vWi8LiTrdxIB0')
