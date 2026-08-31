# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import busio
import math
from adafruit_bno08x import BNO_REPORT_GAME_ROTATION_VECTOR
from adafruit_bno08x.i2c import BNO08X_I2C

bno = None
i2c = None
gesamtwinkel = 0.0
letzterwinkel = 0.0

def gyro_start():
    global i2c
    global bno
    i2c = busio.I2C(board.SCL, board.SDA)
    bno = BNO08X_I2C(i2c)
    bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
    print("gyro startet")


def quaternionToRoll(qw, qx, qy, qz):
    roll = math.atan2(2.0 * (qw * qz + qx * qy), qw * qw + qx * qx - qy * qy - qz * qz)
# Drehung nach links positiv nach rechts negativ
    return roll * (180.0 / math.pi)

def Winkelmessen():
    global gesamtwinkel
    global letzterwinkel
    global bno
    quat_i, quat_j, quat_k, quat_real = bno.game_quaternion  # pylint:disable=no-member
    angle = quaternionToRoll(quat_real, quat_i, quat_j, quat_k)
    aenderung = angle - letzterwinkel
    if aenderung > 180.0:
        aenderung = aenderung - 360.0
        
    if aenderung < -180.0:
        aenderung = aenderung + 360.0
        
    gesamtwinkel = gesamtwinkel + aenderung
    letzterwinkel = angle 

    return angle*(-1), gesamtwinkel*(-1)



if __name__ == '__main__':
    try:
        gyro_start()
        while True:
            time.sleep(0.5)

           # print("Rotation Vector Quaternion:")
           # quat_i, quat_j, quat_k, quat_real = bno.game_quaternion  # pylint:disable=no-member
           # print(
            #    "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real)
           # )
           # print("")
            
            
            
           # angle = quaternionToRoll(quat_real, quat_i, quat_j, quat_k)
           
            winkel, gesamt = Winkelmessen()
           
            print("winkel: ", winkel)
            print("gesamt: ",gesamt)
            
            
           
           
            
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        GPIO.cleanup()
