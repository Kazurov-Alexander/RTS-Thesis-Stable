import pygame as pg

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.direction = "DOWN"   # направление по умолчанию

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

                # ⚠️ Подстройка под твой спрайт-лист:
                if row == 0:
                    frames["UP"].append(frame)
                elif row == 1:
                    frames["LEFT"].append(frame)
                elif row == 2:
                    frames["DOWN"].append(frame)
                elif row == 3:
                    frames["RIGHT"].append(frame)
                # Если нужен idle — можно взять первый кадр из любого ряда
        # Добавим idle как первый кадр "DOWN"
        frames["IDLE"].append(frames["DOWN"][0])

        return frames

    def move(self, direction, boxmap):
        """Перемещение игрока и смена направления"""
        directions = {
            "UP": (0, -1),   # W — вверх
            "DOWN": (0, +1), # S — вниз
            "LEFT": (-1, 0), # A — влево
            "RIGHT": (+1, 0) # D — вправо
        }

        dx, dy = directions[direction]
        new_x = self.x + dx
        new_y = self.y + dy

        if boxmap.is_inside(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.direction = direction  # обновляем направление

    def get_image(self):
        """Возвращает текущий кадр спрайта"""
        # пока берём первый кадр для каждого направления
        return self.frames[self.direction][0]
