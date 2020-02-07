# API DOCS

## @app.route('/', methods=['GET', 'POST'])
```
```

## @app.route('/user/signup', methods=['POST'])
```
- payLoad = {
            'username':'',
            'password':'',
            'email':'',
            'admin_status':0,
            'jwt':'',
            'status':'User Already Exsists'
        }
        return make_response(jsonify(payLoad), 208)

- payLoad = {
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':'',
        'status':"Failed to generate Token"
        }
        return make_response(jsonify(payLoad), 500)

- payLoad = {
        'username':username,
        'password':password,
        'email':email,
        'admin_status':0,
        'jwt':TokenValue,
        'status':"User Created Successfully"
    }
    return make_response(jsonify(payLoad), 200)

```

## @app.route('/user/login', methods=['POST'])
```
- payLoad = {
                'status': 'fail',
                'message': 'User does not exsist',
                'auth_token':'',
                'admin_status':0
            }
            return make_response(jsonify(payLoad), 404)

- payLoad = {
                'status':'success',
                'message':'Successfully logged in',
                'auth_token':auth_token.decode(),
                'admin_status':admin_status_
            }
            return make_response(jsonify(payLoad), 200)

- payLoad = {
                'status': 'fail',
                'message': 'Wrong Credentials! Check Again.',
                'auth_token':'',
                'admin_status':0
            }
            return make_response(jsonify(payLoad), 401)

- payLoad = {
            'status': 'fail',
            'message': 'Wrong Credentials! Check Again.',
            'auth_token':'',
            'admin_status':0
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/user/logged', methods=['GET'])
```
- payLoad = {
                'status': 'success',
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.username,
                    'admin_status': user.admin_status
                }
            }
            return make_response(jsonify(payLoad), 200)

- payLoad = {
            'status':'Fail',
            'message':resp
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(payLoad), 400)

```

## @app.route('/users', methods=['GET'])
```
- payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
                'Status':'Fail',
                'Reason':'Not Admin'
            }
            return make_response(jsonify(payLoad), 403)

- payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/users/<id>', methods=['GET'])
```
- payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
                    'id':id,
                    'email':user.email,
                    'username':user.username,
                    'password':user.password
                }
                return make_response(jsonify(payLoad), 200)

- payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)

- payLoad = {
                'Status':'Fail',
                'Reason':'User Not Found'
            }
            return make_response(jsonify(payLoad), 404)

- payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/event/create', methods=['POST'])
```
- payLoad = {
            'status':'Fail',
            'message':'Failed to get Secrets'
        }
        return make_response(jsonify(payLoad), 500)

- payLoad = {
                'Status': 'Fail',
                'Reason': 'OTP Size Constraint'
            }
            return make_response(jsonify(payLoad), 406)

- payLoad = {
                'Status': 'Fail',
                'Reason': 'Fill All Required Details'
            }
            return make_response(jsonify(payLoad), 400)

- payLoad = {
                'Status': 'Fail',
                'Reason': 'OTP has expired' #used otp
            }
            return make_response(jsonify(payLoad), 400)

- payLoad = {
            'status':'Fail',
            'message':'Not Admin'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/attendence', methods=['POST'])
```
- payLoad = {
            "event_otp":event_otp_,
            "email":'', # Suppose if email failure, then again a new check. So better not returning it.
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)

- payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)

- payLoad = {
                "event_otp":event_otp_,
                "email":email_,
                "datetime":datetime_,
                "status":0
            }
            return make_response(jsonify(payLoad), 423)

- payLoad = {
                    "event_otp":event_otp_,
                    "email":email_,
                    "datetime":datetime_,
                    "status":0
                }
                return make_response(jsonify(payLoad), 400)

- payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":status_
        }
        return make_response(jsonify(payLoad), 200)

- payLoad = {
            "event_otp":event_otp_,
            "email":email_,
            "datetime":datetime_,
            "status":0
        }
        return make_response(jsonify(payLoad), 404)

```

## @app.route('/attendence/update/<email>', methods=['POST'])
```
- payLoad = {
                    "event_otp":event_otp_,
                    "email":email_,
                    "datetime":datetime_,
                    "status":status_
                }
                return make_response(jsonify(payLoad), 200)

- payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)

- payLoad = {
                'Status':'Fail',
                'Reason':'ReCheck OTP and Email'
            }
            return make_response(jsonify(payLoad), 404)

- payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/download/<otp>')
```
- payLoad = {
            'Message': 'Incorrect Event OTP'
        }
        return make_response(jsonify(payLoad), 400)

```

## @app.route('/events/info', methods=['GET'])
```
- payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
                'Status':'Fail',
                'Reason':'Not Admin'
            }
            return make_response(jsonify(payLoad), 403)

- payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/events/info/<otp>', methods=['GET'])
```
- payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
                        'Status':'Fail',
                        'Reason':'Event Not Found'
                    }
                    return make_response(jsonify(payLoad), 404)

- payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)

- payLoad = {
                'Status':'Fail',
                'Reason':'Server Error'
            }
            return make_response(jsonify(payLoad), 500)

- payLoad = {
            'Status':'Fail',
            'Reason':'AuthFail'
        }
        return make_response(jsonify(payLoad), 401)

```

## @app.route('/random/otp', methods=['GET'])
```
- payLoad = {
            'Status':'Fail',
            'Reason':'Failed to Resolve Token'
        }
        return make_response(jsonify(payLoad), 400)

- payLoad = {
                        "otp1": available_otps.pop(),
                        "otp2": available_otps.pop(),
                        "otp3": available_otps.pop()
                } 
                return make_response(jsonify(payLoad), 200)

- payLoad = {
                    'Status':'Fail',
                    'Reason':'Not Admin'
                }
                return make_response(jsonify(payLoad), 403)

- payLoad = {
                'Status':'Fail',
                'Reason':'AuthFail'
            }
            return make_response(jsonify(payLoad), 401)

- payLoad = {
                'Status':'Fail',
                'Reason':'Server Failure'
            }
            return make_response(jsonify(payLoad), 500)

```

## @app.route("/login/google")
```
```

## @app.route("/login/google/callback")
```
- payLoad = {
            'username':'',
            'password':'',
            'email':'',
            'admin_status':0,
            'jwt':'',
            'status':'User Already Exsists'
        }
        return make_response(jsonify(payLoad), 208)

- payLoad = {
        'username':users_name,
        'password':users_password,
        'email':users_email,
        'admin_status':0,
        'jwt':'',
        'status':"Failed to generate Token |  User is Created Successfully"
        }
        return make_response(jsonify(payLoad), 500)

- payLoad = {
        'username':users_name,
        'password':users_password,
        'email':users_email,
        'admin_status':0,
        'jwt':TokenValue,
        'status':"User Created Successfully"
    }
    return make_response(jsonify(payLoad), 200)

```

