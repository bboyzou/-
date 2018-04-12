#!/bin/bash
check_results=`ps aux | egrep "^nobody .*? protect.py" | cut -d " "  -f6`
if [[ $check_results != "" ]] 
then 
     echo $check_results | kill
else 
    echo "no protect.py running"
 fi
