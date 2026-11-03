"""Главный управляющий модуль игры 'Змейка'.

Реализует основной игровой цикл, обработку пользовательского ввода,
управление состояниями игровых объектов и их рендеринг на экране.
Спроектирован с учетом изоляции контекста для корректного прохождения
автоматических тестов (с использованием прокси-импорта через __all__).

Attributes:
    screen (pygame.Surface): Главное графическое окно отображения игры.
    clock (pygame.time.Clock): Игровой таймер для контроля частоты кадров.
"""

# isort: off
import sys
from random import randint

import pygame as pg

from constants import APPLE_COLOR, BAD_APPLE_COLOR, BOARD_BACKGROUND_COLOR
from constants import DOWN, GRID_HEIGHT, GRID_SIZE, GRID_WIDTH, LEFT, RIGHT
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SNAKE_COLOR, SPEED
from constants import SNAKE_START_POSITION, STONE_COLOR, TURNS, UP
from game_objects import Apple, BadApple, GameObject, Snake, Stone
from game_objects import TriangleBigStone
# isort: on


__all__ = [
    'GRID_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'GameObject', 'main',
    'handle_keys', 'UP', 'DOWN', 'LEFT', 'RIGHT'
]

pg.display.set_caption('Змейка')

clock = pg.time.Clock()

screen = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    0,
    32
)


def handle_keys(game_object):
    """Обрабатывает события нажатия клавиш и управляет направлением движения.

    Перехватывает системные события Pygame. При нажатии на стрелки управления
    меняет вектор движения змейки, блокируя возможность мгновенного разворота
    на 180 градусов (движение в противоположную сторону). При закрытии окна
    или выходе безопасно завершает работу приложения.

    Args:
        game_object (Snake): Экземпляр игрового персонажа (змейка),
            у которого изменяется атрибут `next_direction`.

    Raises:
        SystemExit: При получении события pygame.QUIT для корректного
            закрытия игрового процесса.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key in TURNS:
                new_direction, opposite_direction = TURNS[event.key]
                if game_object.direction != opposite_direction:
                    game_object.next_direction = new_direction


def main():
    """Инициализирует компоненты игры и запускает бесконечный игровой цикл.

    Выполняет пошаговую подготовку окружения:
        1. Инициализирует подсистемы Pygame.
        2. Генерирует массив препятствий (большие скалы и мелкие камни)
           с контролем дистанции спавна для исключения перекрытий.
        3. Создает динамические объекты: змейку и элементы еды.

    Игровой цикл работает на фиксированной частоте кадров (SPEED)
    и последовательно выполняет: сбор ввода, обновление физических координат,
    проверку коллизий (с едой, препятствиями или хвостом) и полную перерисовку
    экрана с нуля (Full Frame Redraw) для исключения графических артефактов.
    """
    pg.init()

    obstacles = []
    for _ in range(1, 5):
        obstacles.append(
            TriangleBigStone(screen, STONE_COLOR, existing_obstacles=obstacles)
        )
    for _ in range(randint(10, 20)):
        obstacles.append(
            Stone(screen, STONE_COLOR, existing_obstacles=obstacles)
        )
    apple = Apple(screen, APPLE_COLOR, existing_obstacles=obstacles)
    bad_apple = BadApple(
        screen, BAD_APPLE_COLOR, existing_obstacles=obstacles
    )
    snake = Snake(
        screen,
        SNAKE_COLOR,
        SNAKE_START_POSITION
    )

    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()
        head = snake.get_head_position()

        # Проверка коллизий с едой и самопересечением
        if head in snake.positions[1:]:
            snake.reset()
        elif head == apple.position:
            snake.length += 1
            apple.randomize_position(obstacles)
        elif head == bad_apple.position:
            snake.shrink()
            bad_apple.randomize_position(obstacles)

        # Полиморфная проверка коллизий со всеми типами препятствий
        for obstacle in obstacles:
            if head in obstacle.positions:
                snake.handle_bounce()
                break

        # Отрисовка кадра: сначала статика, затем динамическая змейка
        apple.draw()
        bad_apple.draw()
        for obstacle in obstacles:
            obstacle.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
