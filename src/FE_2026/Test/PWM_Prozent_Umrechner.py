import math

speed = 0

def drive(speed):
    myspeed = int(7000 + speed * (19999 - 7000)) #rechne um
    
    return myspeed

if __name__ == "__main__":
    try:
        print("drive TEST")
        speed = drive(0.31)
        print("speed =", speed)

    except KeyboardInterrupt:
        print("Abbruch")