import LCD_Lib

LCD = LCD_Lib.LCD_1inch3()

def main():
    LCD_Lib.setup()
    LCD.fill(0x0000)
    LCD.show()

def displaycard(title):
    LCD.text(title, 70, 115, LCD.white)

if __name__=='__main__':
    main()
    displaycard("Hello World")
 