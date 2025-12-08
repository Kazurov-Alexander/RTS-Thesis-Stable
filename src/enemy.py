import pygame as pg
import random
import math

class Enemy:
    def __init__(self, x, y, hp=100, speed=1, aggro_range=10):
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.aggro_range = aggro_range
        self.state = "wander"  # "wander" или "attack"

    def distance_to(self, target_x, target_y):
        return math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)

    def update(self, target_x, target_y, box_map):
        dist = self.distance_to(target_x, target_y)

        if dist <= self.aggro_range:
            self.state = "attack"
        else:
            self.state = "wander"

        if self.state == "attack":
            self.move_towards(target_x, target_y, box_map)
        else:
            self.wander(box_map)

    def move_towards(self, target_x, target_y, box_map):
        dx = target_x - self.x
        dy = target_y - self.y

        if abs(dx) > abs(dy):
            step_x = self.speed if dx > 0 else -self.speed
            new_x = self.x + step_x
            new_y = self.y
        else:
            step_y = self.speed if dy > 0 else -self.speed
            new_x = self.x
            new_y = self.y + step_y

        if box_map.is_inside(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def wander(self, box_map):
        # случайное движение раз в несколько кадров
        if random.random() < 0.05:  # вероятность шага
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_x = self.x + dx
            new_y = self.y + dy
            if box_map.is_inside(new_x, new_y):
                self.x = new_x
                self.y = new_y

    def draw(self, screen, tile_size, offset_x, offset_y):
        px = self.x * tile_size + offset_x
        py = self.y * tile_size + offset_y
        rect = pg.Rect(int(px), int(py), tile_size, tile_size)

        color = (50, 50, 200) if self.state == "wander" else (200, 50, 50)
        pg.draw.rect(screen, color, rect)
