#!/bin/bash

if [ ! -f /tmp/foo.txt ]; then
    echo "\`\`ssl-proxy\`\` file is not found - redownloading it now!"
    curl -LJ "https://getbin.io/suyashkumar/ssl-proxy?os=linux" | tar xvz
fi

while true
do
  ./ssl-proxy-linux-amd64 -from 0.0.0.0:443 -to 0.0.0.0:8501 -redirectHTTP -domain=repscoreportal.org &
  kill $( jobs -p )
  sleep 7776000  # sleep for 90 days before regenerating new SSL certificates
done
