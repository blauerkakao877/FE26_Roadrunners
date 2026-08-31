import time
import smbus
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import RPi.GPIO as GPIO

# -----------------------------
# Kanäle
# -----------------------------
SERVO_MOTOR_PWM3 = 6
SERVO_MOTOR_PWM4 = 7
SERVO_MOTOR_PWM5 = 8
SERVO_MOTOR_PWM6 = 9
SERVO_MOTOR_PWM7 = 10
SERVO_MOTOR_PWM8 = 11

DC_MOTOR_PWM1 = 0
DC_MOTOR_INA1 = 2
DC_MOTOR_INA2 = 1
DC_MOTOR_PWM2 = 5
DC_MOTOR_INB1 = 3
DC_MOTOR_INB2 = 4
# -----------------------------
# DrivingBase-Klasse
# -----------------------------
class DrivingBase:
    def __init__(self):
        # I2C und PCA9685 Setup
        self.i2cServo = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2cServo, address=0x7f)
        self.pca.frequency = 50 

        # DC Motor Setup über SMBus
        self.i2c = smbus.SMBus(1)
        self.dev_addr = 0x40  # Prüfe Adresse für DC Motor Controller
        self.myspeed = 0.0
    # -----------------------------
    # DC Motor-Funktionen
    # -----------------------------
    def vor(self, speed):
        speed = max(0.0, min(1.0, speed))
        self.myspeed = int(2000 + speed * (19999 - 2000))
        self.setPWM(DC_MOTOR_INA1, 19999)
        self.setPWM(DC_MOTOR_INA2, 0)
        self.setPWM(DC_MOTOR_PWM1, self.myspeed)

    def ruck(self, speed):
        speed = max(0.0, min(1.0, speed))
        self.myspeed = int(7000 + speed * (19999 - 7000))
        self.setPWM(DC_MOTOR_INA1, 0)
        self.setPWM(DC_MOTOR_INA2, 19999)
        self.setPWM(DC_MOTOR_PWM1, self.myspeed)

    def stop(self):
        self.setPWM(DC_MOTOR_PWM1, 0)
        self.setPWM(DC_MOTOR_PWM2, 0)

    # -----------------------------
    # Hilfsfunktion: PWM schreiben
    # -----------------------------
    def setPWM(self, channel, value):
        # Direkter PWM-Wert auf PCA9685 schreiben
        self.pca.channels[channel].duty_cycle = int(value * 65535 / 20000)  # Skalierung 0-20000 auf 16-bit

# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    try:
        d = DrivingBase()
        
        d.stop()
        print("NOTSTOP ausgeführt!!!")
    except KeyboardInterrupt:
        print("Abbruch")
