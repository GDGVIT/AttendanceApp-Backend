from .__init__ import *


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
        fields = ('id', 'creation_date', 'admin_email', 'otp', 'event_name', \
            'event_description', 'ending_time_delta', 'location_range', 'latitude', 'longitude', 'broadcast_choice')

event_schema = EventSchema()
events_schema = EventSchema(many=True)