import pygame
import sys

from pygame.display import update

import settings
from board import Board
import random

# def random_color():
#     return (random.randint(0, 255),
#             random.randint(0, 255),
#             random.randint(0, 255))

player_col = {
    0: (52, 179, 102),
    1: (179, 52, 52),
}
pygame.init()
pygame.display.set_caption("Connect 4")
screen = pygame.display.set_mode((settings.SCREEN_DIMS))
columns = []
hole_colors = []
clock = pygame.time.Clock()
gb = Board()

def draw_fps():
    clock.tick()
    fps = int(clock.get_fps())

    font = pygame.font.SysFont(None, 30)
    fps_surface = font.render(f"FPS: {fps}", True, (0, 0, 0))
    fps_bg = pygame.Rect(10, 10, 100, 30)
    screen.fill((209, 31, 31), fps_bg)
    screen.blit(fps_surface, (10, 10))

def check_events():
    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(columns):
                if rect.collidepoint(mouse_pos):
                    hole = gb.advance_turn(i)
                    hole_colors[hole[0]][hole[1]] = player_col[gb.turn]

def draw_screen():
    global columns
    columns = []
    hdiv = settings.HEIGHT_DIV
    b_width = settings.BOARD_WIDTH
    b_height = settings.BOARD_HEIGHT
    bg_col = settings.BG_COLOR
    padding = 10

    players_rect = pygame.Rect(screen.get_rect().left, screen.get_rect().top, screen.get_rect().width, 1 * hdiv)
    screen.fill((209, 31, 31), players_rect)

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
        col = []
        for j in range(b_height):
            hole = pygame.draw.circle(screen, bg_col, (left+hdiv//2, top+hdiv//2), hdiv//2-padding/2)
            top += hdiv
            hole_colors[j].append(bg_col)
        column = pygame.Rect(left, board_rect.top, hdiv, board_rect.height)
        # screen.fill(random_color(), column)
        columns.append(column)
        left += hdiv

def udpate_screen():
    hdiv = settings.HEIGHT_DIV
    b_width = settings.BOARD_WIDTH
    b_height = settings.BOARD_HEIGHT
    bg_col = settings.BG_COLOR
    padding = 10
    mouse_pos = pygame.mouse.get_pos()
    color = (41, 88, 112)
    for i, rect in enumerate(columns):
        if rect.collidepoint(mouse_pos):
            color = (55, 118, 149)
        else:
            color = (67, 146, 186)
        pygame.draw.rect(screen, color, rect, border_radius=padding)
        top = rect.top
        for j in range(b_height):
            hole_color = hole_colors[j][i]
            hole = pygame.draw.circle(screen, hole_color, (rect.left + hdiv // 2, top + hdiv // 2), hdiv // 2 - padding / 2)
            top += hdiv

draw_screen()
pygame.display.flip()

while True:
    check_events()
    udpate_screen()
    draw_fps()
    pygame.display.flip()
    if gb.game_over:
        sys.exit()