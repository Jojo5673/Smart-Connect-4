#dims
BOARD_HEIGHT, BOARD_WIDTH = 6,7
SCREEN_DIMS = (1200, 800)
HEIGHT_DIV = 800//9
PADDING = 10
BTN_PADDING = (40, 20)
CENTER_COL = BOARD_WIDTH//2


#colors
BG_COLOR = (39, 37, 46) #the black purplish colour
BTN_COLOR = (50, 168, 94) #darker green
TEXT_COLOR = (255, 255, 255) #white
PLAYER_RECT_COLOR = (67, 146, 186) #blue board color
PLAYER_RECT_COLOR_SELECTED = (55, 118, 149) #darker blue
PLAYER_COLORS = {
    2: (52, 179, 102), #green
    1: (179, 52, 52), #red
}
BOT_LEVEL_COLORS = [
    (52, 179, 102), #green
    (245, 208, 73), #yellow
    (217, 103, 22),  # orange
    (179, 52, 52), #red
]


#misc
FPS_TICK_LIMIT = 60
FPS = 60
PLAYER = 0
BOT = 1