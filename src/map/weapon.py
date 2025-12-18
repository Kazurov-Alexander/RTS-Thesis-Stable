import pygame as pg  # библиотека pygame для работы с графикой

# Кэш путей и изображений оружия
WEAPON_PATHS = {
    "axe": "assets/images/weapons/axe.png",    # путь к картинке топора
    "sword": "assets/images/weapons/sword.png",# путь к картинке меча
    "bow": "assets/images/weapons/bow.png",    # путь к картинке лука
}
_WEAPON_IMAGES_CACHE = {}  # кэш загруженных изображений оружия

class Weapon:
    """
    Оружие как объект на карте.
    - x, y: координаты в координатах карты (тайловые)
    - kind: тип оружия (axe, sword, bow)
    - picked: флаг, что предмет подобран и больше не рисуется на карте
    """

    def __init__(self, x: int, y: int, kind: str):
        self.x = x              # координата X на карте
        self.y = y              # координата Y на карте
        self.kind = kind        # тип оружия
        self.picked = False     # флаг: подобрано ли оружие
        self.image = self._load_image(kind)  # загружаем картинку оружия

    def _load_image(self, kind: str) -> pg.Surface:
        """Ленивая загрузка и кэширование PNG-иконки оружия"""
        if kind in _WEAPON_IMAGES_CACHE:  # если картинка уже загружена
            return _WEAPON_IMAGES_CACHE[kind]

        path = WEAPON_PATHS.get(kind)  # получаем путь к картинке по типу
        if path:
            try:
                img = pg.image.load(path).convert_alpha()  # загружаем картинку
                _WEAPON_IMAGES_CACHE[kind] = img           # сохраняем в кэш
                return img
            except Exception:
                # fallback: простая заливка, если файла нет
                fallback = pg.Surface((40, 40), pg.SRCALPHA)  # создаём пустую поверхность
                pg.draw.rect(fallback, (200, 200, 0), fallback.get_rect())  # рисуем жёлтый квадрат
                _WEAPON_IMAGES_CACHE[kind] = fallback
                return fallback

        # fallback если тип неизвестен
        unknown = pg.Surface((40, 40), pg.SRCALPHA)  # создаём пустую поверхность
        pg.draw.rect(unknown, (180, 180, 180), unknown.get_rect())  # рисуем серый квадрат
        _WEAPON_IMAGES_CACHE[kind] = unknown
        return unknown

    def get_scaled_image(self, tile_size: int, equipped: bool = False) -> pg.Surface:
        """
        Возвращает картинку оружия в нужном масштабе.
        - equipped=True → уменьшенный размер (в 3 раза меньше)
        - equipped=False → обычный размер (как на карте)
        """
        if equipped:
            size = (tile_size // 3, tile_size // 3)  # уменьшенный размер
        else:
            size = (tile_size, tile_size)            # обычный размер
        return pg.transform.scale(self.image, size)  # масштабируем картинку

    def draw(self, screen: pg.Surface, tile_size: int, offset_x: int, offset_y: int):
        """Отрисовка оружия на карте, если оно не подобрано"""
        if self.picked:  # если оружие подобрано — не рисуем
            return
        px = self.x * tile_size + offset_x  # перевод координаты X в пиксели
        py = self.y * tile_size + offset_y  # перевод координаты Y в пиксели
        screen.blit(self.get_scaled_image(tile_size, equipped=False), (int(px), int(py)))  # рисуем оружие

def _is_occupied(x: int, y: int, obstacles) -> bool:
    """
    Проверяет, занята ли клетка любым препятствием/объектом.
    Поддерживает:
    - объекты с полями x, y (точечные)
    - объекты с набором cells (многоклеточные регионы)
    """
    for o in obstacles:
        if hasattr(o, "x") and hasattr(o, "y"):  # если объект имеет координаты
            if o.x == x and o.y == y:            # совпадают с проверяемыми
                return True
        elif hasattr(o, "cells"):                # если объект состоит из множества клеток
            if (x, y) in o.cells:                # проверяем наличие клетки
                return True
    return False  # клетка свободна
