#!/bin/sh

schedule=$1
params=$2

echo "$schedule python /opt/surflog/scrape.py $params" > /etc/crontabs/root
cat /etc/crontabs/root

crond -l2 -f
