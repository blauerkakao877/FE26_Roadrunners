import time
import math
import smbus

# Raspi PCA9685 16-Channel PWM Servo Driver
# Registers/etc.
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
MODE1              = 0x00
MODE2              = 0x01
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALLLED_ON_L        = 0xFA
ALLLED_ON_H        = 0xFB
ALLLED_OFF_L       = 0xFC
ALLLED_OFF_H       = 0xFD
  
SERVO_MOTOR_PWM3        = 6
SERVO_MOTOR_PWM4        = 7
SERVO_MOTOR_PWM5        = 8
SERVO_MOTOR_PWM6        = 9
SERVO_MOTOR_PWM7        = 10
SERVO_MOTOR_PWM8        = 11

DC_MOTOR_PWM1        = 0
DC_MOTOR_INA1        = 2
DC_MOTOR_INA2        = 1

DC_MOTOR_PWM2        = 5
DC_MOTOR_INB1        = 3
DC_MOTOR_INB2        = 4

class PCA9685:
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        self.dev_addr = 0x7f
        self.write_reg(MODE1, 0x00)

    def write_reg(self, reg, value):
        self.i2c.write_byte_data(self.dev_addr, reg, value)

    def read_reg(self, reg):
        res = self.i2c.read_byte_data(self.dev_addr, reg)
        return res

    def setPWMFreq(self, freq):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.read_reg(MODE1)
        print('lodmode:',oldmode)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write_reg(MODE1, newmode)        # go to sleep
        self.write_reg(PRESCALE, int(math.floor(prescale)))
        self.write_reg(MODE1, oldmode)
        time.sleep(0.005)
        self.write_reg(MODE1, oldmode | 0x80)  # 0x80

    def setPWM(self, ch, on, off):
        self.write_reg(LED0_ON_L+4*ch, on & 0xFF)
        self.write_reg(LED0_ON_H+4*ch, on >> 8)
        self.write_reg(LED0_OFF_L+4*ch, off & 0xFF)
        self.write_reg(LED0_OFF_H+4*ch, off >> 8)

    def setServoPulse(self, channel, pulse):
       pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us=20ms
       self.setPWM(channel, 0, int(pulse))

if __name__=='__main__':
    """for servo motor:
    the high part of the pulse is T
    T = 0.5ms => 0   degree
    T = 1.0ms => 45  degree
    T = 1.5ms => 90  degree
    T = 2.0ms => 135 degree
    T = 2.5ms => 180 degree
  
    for 2 channel DC motor driven by TB6612FNG
    IN1   IN2  PWM  STBY  OUT1   OUT2      MODE
    H     H   H/L   H     L      L    short brake
    L     H    H    H     L      H       CCW
    L     H    L    H     L      L    short brake
    H     L    H    H     H      L       CW
    H     L    L    H     L      L    short brake
    L     L    H    H    OFF    OFF      STOP
    H/L   H/L  H/L   L    OFF    OFF    standby
    """
    pwm = PCA9685()
    pwm.setPWMFreq(50) # for servo

    while True:
        """The following code is applied to
        DC motor control
        """
        pwm.setServoPulse(DC_MOTOR_PWM1,8000) # for TB6612 set speed min:8000 max:19999
        # CCW
        pwm.setServoPulse(DC_MOTOR_INA1,0) # set INA1 L 
        pwm.setServoPulse(DC_MOTOR_INA2,19999) # set INA2 H
        print("M1 rotate")
        time.sleep(2)
        # CW
        pwm.setServoPulse(DC_MOTOR_INA1,19999) # set INA1 H 
        pwm.setServoPulse(DC_MOTOR_INA2,0) # set INA2 L
        print("M1 rotate opposite")
        time.sleep(2)
        pwm.setServoPulse(DC_MOTOR_PWM1,0) # for TB6612 set speed to 0, stop        
        print("M1 stop")
        time.sleep(2)
      
        """pwm.setServoPulse(DC_MOTOR_PWM2,15000) # for TB6612 set speed
        # CCW
        pwm.setServoPulse(DC_MOTOR_INB1,0) # set INB1 L 
        pwm.setServoPulse(DC_MOTOR_INB2,19999) # set INB2 H
        print("M2 rorate")
        time.sleep(2)
        # CW
        pwm.setServoPulse(DC_MOTOR_INB1,19999) # set INB1 H 
        pwm.setServoPulse(DC_MOTOR_INB2,0) # set INB2 L
        print("M2 rorate opposite")
        time.sleep(2)
        pwm.setServoPulse(DC_MOTOR_PWM2,0) # for TB6612 set speed to 0, stop
        print("M2 stop")
        time.sleep(2)
        
      
        #The following code is applied to
        #  servo motor control
        """
        """
        print("servo ccw")
        for i in range(500,2500,10):# start 500, end 2500, step is 10  
           #pwm.setServoPulse(SERVO_MOTOR_PWM3,i)
           pwm.setServoPulse(SERVO_MOTOR_PWM8,i)  
           time.sleep(0.02)    
        print("servo cw")
        for i in range(2500,500,-10):
           #pwm.setServoPulse(SERVO_MOTOR_PWM3,i)
           pwm.setServoPulse(SERVO_MOTOR_PWM8,i) 
           time.sleep(0.02)  """

