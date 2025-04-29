import pygame
import random

def circle_crop_image(image):
    size = image.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0]//2, size[1]//2), min(size)//2)
    circular_image = image.copy()
    circular_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return circular_image

def random_color():
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))
