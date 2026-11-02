"""Модуль физических и графических объектов игры 'Змейка'.

Содержит иерархию классов игровых сущностей. Все классы унаследованы от
базового GameObject и поддерживают безопасную инициализацию в тестовой среде
(без графического контекста Pygame) при передаче `surface=None`.
"""

import constants as const
from random import choice, randint
import pygame


# Тут опишите все классы игры.
class GameObject():
    """Базовый абстрактный класс для всех игровых объектов.

    Определяет минимальный интерфейс пространственного расположения
    и отрисовки сущностей на игровом поле.

    Attributes:
        surface (pygame.Surface | None): Поверхность отрисовки кадра.
        body_color (tuple[int, int, int] | None): Базовый цвет объекта.
        position (tuple[int, int] | None): Координаты верхнего левого угла
            (X, Y).
    """

    def __init__(self, surface=None, body_color=None, position=None):
        self.surface = surface
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Отрисовывает объект на игровой поверхности.

        Должен быть переопределен в классах-наследниках.
        """
        pass


class Apple(GameObject):
    """Класс съедобного объекта (яблока), увеличивающего длину змейки.

    Автоматически определяет свою позицию на свободных ячейках поля
    при создании и загружает альфа-текстуру, если передан валидный
    графический контекст.
    """

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
        self.image = None
        if position is None:
            self.randomize_position(existing_obstacles)
        if self.surface is not None:
            self.image = pygame.image.load(
                const.APPLE_IMG_PATH).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (const.GRID_SIZE, const.GRID_SIZE))

    def draw(self):
        """Отрисовывает спрайт яблока на экране.

        Прерывает выполнение, если графическая поверхность или текстура
        не были инициализированы (защита тестового окружения).
        """
        if self.surface is None or self.image is None:
            return
        self.surface.blit(self.image, self.position)

    def randomize_position(self, existing_obstacles):
        """Генерирует новые случайные координаты объекта
        на сетке игрового поля.

        Алгоритм проверяет координаты по сетке GRID_SIZE и исключает наложение
        на занятые ячейки других объектов из переданного буфера препятствий.

        Args:
            existing_obstacles (list[GameObject] | None): Список объектов,
                координаты которых запрещены для генерации точки спавна.
        """
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
    """Класс модификатора (гнилого яблока), уменьшающего длину змейки.

    Наследует алгоритмы позиционирования базового яблока, но инициализирует
    уникальный визуальный спрайт опасного объекта.
    """

    def __init__(
            self,
            surface,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)
        if self.surface is not None:
            self.image = pygame.image.load(
                const.BAD_APPLE_IMG_PATH).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (const.GRID_SIZE, const.GRID_SIZE))


class Stone(GameObject):
    """Класс статичного препятствия единичного размера (одиночный камень).

    Attributes:
        positions (list[tuple[int, int]]): Массив занимаемых ячеек поля.
            Для базового камня всегда содержит один элемент.
    """

    def __init__(
            self,
            surface,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)
        self.image = None
        if position is None:
            self.randomize_position(existing_obstacles)
        self.positions = [self.position]
        if self.surface is not None:
            self.image = pygame.image.load(
                const.STONE_IMG_PATH).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (const.GRID_SIZE, const.GRID_SIZE))

    def randomize_position(self, existing_obstacles):
        """Находит случайную позицию с контролем дистанции Чебышёва.

        Исключает генерацию камня в радиусе двух ячеек (<= 2 * GRID_SIZE)
        вокруг уже существующих на поле объектов для предотвращения
        блокирования проходов.
        """
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
        """Рендерит спрайт камня на игровой поверхности.

        Внимание: требует обязательного наличия инициализированного surface.
        """
        self.surface.blit(self.image, self.position)


class TriangleBigStone(GameObject):
    """Класс сложного статичного препятствия формы 'Большая скала'.

    Занимает на координатной сетке три связанных ячейки в форме треугольника
    (пирамида из камней) и требует расширенной области текстурирования (3х2).
    """

    def __init__(
            self,
            surface,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(surface, body_color, position)
        self.image = None
        if position is None:
            self.randomize_position(existing_obstacles)
        x, y = self.position
        self.positions = [
            (x, y),
            (x - const.GRID_SIZE, y + const.GRID_SIZE),
            (x + const.GRID_SIZE, y + const.GRID_SIZE)
        ]
        if self.surface is not None:
            self.image = pygame.image.load(
                const.MOUNTAIN_IMG_PATH).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (const.GRID_SIZE * 3, const.GRID_SIZE * 2))

    def draw(self):
        """Отрисовывает текстуру скалы со смещением относительно базовой точки.

        Смещение вычисляется автоматически для выравнивания графического
        ресурса размера 3х2 ячейки по маске занимаемых координат.
        """
        if self.surface is None or self.image is None:
            return
        render_x = self.position[0] - const.GRID_SIZE
        render_y = self.position[1]
        self.surface.blit(self.image, (render_x, render_y))

    def randomize_position(self, existing_obstacles):
        """Генерирует позицию вершины скалы с учетом геометрии и отступов.

        Сужает границы генерации `randint`, предотвращая выход
        боковых элементов пирамиды за края игрового экрана, и
        проверяет дистанцию Чебышёва (<= 3 ячейки) до других объектов.
        """
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []
        while True:
            new_x = randint(1, const.GRID_WIDTH - 2) * const.GRID_SIZE
            new_y = randint(0, const.GRID_HEIGHT - 2) * const.GRID_SIZE
            fit_position = True
            for obstacle in existing_obstacles:
                for cell in obstacle.positions:
                    if (
                        abs(new_x - cell[0]) <= 3 * const.GRID_SIZE
                        and abs(new_y - cell[1]) <= 3 * const.GRID_SIZE
                    ):
                        fit_position = False
                        break
                if not fit_position:
                    break
            if fit_position is True:
                self.position = (new_x, new_y)
                break


class Snake(GameObject):
    """Класс управляемого игрового персонажа (Змейка).

    Реализует механику движения по координатной сетке, хранение истории позиций
    сегментов тела, изменение векторов направления и обработку текстур
    поворотов головы.

    Attributes:
        length (int): Текущая длина змейки (количество сегментов).
        positions (list[tuple[int, int]]): Список координат всех сегментов
            тела, где индекс [0] — голова.
        direction (tuple[int, int]): Текущий вектор движения.
        next_direction (tuple[int, int] | None): Буферизованный следующий
            вектор.
        head_image (dict): Словарь предзагруженных спрайтов направлений головы.
    """

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
        self.head_image = {}
        self.body_image = None
        if self.surface is not None:
            self.body_image = pygame.transform.scale(
                pygame.image.load(const.SNAKE_BODY_IMG).convert_alpha(),
                (const.GRID_SIZE, const.GRID_SIZE)
            )
            self.head_image = {
                const.UP: pygame.transform.scale(
                    pygame.image.load(const.SNAKE_HEAD_UP).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)),
                const.DOWN: pygame.transform.scale(
                    pygame.image.load(const.SNAKE_HEAD_DOWN).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)),
                const.LEFT: pygame.transform.scale(
                    pygame.image.load(const.SNAKE_HEAD_LEFT).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)),
                const.RIGHT: pygame.transform.scale(
                    pygame.image.load(const.SNAKE_HEAD_RIGHT).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE))
            }

    def draw(self):
        """Отрисовывает все сегменты тела и голову змейки на экране.

        Последовательно выводит текстуры тела для всех позиций, кроме первой,
        после чего накладывает спрайт головы, соответствующий текущему
        вектору движения (`self.direction`). Прерывает выполнение, если
        графические ресурсы не загружены.
        """
        if not self.head_image or self.body_image is None:
            return
        for position in self.positions[1:]:
            self.surface.blit(self.body_image, position)

        # Отрисовка головы змейки
        current_head_img = self.head_image[self.direction]
        self.surface.blit(current_head_img, self.positions[0])

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки.

        Returns:
            tuple[int, int]: Координаты ячейки (X, Y), где находится голова.
        """
        return self.positions[0]

    def update_direction(self):
        """Обновляет текущий вектор движения змейки на буферизованный.

        Применяет направление, выбранное пользователем в текущем кадре
        (`next_direction`), и очищает буфер ввода для подготовки
        к следующему кадру.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Рассчитывает и обновляет координаты сегментов змейки
        на один шаг вперед.

        Если активен эффект заморозки (`freeze_ticks > 0`), уменьшает счетчик
        тиков и пропускает шаг движения. При обычном движении вычисляет новые
        координаты головы с применением модульной арифметики (оператор `%`),
        обеспечивая бесшовный проход сквозь границы экрана. Добавляет новую
        голову
        в начало списка координат и удаляет лишний сегмент хвоста, если змейка
        превысила свою целевую длину.
        """
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
        """Сбрасывает состояние змейки к начальным игровым параметрам.

        Вызывается при наступлении события Game Over. Возвращает змейку в центр
        экрана, сбрасывает её длину до единицы, очищает буферы направлений
        и устанавливает дефолтный вектор движения вправо.
        """
        self.length = 1
        self.positions = [(const.SCREEN_WIDTH // 2, const.SCREEN_HEIGHT // 2)]
        self.direction = const.RIGHT
        self.next_direction = None
        self.last = None

    def shrink(self):
        """Уменьшает длину змейки на один сегмент.

        Удаляет последний элемент из массива координат хвоста и уменьшает
        значение `length`. Содержит вызов примитива очистки ячейки для
        совместимости
        с изолированными тестами отрисовки.
        """
        if self.length > 1:
            tail_to_erase = self.positions[-1]
            pygame.draw.rect(
                self.surface,
                const.BOARD_BACKGROUND_COLOR,
                pygame.Rect(tail_to_erase, (const.GRID_SIZE, const.GRID_SIZE))
            )
            self.length -= 1
            self.positions.pop()

    def handle_bounce(self):
        """Реализует механику отскока змейки назад при столкновении
        с препятствием.

        Алгоритм выполняет следующие шаги:
            1. Уменьшает длину змейки на один сегмент через вызов `shrink()`.
                2. Активирует штрафную заморозку движения на фиксированное
                    число тиков.
                3. Сдвигает координаты всех оставшихся сегментов тела назад
                    на две ячейки вдоль текущего вектора движения (с учетом
                    прохода сквозь границы экрана).
        """
        for x, y in self.positions:
            pygame.draw.rect(
                self.surface,
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
