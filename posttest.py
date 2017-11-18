import json
import urllib.request
import requests

s = requests.Session()
headertype = {"Content-Type": "application/json"}
data={"mac": "hoge", "id": 2}
r = s.post("http://192.168.11.20/test", json.dumps(data), headers=headertype)
