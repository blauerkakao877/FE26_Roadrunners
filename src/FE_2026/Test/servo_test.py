import time
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# -----------------------------
# Hardware Setup
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x7f)  # Prüfe die Adresse
pca.frequency = 50  # Standard für Servos

# -----------------------------
# Servo initialisieren
# -----------------------------
SERVO_MOTOR_PWM7 = 10
my_servo = servo.Servo(pca.channels[SERVO_MOTOR_PWM7])

# -----------------------------
# Servo auf festen Winkel setzen
# -----------------------------
angle = 32  # Beispiel: Mittelstellung
print(f"Setze Servo auf {angle}°...")
my_servo.angle = angle
time.sleep(0.5)  # Servo Zeit zum Bewegen
print("Fertig!")
