from .__init__ import *

from .MyFunctions import *
from .schemas import *
from .routes import *


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
                admin_email_ = event.admin_email
                attendence_status = 'Success' # This param is for admin only
            except:
                event_name_ = ''
                admin_email_ = ''
                otp_ = -1
                attendence_status = 'Failure' # This param is for admin only
            
            payLoad = {
                'email':user_info(token_).get("email"),
                'username':user_info(token_).get("username"),
                'datetime':str(datetime_),
                'status': attendence_status,
                'event_name':event_name_,
                'admin_email':admin_email_,
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
            'admin_email':'',
            'otp':-1
        }
        emit('admin_listen', json.dumps(payLoad), namespace='/admin_namespace')