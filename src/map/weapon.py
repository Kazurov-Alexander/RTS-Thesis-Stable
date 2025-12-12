import random
import pygame as pg

# Кэш путей и изображений оружия
WEAPON_PATHS = {
    "axe":  "assets/images/weapons/axe.png",
    "sword": "assets/images/weapons/sword.png",
    "bow":  "assets/images/weapons/bow.png",
}
_WEAPON_IMAGES_CACHE = {}


class Weapon:
    """
    Оружие как объект на карте.
    - x, y: координаты в координатах карты (тайловые)
    - kind: тип оружия (axe, sword, bow)
    - picked: флаг, что предмет подобран и больше не рисуется на карте
    """
    def __init__(self, x: int, y: int, kind: str):
        self.x = x
        self.y = y
        self.kind = kind
        self.picked = False
        self.image = self._load_image(kind)

    def _load_image(self, kind: str) -> pg.Surface:
        """Ленивая загрузка и кэширование PNG-иконки оружия"""
        if kind in _WEAPON_IMAGES_CACHE:
            return _WEAPON_IMAGES_CACHE[kind]

        path = WEAPON_PATHS.get(kind)
        if path:
            try:
                img = pg.image.load(path).convert_alpha()
                _WEAPON_IMAGES_CACHE[kind] = img
                return img
            except Exception:
                # fallback: простая заливка, если файла нет
                fallback = pg.Surface((40, 40), pg.SRCALPHA)
                pg.draw.rect(fallback, (200, 200, 0), fallback.get_rect())
                _WEAPON_IMAGES_CACHE[kind] = fallback
                return fallback

        # fallback если тип неизвестен
        unknown = pg.Surface((40, 40), pg.SRCALPHA)
        pg.draw.rect(unknown, (180, 180, 180), unknown.get_rect())
        _WEAPON_IMAGES_CACHE[kind] = unknown
        return unknown

    def get_scaled_image(self, tile_size: int, equipped: bool = False) -> pg.Surface:
        """
        Возвращает картинку оружия в нужном масштабе.
        - equipped=True → уменьшенный размер (в 3 раза меньше)
        - equipped=False → обычный размер (как на карте)
        """
        if equipped:
            size = (tile_size // 3, tile_size // 3)
        else:
            size = (tile_size, tile_size)
        return pg.transform.scale(self.image, size)

    def draw(self, screen: pg.Surface, tile_size: int, offset_x: int, offset_y: int):
        """Отрисовка оружия на карте, если оно не подобрано"""
        if self.picked:
            return
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y
        screen.blit(self.get_scaled_image(tile_size, equipped=False), (int(px), int(py)))


def _is_occupied(x: int, y: int, obstacles) -> bool:
    """
    Проверяет, занята ли клетка любым препятствием/объектом.
    Поддерживает:
    - объекты с полями x, y (точечные)
    - объекты с набором cells (многоклеточные регионы)
    """
    for o in obstacles:
        if hasattr(o, "x") and hasattr(o, "y"):
            if o.x == x and o.y == y:
                return True
        elif hasattr(o, "cells"):
            if (x, y) in o.cells:
                return True
    return False


def generate_weapons(box_map, obstacles):
    """
    Генерирует ровно по одному: axe, sword, bow в случайных свободных клетках.
    Возвращает список из трёх Weapon.
    """
    weapons = []
    kinds = ["axe", "sword", "bow"]

    for kind in kinds:
        attempts = 0
        while True:
            attempts += 1
            if attempts > 300:  # защита от бесконечного цикла
                break

            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)

            if not box_map.is_inside(x, y):
                continue
            if _is_occupied(x, y, obstacles):
                continue

            weapons.append(Weapon(x, y, kind))
            break

    return weapons
