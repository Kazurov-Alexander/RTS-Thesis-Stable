import pygame as pg

class BoxMap:
    def __init__(self, radius=10, tile_size=40):
        self.radius = radius
        self.tile_size = tile_size
        self.tiles = {}
        # Загружаем тайл травы один раз
        self.grass_tile = pg.image.load(
            "assets/images/tiles/grass.png"
        ).convert_alpha()
        # Масштабируем тайл под размер клетки
        self.grass_tile = pg.transform.scale(self.grass_tile, (self.tile_size, self.tile_size))
        self.generate_boxes()

    def generate_boxes(self):
        # генерируем квадратную область [-radius, radius] × [-radius, radius]
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                # вместо строки сохраняем Surface тайла
                self.tiles[(x, y)] = self.grass_tile

    def is_inside(self, x, y):
        return abs(x) <= self.radius and abs(y) <= self.radius
