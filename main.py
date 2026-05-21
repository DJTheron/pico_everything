from LCD_Lib import LCD
from time import sleep
import os
import sys
from keys import keyA, keyB, keyX, keyY, up, down, left, right, ctrl

sys.path.append('apps')


def displaycard(title):
    LCD.fill(0x0000)
    if title.endswith('.py'):
        title = title.replace('.py', '')
    LCD.text(title, 60, 115, LCD.green)
    LCD.show()

def cards(cards, selected):
    displaycard(cards[selected])
    while True:
        if left.value() == 0:
            selected += 1
            if selected >= len(cards):
                selected = 0
            displaycard(cards[selected])
            while left.value() == 0:
                pass
            sleep(0.05)
        
        
        if right.value() == 0:
            selected -= 1
            if selected < 0:
                selected = len(cards) - 1
            displaycard(cards[selected])
            while right.value() == 0:
                pass
            sleep(0.05)

        if keyA.value() == 0:
            apptoopen = __import__(cards[selected].replace('.py', ''))
            apptoopen.run()
            displaycard(cards[selected])
            while keyA.value() == 0:
                pass
            sleep(0.05)

def main():
    LCD.fill(0x0000)
    LCD.show()
    apps = os.listdir('apps')
    cards(apps, 0)
    
 
if __name__=='__main__':
    main()
