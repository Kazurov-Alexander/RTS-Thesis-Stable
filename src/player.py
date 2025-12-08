class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100

    def move(self, direction, boxmap):
        directions = {
            "UP": (0, -1),# W — строго вверх
            "DOWN": (0, +1),# S — строго вниз
            "LEFT": (-1, 0),# A — строго влево
            "RIGHT": (+1, 0),# D — строго вправо
        }

        dx, dy = directions[direction]
        new_x = self.x + dx
        new_y = self.y + dy

        if boxmap.is_inside(new_x, new_y):
            self.x = new_x
            self.y = new_y
