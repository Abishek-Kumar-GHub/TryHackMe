#!/usr/bin/env python3
"""
get_flag.py — Open the recovered KeePass database and print all entries + flag.

Run from your Extractedroom folder:
    pip install pykeepass
    python3 get_flag.py
"""
import pykeepass

KDBX     = "recovered.kdbx"
PASSWORD = "?NoWaYIcanF0rGetThis123"

kp = pykeepass.PyKeePass(KDBX, password=PASSWORD)

print(f"[+] Opened {KDBX} with password: {PASSWORD}\n")
print("=" * 50)

for e in kp.entries:
    print(f"  Title   : {e.title}")
    print(f"  Username: {e.username}")
    print(f"  Password: {e.password}")
    if e.notes: print(f"  Notes   : {e.notes}")
    if e.url:   print(f"  URL     : {e.url}")
    print()

print("=" * 50)
print("\nAnswers:")
print("  Q1 - Initial part of password : NoWaYIcanF0rGetThis123")
print("  Q2 - Missing character        : ?")
print("  Q3 - Flag                     : THM{B3tt3r_Upd4t3_Y0ur_K33p455}")
