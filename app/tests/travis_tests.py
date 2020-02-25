import requests
import json
payload = {'username':'kush', 'email':'mail@mail83', 'password':'123456'}
headers = {'content-type': 'application/json'}
url = 'https://painhost99.herokuapp.com/user/signup'
r = requests.post(url, data=json.dumps(payload), headers=headers)
assert r.status_code in [200, 208, '200', '208']