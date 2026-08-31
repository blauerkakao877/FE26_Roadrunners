from picamera2 import Picamera2
import numpy as np
import cv2
import time
import math
import libcamera
#import LED as L

picam2 = None
picam2_back = None

blob_detector = None
hindernis_detector = None
o_mask = None
b_mask = None
g_mask = None
r_mask = None
M_mask = None
maskL = None
maskR = None
image = None

hoehe = 200
breite = 320

#colorfilter variables
BL_hue = 0
BU_hue = 179
BL_sat = 0
BU_sat = 255
BL_val = 0
BU_val = 255

OL_hue = 0
OU_hue = 179
OL_sat = 0
OU_sat = 255
OL_val = 0
OU_val = 255

RL_hue = 0
RU_hue = 179
RL_sat = 0
RU_sat = 255
RL_val = 0
RU_val = 255

GL_hue = 0
GU_hue = 179
GL_sat = 0
GU_sat = 255
GL_val = 0
GU_val = 255

ML_hue = 0
MU_hue = 179
ML_sat = 0
MU_sat = 255
ML_val = 0
MU_val = 255



def init(mode="obstacle"):
#Kamera settings
    global picam2
    global picam2_back
    global blob_detector
    global hindernis_detector
    
    if mode == "open":
#blob detector für Linien
        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = 50
        blob_params.maxArea = 10000
        blob_params.filterByCircularity = False
        blob_params.filterByConvexity = False
        blob_params.filterByInertia = False
        
#---------------------------------
        
    elif mode == "obstacle":
#blob detector für Linien
        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = 200
        blob_params.maxArea = 10000
        blob_params.filterByCircularity = False
        blob_params.filterByConvexity = False
        blob_params.filterByInertia = False
        
#init front cam
    picam2 = Picamera2(1)
    picam2.preview_configuration.raw.size = (1620, 1232)
    picam2.preview_configuration.main.size = (320, 240)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    #picam2.set_controls({'HdrMode': libcamera.controls.HdrModeEnum.SingleExposure})
    picam2.set_controls({"Saturation": 1.5})
    picam2.set_controls({"Brightness": 0.3})
    picam2.set_controls({"Contrast": 1.5})
    picam2.set_controls({"FrameRate": 40})
    
#init back cam
    picam2_back = Picamera2(0)
    picam2_back.preview_configuration.raw.size = (1620, 1232)
    picam2_back.preview_configuration.main.size = (320, 240)
    picam2_back.preview_configuration.main.format = "RGB888"
    picam2_back.preview_configuration.align()
    picam2_back.configure("preview")
    picam2_back.set_controls({"Saturation": 1.5})
    picam2_back.set_controls({"Brightness": 0.3})
    picam2_back.set_controls({"Contrast": 1.5})
    picam2_back.set_controls({"FrameRate": 40})


#blob detector für Hindernisse
    hindernis_params = cv2.SimpleBlobDetector_Params()
    hindernis_params.filterByArea = True
    hindernis_params.minArea = 400
    hindernis_params.maxArea = 50000
    hindernis_params.filterByCircularity = False
    hindernis_params.filterByConvexity = False
    hindernis_params.filterByInertia = False

    #erstelle blob detector
    blob_detector = cv2.SimpleBlobDetector_create(blob_params)
    
    #erstelle Hindernis blob detector
    hindernis_detector = cv2.SimpleBlobDetector_create(hindernis_params)
    
    get_colorfilter_data()
    picam2.start()
    picam2_back.start()
    time.sleep(2.0)
    
def get_image():
    global hoehe
    global breite
    global picam2
    global image
    
    frame = picam2.capture_array()
    image = frame[0:240, 0:320]
    hoehe = image.shape[0]
    breite = image.shape[1]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv,image

def get_image_back():
    global hoehe
    global breite
    global picam2_back
    global image
    
    frame = picam2_back.capture_array()
    image = frame[0:240, 0:320]
    hoehe = image.shape[0]
    breite = image.shape[1]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv,image


def ende():
    picam2.stop()
    picam2_back.stop()

    
    
def get_colorfilter_data():
    global BL_hue
    global BU_hue
    global BL_sat
    global BU_sat
    global BL_val
    global BU_val
    
    global OL_hue
    global OU_hue
    global OL_sat
    global OU_sat
    global OL_val
    global OU_val
    
    global RL_hue
    global RU_hue
    global RL_sat
    global RU_sat
    global RL_val
    global RU_val
    
    global GL_hue
    global GU_hue
    global GL_sat
    global GU_sat
    global GL_val
    global GU_val
    
    global ML_hue
    global MU_hue
    global ML_sat
    global MU_sat
    global ML_val
    global MU_val
    
    
    with open("/home/pi/FE_2025/Data/Colorfilter.dat", "r") as myfile:
