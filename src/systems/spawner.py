import random
from src.map.obstacles import Obstacle, MountainGroup, WaterGroup, is_blocked
from src.map.weapon import generate_weapons
from src.entities.enemy import Enemy


# ---------- Генераторы ----------

def generate_trees(num_trees, box_map, obstacles, min_distance=2):
    trees = []
    for _ in range(num_trees):
        for attempts in range(200):
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if not box_map.is_inside(x, y):
                continue
            too_close = any(abs(x - t.x) < min_distance and abs(y - t.y) < min_distance for t in trees)
            occupied = any(
                (hasattr(o, "x") and o.x == x and o.y == y) or
                (hasattr(o, "cells") and (x, y) in o.cells)
                for o in obstacles
            )
            if not too_close and not occupied:
                trees.append(Obstacle(x, y, random.choice(["tree-1", "tree-2"])))
                break
    return trees


def generate_bushes(num_bushes, box_map, obstacles, min_distance=2):
    bushes = []
    for _ in range(num_bushes):
        for attempts in range(200):
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if not box_map.is_inside(x, y):
                continue
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


def generate_blob(num_blobs, min_size, max_size, box_map, kind):
    obstacles_out = []
    for _ in range(num_blobs):
        cx = random.randint(-box_map.radius, box_map.radius)
        cy = random.randint(-box_map.radius, box_map.radius)
        target = random.randint(min_size, max_size)
        blob = {(cx, cy)}
        while len(blob) < target:
            bx, by = random.choice(list(blob))
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = bx + dx, by + dy
            if box_map.is_inside(nx, ny):
                blob.add((nx, ny))
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
    lakes = generate_blob(num_blobs=3, min_size=30, max_size=100, box_map=box_map, kind="lake")
    mountains = generate_blob(num_blobs=9, min_size=60, max_size=140, box_map=box_map, kind="mountain")
    obstacles = lakes + mountains

    trees = generate_trees(num_trees=100, box_map=box_map, obstacles=obstacles, min_distance=2)
    obstacles += trees

    bushes = generate_bushes(num_bushes=50, box_map=box_map, obstacles=obstacles, min_distance=2)
    obstacles += bushes

    return obstacles


def spawn_enemies(num_enemies, box_map, player, min_distance=10, obstacles=None):
    enemies = []
    for _ in range(num_enemies):
        for attempts in range(200):
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if not box_map.is_inside(x, y):
                continue
            dist = ((x - player.x) ** 2 + (y - player.y) ** 2) ** 0.5
            if dist >= min_distance and not is_blocked(x, y, obstacles):
                enemies.append(Enemy(x, y))
                break
    return enemies


def spawn_weapons(box_map, obstacles):
    return generate_weapons(box_map, obstacles)
