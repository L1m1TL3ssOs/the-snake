import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, SPEED,
    BOARD_BACKGROUND_COLOR, STONE_COLOR, APPLE_COLOR, BAD_APPLE_COLOR,
    SNAKE_COLOR, UP, DOWN, LEFT, RIGHT
)
from game_objects import (
    GameObject, Apple, BadApple, Stone, TriangleBigStone, Snake,
)
from random import randint

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()
# Настройка игрового окна:
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    0,
    32
)


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_UP
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key == pygame.K_DOWN
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN
            elif (
                event.key == pygame.K_LEFT
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT
            elif (
                event.key == pygame.K_RIGHT
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


def main():
    """Основная функция для запуска игры"""
    pygame.init()
    # Создание объектов
    obstacles = []
    for _ in range(1, 5):
        obstacles.append(TriangleBigStone(screen, STONE_COLOR))
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
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    )
    # Генерация препятствий
    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        clock.tick(SPEED)

        # 1. Обработка ввода и движение
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        head = snake.get_head_position()

        # 2. Проверка коллизий с едой и самопересечением
        if head in snake.positions[1:]:
            snake.reset()
        elif head == apple.position:
            snake.length += 1
            apple.randomize_position(obstacles)
        elif head == bad_apple.position:
            snake.shrink()
            bad_apple.randomize_position(obstacles)

        # 3. Проверка всех препятствий в одном цикле
        # Мы объединяем маленькие камни и большие скалы в общий перебор
        for obstacle in obstacles:
            if head in obstacle.positions:
                snake.handle_bounce()
                break

        # 4. Рендеринг (отрисовка) кадра
        # Сначала рисуем статическое окружение, затем динамическую змейку
        apple.draw()
        bad_apple.draw()
        for obstacle in obstacles:
            obstacle.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
