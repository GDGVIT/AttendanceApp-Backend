<p align="center">
	<img src="https://user-images.githubusercontent.com/30529572/72455010-fb38d400-37e7-11ea-9c1e-8cdeb5f5906e.png" />
	<h2 align="center"> AttendanceApp-Backend  </h2>
	<h4 align="center"> Backend for Real Time Attendence application, which supports mulitple events simultaneously with real time feedback to admin and different admins. It also consists of location feature to detect proxies and many other features. <h4>
</p>
	<h4 align="center"> This is not the complete backend, but all main issues are resolved. Work left is to create some more endpoints for admin, securing of routes and level based access. </h4>
	<h4 align="center"> index.html and index2.html are to test sockets, run them along with server and test their. Keep your dev console open. All things are checked but do testify everything that you think can crash and create issue. Much of left work is written in code but you can create issue for the same. </h4>

---
[![DOCS](https://img.shields.io/badge/Documentation-postman%20docs-green?style=flat-square&logo=appveyor)](https://documenter.getpostman.com/view/9118595/SWTBfJAv)
[![DOCS](https://img.shields.io/badge/Documentation-Testing%20Guide-green?style=flat-square&logo=appveyor)](https://github.com/D-E-F-E-A-T/AttendanceApp-Backend/blob/factored_code_beta/Guides/TestingGuide.md)


## Functionalities
- [x]  Real Time Attendence
- [x]  Multiple Simultaneous events supported
- [x]  Live status to admin
- [x]  Live broadcast to each event participants 
- [x]  Proxy check measure by location check


<br>


#### Pre-requisites:
  - Python3

#### Directions to setup in linux 
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
    export STRIPE_API_KEY=12345
```
  - create Database
```
    python
    from app import db
    db.create_all()
```

#### Directions to start

```
    python app.py
```

<br>

## Contributors

- [ Ubaid ](https://github.com/Geek-ubaid/)
- [ Angad ](https://github.com/L04DB4L4NC3R)
- [ Kush ](https://github.com/D-E-F-E-A-T/)


<br>
<br>

<p align="center">
	Made with :heart: by DSC VIT
</p>


