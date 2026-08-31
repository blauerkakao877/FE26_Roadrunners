#!/bin/bash
#/usr/lib/systemd/system/roadrunner2.service


echo "Roadrunner Start um: "
date
sleep 5s
cd /home/pi/FE_2026/Work

source /home/pi/env/bin/activate
python3 Roadrunner2.py