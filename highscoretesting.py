import json
import os

highscore_file = "game_highscores.json"
if os.path.exists("game_highscores.json"):
    with open(highscore_file, "r") as f:
        highscore_data = json.load(f)
highscore = highscore_data[__file__]
print(highscore)
    