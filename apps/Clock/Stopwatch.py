from LCD_Lib import LCD
import time
from keys import keyA, keyB, keyY#, keyX

ms_passed = 0

def displaytime(ms_passed):
    hours = ms_passed // 3600000
    minutes = (ms_passed % 3600000) // 60000
    seconds = (ms_passed % 60000) // 1000
    ms = ms_passed % 1000
    stopwatch = "%02d" % int(hours) + ":" + "%02d" % int(minutes) + ":" + "%02d" % int(seconds) + "." + "%03d" % int(ms)
    LCD.fill(0x0000)
    LCD.text("Stopwatch", 40, 40, LCD.green, 2)
    LCD.text(stopwatch, 20, 120, LCD.white, 2)
    LCD.show()

def load_in():
    LCD.fill(0x0000)
    LCD.text("Stopwatch", 60, 40, LCD.green)
    displaytime(0)
    LCD.show()

def startstopwatch():
    running = True
    offset = 0
    start = time.ticks_ms()
    while True:
        if running == True:
            ms_passed = (time.ticks_diff(time.ticks_ms(), start)) + offset
        displaytime(ms_passed)
        
        if keyY.value() == 0:
            while keyY.value() == 0: pass
            return
        if keyA.value() == 0:
            if running == True:
                offset = ms_passed
                running = False
            else:
                running = True
                start = time.ticks_ms()
                
            while keyA.value() == 0:
                pass
            time.sleep(0.001)
        time.sleep(0.001)
    
def run():
    load_in()
    global hours, minutes, seconds, stopwatch
    while True:
        if keyA.value() == 0:
            startstopwatch()
            displaytime(0)
            while keyA.value() == 0:
                pass
            time.sleep(0.05)
        if keyY.value() == 0:
            while keyY.value() == 0: pass
            return