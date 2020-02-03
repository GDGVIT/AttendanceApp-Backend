from app import *


from app.MyFunctions import *
from app.models import *
from app.schemas import *
from app.routes import *
from app.sockets import *


if __name__ == '__main__':
    socketio.run(app)