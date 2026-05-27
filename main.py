from LCD_Lib import LCD
from time import sleep
import os
import sys
from keys import keyA, keyB, keyX, keyY, up, down, left, right, ctrl

sys.path.append('apps')


def displaycard(title, path=''):
    path = '>' + 'apps/' + path
    LCD.fill(0x0000)
    LCD.text(title.replace('.py', ''), 60, 115, LCD.green, 2)
    LCD.text(path, 2, 2, LCD.green)
    LCD.show()

def cards(cardsshow, selected, basepath):
    displaycard(cardsshow[selected], cardsshow[selected])
    while True:
        if left.value() == 0:
            selected += 1
            if selected >= len(cardsshow):
                selected = 0
            displaycard(cardsshow[selected], cardsshow[selected])
            while left.value() == 0:
                pass
            sleep(0.05)
        
        
        if right.value() == 0:
            selected -= 1
            if selected < 0:
                selected = len(cardsshow) - 1
            displaycard(cardsshow[selected], cardsshow[selected])
            while right.value() == 0:
                pass
            sleep(0.05)

        if keyA.value() == 0:
            if cardsshow[selected].endswith('.py'):
                apptoopen = __import__(cardsshow[selected].replace('.py', ''))
                apptoopen.run()
            elif (os.stat('apps/' + cardsshow[selected])[0] & 0x4000) == 16384:
                os.chdir('apps/' + cardsshow[selected]) 
                sys.path.append('apps/' + cardsshow[selected])
                newapps = os.listdir()
                cards(newapps, 0)
                os.chdir('..')
                
            displaycard(cardsshow[selected], cardsshow[selected])
            while keyA.value() == 0:
                pass
            sleep(0.05)
        if keyY.value() == 0 and os.getcwd() != '/apps':
            while keyY.value() == 0: pass
            return

def main():
    LCD.fill(0x0000)
    LCD.show()
    apps = os.listdir('apps')
    
    cards(apps, 0)
    
 
if __name__=='__main__':
    main()
