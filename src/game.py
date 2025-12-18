import sys  # стандартный модуль для выхода из программы
import pygame as pg  # библиотека pygame для графики и управления

from src import settings  # модуль с настройками игры
from src.entities.player import Player  # класс игрока
from src.map.map import BoxMap  # класс карты
from src.map.obstacles import is_blocked  # функция проверки препятствий
from src.map.renderer import draw_map, box_to_pixel  # функции для отрисовки карты и перевода координат
from src.systems.spawner import spawn_obstacles, spawn_enemies, generate_weapons  # генераторы объектов
# from src.systems.save_load import save_game, load_game  # импортируем функции сохранения/загрузки
# from src.map.obstacles import Obstacle, MountainGroup, WaterGroup

def main():
    pg.init()  # инициализация pygame
    screen = settings.ScreenManager().get_screen()  # создаём экран
    clock = pg.time.Clock()  # создаём таймер для FPS

    box_map = BoxMap(radius=50)  # создаём карту

    # --- генерация объектов ---
    obstacles = spawn_obstacles(box_map)  # создаём препятствия

    # создаём игрока в центре
    player = Player(x=0, y=0)

    # если клетка занята — перезапускаем игру
    if is_blocked(int(player.x), int(player.y), obstacles):
        print("Стартовая клетка занята, перезапуск игры...")
        return main()  # рекурсивный вызов main()

    # создаём врагов
    enemies = spawn_enemies(num_enemies=10, box_map=box_map,
                            player=player, min_distance=10, obstacles=obstacles)

    # создаём оружие
    weapons = generate_weapons(box_map, obstacles)

    tile_size = 40  # размер тайла
    running, paused = True, False  # флаги состояния игры

    # шрифты для текста
    font_normal = pg.font.SysFont(None, 48, bold=False)
    font_bold = pg.font.SysFont(None, 48, bold=True)
    font_gameover = pg.font.SysFont(None, 120, bold=True)
    font_victory = pg.font.SysFont(None, 120, bold=True)
    font_counter = pg.font.SysFont(None, 36, bold=True)  # шрифт для счётчика врагов

    # функция отрисовки полоски здоровья
    def draw_health_bar(x, y, health, max_health, width=200, height=20):
        pg.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)  # рамка
        fill_width = int((health / max_health) * (width - 4))  # ширина заполнения
        pg.draw.rect(screen, (200, 50, 50), (x + 2, y + 2, fill_width, height - 4))  # красная полоска

    while running:  # основной цикл игры
        for event in pg.event.get():  # обработка событий
            if event.type == pg.QUIT:  # выход из игры
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # пауза по ESC
                paused = not paused
            elif event.type == pg.MOUSEBUTTONDOWN and paused:  # меню при паузе
                if event.button == 1:  # левая кнопка мыши
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
            elif event.type == pg.MOUSEWHEEL and not paused:  # масштабирование карты колесиком мыши
                if event.y > 0:
                    tile_size = min(tile_size + 5, 100)
                elif event.y < 0:
                    tile_size = max(tile_size - 5, 10)

            # --- атака игрока по пробелу ---
            elif event.type == pg.KEYDOWN and not paused and player.alive:
                if event.key == pg.K_SPACE:
                    nearest_enemy = None
                    nearest_dist = float("inf")  # начальное значение — бесконечность
                    for enemy in enemies:  # ищем ближайшего врага
                        dist = ((enemy.x - player.x) ** 2 + (enemy.y - player.y) ** 2) ** 0.5
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest_enemy = enemy
                    if nearest_enemy and nearest_dist <= 1.5:  # радиус атаки игрока
                        player.attack(nearest_enemy)

        if not paused:  # если игра не на паузе
            # --- Управление игроком ---
            keys = pg.key.get_pressed()
            if player.alive:  # мёртвый игрок не двигается
                if keys[pg.K_w]:
                    player.move("UP", box_map, obstacles, is_blocked_fn=is_blocked)
                elif keys[pg.K_s]:
                    player.move("DOWN", box_map, obstacles, is_blocked_fn=is_blocked)
                elif keys[pg.K_a]:
                    player.move("LEFT", box_map, obstacles, is_blocked_fn=is_blocked)
                elif keys[pg.K_d]:
                    player.move("RIGHT", box_map, obstacles, is_blocked_fn=is_blocked)

            # --- Подбор оружия ---
            for weapon in weapons:
                if not weapon.picked and weapon.x == player.x and weapon.y == player.y:
                    weapon.picked = True
                    player.weapon = weapon

            # --- Камера ---
            px, py = box_to_pixel(player.x, player.y, tile_size)
            offset_x = screen.get_width() // 2 - px - tile_size // 4
            offset_y = screen.get_height() // 2 - py - tile_size // 4

            # --- Отрисовка ---
            screen.fill(settings.BACKGROUND_COLOR)  # фон
            draw_map(screen, box_map, size=tile_size, offset_x=offset_x, offset_y=offset_y)  # карта

            for obs in obstacles:  # препятствия
                obs.draw(screen, tile_size, offset_x, offset_y)
            for weapon in weapons:  # оружие
                weapon.draw(screen, tile_size, offset_x, offset_y)

            # --- Игрок ---
            player.draw(screen, tile_size, offset_x, offset_y)
            draw_health_bar(20, 20, player.health, player.max_health)

            # --- Счётчик живых врагов ---
            alive_enemies = sum(1 for enemy in enemies if enemy.alive)  # считаем живых
            counter_surface = font_counter.render(f"Врагов осталось: {alive_enemies}", True, (255, 255, 255))
            counter_rect = counter_surface.get_rect(topright=(screen.get_width() - 20, 20))
            screen.blit(counter_surface, counter_rect)

            # --- Проверка смерти игрока ---
            if not player.alive:
                text_surface = font_gameover.render("GAME OVER", True, (200, 0, 0))
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                screen.blit(text_surface, text_rect)

            # --- Проверка победы ---
            elif all(not enemy.alive for enemy in enemies):
                text_surface = font_victory.render("VICTORY", True, (0, 0, 200))
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                screen.blit(text_surface, text_rect)

            # --- Враги ---
            for enemy in enemies:
                if not is_blocked(enemy.x, enemy.y, obstacles):
                    # передаём player внутрь update
                    enemy.update(player.x, player.y, box_map, obstacles, player_alive=player.alive, player=player)

                # если игрок жив и враг рядом — атакует
                dist = ((enemy.x - player.x) ** 2 + (enemy.y - player.y) ** 2) ** 0.5
                if dist <= 1.1 and player.alive:
                    enemy.attack(player)

                # отрисовка врага
                enemy_img = pg.transform.scale(enemy.get_image(), (tile_size, tile_size))
                screen.blit(enemy_img, (int(enemy.x * tile_size + offset_x),
                                        int(enemy.y * tile_size + offset_y)))

        else:
            # --- Меню ---
            screen.fill((30, 30, 30))
            options = ["Продолжить", "Сохранить игру", "Загрузить игру",
                   "Выход в главное меню", "Выйти из игры"]
            mouse_pos = pg.mouse.get_pos()
            for i, text in enumerate(options):
                rect = pg.Rect(screen.get_width() // 2 - 150, 180 + i * 60, 300, 50)
                label = (font_bold if rect.collidepoint(mouse_pos) else font_normal).render(text, True, (255, 255, 255))
                screen.blit(label, label.get_rect(center=rect.center))

        pg.display.flip() # обновляем экран
        clock.tick(settings.FPS) # ограничиваем FPS

        # Раскоммент для сохранений (в разработке)
        # else:  # если игра на паузе
        # screen.fill((30, 30, 30))
        # options = [
        #     "Продолжить",
        #     "Сохранение",
        #     "Загрузка",
        #     "Выход в главное меню",
        #     "Выйти из игры"
        # ]
        #
        # mouse_pos = pg.mouse.get_pos()
        # rects = []
        # for i, text in enumerate(options):
        #     rect = pg.Rect(screen.get_width() // 2 - 200, 150 + i * 60, 400, 50)
        #     rects.append((rect, text))
        #     label = (font_bold if rect.collidepoint(mouse_pos) else font_normal).render(
        #         text, True, (255, 255, 255)
        #     )
        #     screen.blit(label, label.get_rect(center=rect.center))
        #
        # # обработка кликов
        # for event in pg.event.get():
        #     if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        #         for rect, text in rects:
        #             if rect.collidepoint(event.pos):
        #                 if text == "Продолжить":
        #                     paused = False
        #                 elif text == "Сохранение":
        #                     save_game(player, enemies, obstacles)
        #                 elif text == "Загрузка":
        #                     data = load_game()
        #                     if data:
        #                         player.x = data["player"]["x"]
        #                         player.y = data["player"]["y"]
        #                         player.health = data["player"]["health"]
        #
        #                         for e, saved in zip(enemies, data["enemies"]):
        #                             e.x, e.y, e.alive = saved["x"], saved["y"], saved["alive"]
        #
        #                         obstacles.clear()
        #                         obstacles.extend(data["obstacles"])  # уже готовые объекты
        #                 elif text == "Выход в главное меню":
        #                     running = False
        #                 elif text == "Выйти из игры":
        #                     pg.quit()
        #                     sys.exit()

        pg.display.flip()
        clock.tick(settings.FPS)