#lower and upper hue for blue
        line = myfile.readline()
        txt = line.split(",")
        BL_hue = int(txt[0])
        BU_hue = int(txt[1])
#lower and upper saturation for blue
        line = myfile.readline()
        txt = line.split(",")
        BL_sat = int(txt[0])
        BU_sat = int(txt[1])
#lower and upper Value for blue
        line = myfile.readline()
        txt = line.split(",")
        BL_val = int(txt[0])
        BU_val = int(txt[1])
        
#========================================================================    

#lower and upper hue for orange
        line = myfile.readline()
        txt = line.split(",")
        OL_hue = int(txt[0])
        OU_hue = int(txt[1])
#lower and upper saturation for orange
        line = myfile.readline()
        txt = line.split(",")
        OL_sat = int(txt[0])
        OU_sat = int(txt[1])
#lower and upper Value for orange
        line = myfile.readline()
        txt = line.split(",")
        OL_val = int(txt[0])
        OU_val = int(txt[1])
        
#========================================================================
        
#lower and upper hue for red
        line = myfile.readline()
        txt = line.split(",")
        RL_hue = int(txt[0])
        RU_hue = int(txt[1])
#lower and upper saturation for red
        line = myfile.readline()
        txt = line.split(",")
        RL_sat = int(txt[0])
        RU_sat = int(txt[1])
#lower and upper Value for red
        line = myfile.readline()
        txt = line.split(",")
        RL_val = int(txt[0])
        RU_val = int(txt[1])
        
#========================================================================
        
#lower and upper hue for green
        line = myfile.readline()
        txt = line.split(",")
        GL_hue = int(txt[0])
        GU_hue = int(txt[1])
#lower and upper saturation for green
        line = myfile.readline()
        txt = line.split(",")
        GL_sat = int(txt[0])
        GU_sat = int(txt[1])
#lower and upper Value for green
        line = myfile.readline()
        txt = line.split(",")
        GL_val = int(txt[0])
        GU_val = int(txt[1])
        
#========================================================================
        
#lower and upper hue for magenta
        line = myfile.readline()
        txt = line.split(",")
        ML_hue = int(txt[0])
        MU_hue = int(txt[1])
#lower and upper saturation for magenta
        line = myfile.readline()
        txt = line.split(",")
        ML_sat = int(txt[0])
        MU_sat = int(txt[1])
#lower and upper Value for magenta
        line = myfile.readline()
        txt = line.split(",")
        ML_val = int(txt[0])
        MU_val = int(txt[1])
        
#Close file
        myfile.close()
        

#--------------------BLAU------------------------------------
def finde_blau(crop_img):
    global blob_detector
    global b_mask
    global BL_hue
    global BU_hue
    global BL_sat
    global BU_sat
    global BL_val
    global BU_val
    
    lower_color = np.array([BL_hue, BL_sat, BL_val])
    upper_color = np.array([BU_hue, BU_sat, BU_val])
#Suche nach Linien nur direkt vor dem Auto
    mask = cv2.inRange(crop_img, lower_color, upper_color)
    mask = cv2.copyMakeBorder(mask,1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])
    mask = cv2.bitwise_not(mask)
    b_mask = cv2.medianBlur(mask,5)
    blau_keypoints = blob_detector.detect(b_mask)
    
    if len(blau_keypoints) > 0:
        return True
    else:
        return False
    
#--------------------ORANGE--------------------------------
def finde_orange(crop_img):
    global o_mask
    global blob_detector
    global OL_hue
    global OU_hue
    global OL_sat
    global OU_sat
    global OL_val
    global OU_val
    
    lower_color = np.array([OL_hue, OL_sat, OL_val])
    upper_color = np.array([OU_hue, OU_sat, OU_val])
#Suche nach Linien nur direkt vor dem Auto
    mask = cv2.inRange(crop_img, lower_color, upper_color)
    mask = cv2.copyMakeBorder(mask,1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])
    mask = cv2.bitwise_not(mask)
    o_mask = cv2.medianBlur(mask,5)
    orange_keypoints = blob_detector.detect(o_mask)
    
    if len(orange_keypoints) > 0:
        return True
    else:
        return False
    
#--------------------SCHWARZ/WAND--------------------------------
def wand_filter(bgr_img):
    #filter bgr-Image, wand ist dunkel in allen kanälen
    lower_color = np.array([0,0,0])
    upper_color = np.array([120,90,90])
    mask = cv2.inRange(bgr_img, lower_color, upper_color)

    #cv2.imshow("BGR Wand",mask)
    return mask

