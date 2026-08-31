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

class Gyro:
    def __init__(self):
        self.i2c = None
        self.bno = None
        self.gesamtwinkel = 0.0
        self.letzterwinkel = 0.0

    def start(self):
        """Verbinde zum Sensor und aktiviere den Game Rotation Vector."""
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = BNO08X_I2C(self.i2c)
        time.sleep(0.5)
        if self.bno == None:
            print("init Fehler")
        self.bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR)
        #print("Gyro gestartet")

    @staticmethod
    def quaternionToRoll(qw, qx, qy, qz):
        #Wandelt Quaternion in Roll (Grad) um.
        roll = math.atan2(2.0 * (qw * qz + qx * qy), qw * qw + qx * qx - qy * qy - qz * qz)
        return roll * (180.0 / math.pi)

    def WinkelMessen(self):
        """
        Returns: (winkel, gesamtwinkel)
        """
        if self.bno is None:
            raise RuntimeError("Gyro not started. Call start() before measure().")

        quat_i, quat_j, quat_k, quat_real = self.bno.game_quaternion  # pylint:disable=no-member
        angle = self.quaternionToRoll(quat_real, quat_i, quat_j, quat_k)

        aenderung = angle - self.letzterwinkel
        if aenderung > 180.0:
            aenderung = aenderung - 360.0
        if aenderung < -180.0:
            aenderung = aenderung + 360.0

        self.gesamtwinkel += aenderung
        self.letzterwinkel = angle

        return angle * (-1), self.gesamtwinkel * (-1)
    

if __name__ == '__main__':
    try:
        g = Gyro()
        g.start()
        while True:
            time.sleep(0.3)
            winkel, gesamt = g.WinkelMessen()
            print("winkel:", winkel)
            print("gesamt:", gesamt)

    except KeyboardInterrupt:
        print("Messung vom User gestoppt")