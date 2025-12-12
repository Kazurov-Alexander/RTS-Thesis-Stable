import pygame as pg
import random
import math
from src.map.obstacles import is_blocked  # проверка препятствий

class Enemy:
    def __init__(self, x, y, hp=100, speed=0.1, aggro_range=15):
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.speed = speed
        self.aggro_range = aggro_range
        self.state = "wander"  # "wander" или "attack"
        self.direction = "DOWN"

        # Загружаем спрайт-лист (тот же, что у игрока)
        self.sheet = pg.image.load(
            "assets/images/units/player/BODY_skeleton.png"
        ).convert_alpha()

        # Нарезаем кадры
        self.frames = self.load_frames()

    def load_frames(self):
        sheet_width, sheet_height = self.sheet.get_size()
        cols = 9   # количество столбцов
        rows = 4   # количество строк
        frame_width = sheet_width // cols
        frame_height = sheet_height // rows

        frames = {"UP": [], "LEFT": [], "DOWN": [], "RIGHT": [], "IDLE": []}

        for row in range(rows):
            for col in range(cols):
                rect = pg.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = self.sheet.subsurface(rect)

                if row == 0:
                    frames["UP"].append(frame)
                elif row == 1:
                    frames["LEFT"].append(frame)
                elif row == 2:
                    frames["DOWN"].append(frame)
                elif row == 3:
                    frames["RIGHT"].append(frame)

        frames["IDLE"].append(frames["DOWN"][0])
        return frames

    def distance_to(self, target_x, target_y):
        return math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)

    def update(self, target_x, target_y, box_map, obstacles=None):
        dist = self.distance_to(target_x, target_y)

        if dist <= self.aggro_range:
            self.state = "attack"
        else:
            self.state = "wander"

        if self.state == "attack":
            self.move_towards(target_x, target_y, box_map, obstacles)
        else:
            self.wander(box_map, obstacles)

    def move_towards(self, target_x, target_y, box_map, obstacles=None):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist == 0:
            return

        # нормализованный вектор движения
        step_x = (dx / dist) * self.speed
        step_y = (dy / dist) * self.speed

        new_x = self.x + step_x
        new_y = self.y + step_y

        # направление для анимации
        if abs(dx) > abs(dy):
            self.direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            self.direction = "DOWN" if dy > 0 else "UP"

        # проверяем границы и препятствия (по ближайшей клетке)
        cell_x, cell_y = int(round(new_x)), int(round(new_y))
        if box_map.is_inside(new_x, new_y) and (obstacles is None or not is_blocked(cell_x, cell_y, obstacles)):
            self.x = new_x
            self.y = new_y

    def wander(self, box_map, obstacles=None):
        if random.random() < 0.02:  # вероятность шага
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_x = self.x + dx * self.speed * 10  # чуть длиннее шаг
            new_y = self.y + dy * self.speed * 10

            cell_x, cell_y = int(round(new_x)), int(round(new_y))
            if box_map.is_inside(new_x, new_y) and (obstacles is None or not is_blocked(cell_x, cell_y, obstacles)):
                self.x = new_x
                self.y = new_y
                if dx == 1: self.direction = "RIGHT"
                elif dx == -1: self.direction = "LEFT"
                elif dy == 1: self.direction = "DOWN"
                elif dy == -1: self.direction = "UP"

    def get_image(self):
        """Возвращает текущий кадр спрайта"""
        return self.frames[self.direction][0]

    def draw(self, screen, tile_size, offset_x, offset_y):
        enemy_img = pg.transform.scale(self.get_image(), (tile_size, tile_size))
        screen.blit(enemy_img, (int(self.x * tile_size + offset_x),
                                int(self.y * tile_size + offset_y)))
