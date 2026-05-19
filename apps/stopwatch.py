from LCD_Lib import LCD
import time
from keys import keyA, keyB, keyY, keyX

hours = 0
minutes = 0
seconds = 0
stopwatch = str(hours) + ":" + str(minutes) + ":" + str(seconds)

print(stopwatch)

def stopwatch():
    LCD.fill(0x0000)
    LCD.text("Stopwatch", 60, 40, LCD.green)
    LCD.text(stopwatch, 60, 60, LCD.white)
    LCD.show()
    