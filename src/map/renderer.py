import pygame as pg  # библиотека pygame для работы с графикой

def box_to_pixel(x, y, size):
    # Прямая сетка: каждый тайл имеет размер size × size
    px = x * size  # перевод координаты X из клеток в пиксели
    py = y * size  # перевод координаты Y из клеток в пиксели
    return px, py  # возвращаем координаты в пикселях

def draw_map(screen, boxmap, size=40, offset_x=0, offset_y=0):
    # отрисовка всей карты на экране
    for (x, y), tile_surface in boxmap.tiles.items():  # перебираем все клетки карты
        px, py = box_to_pixel(x, y, size)  # переводим координаты клетки в пиксели
        px += offset_x  # смещение камеры по X
        py += offset_y  # смещение камеры по Y

        # Масштабируем тайл под текущий размер клетки
        scaled_tile = pg.transform.scale(tile_surface, (size, size))
        # рисуем тайл на экране
        screen.blit(scaled_tile, (int(px), int(py)))
