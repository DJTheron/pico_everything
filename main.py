from LCD_Lib import LCD
import os

def main():
    LCD.fill(0x0000)
    LCD.show()

def displaycard(title):
    LCD.text(title, 70, 115, LCD.white)
    
if __name__=='__main__':
    main()
    displaycard("Hello World")
 