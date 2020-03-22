from .__init__ import *


# Distance Calculator
def distance(origin, destination):

    """
    Find distance between two given coordinates
    :param arg1: ['latitudeA', 'longitudeA']
    :param arg2: ['latitudeB', 'longitudeB']
    :type arg1: list
    :type arg2: list
    :return: distance in meters, round by 2
    :type: Integer
    """

    # Conversions:
    # d_km = d_km/1000
    # d_miles = d_km*0.621371

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = abs(radius * c)

    return round(d*1000, 2)  # in meters




# JWT ENCODE/DECODE FUNCTIONS

def encode_auth_token(user_id):

    """
    Generates the Auth Token
    :param arg1: User ID
    :type arg1: Integer
    :return: JWT Token
    :rtype: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e: # Make sure secret key is set in environment, else NoneType ValueError
        return e


def decode_auth_token(auth_token='auth_header'):

    """
    Decodes the auth token
    :param arg1: JWT Token
    :type arg1: String
    :return: User ID | Exception
    :rtype: Integer |  String
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


# Function that gives user id, username, email and admin_status from JWT Token

def user_info(token):

    """
    Give User Details by simplying passing JWT Token
    :param arg1: JWT Token
    :type arg1: String
    :return: User Detail | 'AuthFail'
    :rtype: Dict | String
    """
    try:
        auth_token = token.split(" ")[0]
    except: # No JWT Token in header
        return 'AuthFail'
    resp = decode_auth_token(auth_token)
    if not isinstance(resp, str):
        user = Users.query.filter_by(id=resp).first()

        try: # suppose a user is deleted, then token is valid, and thus request reaches here and then error as no id for deleted user
            return {
                'id':user.id,
                'email':user.email,
                'username':user.username,
                'admin':user.admin_status
            }
        except:
            return 'AuthFail'

    return 'AuthFail' #This should have been changed to dict type


# Function to get the URL to redirect
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# ReCaptchv3 Verify the user
def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = CAPTCHA_SECRET
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']



def validFloat(someString):
    try:
        return float(someString)
    except:
        return -1.1