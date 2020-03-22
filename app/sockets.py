from .__init__ import *

from .MyFunctions import *
from .schemas import *
from .routes import *

# internal
from datetime import timedelta

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
        'username':data.get('username'),
        'RoomName':room
    }

    broadcast_choice_ = Events.query.filter_by(otp = data['otp']).first().broadcast_choice

    if broadcast_choice_:
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
        # :workleft: In client payLoad take latitude and longitude of user and then
        # compare it with admins lat and long and judge on distance param
        # Make change after making change in events model


        try: # Integer, else error thrown from distance function
            # user_latitude = json_['latitude']
            # user_longitude = json_['longitude'] # send them from client
            user_latitude = json_['latitude']
            user_latitude = validFloat(user_latitude)
            user_longitude = json_['longitude'] # send them from client
            user_longitude = validFloat(user_longitude)
            # Not Making Massive Changes, Though some code below can be removed.
            assert type(user_latitude)==type(float()) or type(user_latitude)==type(int())
            assert type(user_longitude)==type(float()) or type(user_longitude)==type(int())
        except:
            user_latitude = None
            user_longitude = None

        try:

            admin_latitude = Events.query.filter_by(otp = otp_).first().latitude
            admin_longitude = Events.query.filter_by(otp = otp_).first().longitude
            location_range_ = Events.query.filter_by(otp = otp_).first().location_range

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

            event_query = Events.query.filter_by(otp=otp_).first()

            admin_datetime = event_query.creation_date
            ending_time_delta_ = event_query.ending_time_delta
            datetime_check = admin_datetime + timedelta(minutes=ending_time_delta_)

            if datetime_ > datetime_check: # After Event has Ended
                time_constraint = 1
            else:
                time_constraint = 0

            event_id_ = Events.query.filter_by(otp=otp_).first().id #Earlier this was in catch block, now more otp_ associated things added in this catch
        except Exception as e: # Event Doesn't Exsist
            event_id_ = -1

        allow_forward = 0 # Flag to allow only Successfull Attendances to be passed to Admin
        if event_id_>=0:
            if time_constraint==1: # Keep Failures Before then the Success.
                Reason='Event has Ended now'
                StatusCode=423
                payLoad = {
                    'Status':'Fail',
                    'Reason':Reason,
                    'StatusCode':StatusCode
                }
                
            elif status_==0: # We are taking attendance but with status 0, which means absent \
                # this is because location failure can occur. So we can consider them present.
                Reason='You are far away from Event Location'
                StatusCode=400               
                payLoad = {
                    'Status':'Fail',
                    'Reason':Reason,
                    'StatusCode':StatusCode
                }
                new_attendence = Attendence(event_id=event_id_, event_otp=otp_, email=email_, \
                    datetime=datetime_, status=status_)
                db.session.add(new_attendence)
                db.session.commit()


            elif status_==1:

                already_given = False
                # Checking if user has already given attendence
                event_attendences = Attendence.query.filter_by(event_otp=otp_).all()
                for user in event_attendences:
                    if user.email == email_ and user.status in ['t', 'True', True, '1', 1]:
                        Reason='Attendence Already Given and Present'
                        StatusCode=400
                        payLoad = {
                            'Status':'Success',
                            'Reason':Reason,
                            'StatusCode':StatusCode
                        }
                        already_given = True
                        break
                
                if not already_given:
                    Reason='Attendence updated'
                    StatusCode=200

                    new_attendence = Attendence(event_id=event_id_, event_otp=otp_, email=email_, \
                        datetime=datetime_, status=status_)
                    db.session.add(new_attendence)
                    db.session.commit()
                    payLoad = {
                        'Status':'Success',
                        'Reason':Reason,
                        'StatusCode':StatusCode
                    }
                    
                    allow_forward = 1

            else:
                Reason='Server Error'
                StatusCode=500
                payLoad = {
                    'Status':'Fail',
                    'Reason': Reason,
                    'StatusCode':StatusCode
                }
                
        else:
            Reason='No such Event'
            StatusCode=404
            payLoad = {
                'Status':'Fail',
                'Reason':Reason,
                'StatusCode':StatusCode
            }
        
    else:
        Reason='AuthFail'
        StatusCode=401
        payLoad = {
            'Status':'Fail',
            'Reason': Reason,
            'StatusCode':StatusCode
        }
        
    emit('attendence_result', json.dumps(payLoad)) #json is emited now, privately
    try:
        # Now Emitting to Admin Namespace and from there it's \
        # sended to specific room also if admin has allowed this.

        # Checking if this user has given attendance for this event (otp) and don't forward it to admin in case attandance is given
        first_time = True
        first_time_count = 0 # Because Attendence is already given above, so 1 entry is already there
        try:
            user_attendences = Attendence.query.filter_by(email=email_)
            for EVENT in user_attendences:
                if EVENT.event_otp==otp_:
                    first_time_count+=1
                    if first_time_count==2:
                        first_time = False
                        break
        except: # Will be handled below
            pass

        if first_time == True:
            if status_: 
                # negative otp means ignore it, wrong entry
                # here recheck for otp is not needed, so can be removed
                try:
                    if allow_forward==0:
                        raise ValueError('Attendance Failure')
                    event = Events.query.filter_by(otp=otp_).first()
                    event_name_ = event.event_name
                    admin_email_ = event.admin_email
                    attendence_status = 'Success' # This param is for admin only
                    broadcast_choice_ = str(event.broadcast_choice)
                except:
                    event_name_ = ''
                    admin_email_ = ''
                    otp_ = -1
                    attendence_status = 'Failure' # This param is for admin only
                    broadcast_choice_ = '0'
                
                payLoad = {
                    'email':user_info(token_).get("email"),
                    'username':user_info(token_).get("username"),
                    'datetime':str(datetime_),
                    'status': attendence_status,
                    'event_name':event_name_,
                    'admin_email':admin_email_, # use this to send to specific admin
                    'otp':otp_,
                    'Reason':Reason,
                    'StatusCode':StatusCode,
                    'BroadcastChoice':broadcast_choice_,
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
            'admin_email':'',
            'otp':-1,
            'Reason':Reason,
            'StatusCode':StatusCode,
            'BroadcastChoice':broadcast_choice_,
        }
        emit('admin_listen', json.dumps(payLoad), namespace='/admin_namespace')
