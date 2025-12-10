import pygame as pg

def box_to_pixel(x, y, size):
    # Прямая сетка: каждый тайл — size × size
    px = x * size
    py = y * size
    return px, py

def draw_map(screen, boxmap, size=40, offset_x=0, offset_y=0):
    for (x, y), tile_surface in boxmap.tiles.items():
        px, py = box_to_pixel(x, y, size)
        px += offset_x
        py += offset_y

        # Масштабируем под текущий size
        scaled_tile = pg.transform.scale(tile_surface, (size, size))
        screen.blit(scaled_tile, (int(px), int(py)))
