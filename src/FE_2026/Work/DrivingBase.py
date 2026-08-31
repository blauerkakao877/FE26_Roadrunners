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
# Setup GPIO für Button
# -----------------------------
BUTTON_PIN = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)

# -----------------------------
# DrivingBase-Klasse
# -----------------------------
class DrivingBase:
    def __init__(self):
        # I2C und PCA9685 Setup
        self.i2cServo = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2cServo, address=0x7f)
        self.pca.frequency = 50 

        # Servos initialisieren
        self.servo = servo.Servo(self.pca.channels[SERVO_MOTOR_PWM8])

        # DC Motor Setup über SMBus
        self.i2c = smbus.SMBus(1)
        self.dev_addr = 0x40  # Prüfe Adresse für DC Motor Controller
        self.myspeed = 0.0
        
        self.servo_center = 96  # Servo Mitte
        self.servo_limit = 30   # ±30° Lenkbereich
        
        

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
        self.myspeed = int(2000 + speed * (19999 - 2000))
        self.setPWM(DC_MOTOR_INA1, 0)
        self.setPWM(DC_MOTOR_INA2, 19999)
        self.setPWM(DC_MOTOR_PWM1, self.myspeed)

    def stop(self):
        self.setPWM(DC_MOTOR_PWM1, 0)
        self.setPWM(DC_MOTOR_PWM2, 0)

    def anfahren(self):
        anf_count = 0
        anf_speed = 0.0
        while anf_count < 3:
            self.vor(anf_speed)
            anf_speed = anf_speed + 0.1
            anf_count = anf_count + 1
            time.sleep(0.1)

    # -----------------------------
    # Hilfsfunktion: PWM schreiben
    # -----------------------------
    def setPWM(self, channel, value):
        # Direkter PWM-Wert auf PCA9685 schreiben
        self.pca.channels[channel].duty_cycle = int(value * 65535 / 20000)  # Skalierung 0-20000 auf 16-bit

    # -----------------------------
    # Servo auf Winkel setzen
    # -----------------------------
    def servo_angle(self, angle):
        """
        angle : 66-126 Grad
        """
        if angle < 66: angle = 66
        if angle > 126: angle = 126
        self.servo.angle = angle
        #time.sleep(0.5)  # Servo Zeit zum Bewegen
        
    def steer(self, offset):
        #offset: Abweichung zur Mitte in Grad
        # Begrenzen des Offsets
        offset = max(-self.servo_limit, min(self.servo_limit, offset))

        # Berechnung absoluter Winkel
        angle = self.servo_center + offset

        # Safety gegen mechanisches Überschlagen
        angle = max(self.servo_center -30, min(self.servo_center +30, angle))

        self.servo.angle = angle
        #print(f"Lenkwinkel: {angle}° (Offset {offset}°)")

    # ----------------------------------------
    # Steuerbefehle fuer Servo
    # ----------------------------------------
    def gerade(self):
        self.steer(0)

    def nach_links(self):
        self.steer(-25)

    def nach_rechts(self):
        self.steer(+25)
        
    def ausweichen_links(self):
        self.steer(-30)

    def ausweichen_rechts(self):
        self.steer(+30)

    # -----------------------------
    # Button helper methods
    # -----------------------------
    def wait_for_button_press(self, my_delay=0.1):
        print("Waiting for button press...")
        # wait until pressed
        while not GPIO.input(BUTTON_PIN):
            time.sleep(my_delay)
        # debounce
        time.sleep(0.05)
        while GPIO.input(BUTTON_PIN):
            time.sleep(my_delay)
        print("Button pressed.")
        
    def button_pressed(self):
        return GPIO.input(BUTTON_PIN) == 1

# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    try:
        d = DrivingBase()
        
        d.wait_for_button_press()
        d.gerade()
        time.sleep(1.0)
        d.steer(30)
        time.sleep(1.0)
        d.gerade()
        
    except KeyboardInterrupt:
        print("Abbruch")