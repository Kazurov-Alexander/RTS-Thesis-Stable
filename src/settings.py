import datetime

# --- Текущие настройки (меняются в игре и меню) ---
CURRENT_WIDTH = 1920
CURRENT_HEIGHT = 1080
CURRENT_MODE = "Оконный режим"   # или "Полноэкранный", "Полноэкранный без рамки"
CURRENT_VOLUME = 1.0

# --- Константы ---
FPS = 60
BACKGROUND_COLOR = (30, 30, 30)

FONT_PATH = "assets/fonts/main_font.ttf"
FONT_SIZE_TITLE = 38
FONT_SIZE_OPTION = 22

# Версия игры с датой сборки
GAME_VERSION = "v1.0.0 (" + datetime.datetime.now().strftime("%Y-%m-%d") + ")"

# --- Опции меню ---
MENU_OPTIONS = [
    "Новая игра",
    "Загрузить игру",
    "Настройки",
    "Выход"
]

DISPLAY_MODES = [
    "Оконный режим",
    "Полноэкранный",
    "Полноэкранный без рамки",
]

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
