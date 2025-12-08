import pygame as pg

def box_to_pixel(x, y, size):
    # Прямая сетка: каждый тайл — size × size
    px = x * size
    py = y * size
    return px, py

def draw_map(screen, boxmap, size=40, offset_x=0, offset_y=0):
    for (x, y), terrain in boxmap.tiles.items():
        px, py = box_to_pixel(x, y, size)
        px += offset_x
        py += offset_y

        rect = pg.Rect(int(px), int(py), size, size)
        color = (50, 200, 50) if terrain == "grass" else (100, 100, 100)
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 1)

