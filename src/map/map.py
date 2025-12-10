import pygame as pg

class BoxMap:
    def __init__(self, radius=10, tile_size=40, base_tile="grass.png"):
        self.radius = radius
        self.tile_size = tile_size
        self.tiles = {}

        # Загружаем оригинальный тайл один раз
        self.grass_tile_original = pg.image.load(
            f"assets/images/tiles/{base_tile}"
        ).convert_alpha()

        # Масштабируем под текущий размер клетки
        self.grass_tile = pg.transform.scale(
            self.grass_tile_original, (self.tile_size, self.tile_size)
        )

        self.generate_boxes()

    def generate_boxes(self):
        """Генерация квадратной области [-radius, radius] × [-radius, radius]"""
        # пересоздаём масштабированный тайл на случай изменения tile_size
        self.grass_tile = pg.transform.scale(
            self.grass_tile_original, (self.tile_size, self.tile_size)
        )

        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                self.tiles[(x, y)] = self.grass_tile

    def is_inside(self, x, y):
        """Проверка: находится ли клетка внутри карты"""
        return abs(x) <= self.radius and abs(y) <= self.radius

    def update_tile_size(self, new_size):
        """Обновление размера клетки (например, при зуме колесиком мыши)"""
        self.tile_size = new_size
        self.generate_boxes()
