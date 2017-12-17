import json
import requests

endpoint = "http://192.168.11.20/test"
s = requests.Session()
headertype = {"Content-Type": "application/json"}
data = {"id": 2, "mac": "hoge", }
r = s.post(endpoint, json.dumps(data), headers=headertype)
