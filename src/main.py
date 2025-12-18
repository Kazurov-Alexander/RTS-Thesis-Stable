import pygame as pg              # библиотека pygame для графики и событий
import pygame.mixer as pgm       # модуль pygame для работы со звуком и музыкой

import settings                  # модуль с настройками игры
from menu import draw_menu       # функция отрисовки меню

def main():
    pg.init()                    # инициализация pygame
    pgm.init()                   # инициализация звукового модуля

    # --- получаем экран через синглтон ---
    screen = settings.ScreenManager().get_screen()

    hover_sound = pgm.Sound("assets/sounds/ui/hover.wav")  # звук наведения курсора

    # Музыка меню
    pgm.music.load("assets/music/menu_music.mp3")          # загружаем музыку меню
    pgm.music.set_volume(settings.CURRENT_VOLUME)          # выставляем громкость
    pgm.music.play(-1)                                     # проигрываем в цикле (-1 = бесконечно)

    clock = pg.time.Clock()        # таймер для FPS
    running = True                 # флаг работы программы
    last_hovered = None            # последняя наведённая опция
    mode = "main"                  # режим меню (главное меню)
    settings_submenu = None        # подменю настроек
    dragging = False               # флаг перетаскивания ползунка громкости

    # виртуальный экран для интерфейса (масштабируемый)
    virtual_screen = pg.Surface((settings.CURRENT_WIDTH, settings.CURRENT_HEIGHT))

    while running:  # основной цикл меню
        virtual_screen.fill(settings.BACKGROUND_COLOR)  # фон меню

        # отрисовываем меню и получаем список опций с их прямоугольниками
        option_rects = draw_menu(virtual_screen, mode, settings_submenu, settings.CURRENT_VOLUME)

        hovered_now = None  # текущая наведённая опция

        # переводим координаты мыши в виртуальные координаты
        screen_w, screen_h = screen.get_size()
        scale_x = settings.CURRENT_WIDTH / screen_w
        scale_y = settings.CURRENT_HEIGHT / screen_h
        mouse_pos_virtual = (int(pg.mouse.get_pos()[0] * scale_x),
                             int(pg.mouse.get_pos()[1] * scale_y))

        for event in pg.event.get():  # обработка событий
            if event.type == pg.QUIT:  # выход из программы
                running = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # выход по ESC
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # клик мышью
                for option, rect in option_rects:  # проверяем все опции меню
                    if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos_virtual):
                        if option == "Выход":
                            running = False

                        elif option == "Настройки":
                            mode = "settings"
                            settings_submenu = None

                        elif option == "Новая игра":
                            # переключаем музыку на игровую
                            pgm.music.stop()
                            pgm.music.load("assets/music/game_music_ambient.mp3")
                            pgm.music.set_volume(settings.CURRENT_VOLUME)
                            pgm.music.play(-1)

                            # запускаем игровой цикл
                            from game import main as game_main
                            game_main()

                            # после выхода из игры возвращаемся в меню
                            pgm.music.stop()
                            pgm.music.load("assets/music/menu_music.mp3")
                            pgm.music.set_volume(settings.CURRENT_VOLUME)
                            pgm.music.play(-1)

                        elif option == "Назад":
                            mode = "main"
                            settings_submenu = None
                            dragging = False

                        elif option == "Разрешение экрана":
                            settings_submenu = "resolution"

                        elif option == "Режим окна":
                            settings_submenu = "display_mode"

                        elif option == "Громкость":
                            settings_submenu = "volume"

                        elif option == "volume_slider":
                            dragging = True  # начинаем перетаскивание ползунка громкости

                        elif "x" in option and settings_submenu == "resolution":
                            try:
                                w, h = map(int, option.split("x"))  # парсим разрешение
                                settings.CURRENT_WIDTH = w
                                settings.CURRENT_HEIGHT = h
                                virtual_screen = pg.Surface((w, h))  # обновляем виртуальный экран
                            except:
                                pass

                        elif option in settings.DISPLAY_MODES and settings_submenu == "display_mode":
                            settings.CURRENT_MODE = option
                            # пересоздаём экран через Singleton
                            screen = settings.ScreenManager().reset_screen()

            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                dragging = False  # отпускаем ползунок

        # Перетаскивание ползунка громкости
        if dragging and settings_submenu == "volume":
            track_rect = None
            for option, rect in option_rects:
                if option == "volume_track" and isinstance(rect, pg.Rect):
                    track_rect = rect
                    break

            if track_rect:
                rel_x = mouse_pos_virtual[0] - track_rect.x  # позиция мыши относительно трека
                rel_x = max(0, min(track_rect.width, rel_x))  # ограничиваем в пределах трека
                settings.CURRENT_VOLUME = rel_x / track_rect.width  # вычисляем громкость
                pgm.music.set_volume(settings.CURRENT_VOLUME)      # применяем громкость

        # Наведение курсора на опцию
        for option, rect in option_rects:
            if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos_virtual):
                hovered_now = option

        # если наведена новая опция — проигрываем звук
        if hovered_now != last_hovered and hovered_now is not None:
            hover_sound.play()
            last_hovered = hovered_now

        # масштабируем виртуальный экран под реальный
        scaled = pg.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled, (0, 0))

        pg.display.flip()          # обновляем экран
        clock.tick(settings.FPS)   # ограничиваем FPS

    # Закрываем pygame только при полном выходе
    pg.quit()

if __name__ == "__main__":
    main()  # запускаем функцию main при старте программы
