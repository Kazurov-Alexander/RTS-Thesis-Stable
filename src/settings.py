import datetime        # модуль для работы с датой и временем
import subprocess      # модуль для выполнения системных команд (например, git)
import pygame as pg    # библиотека pygame для графики

# --- Текущие настройки (меняются в игре и меню) ---
CURRENT_WIDTH = 1920          # текущая ширина окна/экрана
CURRENT_HEIGHT = 1080         # текущая высота окна/экрана
CURRENT_MODE = "Полноэкранный"  # режим отображения: "Полноэкранный" или "Оконный режим"
CURRENT_VOLUME = 1.0          # текущая громкость (от 0.0 до 1.0)

# --- Константы ---
FPS = 60                      # количество кадров в секунду
BACKGROUND_COLOR = (30, 30, 30)  # цвет фона (RGB)

FONT_PATH = "assets/fonts/main_font.ttf"  # путь к основному шрифту
FONT_SIZE_TITLE = 38                      # размер шрифта для заголовков
FONT_SIZE_OPTION = 22                     # размер шрифта для опций меню

def get_last_commit_date():
    """Возвращает дату последнего коммита Git в формате YYYY-MM-DD."""
    try:
        # выполняем команду git для получения даты последнего коммита
        date_str = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short"],
            encoding="utf-8"
        ).strip()
        return date_str
    except Exception:
        # fallback: если git недоступен, берём текущую дату
        return datetime.datetime.now().strftime("%Y-%m-%d")

# Версия игры с датой последнего коммита
VERSION_NUMBER = "v0.1.4"  # номер версии
GAME_VERSION = f"{VERSION_NUMBER} ({get_last_commit_date()})"  # версия + дата коммита

# --- Опции меню ---
MENU_OPTIONS = [
    "Новая игра",
    "Загрузить игру",
    "Настройки",
    "Выход"
]

# --- Режимы отображения ---
DISPLAY_MODES = [
    "Полноэкранный",  # индекс 0
    "Оконный режим",  # индекс 1
]

# --- Отступы для каждого режима (связаны по индексу с DISPLAY_MODES) ---
WINDOW_MARGINS = [
    (0, 0),    # для полноэкранного режима (без отступов)
    (20, 80),  # для оконного режима (учёт границ окна)
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
    _instance = None  # единственный экземпляр класса
    _screen = None    # объект экрана

    def __new__(cls):
        # создаём новый экземпляр только один раз
        if cls._instance is None:
            cls._instance = super(ScreenManager, cls).__new__(cls)
        return cls._instance

    def get_screen(self):
        # возвращаем экран, создаём если ещё не создан
        if self._screen is None:
            self._screen = self._create_screen()
        return self._screen

    def reset_screen(self):
        # пересоздаём экран при смене режима
        self._screen = self._create_screen()
        return self._screen

    @staticmethod
    def _create_screen():
        # определяем индекс режима (0 = полноэкранный, 1 = оконный)
        mode_index = DISPLAY_MODES.index(CURRENT_MODE)
        margin_x, margin_y = WINDOW_MARGINS[mode_index]  # отступы для режима
        flags = pg.FULLSCREEN if mode_index == 0 else 0  # флаг режима

        # вычисляем размеры окна с учётом отступов
        width = CURRENT_WIDTH - margin_x
        height = CURRENT_HEIGHT - margin_y

        # создаём окно игры
        screen = pg.display.set_mode((width, height), flags)
        pg.display.set_caption(f"RTS Thesis Project {GAME_VERSION}")  # заголовок окна
        return screen
