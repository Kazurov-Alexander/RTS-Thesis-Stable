import math  # модуль для математических функций

import pygame as pg  # библиотека pygame для графики и управления

from src.map.obstacles import is_blocked  # функция проверки препятствий


class Player:
    def __init__(self, x, y, speed=0.50):
        self.x = float(x)  # координата X игрока
        self.y = float(y)  # координата Y игрока
        self.health = 100  # текущее здоровье
        self.max_health = 100  # максимальное здоровье
        self.direction = "DOWN"  # направление по умолчанию
        self.speed = speed  # скорость передвижения
        self.weapon = None  # ссылка на объект Weapon (оружие)
        self.alive = True  # состояние игрока (жив/мертв)

        # Загружаем спрайт-лист (анимация движения)
        self.sheet = pg.image.load(
            "assets/images/units/player/BODY_skeleton.png"
        ).convert_alpha()

        # Загружаем спрайт смерти
        self.dead_img = pg.image.load(
            "assets/images/units/player/dead.png"
        ).convert_alpha()

        # Нарезаем кадры анимации
        self.frames = self.load_frames()

    def load_frames(self):
        sheet_width, sheet_height = self.sheet.get_size()  # размеры спрайт-листа
        cols = 9  # количество столбцов
        rows = 4  # количество строк
        frame_width = sheet_width // cols  # ширина одного кадра
        frame_height = sheet_height // rows  # высота одного кадра

        frames = {"UP": [], "LEFT": [], "DOWN": [], "RIGHT": [], "IDLE": []}

        # нарезаем кадры по строкам и столбцам
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

        frames["IDLE"].append(frames["DOWN"][0])  # кадр для состояния покоя
        return frames

    def move(self, direction, boxmap, obstacles=None, is_blocked_fn=is_blocked):
        if not self.alive:
            return  # мёртвый игрок не двигается

        # словарь направлений движения
        directions = {
            "UP": (0, -1),
            "DOWN": (0, +1),
            "LEFT": (-1, 0),
            "RIGHT": (+1, 0)
        }

        dx, dy = directions[direction]  # смещение по X и Y
        dist = math.sqrt(dx ** 2 + dy ** 2)  # длина шага (обычно = 1)
        if dist == 0:
            return

        # шаг с учётом скорости
        step_x = (dx / dist) * self.speed
        step_y = (dy / dist) * self.speed

        new_x = self.x + step_x
        new_y = self.y + step_y

        cell_x = int(round(new_x))  # проверка клетки по X
        cell_y = int(round(new_y))  # проверка клетки по Y

        # проверка границ карты и препятствий
        if boxmap.is_inside(cell_x, cell_y) and (obstacles is None or not is_blocked_fn(cell_x, cell_y, obstacles)):
            self.x = new_x
            self.y = new_y
            self.direction = direction  # обновляем направление

    def get_image(self):
        """Возвращает текущий кадр спрайта"""
        if not self.alive:
            return self.dead_img  # если игрок мёртв — показываем спрайт смерти
        return self.frames[self.direction][0]  # иначе кадр по направлению

    def draw(self, screen, tile_size, offset_x, offset_y):
        # перевод координат игрока в пиксели
        px = int(self.x * tile_size + offset_x)
        py = int(self.y * tile_size + offset_y)

        # отрисовка игрока
        player_img = pg.transform.scale(self.get_image(), (tile_size, tile_size))
        screen.blit(player_img, (px, py))

        # отрисовка оружия, если оно есть
        if self.weapon and self.alive:
            weapon_img = self.weapon.get_scaled_image(tile_size, equipped=True)
            offset_weapon_x, offset_weapon_y = px, py

            if self.direction == "LEFT":
                weapon_img = pg.transform.flip(weapon_img, True, False)  # зеркалим спрайт
                offset_weapon_x = px - tile_size // -8
                offset_weapon_y = py + tile_size // 2
            elif self.direction == "RIGHT":
                offset_weapon_x = px + tile_size // 3
                offset_weapon_y = py + tile_size // 2
            elif self.direction == "DOWN":
                offset_weapon_x = px + tile_size // 4
                offset_weapon_y = py + tile_size // 2
            elif self.direction == "UP":
                return  # оружие не рисуется при движении вверх

            screen.blit(weapon_img, (offset_weapon_x, offset_weapon_y))

    # ---------- Боевая система ----------

    def take_damage(self, amount: int):
        if not self.alive:
            return
        self.health -= amount  # уменьшаем здоровье
        if self.health <= 0:
            self.health = 0
            self.alive = False  # игрок умирает

    def attack(self, enemy):
        if not self.alive:
            return
        # тестовый вариант: огромный урон, чтобы враг сразу умирал
        damage = 999
        enemy.take_damage(damage)
