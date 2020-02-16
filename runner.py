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
    socketio.run(app, host='0.0.0.0', port=port, threaded=True) # when running on heroku
    #   socketio.run(app, host='127.0.0.1', port=port, ssl_context="adhoc") # when running locally with cert and for Gauth API# pip install pyOpenSSL
    #   socketio.run(app, host="127.0.0.1", port=3000) # when running locally without cert