import sys
import pygame as pg
from src import settings
from src.map.map import BoxMap
from src.map.renderer import draw_map, box_to_pixel
from src.entities.player import Player
from src.map.obstacles import is_blocked
from src.systems.spawner import spawn_obstacles, spawn_enemies, spawn_weapons

# ---------- Вспомогательная функция перекраски ----------
def tint_image(image, color):
    """Перекрашивает спрайт в указанный цвет"""
    tinted = image.copy()
    tinted.fill(color, special_flags=pg.BLEND_RGBA_MULT)
    return tinted

# ---------- Основной цикл ----------
def main():
    pg.init()

    # --- выбор режима окна ---
    flags = 0
    if settings.CURRENT_MODE == "Полноэкранный":
        flags = pg.FULLSCREEN
    elif settings.CURRENT_MODE == "Полноэкранный без рамки":
        flags = pg.NOFRAME | pg.FULLSCREEN

    screen = pg.display.set_mode((settings.CURRENT_WIDTH, settings.CURRENT_HEIGHT), flags)
    pg.display.set_caption("RTS Thesis Project")

    clock = pg.time.Clock()
    box_map = BoxMap(radius=50)
    player = Player(x=0, y=0)

    # --- генерация объектов ---
    obstacles = spawn_obstacles(box_map)
    enemies = spawn_enemies(num_enemies=10, box_map=box_map, player=player, min_distance=10, obstacles=obstacles)
    weapons = spawn_weapons(box_map, obstacles)

    tile_size = 40
    running = True
    paused = False

    font_normal = pg.font.SysFont(None, 48, bold=False)
    font_bold = pg.font.SysFont(None, 48, bold=True)

    def draw_health_bar(screen, x, y, health, max_health, width=200, height=20):
        # рамка
        pg.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        # заполнение
        fill_width = int((health / max_health) * (width - 4))
        pg.draw.rect(screen, (200, 50, 50), (x + 2, y + 2, fill_width, height - 4))

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                paused = not paused

            elif event.type == pg.MOUSEBUTTONDOWN and paused:
                if event.button == 1:  # ЛКМ
                    mouse_pos = pg.mouse.get_pos()
                    options = ["Продолжить", "Сохранить игру", "Загрузить игру",
                               "Выход в главное меню", "Выйти из игры"]

                    for i, text in enumerate(options):
                        rect = pg.Rect(screen.get_width() // 2 - 150, 180 + i * 60, 300, 50)
                        if rect.collidepoint(mouse_pos):
                            if text == "Продолжить":
                                paused = False
                            elif text == "Выйти из игры":
                                pg.quit()
                                sys.exit()
                            elif text == "Выход в главное меню":
                                running = False

            elif event.type == pg.MOUSEWHEEL and not paused:
                if event.y > 0:
                    tile_size = min(tile_size + 5, 100)
                elif event.y < 0:
                    tile_size = max(tile_size - 5, 10)

        if not paused:
            # --- Управление игроком ---
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                new_x, new_y = player.x, player.y - 1
                if not is_blocked(new_x, new_y, obstacles):
                    player.move("UP", box_map)
            elif keys[pg.K_s]:
                new_x, new_y = player.x, player.y + 1
                if not is_blocked(new_x, new_y, obstacles):
                    player.move("DOWN", box_map)
            elif keys[pg.K_a]:
                new_x, new_y = player.x - 1, player.y
                if not is_blocked(new_x, new_y, obstacles):
                    player.move("LEFT", box_map)
            elif keys[pg.K_d]:
                new_x, new_y = player.x + 1, player.y
                if not is_blocked(new_x, new_y, obstacles):
                    player.move("RIGHT", box_map)

            # --- Проверка подбора оружия ---
            for weapon in weapons:
                if not weapon.picked and weapon.x == player.x and weapon.y == player.y:
                    weapon.picked = True
                    player.weapon = weapon

            # --- Камера ---
            px, py = box_to_pixel(player.x, player.y, tile_size)
            offset_x = screen.get_width() // 2 - px - tile_size // 4
            offset_y = screen.get_height() // 2 - py - tile_size // 4

            # --- Отрисовка карты ---
            screen.fill(settings.BACKGROUND_COLOR)
            draw_map(screen, box_map, size=tile_size, offset_x=offset_x, offset_y=offset_y)

            # --- Отрисовка препятствий ---
            for obs in obstacles:
                obs.draw(screen, tile_size, offset_x, offset_y)

            # --- Отрисовка оружия ---
            for weapon in weapons:
                weapon.draw(screen, tile_size, offset_x, offset_y)

            # --- Игрок ---
            player_img = pg.transform.scale(player.get_image(), (tile_size, tile_size))
            player_img = tint_image(player_img, (50, 50, 255))  # синий
            screen.blit(player_img, (int(px + offset_x), int(py + offset_y)))

            # --- Health bar HUD ---
            draw_health_bar(screen, 20, 20, player.health, player.max_health)

            # --- Логика врагов ---
            for enemy in enemies:
                if not is_blocked(enemy.x, enemy.y, obstacles):
                    enemy.update(player.x, player.y, box_map, obstacles)
                enemy_img = pg.transform.scale(enemy.get_image(), (tile_size, tile_size))
                enemy_img = tint_image(enemy_img, (255, 50, 50))  # красный
                screen.blit(enemy_img, (int(enemy.x * tile_size + offset_x),
                                        int(enemy.y * tile_size + offset_y)))

        else:
            # --- Отрисовка меню ---
            screen.fill((30, 30, 30))
            options = ["Продолжить", "Сохранить игру", "Загрузить игру",
                       "Выход в главное меню", "Выйти из игры"]

            mouse_pos = pg.mouse.get_pos()

            for i, text in enumerate(options):
                rect = pg.Rect(screen.get_width() // 2 - 150, 180 + i * 60, 300, 50)
                if rect.collidepoint(mouse_pos):
                    label = font_bold.render(text, True, (255, 255, 255))
                else:
                    label = font_normal.render(text, True, (255, 255, 255))
                label_rect = label.get_rect(center=rect.center)
                screen.blit(label, label_rect)

        pg.display.flip()
        clock.tick(settings.FPS)
