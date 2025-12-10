import pygame as pg
import settings  # модуль с константами, где есть GAME_VERSION и CURRENT_* параметры

def render_button(screen, text, center_x, center_y, mouse_pos):
    font = pg.font.Font(settings.FONT_PATH, settings.FONT_SIZE_OPTION)
    temp_surface = font.render(text, True, (0, 0, 0))
    temp_rect = temp_surface.get_rect(center=(center_x, center_y))

    is_hovered = temp_rect.collidepoint(mouse_pos)
    font.set_bold(is_hovered)
    color = (255, 255, 255) if is_hovered else (200, 200, 200)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    screen.blit(text_surface, text_rect)

    return text, text_rect

def draw_volume_slider(screen, mouse_pos, current_volume):
    # Параметры слайдера (в виртуальных координатах)
    slider_x = settings.CURRENT_WIDTH // 2 - 150
    slider_y = 250
    slider_width = 300
    slider_height = 10

    # Прямоугольник трека
    track_rect = pg.Rect(slider_x, slider_y, slider_width, slider_height)
    pg.draw.rect(screen, (180, 180, 180), track_rect)

    # Позиция ползунка
    knob_x = slider_x + int(current_volume * slider_width)
    knob_y = slider_y + slider_height // 2

    knob_rect = pg.Rect(knob_x - 8, knob_y - 8, 16, 16)
    pg.draw.rect(screen, (255, 255, 255), knob_rect)

    return knob_rect, track_rect

def draw_menu(screen, mode="main", submode=None, current_volume=None):
    try:
        background = pg.image.load("assets/images/ui/background_menu.png")
        background = pg.transform.scale(background, (settings.CURRENT_WIDTH, settings.CURRENT_HEIGHT))
        screen.blit(background, (0, 0))
    except:
        screen.fill(settings.BACKGROUND_COLOR)

    font_title = pg.font.Font(settings.FONT_PATH, settings.FONT_SIZE_TITLE)

    # --- масштабируем мышь в виртуальные координаты ---
    screen_w, screen_h = pg.display.get_surface().get_size()
    scale_x = settings.CURRENT_WIDTH / screen_w
    scale_y = settings.CURRENT_HEIGHT / screen_h
    mouse_pos = (int(pg.mouse.get_pos()[0] * scale_x),
                 int(pg.mouse.get_pos()[1] * scale_y))

    option_rects = []

    if mode == "main":
        title_surface = font_title.render("RTS Thesis Project", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(settings.CURRENT_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        for i, option in enumerate(settings.MENU_OPTIONS):
            item = render_button(screen, option, settings.CURRENT_WIDTH // 2, 200 + i * 60, mouse_pos)
            option_rects.append(item)

    elif mode == "settings":
        title_surface = font_title.render("Настройки", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(settings.CURRENT_WIDTH // 2, 60))
        screen.blit(title_surface, title_rect)

        if submode is None:
            for i, tab in enumerate(settings.DISPLAY_SETTINGS_MENU):
                item = render_button(screen, tab, settings.CURRENT_WIDTH // 2, 140 + i * 50, mouse_pos)
                option_rects.append(item)
        else:
            selected_tab_text = get_tab_text(submode)
            if selected_tab_text:
                font_tab = pg.font.Font(settings.FONT_PATH, settings.FONT_SIZE_OPTION)
                tab_surface = font_tab.render(selected_tab_text, True, (255, 255, 255))
                tab_rect = tab_surface.get_rect(center=(settings.CURRENT_WIDTH // 2, 120))
                screen.blit(tab_surface, tab_rect)

            if submode == "resolution":
                for i, (w, h) in enumerate(settings.RESOLUTIONS):
                    text = f"{w} x {h}"
                    item = render_button(screen, text, settings.CURRENT_WIDTH // 2, 220 + i * 30, mouse_pos)
                    option_rects.append(item)

            elif submode == "display_mode":
                for i, mode_name in enumerate(settings.DISPLAY_MODES):
                    item = render_button(screen, mode_name, settings.CURRENT_WIDTH // 2, 220 + i * 40, mouse_pos)
                    option_rects.append(item)

            elif submode == "volume":
                if current_volume is None:
                    current_volume = settings.CURRENT_VOLUME
                knob_rect, track_rect = draw_volume_slider(screen, mouse_pos, current_volume)
                option_rects.append(("volume_slider", knob_rect))
                option_rects.append(("volume_track", track_rect))

        # "Назад"
        item = render_button(screen, "Назад", settings.CURRENT_WIDTH // 2, settings.CURRENT_HEIGHT - 200, mouse_pos)
        option_rects.append(item)

    # --- Версия игры справа снизу ---
    font_version = pg.font.Font(settings.FONT_PATH, 20)
    version_surface = font_version.render(settings.GAME_VERSION, True, (200, 200, 200))
    version_rect = version_surface.get_rect(bottomright=(settings.CURRENT_WIDTH - 10, settings.CURRENT_HEIGHT - 10))
    screen.blit(version_surface, version_rect)

    return option_rects

def get_tab_text(submode):
    if submode == "resolution":
        return "Разрешение экрана"
    elif submode == "display_mode":
        return "Режим окна"
    elif submode == "volume":
        return "Громкость"
    return None
