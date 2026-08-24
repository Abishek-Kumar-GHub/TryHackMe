import requests, hmac, hashlib, time

BASE     = "http://gla2.thm"
SIGN_KEY = b"gla2_crew_sign_v1_2f9b6c8ad14e"

def sign(msg):
    return hmac.new(SIGN_KEY, msg.encode(), hashlib.sha256).hexdigest()

def derive_staff_role(stash_order):
    s = f"heat5_stash{stash_order[0]}_stash{stash_order[1]}_stash{stash_order[2]}_vault"
    return hashlib.sha1(s.encode()).hexdigest()

def checkpoint(session_id, step, token, delay=7):
    print(f"[*] waiting {delay}s before '{step}'...")
    time.sleep(delay)
    sig = sign(f"{session_id}|{step}|{token}")
    r = requests.post(f"{BASE}/checkpoint", json={
        "session_id": session_id,
        "step":       step,
        "token":      token,
        "sig":        sig
    })
    print(f"    {r.status_code} {r.text[:200]}")
    d = r.json()
    if "token" in d:
        token = d["token"]
        print(f"    token updated -> {token}")
    return token, d

# Step 1: session
print("[*] POST /session")
r = requests.post(f"{BASE}/session", json={})
print(f"    {r.status_code} {r.text}")
data        = r.json()
session_id  = data["session_id"]
token       = data["token"]
stash_order = list(data.get("stash_order", [0,1,2]))
print(f"    session_id={session_id}")
print(f"    token={token}")
print(f"    stash_order={stash_order}")

# Step 2: checkpoints in order with delays
steps = ["heat5"] + [f"stash{i}" for i in stash_order] + ["vault"]
print(f"\n[*] Steps to complete: {steps}")

for step in steps:
    token, d = checkpoint(session_id, step, token, delay=7)
    if "error" in d:
        print(f"    [!] ERROR: {d}")
        # if too_fast, wait longer and retry
        if d.get("error") == "too_fast":
            wait = int(d.get("need", 10)) + 2
            print(f"    [!] Retrying after {wait}s")
            time.sleep(wait)
            token, d = checkpoint(session_id, step, token, delay=0)

# Step 3: claim
staff_role = derive_staff_role(stash_order)
print(f"\n[*] DeriveStaffRole => {staff_role}")

for role in ["player", staff_role]:
    print(f"\n[*] POST /claim (role={role})")
    sig = sign(f"{session_id}|claim|{token}")
    r = requests.post(f"{BASE}/claim", json={
        "session_id": session_id,
        "role":       role,
        "token":      token,
        "sig":        sig
    })
    print(f"    {r.status_code} {r.text}")
    if "flag" in r.text:
        print("\n[+] FLAG OBTAINED!")
        break
