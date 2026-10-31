from random import choice, randint
import constants as const

import pygame


# Настройка игрового окна:
screen = pygame.display.set_mode(
    (const.SCREEN_WIDTH, const.SCREEN_HEIGHT),
    0,
    32
)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject():
    """Основной класс игры"""

    def __init__(self, surface=None, body_color=None, position=None):
        self.surface = surface
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Метод отрисовки класса"""
        pass


class Apple(GameObject):
    """Класс Apple реализует яблоко в игре"""

    def __init__(
            self,
            surface=None,
            body_color=const.APPLE_COLOR,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)
        self.color = body_color
        self.position = position
        if position is None:
            self.randomize_position(existing_obstacles)

    def draw(self):
        """Метод draw класса Apple"""
        rect = pygame.Rect(self.position, (const.GRID_SIZE, const.GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, const.BORDER_COLOR, rect, 1)

    def randomize_position(self, existing_obstacles):
        """Метод отвечает за случайную позицию яблока на экране"""
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []
        while True:
            new_x = randint(0, const.GRID_WIDTH - 1) * const.GRID_SIZE
            new_y = randint(0, const.GRID_HEIGHT - 1) * const.GRID_SIZE
            fit_position = True
            for obstacle in existing_obstacles:
                for cell in obstacle.positions:
                    if new_x == cell[0] and new_y == cell[1]:
                        fit_position = False
                        break
                if not fit_position:
                    break
            if fit_position is True:
                self.position = (new_x, new_y)
                break


class BadApple(Apple):
    """Класс BadApple уменьшает хвост змейки"""

    def __init__(
            self,
            surface,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)


class Stone(GameObject):
    """Класс Stone - препятствие для змейки"""

    def __init__(
            self,
            surface,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)
        if position is None:
            self.randomize_position(existing_obstacles)
        self.positions = [self.position]

    def randomize_position(self, existing_obstacles):
        """Метод отвечает за случайную позицию камня на экране"""
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []
        while True:
            new_x = randint(0, const.GRID_WIDTH - 1) * const.GRID_SIZE
            new_y = randint(0, const.GRID_HEIGHT - 1) * const.GRID_SIZE
            fit_position = True
            for obstacle in existing_obstacles:
                for cell in obstacle.positions:
                    if (
                        abs(new_x - cell[0]) <= 2 * const.GRID_SIZE
                        and abs(new_y - cell[1]) <= 2 * const.GRID_SIZE
                    ):
                        fit_position = False
                        break
                if not fit_position:
                    break
            if fit_position is True:
                self.position = (new_x, new_y)
                break

    def draw(self):
        """Отрисовка камней"""
        rect = pygame.Rect(self.position, (const.GRID_SIZE, const.GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, const.BORDER_COLOR, rect, 1)


class TriangleBigStone(GameObject):
    """Класс TriangleBigStone - препятствие для змейки"""

    def __init__(self, surface, body_color, position=None):
        super().__init__(surface, body_color, position)
        if position is None:
            self.randomize_position()
        x, y = self.position
        self.positions = [
            (x, y),
            (x - const.GRID_SIZE, y + const.GRID_SIZE),
            (x + const.GRID_SIZE, y + const.GRID_SIZE)
        ]

    def draw(self):
        """Отрисовка камней"""
        x, y = self.position
        pygame.draw.polygon(
            screen,
            const.STONE_COLOR,
            [
                (x + const.GRID_SIZE // 2, y),
                (x - const.GRID_SIZE, y + 2 * const.GRID_SIZE),
                (x + 2 * const.GRID_SIZE, y + 2 * const.GRID_SIZE),
            ],
        )

    def randomize_position(self):
        """Метод отвечает за случайную позицию камня на экране"""
        new_position_x = randint(1, const.GRID_WIDTH - 2) * const.GRID_SIZE
        new_position_y = randint(1, const.GRID_HEIGHT - 2) * const.GRID_SIZE
        self.position = (new_position_x, new_position_y)


class Snake(GameObject):
    """Класс Snake реализует змейку в игре"""

    def __init__(
            self,
            surface=None,
            body_color=const.SNAKE_COLOR,
            position=None
    ):
        if position is None:
            position = (const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
        super().__init__(surface, body_color, position)
        self.length = 1
        self.positions = [position]
        self.direction = choice(
            [const.RIGHT, const.LEFT, const.UP, const.DOWN])
        self.next_direction = None
        self.last = None
        self.freeze_ticks = 0

    def draw(self):
        """Метод draw класса Snake"""
        for position in self.positions:
            rect = (pygame.Rect(position, (const.GRID_SIZE, const.GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, const.BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(
            self.positions[0], (const.GRID_SIZE, const.GRID_SIZE))
        pygame.draw.rect(screen, const.SNAKE_COLOR, head_rect)
        pygame.draw.rect(screen, const.BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        # if self.last:
        #     last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
        #     pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает координаты головы змейки"""
        return self.positions[0]

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Движение змейки"""
        if self.freeze_ticks > 0:
            self.freeze_ticks -= 1
            return
        current_position = self.get_head_position()
        new_position_x = (
            (current_position[0] + self.direction[0] * const.GRID_SIZE)
            % const.SCREEN_WIDTH
        )
        new_position_y = (
            (current_position[1] + self.direction[1] * const.GRID_SIZE)
            % const.SCREEN_HEIGHT
        )
        self.positions.insert(0, (new_position_x, new_position_y))
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние при Game Over."""
        self.length = 1
        self.positions = [(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)]
        self.direction = const.RIGHT
        self.next_direction = None
        self.last = None

    def shrink(self):
        """Метод уменьшает змейку на 1 сегмент и затирает его на экране."""
        if self.length > 1:
            tail_to_erase = self.positions[-1]
            pygame.draw.rect(
                screen,
                const.BOARD_BACKGROUND_COLOR,
                pygame.Rect(tail_to_erase, (const.GRID_SIZE, const.GRID_SIZE))
            )
            self.length -= 1
            self.positions.pop()

    def handle_bounce(self):
        """Метод обработки отскока змейки"""
        for x, y in self.positions:
            pygame.draw.rect(
                screen,
                const.BOARD_BACKGROUND_COLOR,
                pygame.Rect((x, y), (const.GRID_SIZE, const.GRID_SIZE))
            )
        self.shrink()
        self.freeze_ticks = const.BOUNCE_FREEZE_TICKS
        new_positions = []
        for x, y in self.positions:
            new_x = (
                x - self.direction[0] * 2 * const.GRID_SIZE
            ) % const.SCREEN_WIDTH
            new_y = (
                y - self.direction[1] * 2 * const.GRID_SIZE
            ) % const.SCREEN_HEIGHT
            new_positions.append((new_x, new_y))
        self.positions = new_positions
        self.last = None


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_UP
                and game_object.direction != const.DOWN
            ):
                game_object.next_direction = const.UP
            elif (
                event.key == pygame.K_DOWN
                and game_object.direction != const.UP
            ):
                game_object.next_direction = const.DOWN
            elif (
                event.key == pygame.K_LEFT
                and game_object.direction != const.RIGHT
            ):
                game_object.next_direction = const.LEFT
            elif (
                event.key == pygame.K_RIGHT
                and game_object.direction != const.LEFT
            ):
                game_object.next_direction = const.RIGHT


def main():
    """Основная функция для запуска игры"""
    pygame.init()
    # Создание объектов
    obstacles = []
    for _ in range(1, 5):
        obstacles.append(TriangleBigStone(screen, const.STONE_COLOR))
    for _ in range(randint(10, 20)):
        obstacles.append(
            Stone(screen, const.STONE_COLOR, existing_obstacles=obstacles)
        )
    apple = Apple(screen, const.APPLE_COLOR, existing_obstacles=obstacles)
    bad_apple = BadApple(
        screen, const.BAD_APPLE_COLOR, existing_obstacles=obstacles
    )
    snake = Snake(
        screen,
        const.SNAKE_COLOR,
        (const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)
    )
    # Генерация препятствий
    while True:
        screen.fill(const.BOARD_BACKGROUND_COLOR)
        clock.tick(const.SPEED)

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
