from ppadb.client import Client as AdbClient
from com.dtmilano.android.viewclient import ViewClient
import PIL
import numpy as np
import cv2
import time
import threading
from threading import Timer
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\e-Kostia.Tokariev2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# ref_Austin = np.array(Image.open('ref_Austin_available.png'))
# ref_in_round = np.array(Image.open("ref_in_round.png"))

ref_Austin = cv2.imread("referals/ref_Austin_available.png", 0)
ref_in_round = cv2.imread("referals/ref_in_round.png", 0)
ref_Okay_victory = cv2.imread("referals/ref_Okay_victory.png", 0)

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)

# device = client.device("9B211FFAZ00480")
device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device=device, serialno=serialno)

# device.shell("input tap 523 1272")

# vc.dump()


def takeAScreen():
    print("take a screen")
    wholeSecreen = device.takeSnapshot(reconnect=True)
    wholeSecreen.crop((1480, 860, 1640, 1020)).save('screens/check_Austin.png', 'PNG') # Check if Austin available
    wholeSecreen.crop((7, 8, 40, 36)).save('screens/check_in_round.png', 'PNG') # check if we are in the round
    wholeSecreen.crop((2060, 106, 2120, 160)).save('screens/fuel_left.png', 'PNG') # check if we are in the round
    wholeSecreen.crop((1103, 880, 1170, 940)).save('screens/Okay_victory.png', 'PNG') # check if we are in the round
    wholeSecreen.save('myscreencap.png', 'PNG')

def screenTap(x, y):
    #device.shell("input tap 1550 950")
    device.shell("input tap " + str(x) + " "+ str(y))

def isAustinAvailable():
    checkAustin = cv2.imread("screens/check_Austin.png", 0)
    result = imageCompare2(ref_Austin, checkAustin)
    print("is Austin Available",result)
    return result

#--- check if we are stil in Round
def isInRound():
    #--- Check if Pause simbol is present
    checkInRound = cv2.imread("screens/check_in_round.png", 0)
    result = imageCompare2(ref_in_round, checkInRound)
    print("is in round", result)
    return result

#--- Check if Victory screen
def isVictory():
    OkayVictory = cv2.imread("screens/Okay_victory.png", 0)
    result = imageCompare2(ref_Okay_victory, OkayVictory)
    print("OkayVictory", result)
    return result

# Compare two images pixel by pixel
def imageCompare2(img1, img2):
    #--- take the absolute difference of the images ---
    res = cv2.absdiff(img1, img2)
    
    #--- convert the result to integer type ---
    res = res.astype(np.uint8)

    #--- find percentage difference based on number of pixels that are not zero ---
    percentage = (np.count_nonzero(res) * 100)/ res.size

    print("image match", abs(percentage - 100))
    
    #--- True if match > 90%
    if percentage < 10:
        return True
    else:
        return False
    
def callMechanic():
    print("call Mechanic")
    screenTap(1400, 950)

# def callMechanicWithDelay(delay):
#     #--- call Mechanic in 200 sec after round beggins.
#     t = Timer(delay, callMechanic)
#     t.start()
    
def gameRound():
    inRound = True

    timer = threading.Timer(210.0, callMechanic)
    timer.start()

    print("wait fo 17s")
    time.sleep(17)

    callMechanic() # call first melee guy to get rage for Austin
    
    time.sleep(2)
    
    takeAScreen()    
    
    while inRound:
        if isAustinAvailable():
            screenTap(1550, 950)
            print("call Austin")
            time.sleep(20)
        else:
            time.sleep(5)
        
        print("wait for Austin")

        if not isInRound():
            inRound = False
            print("Round eneded")
        else:
            print("still in Round")

        takeAScreen()

def getNumber(image):

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    erodeImg = cv2.erode(img,kernel)

    thresh, image_bin = cv2.threshold(erodeImg, 125, 255, cv2.THRESH_BINARY)

    image_final = PIL.Image.fromarray(image_bin)
    image_final.save('teseract.png', 'PNG')

    txt = pytesseract.image_to_string(
        image_final, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
    print(txt)
    #--- conver reconised text to int
    try:
        i = int(txt)
    except ValueError as verr:
        i = 0
    print(i)

    return i

def main():
    takeAScreen()

    hasFuel = True

    while hasFuel:    

        if getNumber(cv2.imread("screens/fuel_left.png")) > 1: 
            
            print("Start new game round")
            screenTap(1130, 750) # press "Resume"
            screenTap(1300, 770) # press "Retry"

            #--- Start new game round
            gameRound()

        if isVictory():
            #--- if victory start new round
            print("Victory screen, press OK")
            screenTap(1130, 900) # press OK

            time.sleep(10)

            print("select location on a map")
            screenTap(1390, 500) # select location on a map

            time.sleep(3)

            takeAScreen()

        else:
            print("Game over")
            hasFuel = False
                       
main()
