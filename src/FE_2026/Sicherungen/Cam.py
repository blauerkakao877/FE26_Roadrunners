from picamera2 import Picamera2
from threading import Thread
import numpy as np
import cv2
import time
import math
import libcamera

class Cam:
    def __init__(self, Cam_id=0):
        self.Cam_id = Cam_id
        self.picam2 = Picamera2(self.Cam_id)
        self.picam2.preview_configuration.raw.size = (1620, 1232)
        self.picam2.preview_configuration.main.size = (320, 240)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.preview_configuration.align()
        self.picam2.configure("preview")
        self.picam2.set_controls({"Saturation": 1.5})
        self.picam2.set_controls({"Brightness": 0.3})
        self.picam2.set_controls({"Contrast": 1.5})
        self.picam2.set_controls({"FrameRate": 40})

    def start(self):
        self.picam2.start()
        time.sleep(2.0)
        
    def stop(self):
        self.picam2.stop()
        self.picam2.close()
        
    def get_image(self):
        self.frame = self.picam2.capture_array()
        self.image = self.frame[0:240, 0:320]
        return self.image

if __name__ == '__main__':
    try:
        frontcam = Cam(1)
        #backcam = Cam(0)
        frontcam.start()
        #backcam.start()

        while True:
            bild_f = frontcam.get_image()
            #bild_b = backcam.get_image()
            cv2.imshow("original front", bild_f)
            #cv2.imshow("original back", bild_b)

            if cv2.waitKey(1) & 0xFF == 27: #ESC
                print("escaped with keyboard")
                break

    except KeyboardInterrupt:
        pass

    finally:
        frontcam.stop()
        cv2.destroyAllWindows()