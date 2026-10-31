#!/bin/bash

sleep 10s

echo "Lidar_logger Start um: "
date
cd /home/pi/FE_2026/Work
source /home/pi/env/bin/activate

 python3 lidar_logger.py