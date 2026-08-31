import cv2
import time
import numpy as np
from Cam import Cam

FILE = "/home/pi/FE_2026/Data/Colorfilter.dat"

def nothing(x):
    pass

# ------------------ Daten lesen ------------------
def read_data():
    try:
        with open(FILE, "r") as f:
            windows = list(colors.keys())
            lines = [line.strip() for line in f if line.strip() != ""]

            i = 0
            for w in windows:
                for name in ["Hue", "Sat", "Val"]:
                    if i >= len(lines):
                        continue
                    lower, upper = map(int, lines[i].split(","))
                    cv2.setTrackbarPos(f"Lower {name}", w, lower)
                    cv2.setTrackbarPos(f"Upper {name}", w, upper)
                    i += 1
    except:
        print("No file → using defaults")

# ------------------ Daten schreiben ------------------
def write_data():
    lines = []
    for w in colors:
        for name in ["Hue", "Sat", "Val"]:
            l = cv2.getTrackbarPos(f"Lower {name}", w)
            u = cv2.getTrackbarPos(f"Upper {name}", w)
            lines.append(f"{l},{u}")

    with open(FILE, "w") as f:
        f.write("\n".join(lines))

    print("saved")

# ------------------ Maske verbessern ------------------
def clean_mask(mask):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.medianBlur(mask, 5)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

# ------------------ Farbe erkennen ------------------
def detect_color(hsv, w):
    lH = cv2.getTrackbarPos("Lower Hue", w)
    uH = cv2.getTrackbarPos("Upper Hue", w)
    lS = cv2.getTrackbarPos("Lower Sat", w)
    uS = cv2.getTrackbarPos("Upper Sat", w)
    lV = cv2.getTrackbarPos("Lower Val", w)
    uV = cv2.getTrackbarPos("Upper Val", w)

    # --- ROT SPEZIAL ---
    if w == "Red Detection":
        lower1 = np.array([0, lS, lV])
        upper1 = np.array([lH, uS, uV])

        lower2 = np.array([uH, lS, lV])
        upper2 = np.array([179, uS, uV])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)

        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower = np.array([lH, lS, lV])
        upper = np.array([uH, uS, uV])
        mask = cv2.inRange(hsv, lower, upper)

    return clean_mask(mask)

# ------------------ Wall Detection ------------------
def detect_wall(hsv):
    lV = cv2.getTrackbarPos("Lower Val", "Wall Detection")
    uV = cv2.getTrackbarPos("Upper Val", "Wall Detection")

    lower = np.array([0, 0, lV])
    upper = np.array([179, 255, uV])

    return clean_mask(cv2.inRange(hsv, lower, upper))

# ------------------ Trackbars ------------------
colors = {
    "Blue Detection": (90, 130),
    "Orange Detection": (5, 25),
    "Red Detection": (10, 170),
    "Green Detection": (35, 85),
    "Magenta Detection": (125, 160)
}

for w, (lh, uh) in colors.items():
    cv2.namedWindow(w)
    cv2.createTrackbar("Lower Hue", w, lh, 179, nothing)
    cv2.createTrackbar("Upper Hue", w, uh, 179, nothing)
    cv2.createTrackbar("Lower Sat", w, 80, 255, nothing)
    cv2.createTrackbar("Upper Sat", w, 255, 255, nothing)
    cv2.createTrackbar("Lower Val", w, 80, 255, nothing)
    cv2.createTrackbar("Upper Val", w, 255, 255, nothing)

# Wall Fenster
cv2.namedWindow("Wall Detection")
cv2.createTrackbar("Lower Val", "Wall Detection", 0, 255, nothing)
cv2.createTrackbar("Upper Val", "Wall Detection", 80, 255, nothing)

read_data()

# ------------------ Kamera ------------------
cam_f = Cam(1)
cam_f.start()
time.sleep(1.0)

print("s = save | x/esc = exit")

# ------------------ Loop ------------------
while True:
    bgr = cam_f.get_image()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    cv2.imshow("Original", bgr)

    for w in colors:
        mask = detect_color(hsv, w)
        cv2.imshow(w, mask)

    wall = detect_wall(hsv)
    cv2.imshow("Wall Detection", wall)

    key = cv2.waitKey(1) & 0xFF

    if key == 27 or key == ord('x'):
        break
    elif key == ord('s'):
        write_data()
        time.sleep(0.2)

cv2.destroyAllWindows()