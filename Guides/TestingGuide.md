## Testing
- setup environment
```
    python3 -m venv env
    source env/bin/activate
```
- install requirements
```
    pip install -r req.txt
```
- set SecretKey
```
    export STRIPE_API_KEY="12345"
```
- create Database
```
    python
    from app import *
    db.create_all()
```
- start app
```
  python app.py
```

### API Testing
- export postman file from testing folder
- test all api from here
  - JWT Auth is used
  - Test conditions which can break program like unauthorized access, asking detail of user that doesn't exsist

### Sockets Testing (Pull Request 2)
- open index.html from Testing folder twice
- open index2.html once
- open console for all three
- give attendence now, valid and invalid
##### Expected Behaviour
- both index.html file when given same valid otp(event) will group them and start showing on both of them (notice in console)
##### YouAreDoingWrong!
- update index.html and index.html2 with valid JWT token before you start
- Understand how different event users are getting grouped event wise so to test more breifly