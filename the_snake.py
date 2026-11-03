"""Главный управляющий модуль игры 'Змейка'.

Реализует декомпозированный игровой цикл, диспетчеризацию ввода,
обсчет физики коллизий и полиморфный рендеринг объектов на экране.
Спроектирован с учетом требований изоляции контекста для совместимости
с автоматическими тестами платформы.

Функции модуля:
    handle_keys(game_object): Обработка ввода и смена вектора движения.
    main(): Точка входа, координирующая подсистемы игрового цикла.

Внутренние утилиты (поддержка декомпозиции):
    _create_game_objects(): Фабрика инициализации игровых сущностей.
    _handle_collisions(): Диспетчер проверки всех типов коллизий.
    _reset_after_self_collision(): Безопасный респавн с защитой от наложений.
    _draw_frame(): Очистка кадра и последовательный рендеринг слоев.
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


def _create_game_objects():
    """Инициализирует и возвращает стартовый набор игровых объектов."""
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
    snake = Snake(screen, SNAKE_COLOR, SNAKE_START_POSITION)
    return obstacles, apple, bad_apple, snake


def _reset_after_self_collision(snake, obstacles, apple, bad_apple):
    """Сбрасывает позиции всех объектов на поле без взаимных перекрытий."""
    snake.reset()

    new_obstacles, new_apple, new_bad_apple, _ = _create_game_objects()

    obstacles.clear()
    obstacles.extend(new_obstacles)

    apple.position = new_apple.position
    bad_apple.position = new_bad_apple.position


def _handle_collisions(snake, head, apple, bad_apple, obstacles):
    """Выполняет проверку всех типов коллизий на текущем шаге симуляции."""
    if head in snake.positions[1:]:
        _reset_after_self_collision(snake, obstacles, apple, bad_apple)
    elif head == apple.position:
        snake.length += 1
        apple.randomize_position(obstacles)
    elif head == bad_apple.position:
        snake.shrink()
        bad_apple.randomize_position(obstacles)

    for obstacle in obstacles:
        if head in obstacle.positions:
            snake.handle_bounce()
            break


def _draw_frame(apple, bad_apple, obstacles, snake):
    """Отрисовывает все игровые слои на экране и обновляет дисплей."""
    apple.draw()
    bad_apple.draw()
    for obstacle in obstacles:
        obstacle.draw()
    snake.draw()
    pg.display.update()


def main():
    """Координирует инициализацию систем и запускает главный игровой цикл.

    Вызывает создание объектов, обеспечивает фиксированную частоту
    кадров (SPEED) и последовательно делегирует задачи сбора ввода,
    физических обновлений, обсчета коллизий и рендеринга специализированным
    внутренним функциям модуля.
    """
    pg.init()

    obstacles, apple, bad_apple, snake = _create_game_objects()

    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()
        head = snake.get_head_position()

        _handle_collisions(snake, head, apple, bad_apple, obstacles)
        _draw_frame(apple, bad_apple, obstacles, snake)


if __name__ == '__main__':
    main()
