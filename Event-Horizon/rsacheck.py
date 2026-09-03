import urllib.parse, json
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
import xml.etree.ElementTree as ET
import struct

lines = open("texttraffic.txt").read().strip().splitlines()
init_key = b64decode("l86TfRDvvJMtXWxr1PSoh1QlXHnZnLwn+wz+aYy3/s8=")

def aes_decrypt(key, iv_b64, ct_b64):
    iv = b64decode(iv_b64 + '==')
    ct = b64decode(ct_b64 + '==')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    return pt[:-pt[-1]]

def decode_hex_line(line):
    try:
        return bytes.fromhex(line.strip()).decode('utf-8', errors='replace')
    except:
        return None

def parse_pkt(raw):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except:
        pass
    try:
        return json.loads(b64decode(raw + '==').decode('utf-8', errors='replace'))
    except:
        return None

# Step 1: decrypt Line 1 to get RSA public key XML
line1 = decode_hex_line(lines[1])
params = urllib.parse.parse_qs(line1)
pkt1 = parse_pkt(params['data'][0])
rsa_xml = aes_decrypt(init_key, pkt1['IV'], pkt1['EncryptedMessage']).decode('utf-8', errors='replace')
print(f"RSA XML (truncated): {rsa_xml[:200]}")

# Parse RSA public key from XML
root = ET.fromstring(rsa_xml)
mod_b64 = root.find('Modulus').text.strip()
exp_b64 = root.find('Exponent').text.strip()

def b64_to_int(s):
    b = b64decode(s + '==')
    return int.from_bytes(b, 'big')

mod = b64_to_int(mod_b64)
exp = b64_to_int(exp_b64)
pub_key = RSAPublicNumbers(exp, mod).public_key()
print(f"RSA key loaded: {pub_key.key_size} bits")

# Step 2: decrypt Line 2 response with init_key → get RSA-encrypted session key
line2_text = decode_hex_line(lines[2])
marker = '// Hello World! '
after = line2_text.split(marker)[1].split('\n')[0].strip()
pkt2 = parse_pkt(after)
line2_raw = aes_decrypt(init_key, pkt2['IV'], pkt2['EncryptedMessage'])
print(f"\nLine 2 raw decrypted ({len(line2_raw)} bytes): {line2_raw[:64].hex()}")
print(f"As text: {line2_raw[:64]}")

# The decrypted blob IS the new session AES key (server sends it directly or RSA-wrapped)
# Try using it directly as AES key
if len(line2_raw) == 32:
    session_key = line2_raw
    print(f"\nSession AES key (32 bytes): {session_key.hex()}")
elif len(line2_raw) == 16:
    session_key = line2_raw
    print(f"\nSession AES key (16 bytes): {session_key.hex()}")
else:
    print(f"\nUnexpected length {len(line2_raw)} — trying first 32 bytes as key")
    session_key = line2_raw[:32]

# Step 3: try session_key on Line 3+
print("\n=== Decrypting remaining packets with session key ===")
for i, line in enumerate(lines):
    text = decode_hex_line(line)
    if not text:
        continue

    if text.startswith('i='):
        params = urllib.parse.parse_qs(text)
        if 'data' not in params:
            continue
        pkt = parse_pkt(params['data'][0])
        label = "REQUEST"
    elif '<html>' in text and '// Hello World! ' in text:
        after = text.split('// Hello World! ')[1].split('\n')[0].strip()
        if not after:
            continue
        pkt = parse_pkt(after)
        label = "RESPONSE"
    else:
        continue

    if not pkt or not pkt.get('EncryptedMessage') or not pkt.get('IV'):
        continue

    try:
        pt = aes_decrypt(session_key, pkt['IV'], pkt['EncryptedMessage'])
        print(f"\nLine {i} [{label}] Type={pkt.get('Type')} Meta={repr(pkt.get('Meta',''))}")
        print(f"  {pt[:400]}")
    except Exception as e:
        print(f"\nLine {i}: ERROR {e}")
