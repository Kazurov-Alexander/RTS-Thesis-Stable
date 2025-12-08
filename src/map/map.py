class BoxMap:
    def __init__(self, radius=10, tile_size=40):
        self.radius = radius
        self.tile_size = tile_size
        self.tiles = {}
        self.generate_boxes()

    def generate_boxes(self):
        # генерируем квадратную область [-radius, radius] × [-radius, radius]
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                self.tiles[(x, y)] = "grass"

    def is_inside(self, x, y):
        return abs(x) <= self.radius and abs(y) <= self.radius
