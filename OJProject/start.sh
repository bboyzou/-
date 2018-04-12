#!/bin/bash
kill `ps aux | egrep "^nobody .*? protect.py" | cut -d " "  -f6`
nohup python protect.py &
