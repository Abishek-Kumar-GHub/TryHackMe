from scapy.all import rdpcap, TCP
import re, os

os.makedirs("frames", exist_ok=True)

packets = rdpcap("security-footage-1648933966395.pcap")

# Collect all TCP payloads
raw = b""
for pkt in packets:
    if pkt.haslayer(TCP) and pkt[TCP].payload:
        raw += bytes(pkt[TCP].payload)

# Carve JPEGs by magic bytes
frames = re.findall(b'\xff\xd8\xff.*?\xff\xd9', raw, re.DOTALL)

for i, frame in enumerate(frames):
    with open(f"frames/frame_{i:04d}.jpg", "wb") as f:
        f.write(frame)

print(f"Extracted {len(frames)} frames")
