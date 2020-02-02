from .__init__ import *


from .MyFunctions import *
# from .models import *
from .schemas import *
from .sockets import *

@app.route('/', methods=['GET', 'POST'])
def testing_purpose():
    return "<h1> Hi </h1>"

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

    try:
        TokenValue = auth_token.decode()
    except: # TypeError object has no attribute Token
        return jsonify({
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':'',
        'status':"Failed to generate Token"
        })

    return jsonify({
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':TokenValue,
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
            'message':'Not Admin'
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