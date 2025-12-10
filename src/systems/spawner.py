from src.map.obstacles import generate_trees, generate_bushes, generate_blob
from src.map.weapon import generate_weapons
from src.entities.enemy import Enemy
from src.map.obstacles import is_blocked
import random

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
        attempts = 0
        while True:
            attempts += 1
            if attempts > 200:
                break
            x = random.randint(-box_map.radius, box_map.radius)
            y = random.randint(-box_map.radius, box_map.radius)
            if box_map.is_inside(x, y):
                dist = ((x - player.x)**2 + (y - player.y)**2) ** 0.5
                if dist >= min_distance and not is_blocked(x, y, obstacles):
                    enemies.append(Enemy(x, y))
                    break
    return enemies

def spawn_weapons(box_map, obstacles):
    return generate_weapons(box_map, obstacles)
