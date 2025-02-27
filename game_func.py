import pygame
import sys

def init():
    pygame.init()

def update():
    pass

def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

def draw_board():
    pass