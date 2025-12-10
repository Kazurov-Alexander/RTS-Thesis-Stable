import random
import pygame as pg

class Obstacle:
    TILE_PATHS = {
        "tree-1": "assets/images/tiles/tree-1.png",
        "tree-2": "assets/images/tiles/tree-2.png",
        "bush": "assets/images/tiles/bush.png"
    }

    TILE_IMAGES = {}

    def __init__(self, x, y, kind, shade_factor=1.0):
        self.x = x
        self.y = y
        self.kind = kind
        self.shade_factor = shade_factor

        if kind in Obstacle.TILE_PATHS:
            if kind not in Obstacle.TILE_IMAGES:
                img = pg.image.load(Obstacle.TILE_PATHS[kind]).convert_alpha()
                Obstacle.TILE_IMAGES[kind] = img
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


# ---------- Группа гор ----------

class MountainGroup:
    GROUP_IMAGE = None

    def __init__(self, cells):
        self.cells = cells
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        if MountainGroup.GROUP_IMAGE is None:
            MountainGroup.GROUP_IMAGE = pg.image.load("assets/images/tiles/mountains.png").convert_alpha()

        self.original_image = MountainGroup.GROUP_IMAGE

    def draw(self, screen, tile_size, offset_x, offset_y):
        w = (self.max_x - self.min_x + 1) * tile_size
        h = (self.max_y - self.min_y + 1) * tile_size

        stretched = pg.transform.scale(self.original_image, (w, h))

        mask = pg.Surface((w, h), pg.SRCALPHA)
        for (cx, cy) in self.cells:
            rx = (cx - self.min_x) * tile_size
            ry = (cy - self.min_y) * tile_size
            rect = pg.Rect(rx, ry, tile_size, tile_size)
            mask.fill((255, 255, 255, 255), rect)

        stretched.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        px = self.min_x * tile_size + offset_x
        py = self.min_y * tile_size + offset_y
        screen.blit(stretched, (px, py))


# ---------- Группа воды ----------

class WaterGroup:
    GROUP_IMAGE = None

    def __init__(self, cells):
        self.cells = cells
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
            rect = pg.Rect(rx, ry, tile_size, tile_size)
            mask.fill((255, 255, 255, 255), rect)

        stretched.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        px = self.min_x * tile_size + offset_x
        py = self.min_y * tile_size + offset_y
        screen.blit(stretched, (px, py))


# ---------- Генераторы ----------

def generate_trees(num_trees, box_map, obstacles, min_distance=2):
    trees = []
    for _ in range(num_trees):
        attempts = 0
        while True:
            attempts += 1
            if attempts > 200:
                break

            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)

            if box_map.is_inside(x, y):
                too_close = any(abs(x - t.x) < min_distance and abs(y - t.y) < min_distance for t in trees)
                occupied = any(
                    (hasattr(o, "x") and o.x == x and o.y == y) or
                    (hasattr(o, "cells") and (x, y) in o.cells)
                    for o in obstacles
                )
                if not too_close and not occupied:
                    kind = random.choice(["tree-1", "tree-2"])
                    trees.append(Obstacle(x, y, kind))
                    break
    return trees


def generate_bushes(num_bushes, box_map, obstacles, min_distance=2):
    bushes = []
    for _ in range(num_bushes):
        attempts = 0
        while True:
            attempts += 1
            if attempts > 200:
                break

            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)

            if box_map.is_inside(x, y):
                too_close = any(abs(x - b.x) < min_distance and abs(y - b.y) < min_distance for b in bushes)
                occupied = any(
                    (hasattr(o, "x") and o.x == x and o.y == y) or
                    (hasattr(o, "cells") and (x, y) in o.cells)
                    for o in obstacles
                )
                if not too_close and not occupied:
                    bushes.append(Obstacle(x, y, "bush"))
                    break
    return bushes


def generate_blob(num_blobs, min_size, max_size, box_map, kind, tile_size=40):
    obstacles = []

    for _ in range(num_blobs):
        cx = random.randint(-box_map.radius, box_map.radius)
        cy = random.randint(-box_map.radius, box_map.radius)
        target_size = random.randint(min_size, max_size)

        blob_cells = {(cx, cy)}
        while len(blob_cells) < target_size:
            bx, by = random.choice(list(blob_cells))
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = bx + dx, by + dy
            if box_map.is_inside(nx, ny):
                blob_cells.add((nx, ny))

        if kind == "mountain":
            obstacles.append(MountainGroup(blob_cells))
        elif kind == "lake":
            obstacles.append(WaterGroup(blob_cells))
        else:
            for (x, y) in blob_cells:
                obstacles.append(Obstacle(x, y, kind))

    return obstacles


# ---------- Проверки ----------

def is_blocked(x, y, obstacles):
    return any(
        (hasattr(o, "x") and o.x == x and o.y == y) or
        (hasattr(o, "cells") and (x, y) in o.cells)
        for o in obstacles
    )

def is_area_free(x, y, obstacles):
    return not is_blocked(x, y, obstacles)
