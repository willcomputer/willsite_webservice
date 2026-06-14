#!/bin/bash

python3 -m pip install flask flask_cors psutil gunicorn --break-system-packages --no-warn-script-location

sudo cp webservice.service /etc/systemd/system/webservice.service 

sudo systemctl daemon-reload

sudo systemctl enable webservice

sudo systemctl start webservice

sudo apt install nginx

sudo cp nginx.conf /etc/nginx/conf.d/willsite_webservice.conf

sudo nginx -s reload
