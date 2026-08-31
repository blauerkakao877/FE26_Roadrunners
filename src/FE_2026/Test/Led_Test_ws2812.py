from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import time

if __name__ == "__main__":

    # Initialize the WS2812 strip with 100 leds and SPI channel 0, CE0
    strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=100).get_strip()
    
    i = 0
    
    while i < 3:
        strip.set_pixel_color(0, Color(255, 0, 0))
        strip.show()
        time.sleep(1)
        strip.set_pixel_color(0, Color(0, 255, 0))
        strip.show()
        time.sleep(1)
        i = i+1
    strip.set_all_pixels(Color(0, 0, 0))
    strip.show()