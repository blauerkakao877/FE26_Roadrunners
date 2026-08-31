import time
from enum import Enum
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver

from Color_defs import *

class Led_dots(Enum):
    vl = 0
    vr = 1
    hl = 2
    hr = 3


class Led:
    """
    class to use the LEDs
    """
    strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=100).get_strip()

    def on(self, num, color):
        self.strip.set_pixel_color(num, color)
        self.strip.show()
        
    def all_on(self, color):
        self.strip.set_pixel_color(0, color)
        self.strip.set_pixel_color(1, color)
        self.strip.set_pixel_color(2, color)
        self.strip.set_pixel_color(3, color)
        self.strip.show()
        
    def off(self, num):
        self.strip.set_pixel_color(num, Color(0,0,0))
        self.strip.show()

    def all_off(self):
        self.strip.set_all_pixels(Color(0,0,0))
        self.strip.show()
            
    def B(self):
        self.strip.set_pixel_color(2, Color(0,0,255))
        self.strip.set_pixel_color(3, Color(0,0,255))
        self.strip.show()
        
    def O(self):
        self.strip.set_pixel_color(2, Color(255,165,0))
        self.strip.set_pixel_color(3, Color(255,165,0))
        self.strip.show()
        
    def all_W(self):
        self.strip.set_all_pixels(Color(255,255,255))
        self.strip.show()
        
    def stop(self):
        self.strip.set_all_pixels(Color(255,0,0))
        self.strip.show()
        
    def booting(self):
        i = 0
        self.strip.set_all_pixels(Color(0,0,0))
        self.strip.show()
        
        for led_num in range(4):
            self.strip.set_pixel_color(led_num, Color(255,255,0))
            self.strip.show()
            time.sleep(0.25)
            self.strip.set_pixel_color(led_num, Color(0,0,0))
            self.strip.show()
            
        time.sleep(0.2)
        
        while i < 3:
            self.strip.set_all_pixels(Color(255,255,0))
            self.strip.show()
            time.sleep(0.3)
            self.strip.set_all_pixels(Color(0,0,0))
            self.strip.show()
            time.sleep(0.1)
            i = i+1
            
        self.strip.set_all_pixels(Color(0,0,0))
        self.strip.show()
        
    def waiting(self):
        self.strip.set_all_pixels(Color(0, 255, 0))
        self.strip.show()
    
    def waiting_S(self):
        self.strip.set_pixel_color(0, Color(0,255,0))
        self.strip.set_pixel_color(1, Color(0,255,0))
        self.strip.set_pixel_color(2, Color(255,0,0))
        self.strip.set_pixel_color(3, Color(255,0,0))
        self.strip.show()
        
    def waiting_M(self):
        self.strip.set_pixel_color(0, Color(0,255,0))
        self.strip.set_pixel_color(1, Color(0,255,0))
        self.strip.set_pixel_color(2, Color(255,165,0))
        self.strip.set_pixel_color(3, Color(255,165,0))
        self.strip.show()
        
    def waiting_F(self):
        self.strip.set_pixel_color(0, Color(0,255,0))
        self.strip.set_pixel_color(1, Color(0,255,0))
        self.strip.set_pixel_color(2, Color(0,0,255))
        self.strip.set_pixel_color(3, Color(0,0,255))
        self.strip.show()
        
    def countdown3(self):
        self.strip.set_all_pixels(Color(0,0,0))
        self.strip.show()
        self.strip.set_pixel_color(0, Color(255,0,0))
        self.strip.show()
        time.sleep(1.0)
        self.strip.set_pixel_color(0, Color(0,0,0))
        self.strip.set_pixel_color(1, Color(255,0,0))
        self.strip.show()
        time.sleep(1.0)
        self.strip.set_pixel_color(1, Color(0,0,0))
        self.strip.set_pixel_color(2, Color(255,0,0))
        self.strip.show()
        time.sleep(0.7)
        self.strip.set_pixel_color(2, Color(0,0,0))
        self.strip.set_all_pixels(Color(0,355,0))
        self.strip.show()
        time.sleep(0.3)
        self.strip.set_all_pixels(Color(0,0,0))
        self.strip.show()
        
        
        
        

if __name__ == "__main__":
    led = Led()

    led.countdown3()
    