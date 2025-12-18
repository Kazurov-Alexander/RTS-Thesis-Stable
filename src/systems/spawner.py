import random  # модуль для генерации случайных чисел

# импортируем классы и функции из других модулей
from src.entities.enemy import Enemy
from src.map.obstacles import Obstacle, MountainGroup, WaterGroup, is_blocked
from src.map.weapon import Weapon

# ---------- Генераторы ----------

def generate_trees(num_trees, box_map, obstacles, min_distance=2):
    trees = []  # список деревьев
    for _ in range(num_trees):  # создаём указанное количество деревьев
        for attempts in range(200):  # ограничение числа попыток
            x = random.randint(-box_map.radius, box_map.radius)  # случайная координата X
            y = random.randint(-box_map.radius, box_map.radius)  # случайная координата Y
            if not box_map.is_inside(x, y):  # проверка: внутри ли карты
                continue
            # проверка: не слишком ли близко к другим деревьям
            too_close = any(abs(x - t.x) < min_distance and abs(y - t.y) < min_distance for t in trees)
            # проверка: не занята ли клетка другим препятствием
            occupied = any(
                (hasattr(o, "x") and o.x == x and o.y == y) or
                (hasattr(o, "cells") and (x, y) in o.cells)
                for o in obstacles
            )
            if not too_close and not occupied:
                # создаём дерево случайного типа
                trees.append(Obstacle(x, y, random.choice(["tree-1", "tree-2"])))
                break
    return trees

def generate_bushes(num_bushes, box_map, obstacles, min_distance=2):
    bushes = []  # список кустов
    for _ in range(num_bushes):
        for attempts in range(200):
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if not box_map.is_inside(x, y):
                continue
            # проверка: не слишком ли близко к другим кустам
            too_close = any(abs(x - b.x) < min_distance and abs(y - b.y) < min_distance for b in bushes)
            # проверка: не занята ли клетка другим препятствием
            occupied = any(
                (hasattr(o, "x") and o.x == x and o.y == y) or
                (hasattr(o, "cells") and (x, y) in o.cells)
                for o in obstacles
            )
            if not too_close and not occupied:
                bushes.append(Obstacle(x, y, "bush"))  # создаём куст
                break
    return bushes

def generate_blob(num_blobs, min_size, max_size, box_map, kind):
    obstacles_out = []  # список препятствий
    for _ in range(num_blobs):  # создаём несколько blob-объектов
        cx = random.randint(-box_map.radius, box_map.radius)  # случайная стартовая точка X
        cy = random.randint(-box_map.radius, box_map.radius)  # случайная стартовая точка Y
        target = random.randint(min_size, max_size)  # размер blob-а
        blob = {(cx, cy)}  # множество клеток blob-а
        while len(blob) < target:  # пока не достигнут нужный размер
            bx, by = random.choice(list(blob))  # выбираем случайную клетку внутри blob-а
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])  # случайное направление
            nx, ny = bx + dx, by + dy
            if box_map.is_inside(nx, ny):  # проверка: внутри карты
                blob.add((nx, ny))
        # создаём объект в зависимости от типа
        if kind == "mountain":
            obstacles_out.append(MountainGroup(blob))
        elif kind == "lake":
            obstacles_out.append(WaterGroup(blob))
        else:
            for (x, y) in blob:
                obstacles_out.append(Obstacle(x, y, kind))
    return obstacles_out

# ---------- Спавн ----------

def spawn_obstacles(box_map):
    # создаём озёра
    lakes = generate_blob(num_blobs=3, min_size=30, max_size=100, box_map=box_map, kind="lake")
    # создаём горы
    mountains = generate_blob(num_blobs=9, min_size=60, max_size=140, box_map=box_map, kind="mountain")
    obstacles = lakes + mountains  # объединяем

    # создаём деревья
    trees = generate_trees(num_trees=100, box_map=box_map, obstacles=obstacles, min_distance=2)
    obstacles += trees

    # создаём кусты
    bushes = generate_bushes(num_bushes=50, box_map=box_map, obstacles=obstacles, min_distance=2)
    obstacles += bushes

    return obstacles

def spawn_enemies(num_enemies, box_map, player, min_distance=10, obstacles=None):
    enemies = []  # список врагов
    for _ in range(num_enemies):
        for attempts in range(200):
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if not box_map.is_inside(x, y):
                continue
            # проверка: враг не должен появляться слишком близко к игроку
            dist = ((x - player.x) ** 2 + (y - player.y) ** 2) ** 0.5
            if dist >= min_distance and not is_blocked(x, y, obstacles):
                enemies.append(Enemy(x, y))  # создаём врага
                break
    return enemies

def generate_weapons(box_map, obstacles):
    """
    Генерирует ровно по одному: axe, sword, bow в случайных свободных клетках.
    Возвращает список из трёх Weapon.
    """
    weapons = []  # список оружия
    kinds = ["axe", "sword", "bow"]  # типы оружия

    for kind in kinds:
        attempts = 0
        while True:
            attempts += 1
            if attempts > 300:  # защита от бесконечного цикла
                break

            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)

            if not box_map.is_inside(x, y):  # проверка: внутри карты
                continue
            if is_blocked(x, y, obstacles):  # проверка: клетка занята
                continue

            weapons.append(Weapon(x, y, kind))  # создаём оружие
            break

    return weapons

def spawn_weapons(box_map, obstacles):
    # спавн оружия через генератор
    return generate_weapons(box_map, obstacles)
