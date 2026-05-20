from LCD_Lib import LCD
import time
from keys import keyA, keyB, keyY#, keyX

seconds_passed = 0

def displaytime(seconds_passed):
    hours = seconds_passed // 3600
    minutes = (seconds_passed % 3600) // 60
    seconds = seconds_passed % 60 
    stopwatch = "%02d" % int(hours) + ":" + "%02d" % int(minutes) + ":" + "%02d" % int(seconds)
    LCD.fill(0x0000)
    LCD.text("Stopwatch", 60, 40, LCD.green)
    LCD.text(stopwatch, 80, 120, LCD.white)
    LCD.show()

def load_in():
    LCD.fill(0x0000)
    LCD.text("Stopwatch", 60, 40, LCD.green)
    displaytime(seconds_passed)
    LCD.show()

def startstopwatch():
    running = True
    offset = 0
    start = time.ticks_ms()
    while True:
        if running == True:
            seconds_passed = (time.ticks_diff(time.ticks_ms(), start) // 1000) + offset
        displaytime(seconds_passed)
        
        if keyY.value() == 0:
            return
        if keyA.value() == 0:
            if running == True:
                offset = seconds_passed
                running = False
            else:
                running = True
                start = time.ticks_ms()
                
            while keyA.value() == 0:
                pass
            time.sleep(0.01)
        time.sleep(0.01)
    
def run():
    load_in()
    global hours, minutes, seconds, stopwatch
    while True:
        if keyA.value() == 0:
            startstopwatch()
            displaytime(seconds_passed)
            while keyA.value() == 0:
                pass
            time.sleep(0.05)
        if keyY.value() == 0:
            return