import pygame as pg  # библиотека pygame для работы с графикой

# ---------- Базовый объект-препятствие ----------

class Obstacle:
    # пути к изображениям для разных типов препятствий
    TILE_PATHS = {
        "tree-1": "assets/images/tiles/tree-1.png",
        "tree-2": "assets/images/tiles/tree-2.png",
        "bush": "assets/images/tiles/bush.png",
    }
    TILE_IMAGES = {}  # кэш загруженных изображений

    def __init__(self, x, y, kind, shade_factor=1.0):
        self.x, self.y = x, y          # координаты препятствия
        self.kind = kind               # тип препятствия (дерево, куст и т.д.)
        self.shade_factor = shade_factor  # коэффициент затемнения (для будущих эффектов)

        # если тип есть в словаре путей
        if kind in Obstacle.TILE_PATHS:
            # загружаем изображение только один раз
            if kind not in Obstacle.TILE_IMAGES:
                Obstacle.TILE_IMAGES[kind] = pg.image.load(
                    Obstacle.TILE_PATHS[kind]
                ).convert_alpha()
            self.base_img = Obstacle.TILE_IMAGES[kind]  # сохраняем картинку
        else:
            # если тип неизвестен — рисуем цветной квадрат
            self.base_img = None
            self.color = (200, 0, 200)

    def draw(self, screen, tile_size, offset_x, offset_y):
        # переводим координаты в пиксели
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y

        if self.base_img:
            # для деревьев картинка выше клетки (2 тайла по высоте)
            if self.kind in ("tree-1", "tree-2"):
                scaled = pg.transform.scale(self.base_img, (tile_size, tile_size * 2))
                screen.blit(scaled, (int(px), int(py - tile_size)))
            else:
                # для остальных препятствий картинка размером с клетку
                scaled = pg.transform.scale(self.base_img, (tile_size, tile_size))
                screen.blit(scaled, (int(px), int(py)))
        else:
            # если нет картинки — рисуем квадрат
            rect = pg.Rect(int(px), int(py), tile_size, tile_size)
            pg.draw.rect(screen, self.color, rect)


# ---------- Горы с авторезкой 3×3 ----------

def mount_rules(up: bool, down: bool, left: bool, right: bool, textures: dict) -> pg.Surface:
    """
    Определяет тип горной текстуры на основе соседей.
    Использует битовую маску:
    - Бит 0 (1): гора сверху
    - Бит 1 (2): гора снизу
    - Бит 2 (4): гора слева
    - Бит 3 (8): гора справа
    """
    mnt_state = (
            (0 if up else 1) |   # бит 0: нет соседа сверху
            (0 if down else 2) | # бит 1: нет соседа снизу
            (0 if left else 4) | # бит 2: нет соседа слева
            (0 if right else 8)  # бит 3: нет соседа справа
    )

    # правила выбора текстуры
    rules = {
        0b0000: "center",     # все соседи есть
        0b0101: "corner_tl",  # нет сверху и слева
        0b1001: "corner_tr",  # нет сверху и справа
        0b0110: "corner_bl",  # нет снизу и слева
        0b1010: "corner_br",  # нет снизу и справа
        0b0001: "top",        # нет сверху
        0b0010: "bottom",     # нет снизу
        0b0100: "left",       # нет слева
        0b1000: "right",      # нет справа
    }

    return textures.get(rules.get(mnt_state, "center"))  # возвращаем нужную текстуру


class MountainGroup:
    TILESET = None  # набор текстур для гор

    def __init__(self, cells):
        self.cells = set(cells)  # множество клеток, занятых горами
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        self.min_x, self.max_x = min(xs), max(xs)  # границы по X
        self.min_y, self.max_y = min(ys), max(ys)  # границы по Y

        # загружаем тайлсет один раз
        if MountainGroup.TILESET is None:
            full_image = pg.image.load("assets/images/tiles/mountains.png").convert_alpha()
            tw, th = full_image.get_width() // 3, full_image.get_height() // 3

            def crop(i, j):
                rect = pg.Rect(j * tw, i * th, tw, th)
                return full_image.subsurface(rect)

            MountainGroup.TILESET = {
                "center": crop(1, 1),
                "top": crop(0, 1),
                "bottom": crop(2, 1),
                "left": crop(1, 0),
                "right": crop(1, 2),
                "corner_tl": crop(0, 0),
                "corner_tr": crop(0, 2),
                "corner_bl": crop(2, 0),
                "corner_br": crop(2, 2),
            }

    def draw(self, screen, tile_size, offset_x, offset_y):
        # отрисовка каждой клетки гор
        for (cx, cy) in self.cells:
            up = (cx, cy - 1) in self.cells
            down = (cx, cy + 1) in self.cells
            left = (cx - 1, cy) in self.cells
            right = (cx + 1, cy) in self.cells

            tile = mount_rules(up, down, left, right, MountainGroup.TILESET)

            px = cx * tile_size + offset_x
            py = cy * tile_size + offset_y
            screen.blit(pg.transform.scale(tile, (tile_size, tile_size)), (px, py))


# ---------- Вода ----------

class WaterGroup:
    GROUP_IMAGE = None  # общий спрайт воды

    def __init__(self, cells):
        self.cells = set(cells)  # множество клеток воды
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        # загружаем картинку воды один раз
        if WaterGroup.GROUP_IMAGE is None:
            WaterGroup.GROUP_IMAGE = pg.image.load("assets/images/tiles/see.png").convert_alpha()
        self.original_image = WaterGroup.GROUP_IMAGE

    def draw(self, screen, tile_size, offset_x, offset_y):
        # вычисляем размеры области воды
        w = (self.max_x - self.min_x + 1) * tile_size
        h = (self.max_y - self.min_y + 1) * tile_size
        stretched = pg.transform.scale(self.original_image, (w, h))  # растягиваем картинку
        mask = pg.Surface((w, h), pg.SRCALPHA)  # создаём маску прозрачности

        # заполняем маску по клеткам воды
        for (cx, cy) in self.cells:
            rx = (cx - self.min_x) * tile_size
            ry = (cy - self.min_y) * tile_size
            mask.fill((255, 255, 255, 255), pg.Rect(rx, ry, tile_size, tile_size))

        # применяем маску к картинке
        stretched.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # отрисовываем воду на экране
        px = self.min_x * tile_size + offset_x
        py = self.min_y * tile_size + offset_y
        screen.blit(stretched, (px, py))


# ---------- Проверки ----------

def is_blocked(x, y, obstacles):
    # проверка: занята ли клетка препятствием
    return any(
        (hasattr(o, "x") and o.x == x and o.y == y) or   # одиночный объект
        (hasattr(o, "cells") and (x, y) in o.cells)      # группа клеток (горы, вода)
        for o in obstacles
    )

def is_area_free(x, y, obstacles):
    # проверка: свободна ли клетка
    return not is_blocked(x, y, obstacles)
