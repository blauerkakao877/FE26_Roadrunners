import Cam as C
import cv2

if __name__ == '__main__':
    try:
        frontcam = C.Cam(1)
        frontcam.start()
        backcam = C.Cam(0)
        backcam.start()

        while True:
            bild_f = frontcam.get_image()
            cv2.imshow("original_f", bild_f)
            
            bild_b = backcam.get_image()
            cv2.imshow("original_b", bild_b)

            if cv2.waitKey(1) & 0xFF == 27: #ESC
                break

    except KeyboardInterrupt:
        pass
    
    finally:
        frontcam.stop()
        backcam.stop()
        cv2.destroyAllWindows()
