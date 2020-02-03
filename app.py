from app import *


from app.MyFunctions import *
from app.models import *
from app.schemas import *
from app.routes import *
from app.sockets import *


port=os.environ.get("PORT")

if port is None or port == "":
    port = 3000

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port)