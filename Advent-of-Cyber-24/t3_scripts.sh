#!/bin/bash

cat hashes.txt | xargs -I {} -P 4 bash -c 'if 7z x -y -p$(./enc {}) ./secure-storage.zip > /dev/null 2>&1; then echo "password hash: {}"; exit 0; fi'
