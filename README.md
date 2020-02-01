<p align="center">
	<img src="https://user-images.githubusercontent.com/30529572/72455010-fb38d400-37e7-11ea-9c1e-8cdeb5f5906e.png" />
	<h2 align="center"> AttendanceApp-Backend  </h2>
	<h4 align="center"> Backend for Real Time Attendence application, which supports mulitple events simultaneously with real time feedback to admin and different admins. It also consists of location feature to detect proxies and many other features. <h4>
</p>
	<h4 align="center"> This is not the complete backend, but all main issues are resolved. Work left is to create some more endpoints for admin, securing of routes and level based access. </h4>
	<h4 align="center"> index.html and index2.html are to test sockets, run them along with server and test their. Keep your dev console open. All things are checked but do testify everything that you think can crash and create issue. Much of left work is written in code but you can create issue for the same. </h4>


[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) [![ForTheBadge built-with-swag](http://ForTheBadge.com/images/badges/built-with-swag.svg)](https://GitHub.com/D-E-F-E-A-T/) [![4U](https://forthebadge.com/images/badges/for-you.svg)](https://github.com/GDGVIT/)
</br>
[![GitHub stars](https://img.shields.io/github/stars/GDGVIT/AttendanceApp-Backend.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/stargazers/)[![GitHub followers](https://img.shields.io/github/followers/D-E-F-E-A-T.svg?style=social&label=Follow&maxAge=2592000)](https://github.com/D-E-F-E-A-T?tab=followers)
[![GitHub repo size](https://img.shields.io/github/repo-size/GDGVIT/AttendanceApp-Backend.svg?logo=git&style=social)](https://github.com/GDGVIT/) [![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/GDGVIT/AttendanceApp-Backend.svg?logo=python&style=social)](https://github.com/GDGVIT/AttendanceApp-Backend)
 [![GitHub last commit](https://img.shields.io/github/last-commit/GDGVIT/AttendanceApp-Backend.svg?color=critical&logo=github&style=social)](https://github.com/GDGVIT/AttendanceApp-Backend/) [![GitHub contributors](https://img.shields.io/github/contributors/GDGVIT/AttendanceApp-Backend.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/graphs/contributors/) [![Open Source Love png3](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
 </br>
 [![GitHub issues](https://img.shields.io/github/issues/GDGVIT/AttendanceApp-Backend.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/issues/) [![GitHub issues-closed](https://img.shields.io/github/issues-closed/GDGVIT/AttendanceApp-Backend.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/issues?q=is%3Aissue+is%3Aclosed)
</br>
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/GDGVIT/AttendanceApp-Backend.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/pull/) [![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/GDGVIT/AttendanceApp-Backend.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend/pull/)
</br>
[![DOCS](https://img.shields.io/badge/Documentation-postman%20docs-green?style=flat-square&logo=appveyor)](https://documenter.getpostman.com/view/9118595/SWTBfJAv)
[![DOCS](https://img.shields.io/badge/Documentation-Testing%20Guide-green?style=flat-square&logo=appveyor)](https://github.com/D-E-F-E-A-T/AttendanceApp-Backend/blob/factored_code_beta/Guides/TestingGuide.md)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
[![HitCount](http://hits.dwyl.io/D-E-F-E-A-T/AttendanceApp-Backend.svg)](http://hits.dwyl.io/D-E-F-E-A-T/AttendanceApp-Backend)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/GDGVIT/AttendanceApp-Backend)

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


<br>
<br>

<p align="center">
	Made with :heart: by DSC VIT
</p>


[![saythanks](https://img.shields.io/badge/say-thanks-ff69b4.svg)](https://github.com/D-E-F-E-A-T) 
[![LinkedIn](https://img.shields.io/static/v1.svg?label=Connect&message=@Kush&color=grey&logo=linkedin&labelColor=blue&style=social)](https://www.linkedin.com/in/kush-choudhary-567b38169?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BDYkgbUGhTniMSRqOUkdN3A%3D%3D) [![Instagram](https://img.shields.io/badge/Instagram-follow-yellow.svg?logo=instagram&logoColor=white)](https://www.instagram.com/kush.philosopher/)
