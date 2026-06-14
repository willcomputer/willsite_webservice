#!/bin/bash

sudo cp webservice.service /etc/systemd/system/webservice.service 

sudo systemctl daemon-reload
sudo systemctl enable webservice
sudo systemctl start webservice