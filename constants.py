"""Глобальные конфигурационные константы игры 'Змейка'.

Модуль инкапсулирует все статические настройки приложения,
разделенные на блоки:
    - Размеры графического окна и математические параметры координатной сетки.
    - Двумерные векторы направлений дискретного перемещения.
    - Цветовые палитры (RGB-кортежи) для фонов, интерфейса и базовых объектов.
    - Настройки физики (скорость, длительность штрафной заморозки `bounce`).
    - Относительные файловые пути к растровым графическим ассетам (.png).

Все геометрические расчеты опираются на размер ячейки GRID_SIZE. Векторы
движения используют декартову систему координат, где начало (0, 0) находится
в левом верхнем углу экрана (ось Y направлена вниз).
"""
import pygame as pg

# Геометрия игрового поля и координатной сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Дискретные векторы направлений движения (X, Y)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
    pg.K_w: (UP, DOWN),
    pg.K_s: (DOWN, UP),
    pg.K_a: (LEFT, RIGHT),
    pg.K_d: (RIGHT, LEFT),
}

# Цветовая палитра RGB
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_PURPLE = (128, 0, 128)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_ICE_BLUE = (93, 216, 228)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (40, 40, 40)

# Цвета игровых объектов и интерфейса
BOARD_BACKGROUND_COLOR = COLOR_BLACK
BORDER_COLOR = COLOR_ICE_BLUE
APPLE_COLOR = COLOR_RED
BAD_APPLE_COLOR = COLOR_PURPLE
SNAKE_COLOR = COLOR_GREEN
STONE_COLOR = COLOR_GRAY

# Физические параметры игрового процесса
SPEED = 5
BOUNCE_FREEZE_TICKS = 5

# Пути к готовым спрайтам объектов окружения:
APPLE_IMG_PATH = 'assets/apple_64.png'
BAD_APPLE_IMG_PATH = 'assets/mushroom_64.png'
STONE_IMG_PATH = 'assets/stone_small.png'
MOUNTAIN_IMG_PATH = 'assets/mountain_big.png'

# Пути к спрайтам змейки
SNAKE_HEAD_UP = 'assets/snake_green_head_64_u.png'
SNAKE_HEAD_DOWN = 'assets/snake_green_head_64_d.png'
SNAKE_HEAD_LEFT = 'assets/snake_green_head_64_l.png'
SNAKE_HEAD_RIGHT = 'assets/snake_green_head_64_r.png'
SNAKE_BODY_IMG = 'assets/snake_green_64_ud.png'
