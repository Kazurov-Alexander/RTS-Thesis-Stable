import random
import pygame as pg

class Obstacle:
    # пути к текстурам
    TILE_PATHS = {
        "mountain": "assets/images/tiles/stone.png",
        "lake": "assets/images/tiles/water.png",
        "tree-1": "assets/images/tiles/tree-1.png",
        "tree-2": "assets/images/tiles/tree-2.png",
        "bush": "assets/images/tiles/bush.png"
    }

    # кэш для загруженных картинок
    TILE_IMAGES = {}

    def __init__(self, x, y, kind, shade_factor=1.0):
        self.x = x
        self.y = y
        self.kind = kind

        # загружаем текстуру
        if kind in Obstacle.TILE_PATHS:
            if kind not in Obstacle.TILE_IMAGES:
                img = pg.image.load(Obstacle.TILE_PATHS[kind]).convert_alpha()
                Obstacle.TILE_IMAGES[kind] = img
            base_img = Obstacle.TILE_IMAGES[kind]

            # для гор и озёр применяем затемнение
            if kind in ("mountain", "lake"):
                self.image = self.apply_shade(base_img, shade_factor)
            else:
                self.image = base_img
        else:
            # fallback — просто цветной квадрат
            self.image = None
            self.color = (200, 0, 200)

    def apply_shade(self, image, factor):
        """Затемняет картинку: factor от 0.6 (тёмная) до 1.0 (без изменений)"""
        shaded = image.copy()
        shade_color = (int(255 * factor), int(255 * factor), int(255 * factor))
        shaded.fill(shade_color, special_flags=pg.BLEND_RGBA_MULT)
        return shaded

    def draw(self, screen, tile_size, offset_x, offset_y):
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y

        if self.image:
            if self.kind in ("tree-1", "tree-2"):
                # дерево занимает два тайла по высоте
                scaled = pg.transform.scale(self.image, (tile_size, tile_size * 2))
                # смещаем вверх на один тайл, чтобы нижняя часть совпадала с клеткой
                screen.blit(scaled, (int(px), int(py - tile_size)))
            else:
                # обычные препятствия (кусты, горы, озёра)
                scaled = pg.transform.scale(self.image, (tile_size, tile_size))
                screen.blit(scaled, (int(px), int(py)))
        else:
            rect = pg.Rect(int(px), int(py), tile_size, tile_size)
            pg.draw.rect(screen, self.color, rect)


# ---------- Генераторы ----------

def generate_trees(num_trees, box_map, min_distance=2):
    trees = []
    for _ in range(num_trees):
        while True:
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if box_map.is_inside(x, y):
                too_close = any(abs(x - t.x) < min_distance and abs(y - t.y) < min_distance for t in trees)
                if not too_close:
                    # случайно выбираем модель дерева
                    kind = random.choice(["tree-1", "tree-2"])
                    trees.append(Obstacle(x, y, kind))
                    break
    return trees


def generate_bushes(num_bushes, box_map, min_distance=2):
    bushes = []
    for _ in range(num_bushes):
        while True:
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if box_map.is_inside(x, y):
                too_close = any(abs(x - b.x) < min_distance and abs(y - b.y) < min_distance for b in bushes)
                if not too_close:
                    bushes.append(Obstacle(x, y, "bush"))
                    break
    return bushes


def generate_blob(num_blobs, min_size, max_size, box_map, kind):
    """Генерация случайных сцепленных пятен (озёра, горы) с эффектом глубины"""
    obstacles = []

    for _ in range(num_blobs):
        cx = random.randint(-box_map.radius, box_map.radius)
        cy = random.randint(-box_map.radius, box_map.radius)
        target_size = random.randint(min_size, max_size)

        blob_cells = {(cx, cy)}

        while len(blob_cells) < target_size:
            bx, by = random.choice(list(blob_cells))
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            nx, ny = bx + dx, by + dy
            if box_map.is_inside(nx, ny):
                blob_cells.add((nx, ny))

        # вычисляем максимальное расстояние от центра
        max_dist = max(((x - cx)**2 + (y - cy)**2)**0.5 for (x,y) in blob_cells)

        for (x, y) in blob_cells:
            dist = ((x - cx)**2 + (y - cy)**2)**0.5
            factor = 0.6 + 0.4 * (dist / max_dist)  # центр темнее, край светлее

            obstacles.append(Obstacle(x, y, kind, shade_factor=factor))

    return obstacles


# ---------- Проверки ----------

def is_blocked(x, y, obstacles):
    """Проверка: занята ли клетка препятствием"""
    return any(o.x == x and o.y == y for o in obstacles)


def is_area_free(x, y, obstacles):
    """Проверка: клетка свободна от препятствий"""
    return not is_blocked(x, y, obstacles)