def waende(bgr_img):
    global hoehe
    global maskL
    global maskR
# finde wände
    crop_image = bgr_img[hoehe - 150:hoehe, 0:320]
    #mask = wand_filterRGB(crop_image)
    mask = wand_filter(crop_image)

# Betrachte linke und rechte Seite getrennt, nur Ausschnitt
    maskL = mask[0:150, 20:159]
    maskR = mask[0:150, 160:300]
    
    #cv2.imshow("histL",maskL)
    #cv2.imshow("histR",maskR)
    
#histogramm, um Höhe der Wände zu bestimmen
    histL = np.sum(maskL, axis=0)
    histR = np.sum(maskR, axis=0)
    maxHistL = np.max(histL)
    maxHistR = np.max(histR)
    #print("maxL :",maxHistL)
    #print("maxR :",maxHistR)
    
    # Seitenkollisionen:
    if maxHistL > 12000:
        kollL = True
    else:
        kollL = False
    
    if maxHistR > 12000:
        kollR = True
    else:
        kollR = False

    #Frontkollision:
    #if maxHistL > 25000 and maxHistR > 25000:
    if maxHistL > 11000 and maxHistR > 11000:
        kollL = True
        kollR = True
    else:
     #Seitenkollisionen:
        if maxHistL > 12000:
            kollL = True
        else:
            kollL = False
        
        if maxHistR > 12000:
            kollR = True
        else:
            kollR = False
        
# Helligkeit links und rechts
    hellL = maxHistL
    hellR = maxHistR
   # print("hellL :",hellL)
   # print("hellR :",hellR)

    return kollL, kollR, hellL, hellR

#--------------------Magenta--------------------------------
def wand_Magenta_filter(hsv_img):
    global M_mask
    global ML_hue
    global MU_hue
    global ML_sat
    global MU_sat
    global ML_val
    global MU_val
    
    lower_color = np.array([ML_hue, ML_sat, ML_val])
    upper_color = np.array([MU_hue, MU_sat, MU_val])
    M_mask = cv2.inRange(hsv_img, lower_color, upper_color)    #cv2.imshow("BGR Wand",mask)
    return M_mask

def waende_Magenta(hsv_img):
    global hoehe
# finde wände
    #crop_image = hsv_img[hoehe - 150:hoehe, 0:320]
    crop_image = hsv_img
    mask = wand_Magenta_filter(crop_image)

# Betrachte linke und rechte Seite getrennt, nur Ausschnitt
    maskL = mask[0:150, 20:159]
    maskR = mask[0:150, 160:300]
    
#histogramm, um Höhe der Wände zu bestimmen
    histL = np.sum(maskL, axis=0)
    histR = np.sum(maskR, axis=0)
    maxHistL = np.max(histL)
    maxHistR = np.max(histR)
    #print("maxL :",maxHistL)
    #print("maxR :",maxHistR)
    
    # Seitenkollisionen:
    if maxHistL > 12000:
        kollL = True
    else:
        kollL = False
    
    if maxHistR > 12000:
        kollR = True
    else:
        kollR = False
    
    #if kollL or kollR:
        #L.led_W1()
    #else:
        #L.led_W0()
        

    # Helligkeit links und rechts
    hellL = maxHistL
    hellR = maxHistR

    return kollL, kollR, hellL, hellR

#--------------------HINDERNISSE--------------------------------
def finde_rot(hsv_img):
    global hindernis_detector
    global r_mask
    global RL_hue
    global RU_hue
    global RL_sat
    global RU_sat
    global RL_val
    global RU_val
    
    lower_color1 = np.array([0, RL_sat, RL_val])
    upper_color1 = np.array([RL_hue, RU_sat, RU_val])
    lower_color2 = np.array([RU_hue, RL_sat, RL_val])
    upper_color2 = np.array([179, RU_sat, RU_val])
    
    #Threshold the HSV image to get only the specified color
    mask1 = cv2.inRange(hsv_img, lower_color1, upper_color1)
    mask2 = cv2.inRange(hsv_img, lower_color2, upper_color2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    mask = cv2.copyMakeBorder(mask,1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])
    mask = cv2.bitwise_not(mask)
    r_mask = cv2.medianBlur(mask,5)
    rot_keypoints = hindernis_detector.detect(r_mask)
    anzahl_keys = len(rot_keypoints)
    s_max = 0
    x = 0
    y = 0
    
    if anzahl_keys > 0:
        i = 0
        while i < anzahl_keys:
            s = rot_keypoints[i].size
            if s > s_max: 
                x = rot_keypoints[i].pt[0]
                y = rot_keypoints[i].pt[1]
                s_max = s
            i = i+1
        
    return x, y, s_max



