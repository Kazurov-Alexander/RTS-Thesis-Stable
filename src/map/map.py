import pygame as pg  # библиотека pygame для работы с графикой

class BoxMap:
    def __init__(self, radius=10, tile_size=40, base_tile="grass.png"):
        self.radius = radius          # радиус карты (от центра до края в клетках)
        self.tile_size = tile_size    # размер одной клетки (в пикселях)
        self.tiles = {}               # словарь для хранения тайлов карты

        # Загружаем оригинальный тайл один раз (например, grass.png)
        self.grass_tile_original = pg.image.load(
            f"assets/images/tiles/{base_tile}"
        ).convert_alpha()

        # Масштабируем тайл под текущий размер клетки
        self.grass_tile = pg.transform.scale(
            self.grass_tile_original, (self.tile_size, self.tile_size)
        )

        # Генерируем клетки карты
        self.generate_boxes()

    def generate_boxes(self):
        """Генерация квадратной области [-radius, radius] × [-radius, radius]"""
        # пересоздаём масштабированный тайл на случай изменения tile_size
        self.grass_tile = pg.transform.scale(
            self.grass_tile_original, (self.tile_size, self.tile_size)
        )

        # создаём сетку тайлов от -radius до +radius по X и Y
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                self.tiles[(x, y)] = self.grass_tile  # сохраняем тайл в словарь

    def is_inside(self, x, y):
        """Проверка: находится ли клетка внутри карты"""
        return abs(x) <= self.radius and abs(y) <= self.radius

    def update_tile_size(self, new_size):
        """Обновление размера клетки (например, при зуме колесиком мыши)"""
        self.tile_size = new_size     # обновляем размер клетки
        self.generate_boxes()         # пересоздаём тайлы под новый размер
