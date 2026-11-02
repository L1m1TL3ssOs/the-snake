# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет гнилого яблока
BAD_APPLE_COLOR = (148, 0, 211)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет камня
STONE_COLOR = (128, 128, 128)

# Скорость движения змейки:
SPEED = 5

# Таймер замерания змейки:
BOUNCE_FREEZE_TICKS = 5

# Пути к готовым спрайтам:
APPLE_IMG_PATH = 'assets/apple_64.png'
BAD_APPLE_IMG_PATH = 'assets/mushroom_64.png'
STONE_IMG_PATH = 'assets/stone_small.png'
MOUNTAIN_IMG_PATH = 'assets/mountain_big.png'
