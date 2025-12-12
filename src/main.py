import pygame as pg
import pygame.mixer as pgm
import settings
from menu import draw_menu

def main():
    pg.init()
    pgm.init()

    # --- получаем экран через синглтон ---
    screen = settings.ScreenManager().get_screen()

    hover_sound = pgm.Sound("assets/sounds/ui/hover.wav")

    # Музыка меню
    pgm.music.load("assets/music/menu_music.mp3")
    pgm.music.set_volume(settings.CURRENT_VOLUME)
    pgm.music.play(-1)

    clock = pg.time.Clock()
    running = True
    last_hovered = None
    mode = "main"
    settings_submenu = None
    dragging = False

    # виртуальный экран для интерфейса
    virtual_screen = pg.Surface((settings.CURRENT_WIDTH, settings.CURRENT_HEIGHT))

    while running:
        virtual_screen.fill(settings.BACKGROUND_COLOR)

        option_rects = draw_menu(virtual_screen, mode, settings_submenu, settings.CURRENT_VOLUME)

        hovered_now = None

        # переводим мышь в виртуальные координаты
        screen_w, screen_h = screen.get_size()
        scale_x = settings.CURRENT_WIDTH / screen_w
        scale_y = settings.CURRENT_HEIGHT / screen_h
        mouse_pos_virtual = (int(pg.mouse.get_pos()[0] * scale_x),
                             int(pg.mouse.get_pos()[1] * scale_y))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for option, rect in option_rects:
                    if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos_virtual):
                        if option == "Выход":
                            running = False

                        elif option == "Настройки":
                            mode = "settings"
                            settings_submenu = None

                        elif option == "Новая игра":
                            # переключаем музыку
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
                            dragging = True  # начинаем перетаскивание

                        elif "x" in option and settings_submenu == "resolution":
                            try:
                                w, h = map(int, option.split("x"))
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
                dragging = False

        # Перетаскивание ползунка
        if dragging and settings_submenu == "volume":
            track_rect = None
            for option, rect in option_rects:
                if option == "volume_track" and isinstance(rect, pg.Rect):
                    track_rect = rect
                    break

            if track_rect:
                rel_x = mouse_pos_virtual[0] - track_rect.x
                rel_x = max(0, min(track_rect.width, rel_x))
                settings.CURRENT_VOLUME = rel_x / track_rect.width
                pgm.music.set_volume(settings.CURRENT_VOLUME)

        # Наведение
        for option, rect in option_rects:
            if isinstance(rect, pg.Rect) and rect.collidepoint(mouse_pos_virtual):
                hovered_now = option

        if hovered_now != last_hovered and hovered_now is not None:
            hover_sound.play()
            last_hovered = hovered_now

        # масштабируем виртуальный экран под реальный
        scaled = pg.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled, (0, 0))

        pg.display.flip()
        clock.tick(settings.FPS)

    # Закрываем pygame только при полном выходе
    pg.quit()

if __name__ == "__main__":
    main()
