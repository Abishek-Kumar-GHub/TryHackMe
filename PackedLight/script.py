import base64

key = b"H0t3lSt@ff0NlyK3epS3cr3t!"

cookies = [
    "HA==", "AA==", "BQ==", "Mw==", "Hg==", "ew==", "Og==", "fA==",
    "Fw==", "eQ==", "Ow==", "Fw==", "Pw==", "fA==", "PA==", "Kw==",
    "IA==", "eQ==", "Jg==", "Lw==", "Fw==", "eA==", "Pg==", "LQ==",
    "Gg==", "Fw==", "MQ==", "eA==", "PQ==", "NQ==",
]

flag = ""
for c in cookies:
    encrypted = base64.b64decode(c)
    char = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    flag += char.decode('utf-8')

print(flag)
