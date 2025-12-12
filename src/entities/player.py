import pygame as pg
import math
from src.map.obstacles import is_blocked  # проверка препятствий

class Player:
    def __init__(self, x, y, speed=0.50):
        self.x = float(x)
        self.y = float(y)
        self.health = 100
        self.max_health = 100
        self.direction = "DOWN"   # направление по умолчанию
        self.speed = speed
        self.weapon = None  # ссылка на объект Weapon

        # Загружаем спрайт-лист
        self.sheet = pg.image.load(
            "assets/images/units/player/BODY_skeleton.png"
        ).convert_alpha()

        # Нарезаем кадры
        self.frames = self.load_frames()

    def load_frames(self):
        sheet_width, sheet_height = self.sheet.get_size()
        cols = 9   # количество столбцов в спрайте
        rows = 4   # количество строк в спрайте
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

    def move(self, direction, boxmap, obstacles=None, is_blocked_fn=is_blocked):
        """Плавное перемещение игрока с учётом препятствий"""
        directions = {
            "UP": (0, -1),
            "DOWN": (0, +1),
            "LEFT": (-1, 0),
            "RIGHT": (+1, 0)
        }

        dx, dy = directions[direction]
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist == 0:
            return

        step_x = (dx / dist) * self.speed
        step_y = (dy / dist) * self.speed

        new_x = self.x + step_x
        new_y = self.y + step_y

        cell_x = int(round(new_x))
        cell_y = int(round(new_y))

        if boxmap.is_inside(cell_x, cell_y) and (obstacles is None or not is_blocked_fn(cell_x, cell_y, obstacles)):
            self.x = new_x
            self.y = new_y
            self.direction = direction

    def get_image(self):
        """Возвращает текущий кадр спрайта"""
        return self.frames[self.direction][0]

    def draw(self, screen, tile_size, offset_x, offset_y):
        """Отрисовка игрока и экипированного оружия"""
        px = int(self.x * tile_size + offset_x)
        py = int(self.y * tile_size + offset_y)

        # сам игрок
        player_img = pg.transform.scale(self.get_image(), (tile_size, tile_size))
        screen.blit(player_img, (px, py))

        # поверх игрока — уменьшенное оружие
        if self.weapon:
            weapon_img = self.weapon.get_scaled_image(tile_size, equipped=True)

            # значения по умолчанию (чтобы IDE не ругалась)
            offset_weapon_x, offset_weapon_y = px, py

        # поверх игрока — уменьшенное оружие
        if self.weapon:
            weapon_img = self.weapon.get_scaled_image(tile_size, equipped=True)

            if self.direction == "LEFT":
                # отразим по горизонтали и сместим вниз
                weapon_img = pg.transform.flip(weapon_img, True, False)
                offset_weapon_x = px - tile_size // -3
                offset_weapon_y = py + tile_size // 2

            elif self.direction == "RIGHT":
                offset_weapon_x = px + tile_size // 3
                offset_weapon_y = py + tile_size // 2

            elif self.direction == "DOWN":
                offset_weapon_x = px + tile_size // 4
                offset_weapon_y = py + tile_size // 2

            elif self.direction == "UP":
                # оружие не видно, силуэт игрока его закрывает
                return

            screen.blit(weapon_img, (offset_weapon_x, offset_weapon_y))
