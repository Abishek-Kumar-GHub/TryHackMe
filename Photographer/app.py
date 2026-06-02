import os
import pycurl
from io import BytesIO
from flask import Flask, send_from_directory, render_template, request, redirect, url_for, Response

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    if request.remote_addr == '127.0.0.1':
        return send_from_directory('private-docs', 'flag.pdf')
    return "Admin interface only available from localhost!!!"

@app.route("/download")
def download():
    file_id = request.args.get('id','')
    server = request.args.get('server','')

    if file_id!='':
        filename = str(int(file_id)) + '.pdf'

        response_buf = BytesIO()
        crl = pycurl.Curl()
        crl.setopt(crl.URL, server + '/public-docs-k057230990384293/' + filename)
        crl.setopt(crl.WRITEDATA, response_buf)
        crl.setopt(crl.HTTPHEADER, ['X-API-KEY: THM{Hello_Im_just_an_API_key}'])
        crl.perform()
        crl.close()
        file_data = response_buf.getvalue()

        resp = Response(file_data)
        resp.headers['Content-Type'] = 'application/pdf'
        resp.headers['Content-Disposition'] = 'attachment'
        return resp
    else:
        return 'No file selected... '

@app.route('/public-docs-k057230990384293/<path:path>')
def public_docs(path):
    return send_from_directory('public-docs', path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8087, debug=True)
