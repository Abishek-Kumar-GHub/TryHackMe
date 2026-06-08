import re
import requests

url = "http://10.49.140.239"
username = "natalie"
password = "sk8board"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": f"{url}/login",
}

def calculate(num1, op, num2):
    ops = {'*': num1 * num2, '+': num1 + num2, '-': num1 - num2, '/': num1 / num2}
    return ops[op]

session = requests.Session()

# Step 1 — GET login page to grab captcha
print("[*] Fetching login page...")
get_response = session.get(f"{url}/login", headers=headers)
print(f"[*] Status: {get_response.status_code}")

match = re.search(r"(\d+)\s*([\+\-\*/])\s*(\d+)", get_response.text)
if not match:
    print("[-] No captcha found on login page. Trying without it...")
    captcha_answer = None
else:
    num1, op, num2 = int(match.group(1)), match.group(2), int(match.group(3))
    captcha_answer = calculate(num1, op, num2)
    print(f"[*] Captcha: {num1} {op} {num2} = {captcha_answer}")

# Step 2 — POST with credentials + captcha
data = {"username": username, "password": password}
if captcha_answer is not None:
    data["captcha"] = captcha_answer

print("[*] Logging in...")
response = session.post(f"{url}/login", headers=headers, data=data, allow_redirects=True)
print(f"[*] Landed on: {response.url} (size: {len(response.content)})")

if "/login" in response.url:
    print("[-] Login failed — still on login page.")
    print("[*] Page snippet:")
    print(response.text[:500])
    exit(1)

print("[+] Login successful!")

# Step 3 — Save landing page
with open("landing.html", "w") as f:
    f.write(response.text)
print("[+] Saved to landing.html")