#-----------------------------------
def finde_gruen(hsv_img):
    global hindernis_detector
    global g_mask
    global GL_hue
    global GU_hue
    global GL_sat
    global GU_sat
    global GL_val
    global GU_val
    
    lower_color = np.array([GL_hue, GL_sat, GL_val])
    upper_color = np.array([GU_hue, GU_sat, GU_val])
    mask = cv2.inRange(hsv_img, lower_color, upper_color)
    mask = cv2.copyMakeBorder(mask,1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])
    mask = cv2.bitwise_not(mask)
    g_mask = cv2.medianBlur(mask,5)
    gruen_keypoints = hindernis_detector.detect(g_mask)
    anzahl_keys = len(gruen_keypoints)
    s_max = 0
    x = 0
    y = 0
    
    if anzahl_keys > 0:
        i = 0
        while i < anzahl_keys:
            s = gruen_keypoints[i].size
            if s > s_max: 
                x = gruen_keypoints[i].pt[0]
                y = gruen_keypoints[i].pt[1]
                s_max = s
            i = i+1
        
    return x, y, s_max

#-------------------
def finde_hindernisse(hsv_img):
    rot_x, rot_y, rot_s = finde_rot(hsv_img)
    gruen_x, gruen_y, gruen_s = finde_gruen(hsv_img)
    
    if rot_s > gruen_s and rot_s > 0:
        #L.led_R1()
        #L.led_G0()
        return round(rot_x), round(rot_y), round(rot_s), "R"
    
    
    elif gruen_s >= rot_s and gruen_s > 0:
        #L.led_G1()
        #L.led_R0()
        return round(gruen_x), round(gruen_y), round(gruen_s), "G"
    
    else:
        #L.led_R0()
        #L.led_G0()
        return 0, 0, 0, "N"
    
    
#=============================MAIN========================================
    
if __name__ == '__main__':
        try:
#=======change challenge mode here=========
            #mode = "open"
            mode = "obstacle"
            init(mode)
            print("running in mode:",mode)
            
            linien_zeit = time.time()
            while True:
                
                hsv_bild, bgr_bild = get_image() #test front camera
                #hsv_bild, bgr_bild = get_image_back() #test back camera
                
                b_linie = finde_blau(hsv_bild)
                o_linie = finde_orange(hsv_bild)
                #cv2.imshow("Maske blau", b_mask)
                links, rechts, hell_L, hell_R = waende(bgr_bild)
                Mlinks, Mrechts, Mhell_L, Mhell_R = waende_Magenta(hsv_bild)
                x_pos, y, s, farbe = finde_hindernisse(hsv_bild)
                x = round(x_pos)
                if b_linie:
                    cv2.line(bgr_bild, (0, 178), (320, 178), (255, 0, 0), 2)
                if o_linie:	
                    cv2.line(bgr_bild, (0, 180), (320, 180), (0, 128, 255), 2)
                if farbe == "R":
                    cv2.line(bgr_bild, (x, 0), (x, hoehe), (0, 0, 255), 2)
                if farbe == "G":
                    cv2.line(bgr_bild, (x, 0), (x, hoehe), (0, 255, 0), 2)
                if links:
                    cv2.line(bgr_bild, (10, 0), (10, hoehe), (128, 128, 128), 2)
                if rechts:
                    cv2.line(bgr_bild, (310, 0), (310, hoehe), (128, 128, 128), 2)
                    
                cv2.imshow("Original", bgr_bild)
                cv2.imshow("Rot_Maske", r_mask)
                cv2.imshow("Gruen_Maske", g_mask)
                cv2.imshow("Blau_Maske", b_mask)
                cv2.imshow("Orange_Maske", o_mask)
                cv2.imshow("Magenta_Maske", M_mask)
                cv2.imshow("Maske_links", maskL)
                cv2.imshow("Maske_rechts",maskR)
                
                
                
                
              #  if time.time() - linien_zeit > 1000:
               #     linie = finde_orange(bild)
               #     if linie == True:
                #        linien_zeit = time.time
               #     cv2.imshow("Maske orange", mask)
                
                

                # Exit loop if 'x' is pressed
                if cv2.waitKey(1) == ord('x'):
                    break
            cv2.destroyAllWindows()
            ende()
            
        except KeyboardInterrupt:
            GPIO.cleanup()

