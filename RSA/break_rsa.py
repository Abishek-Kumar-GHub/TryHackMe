from gmpy2 import isqrt
from math import lcm
from Crypto.PublicKey import RSA

def fermat_factorize(n):
    a = isqrt(n)
    if a * a == n:
        return int(a), int(a)
    while True:
        a += 1
        bsq = a * a - n
        b = isqrt(bsq)
        if b * b == bsq:
            break
    return int(a + b), int(a - b)

pub = RSA.import_key(open('id_rsa.pub').read())
n, e = pub.n, pub.e

print("[*] Factorizing n (this may take a moment)...")
p, q = fermat_factorize(n)
print(f"[+] p = {p}")
print(f"[+] q = {q}")
print(f"[+] |p - q| = {abs(p - q)}")

d = pow(e, -1, lcm(p - 1, q - 1))
priv = RSA.construct((n, e, d, p, q))
pem = priv.export_key("PEM").decode()

with open("id_rsa_cracked", "w") as f:
    f.write(pem)

print("[+] Private key saved to id_rsa_cracked")
print(pem)
