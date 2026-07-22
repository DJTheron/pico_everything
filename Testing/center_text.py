SCREEN_W = 240
SCREEN_H = 240
CHAR_SIZE = 8

text = input("Text: ")
size_input = input("Font size (default 1): ").strip()
size = int(size_input) if size_input else 1

char_w = CHAR_SIZE * size
char_h = CHAR_SIZE * size
text_w = len(text) * char_w

if text_w > SCREEN_W:
    print(f"Warning: text is {text_w}px wide — won't fit on screen ({SCREEN_W}px)")

x = (SCREEN_W - text_w) // 2
y = (SCREEN_H - char_h) // 2

print(f"x={x}, y={y}")
