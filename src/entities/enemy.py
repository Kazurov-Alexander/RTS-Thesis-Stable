import math  # модуль для математических функций
import random  # модуль для случайных чисел

import pygame as pg  # библиотека pygame для графики и управления

from src.map.obstacles import is_blocked  # функция проверки препятствий


class Enemy:
    def __init__(self, x, y, hp=100, speed=0.1, aggro_range=15, damage=5):
        self.x = float(x)  # координата X врага
        self.y = float(y)  # координата Y врага
        self.hp = hp  # здоровье врага
        self.speed = speed  # скорость передвижения
        self.aggro_range = aggro_range  # радиус агрессии (видимости игрока)
        self.damage = damage  # базовый урон врага
        self.state = "wander"  # текущее состояние ("wander" или "attack")
        self.direction = "DOWN"  # направление движения
        self.alive = True  # жив ли враг

        # таймер атаки
        self.attack_cooldown = 1000  # задержка между атаками (мс)
        self.last_attack_time = 0  # время последней атаки

        # Загружаем спрайт-лист (тот же, что у игрока)
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

    def distance_to(self, target_x, target_y):
        # вычисляем расстояние до цели (например, игрока)
        return math.sqrt((target_x - self.x) ** 2 + (target_y - self.y) ** 2)

    def update(self, target_x, target_y, box_map, obstacles=None, player_alive=True, player=None):
        if not self.alive:
            return

        # если игрок мёртв — враг всегда блуждает
        if not player_alive:
            self.state = "wander"
            self.wander(box_map, obstacles)
            return

        dist = self.distance_to(target_x, target_y)

        # переключение состояния врага
        if dist <= self.aggro_range:
            self.state = "attack"
        else:
            self.state = "wander"

        # выполняем действие в зависимости от состояния
        if self.state == "attack":
            self.move_towards(target_x, target_y, box_map, obstacles, player)
        else:
            self.wander(box_map, obstacles)

    def move_towards(self, target_x, target_y, box_map, obstacles=None, player=None):
        if not self.alive:
            return

        dx = target_x - self.x  # разница по X
        dy = target_y - self.y  # разница по Y
        dist = math.sqrt(dx ** 2 + dy ** 2)  # расстояние до цели

        if dist == 0:
            return

        # шаг в сторону игрока
        step_x = (dx / dist) * self.speed
        step_y = (dy / dist) * self.speed

        new_x = self.x + step_x
        new_y = self.y + step_y

        # определяем направление движения для анимации
        if abs(dx) > abs(dy):
            self.direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            self.direction = "DOWN" if dy > 0 else "UP"

        cell_x, cell_y = int(round(new_x)), int(round(new_y))

        # 🚫 запрет на вход в клетку игрока
        if player:
            dist_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            if dist_to_player <= 1.0:
                return  # враг остаётся рядом и атакует, но не входит внутрь
            if cell_x == int(round(player.x)) and cell_y == int(round(player.y)):
                return

        # проверка границ карты и препятствий
        if box_map.is_inside(new_x, new_y) and (obstacles is None or not is_blocked(cell_x, cell_y, obstacles)):
            self.x = new_x
            self.y = new_y

    def wander(self, box_map, obstacles=None):
        if not self.alive:
            return

        # случайное блуждание
        if random.random() < 0.02:  # вероятность шага
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            new_x = self.x + dx * self.speed * 10
            new_y = self.y + dy * self.speed * 10

            cell_x, cell_y = int(round(new_x)), int(round(new_y))
            if box_map.is_inside(new_x, new_y) and (obstacles is None or not is_blocked(cell_x, cell_y, obstacles)):
                self.x = new_x
                self.y = new_y
                if dx == 1:
                    self.direction = "RIGHT"
                elif dx == -1:
                    self.direction = "LEFT"
                elif dy == 1:
                    self.direction = "DOWN"
                elif dy == -1:
                    self.direction = "UP"

    def get_image(self):
        """Возвращает текущий кадр спрайта"""
        if not self.alive:
            return self.dead_img  # если враг мёртв — показываем спрайт смерти
        return self.frames[self.direction][0]  # иначе кадр по направлению

    def draw(self, screen, tile_size, offset_x, offset_y):
        # отрисовка врага на экране
        enemy_img = pg.transform.scale(self.get_image(), (tile_size, tile_size))
        screen.blit(enemy_img, (int(self.x * tile_size + offset_x),
                                int(self.y * tile_size + offset_y)))

    # ---------- Боевая система ----------

    def take_damage(self, amount: int):
        """Получение урона от игрока"""
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False  # враг умирает

    def attack(self, player):
        """Атака игрока с задержкой"""
        if not self.alive:
            return

        current_time = pg.time.get_ticks()  # текущее время в мс
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # наносим увеличенный урон
            player.take_damage(self.damage * 2)
            self.last_attack_time = current_time
