from LCD_Lib import LCD
import time
from keys import keyA, keyY

# add a thing of stats of total work time, saves to file,, cool feature

worktime = 25 * 60 * 1000
breaktime = 5 * 60 * 1000

def displaytime(s_passed, work):
    minutes = (s_passed % 3600000) // 60000
    seconds = (s_passed % 60000) // 1000
    timeleft = "%02d" % int(minutes) + ":" + "%02d" % int(seconds)
    LCD.fill(0x0000)
    if work:
        LCD.text("Work Time", 60, 40, LCD.green, 2)
    else:
        LCD.text("Break Time", 60, 40, LCD.blue, 2)
    LCD.text(timeleft, 80, 120, LCD.white, 2)
    LCD.show()
    
def pomo():
    start = time.ticks_ms() #type: ignore
    working = True
    while True:
        while time.ticks_diff(time.ticks_ms(), start) < worktime and working == True:
            s_left = worktime - time.ticks_diff(time.ticks_ms(), start)
            displaytime(s_left, working)
            time.sleep(0.267)
            if keyY.value() == 0:
                while keyY.value() == 0: pass
                return
            
        if time.ticks_diff(time.ticks_ms(), start) >= worktime:
            working = False
            start = time.ticks_ms()
            
        while working == False:
            working = False
            s_left = time.ticks_diff(breaktime, time.ticks_diff(time.ticks_ms(), start))
            
            if time.ticks_diff(time.ticks_ms(), start - worktime) >= breaktime:
                working = True
                start = time.ticks_ms()
                
            if keyY.value() == 0:
                while keyY.value() == 0: pass
                return
            
            displaytime(s_left, working)
            time.sleep(0.267)
            
        if keyY.value() == 0:
            while keyY.value() == 0: pass
            return
        
def load_in():
    LCD.fill(0x0000)
    LCD.text("Pomodoro", 60, 40, LCD.green, 2)
    displaytime(worktime, True)
    LCD.show()
    
def run():
    load_in()
    while True:
        if keyA.value() == 0:
            pomo()
            displaytime(worktime, True)
            while keyA.value() == 0: pass
            time.sleep(0.05)
        if keyY.value() == 0:
            while keyY.value() == 0: pass
            return