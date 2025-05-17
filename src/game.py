import pygame, sys
import settings
from concurrent.futures import ThreadPoolExecutor

from ai import AI
from board import Board
import utility

pygame.init()
pygame.display.set_caption("Connect 4")
clock = pygame.time.Clock()
screen = pygame.display.set_mode((settings.SCREEN_DIMS))
game_active = False
fps_ticks = 0
curr_fps = 0
active_pos = {
    1: (settings.SCREEN_DIMS[0]//4, screen.get_rect().top + settings.HEIGHT_DIV // 2),
    2: (3 * settings.SCREEN_DIMS[0]//4, screen.get_rect().top + settings.HEIGHT_DIV // 2)
}
columns = []
hole_colors = []
PLAYER = settings.PLAYER
BOT = settings.BOT

players_rect = pygame.Rect(screen.get_rect().left, screen.get_rect().top, screen.get_rect().width, 1 * settings.HEIGHT_DIV)
bot = utility.circle_crop_image(pygame.image.load("assets/images/robot.png").convert_alpha())
person = utility.circle_crop_image(pygame.image.load("assets/images/you.png").convert_alpha())
gb = Board()
ai = AI(gb)
executor = ThreadPoolExecutor(max_workers=2)
future = None


def draw_button(msg):
    font = pygame.font.SysFont(None, 48)
    msg_image = font.render(msg, True, settings.TEXT_COLOR, settings.BTN_COLOR)
    msg_rect = msg_image.get_rect()

    width, height = msg_rect.width + settings.BTN_PADDING[0], msg_rect.height + settings.BTN_PADDING[1]
    color = settings.BTN_COLOR
    rect = pygame.Rect(0,0,width, height)
    rect.center = (screen.get_rect().centerx, screen.get_rect().bottom - settings.HEIGHT_DIV // 2)

    msg_rect.center = rect.center
    screen.fill(color, rect)
    screen.blit(msg_image, msg_rect)
    return rect

button_rect = draw_button("")

def check_button(mouse_x, mouse_y):
    global game_active, gb, hole_colors
    button_clicked = button_rect.collidepoint(mouse_x, mouse_y)
    if button_clicked:
        game_active = True
        gb = Board()
        hole_colors = []
        draw_screen()

def draw_message(msg):
    font = pygame.font.SysFont(None, 48)
    msg_image = font.render(msg, True, settings.TEXT_COLOR, settings.PLAYER_RECT_COLOR)
    msg_rect = msg_image.get_rect()
    msg_rect.center = (screen.get_rect().centerx, screen.get_rect().top + settings.HEIGHT_DIV // 2)
    screen.blit(msg_image, msg_rect)

def draw_fps():
    global fps_ticks, curr_fps
    clock.tick()
    fps_ticks += 1
    if fps_ticks > settings.FPS_TICK_LIMIT:
        curr_fps = int(clock.get_fps())
        fps_ticks = 0

    font = pygame.font.SysFont(None, 30)
    fps_surface = font.render(f"FPS: {curr_fps}", True, (0, 0, 0))
    fps_bg = pygame.Rect(10, 10, 100, 30)
    screen.fill((settings.PLAYER_RECT_COLOR), fps_bg)
    screen.blit(fps_surface, (10, 10))

def place_at(col):
    hole = gb.advance_turn(col)
    hole_colors[hole[0]][hole[1]] = settings.PLAYER_COLORS[gb.turn + 1]

def check_events():
    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            executor.shutdown()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            check_button(*mouse_pos)
            if game_active and gb.turn == PLAYER:
                for i, rect in enumerate(columns):
                    if rect.collidepoint(mouse_pos):
                        place_at(i)

def draw_screen():
    global columns, players_rect
    columns = []
    hdiv = settings.HEIGHT_DIV
    b_width = settings.BOARD_WIDTH
    b_height = settings.BOARD_HEIGHT
    bg_col = settings.BG_COLOR
    padding = settings.PADDING

    screen.fill((settings.PLAYER_RECT_COLOR), players_rect)
    bg = pygame.Rect(screen.get_rect().left, players_rect.bottom, screen.get_rect().width, screen.get_height() - players_rect.height)
    screen.fill(bg_col, bg)

    board_left = int(screen.get_rect().centerx - hdiv * b_width / 2)
    board_top = bg.top + hdiv
    board_rect = pygame.Rect(board_left, board_top, b_width*hdiv, b_height*hdiv)
    board = pygame.Rect(board_left - padding, board_top - padding, board_rect.width + 2 * padding , board_rect.height + 2 * padding)
    pygame.draw.rect(screen, (67, 146, 186), board, border_radius=padding)
    for row in range(b_height):
        hole_colors.append([])

    left = board_rect.left
    for i in range(b_width):
        top = board_rect.top
        for j in range(b_height):
            hole = pygame.draw.circle(screen, bg_col, (left+hdiv//2, top+hdiv//2), hdiv//2-padding/2)
            top += hdiv
            hole_colors[j].append(bg_col)
        column = pygame.Rect(left, board_rect.top, hdiv, board_rect.height)
        # screen.fill(random_color(), column)
        columns.append(column)
        left += hdiv

def update_screen():
    global bot, person
    hdiv = settings.HEIGHT_DIV
    b_height = settings.BOARD_HEIGHT
    screen_quarter = settings.SCREEN_DIMS[0]//4
    padding = settings.PADDING
    mouse_pos = pygame.mouse.get_pos()

    screen.fill((settings.PLAYER_RECT_COLOR), players_rect)
    pygame.draw.circle(screen, (255,255,255), active_pos[gb.turn+1],hdiv // 2 - padding/2)

    bot = pygame.transform.scale(bot, (hdiv - 2*padding, hdiv - 2*padding))
    person = pygame.transform.scale(person, (hdiv - 2*padding, hdiv - 2*padding))
    player_circle = pygame.draw.circle(screen, settings.PLAYER_COLORS[2], (screen_quarter, screen.get_rect().top + hdiv // 2),
                                       hdiv // 2 - padding)
    ai_circle = pygame.draw.circle(screen, settings.PLAYER_COLORS[1], (screen_quarter * 3, screen.get_rect().top + hdiv // 2),
                                   hdiv // 2 - padding)
    screen.blit(bot, bot.get_rect(center=(screen_quarter * 3, screen.get_rect().top + hdiv//2)))
    screen.blit(person, person.get_rect(center=(screen_quarter, screen.get_rect().top + hdiv//2)))

    for i, rect in enumerate(columns):
        if rect.collidepoint(mouse_pos):
            color = (55, 118, 149)
        else:
            color = (67, 146, 186)
        pygame.draw.rect(screen, color, rect, border_radius=padding)
        top = rect.top
        for j in range(b_height):
            hole_color = hole_colors[b_height - 1 - j][i]
            pygame.draw.circle(screen, hole_color, (rect.left + hdiv // 2, top + hdiv // 2), hdiv // 2 - padding / 2)
            top += hdiv
    draw_fps()

draw_screen()
pygame.display.flip()

while True:
    check_events()
    if game_active:
        if gb.game_over:
            update_screen()
            game_active = False
        else:
            update_screen()
        draw_message(gb.msg)
        if gb.turn == BOT and future is None:
            ai.gb = gb
            future = executor.submit(ai.get_move)
        elif future and future.done():
            move = future.result()
            place_at(move)
            future = None
    else:
        button_rect = draw_button("Play")
    pygame.display.flip()
    clock.tick(settings.FPS)
