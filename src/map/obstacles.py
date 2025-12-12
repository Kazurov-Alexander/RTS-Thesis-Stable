import pygame as pg


# ---------- Базовый объект-препятствие ----------

class Obstacle:
    TILE_PATHS = {
        "tree-1": "assets/images/tiles/tree-1.png",
        "tree-2": "assets/images/tiles/tree-2.png",
        "bush": "assets/images/tiles/bush.png",
    }
    TILE_IMAGES = {}

    def __init__(self, x, y, kind, shade_factor=1.0):
        self.x, self.y = x, y
        self.kind = kind
        self.shade_factor = shade_factor

        if kind in Obstacle.TILE_PATHS:
            if kind not in Obstacle.TILE_IMAGES:
                Obstacle.TILE_IMAGES[kind] = pg.image.load(
                    Obstacle.TILE_PATHS[kind]
                ).convert_alpha()
            self.base_img = Obstacle.TILE_IMAGES[kind]
        else:
            self.base_img = None
            self.color = (200, 0, 200)

    def draw(self, screen, tile_size, offset_x, offset_y):
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y

        if self.base_img:
            if self.kind in ("tree-1", "tree-2"):
                scaled = pg.transform.scale(self.base_img, (tile_size, tile_size * 2))
                screen.blit(scaled, (int(px), int(py - tile_size)))
            else:
                scaled = pg.transform.scale(self.base_img, (tile_size, tile_size))
                screen.blit(scaled, (int(px), int(py)))
        else:
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
            (0 if up else 1) |  # бит 0: нет соседа сверху
            (0 if down else 2) |  # бит 1: нет соседа снизу
            (0 if left else 4) |  # бит 2: нет соседа слева
            (0 if right else 8)  # бит 3: нет соседа справа
    )

    rules = {
        0b0000: "center",  # все соседи есть
        0b0101: "corner_tl",  # нет сверху и слева
        0b1001: "corner_tr",  # нет сверху и справа
        0b0110: "corner_bl",  # нет снизу и слева
        0b1010: "corner_br",  # нет снизу и справа
        0b0001: "top",  # нет сверху
        0b0010: "bottom",  # нет снизу
        0b0100: "left",  # нет слева
        0b1000: "right",  # нет справа
    }

    return textures.get(rules.get(mnt_state, "center"))


class MountainGroup:
    TILESET = None

    def __init__(self, cells):
        self.cells = set(cells)
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        if MountainGroup.TILESET is None:
            full_image = pg.image.load("assets/images/tiles/mountains.png").convert_alpha()
            tw, th = full_image.get_width() // 3, full_image.get_height() // 3

            def crop(i, j):
                rect = pg.Rect(j * tw, i * th, tw, th)
                return full_image.subsurface(rect)

            MountainGroup.TILESET = {
                "center":     crop(1, 1),
                "top":        crop(0, 1),
                "bottom":     crop(2, 1),
                "left":       crop(1, 0),
                "right":      crop(1, 2),
                "corner_tl":  crop(0, 0),
                "corner_tr":  crop(0, 2),
                "corner_bl":  crop(2, 0),
                "corner_br":  crop(2, 2),
            }

    def draw(self, screen, tile_size, offset_x, offset_y):
        for (cx, cy) in self.cells:
            up    = (cx, cy - 1) in self.cells
            down  = (cx, cy + 1) in self.cells
            left  = (cx - 1, cy) in self.cells
            right = (cx + 1, cy) in self.cells

            tile = mount_rules(up, down, left, right, MountainGroup.TILESET)

            px = cx * tile_size + offset_x
            py = cy * tile_size + offset_y
            screen.blit(pg.transform.scale(tile, (tile_size, tile_size)), (px, py))


# ---------- Вода ----------

class WaterGroup:
    GROUP_IMAGE = None

    def __init__(self, cells):
        self.cells = set(cells)
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        if WaterGroup.GROUP_IMAGE is None:
            WaterGroup.GROUP_IMAGE = pg.image.load("assets/images/tiles/see.png").convert_alpha()
        self.original_image = WaterGroup.GROUP_IMAGE

    def draw(self, screen, tile_size, offset_x, offset_y):
        w = (self.max_x - self.min_x + 1) * tile_size
        h = (self.max_y - self.min_y + 1) * tile_size
        stretched = pg.transform.scale(self.original_image, (w, h))
        mask = pg.Surface((w, h), pg.SRCALPHA)
        for (cx, cy) in self.cells:
            rx = (cx - self.min_x) * tile_size
            ry = (cy - self.min_y) * tile_size
            mask.fill((255, 255, 255, 255), pg.Rect(rx, ry, tile_size, tile_size))
        stretched.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        px = self.min_x * tile_size + offset_x
        py = self.min_y * tile_size + offset_y
        screen.blit(stretched, (px, py))


# ---------- Проверки ----------

def is_blocked(x, y, obstacles):
    return any(
        (hasattr(o, "x") and o.x == x and o.y == y) or
        (hasattr(o, "cells") and (x, y) in o.cells)
        for o in obstacles
    )


def is_area_free(x, y, obstacles):
    return not is_blocked(x, y, obstacles)
