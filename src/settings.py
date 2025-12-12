import subprocess
import datetime
import pygame as pg

# --- Текущие настройки (меняются в игре и меню) ---
CURRENT_WIDTH = 1920
CURRENT_HEIGHT = 1080
CURRENT_MODE = "Полноэкранный"   # или "Оконный режим"
CURRENT_VOLUME = 1.0

# --- Константы ---
FPS = 60
BACKGROUND_COLOR = (30, 30, 30)

FONT_PATH = "assets/fonts/main_font.ttf"
FONT_SIZE_TITLE = 38
FONT_SIZE_OPTION = 22

def get_last_commit_date():
    """Возвращает дату последнего коммита Git в формате YYYY-MM-DD."""
    try:
        date_str = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short"],
            encoding="utf-8"
        ).strip()
        return date_str
    except Exception:
        # fallback: если git недоступен
        return datetime.datetime.now().strftime("%Y-%m-%d")

# Версия игры с датой последнего коммита
VERSION_NUMBER = "v1.0.4"
GAME_VERSION = f"{VERSION_NUMBER} ({get_last_commit_date()})"

# --- Опции меню ---
MENU_OPTIONS = [
    "Новая игра",
    "Загрузить игру",
    "Настройки",
    "Выход"
]

# --- Режимы отображения ---
DISPLAY_MODES = [
    "Полноэкранный",   # индекс 0
    "Оконный режим",   # индекс 1
]

# --- Отступы для каждого режима (связаны по индексу с DISPLAY_MODES) ---
WINDOW_MARGINS = [
    (0, 0),    # для полноэкранного режима
    (20, 80),  # для оконного режима (границы окна)
]

# --- Настройки меню ---
DISPLAY_SETTINGS_MENU = [
    "Разрешение экрана",
    "Режим окна",
    "Громкость"
]

RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
]

# --- Singleton для экрана ---
class ScreenManager:
    _instance = None
    _screen = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScreenManager, cls).__new__(cls)
        return cls._instance

    def get_screen(self):
        if self._screen is None:
            self._screen = self._create_screen()
        return self._screen

    def reset_screen(self):
        # пересоздаём экран при смене режима
        self._screen = self._create_screen()
        return self._screen

    @staticmethod
    def _create_screen():
        mode_index = DISPLAY_MODES.index(CURRENT_MODE)
        margin_x, margin_y = WINDOW_MARGINS[mode_index]
        flags = pg.FULLSCREEN if mode_index == 0 else 0

        width = CURRENT_WIDTH - margin_x
        height = CURRENT_HEIGHT - margin_y
        screen = pg.display.set_mode((width, height), flags)
        pg.display.set_caption(f"RTS Thesis Project {GAME_VERSION}")
        return screen

