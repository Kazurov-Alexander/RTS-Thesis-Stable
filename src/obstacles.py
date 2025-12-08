import random
import pygame as pg

class Obstacle:
    COLORS = {
        "tree": (139, 69, 19),      # коричневый
        "lake": (0, 191, 255),      # голубой (базовый для озёр)
        "mountain": (80, 80, 80),   # тёмно-серый (базовый для гор)
        "bush": (20, 100, 20)       # тёмно-зелёный
    }

    def __init__(self, x, y, kind, color=None):
        self.x = x
        self.y = y
        self.kind = kind
        # если передан цвет — используем его, иначе базовый
        self.color = color if color else Obstacle.COLORS[kind]

    def draw(self, screen, tile_size, offset_x, offset_y):
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y
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
                    trees.append(Obstacle(x, y, "tree"))
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
    base_color = Obstacle.COLORS[kind]

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
            factor = dist / max_dist  # от 0 (центр) до 1 (край)

            r, g, b = base_color
            # затемняем цвет ближе к центру (глубина/рельеф)
            shade = (int(r * (1 - 0.4*(1-factor))),
                     int(g * (1 - 0.4*(1-factor))),
                     int(b * (1 - 0.4*(1-factor))))

            obstacles.append(Obstacle(x, y, kind, color=shade))

    return obstacles


# ---------- Проверки ----------

def is_blocked(x, y, obstacles):
    """Проверка: занята ли клетка препятствием"""
    return any(o.x == x and o.y == y for o in obstacles)


def is_area_free(x, y, obstacles):
    """Проверка: клетка свободна от препятствий"""
    return not is_blocked(x, y, obstacles)
