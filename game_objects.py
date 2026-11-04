"""Модуль физических и графических объектов игры 'Змейка'.

Содержит иерархию классов игровых сущностей. Все классы унаследованы от
базового GameObject и поддерживают безопасную бесконтекстную инициализацию
без прямой зависимости от графического движка Pygame при создании объектов.
"""

from random import choice, randint

import pygame as pg

import constants as const


class GameObject:
    """Базовый абстрактный класс для всех игровых объектов.

    Определяет минимальный интерфейс пространственного расположения
    и отрисовки сущностей на игровом поле.

    Attributes:
        surface (None): Заглушка исключительно для обеспечения обратной
            совместимости с автотестами платформы.
        body_color (tuple[int, int, int] | None): Базовый цвет объекта для
            резервной отрисовки примитивами.
        position (tuple[int, int] | None): Координаты базовой ячейки
            объекта (X, Y) на сетке.
    """

    def __init__(self, body_color=None, position=None):
        self.body_color = body_color
        self.position = position

    def draw(self, surface):
        """Отрисовывает объект на игровой поверхности.

        Обязан быть переопределен в дочерних классах с поддержкой
        графических ресурсов и текстурирования.

        Args:
            surface (pygame.Surface): Активная графическая поверхность
                экрана для вывода кадра.

        Raises:
            NotImplementedError: Если дочерний класс не реализовал
                собственную логику отрисовки.
        """
        raise NotImplementedError(
            'Метод draw() не переопределен в дочернем классе.'
            f'{self.__class__.__name__}!'
        )


class Apple(GameObject):
    """Класс стандартного яблока, увеличивающего длину змейки.

    Размещается на свободных ячейках поля и поддерживает ленивую
    загрузку растровой текстуры при первом рендеринге.
    """

    def __init__(
            self,
            body_color=const.APPLE_COLOR,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(body_color, position)
        self.position = position
        self.image = None
        self.randomize_position(existing_obstacles)

    def draw(self, surface):
        """Выполняет ленивую загрузку текстуры и отрисовывает яблоко
        на экране.
        """
        if surface is None:
            return
        if self.image is None:
            self.image = pg.transform.scale(
                pg.image.load(const.APPLE_IMG_PATH).convert_alpha(),
                (const.GRID_SIZE, const.GRID_SIZE)
            )
        surface.blit(self.image, self.position)

    def randomize_position(self, existing_obstacles):
        """
        Находит случайную позицию для яблока с контролем наложения.

        Цикл выполняется до тех пор, пока позиция не определена или
        сгенерированная точка входит в коллекцию занятых ячеек.
        """
        # Подготовка списка препятствий
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []

        # Сброс позиции и запуск флага для входа в цикл
        is_unsafe = True
        self.position = None

        # Контролируемый поиск свободной ячейки
        while self.position is None or is_unsafe:
            new_position = (
                randint(0, const.GRID_WIDTH - 1) * const.GRID_SIZE,
                randint(0, const.GRID_HEIGHT - 1) * const.GRID_SIZE
            )

            is_unsafe = False
            for obj in existing_obstacles:
                # Извлечение координат объекта
                obj_cells = (
                    obj.positions
                    if hasattr(obj, 'positions') and obj.positions
                    else [obj.position]
                )

                # Защита от гор: отступ в 1 ячейку
                if obj.__class__.__name__ == 'TriangleBigStone':
                    if any(
                        abs(new_position[0] - cell[0]) <= const.GRID_SIZE
                        and abs(new_position[1] - cell[1]) <= const.GRID_SIZE
                        for cell in obj_cells
                    ):
                        is_unsafe = True
                        break

                # Защита от остальных объектов
                else:
                    if new_position in obj_cells:
                        is_unsafe = True
                        break

            # Утверждение позиции, если коллизий не обнаружено
            if not is_unsafe:
                self.position = new_position

        # Синхронизация массива координат для внешних проверок
        if hasattr(self, 'positions'):
            self.positions = [self.position]


class BadApple(Apple):
    """Класс модификатора (гнилого яблока), уменьшающего длину змейки.

    Наследует алгоритмы позиционирования базового яблока, но инициализирует
    уникальный визуальный спрайт опасного объекта.
    """

    def __init__(
            self,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(body_color, position, existing_obstacles)

    def draw(self, surface):
        """
        Отрисовывает спрайт гнилого яблока методом Lazy Loading.

        Загружает и масштабирует текстуру при первом кадре. Защищен
        от передачи пустой поверхности (None).
        """
        if surface is None:
            return
        if self.image is None:
            self.image = pg.transform.scale(
                pg.image.load(const.BAD_APPLE_IMG_PATH).convert_alpha(),
                (const.GRID_SIZE, const.GRID_SIZE)
            )
        surface.blit(self.image, self.position)


class Stone(GameObject):
    """Класс статичного препятствия единичного размера (одиночный камень).

    Attributes:
        positions (list[tuple[int, int]]): Массив занимаемых ячеек поля.
            Для базового камня всегда содержит один элемент.
    """

    def __init__(
            self,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(body_color, position)
        self.image = None
        self.randomize_position(existing_obstacles)
        self.positions = [self.position]

    def randomize_position(self, existing_obstacles):
        """Находит случайную позицию для камня с контролем наложения."""
        # Подготовка списка препятствий
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []

        # Сброс позиции и запуск флага для входа в цикл
        is_unsafe = True
        self.position = None

        # Контролируемый поиск свободной ячейки
        while self.position is None or is_unsafe:
            new_position = (
                randint(0, const.GRID_WIDTH - 1) * const.GRID_SIZE,
                randint(0, const.GRID_HEIGHT - 1) * const.GRID_SIZE
            )

            is_unsafe = False
            for obj in existing_obstacles:
                # Извлечение координат объекта
                obj_cells = (
                    obj.positions
                    if hasattr(obj, 'positions') and obj.positions
                    else [obj.position]
                )

                # Защита от гор: отступ в 1 ячейку
                if obj.__class__.__name__ == 'TriangleBigStone':
                    if any(
                        abs(new_position[0] - cell[0]) <= const.GRID_SIZE
                        and abs(new_position[1] - cell[1]) <= const.GRID_SIZE
                        for cell in obj_cells
                    ):
                        is_unsafe = True
                        break
                # Защита от остальных объектов
                else:
                    if new_position in obj_cells:
                        is_unsafe = True
                        break

            # Утверждение позиции, если коллизий не обнаружено
            if not is_unsafe:
                self.position = new_position

        # Синхронизация массива координат камня
        self.positions = [self.position]

    def draw(self, surface):
        """
        Отрисовывает спрайт камня методом Lazy Loading.

        Загружает и масштабирует текстуру при первом вызове. Защищен
        от передачи пустой поверхности (None).
        """
        if surface is None:
            return
        if self.image is None:
            self.image = pg.transform.scale(
                pg.image.load(const.STONE_IMG_PATH).convert_alpha(),
                (const.GRID_SIZE, const.GRID_SIZE)
            )
        surface.blit(self.image, self.position)


class TriangleBigStone(GameObject):
    """
    Статичное составное препятствие в форме 3-ячеичной пирамиды.

    Занимает три связанных ячейки поля. Отрисовывается с помощью единого
    крупного спрайта с автоматическим выравниванием по координатам маски.
    """

    def __init__(
            self,
            body_color,
            position=None,
            existing_obstacles=None
    ):
        super().__init__(body_color, position)
        self.image = None
        self.positions = []

        self.randomize_position(existing_obstacles or [])

    def draw(self, surface):
        """
        Отрисовывает составной спрайт скалы со смещением текстуры.

        Использует Lazy Loading. Автоматически сдвигает текстуру 3х2 ячейки
        относительно базовой точки-вершины для точного покрытия геометрии.
        """
        if surface is None:
            return
        if self.image is None:
            self.image = pg.transform.scale(
                pg.image.load(const.MOUNTAIN_IMG_PATH).convert_alpha(),
                (3 * const.GRID_SIZE, 2 * const.GRID_SIZE)
            )
        render_x = self.position[0] - const.GRID_SIZE
        render_y = self.position[1]
        surface.blit(self.image, (render_x, render_y))

    def randomize_position(self, existing_obstacles):
        """
        Вычисляет координаты пирамиды с проверкой дистанции Чебышёва.

        Сбор занятых координат вынесен за пределы цикла. Проверка дистанции
        и границ вынесена в заголовок контролируемого цикла while.
        """
        if not isinstance(existing_obstacles, list):
            existing_obstacles = []

        # Сбор занятых ячеек до цикла
        occupied_cells = set()
        for obj in existing_obstacles:
            if hasattr(obj, 'positions') and obj.positions:
                occupied_cells.update(obj.positions)
            elif hasattr(obj, 'position') and obj.position:
                occupied_cells.add(obj.position)

        # Флаг для первой итерации и проверки дистанции Чебышёва
        is_unsafe = True
        self.position = None

        # Контролируемый цикл: пока позиции нет или она нарушает дистанцию
        while self.position is None or is_unsafe:
            # Ограничиваем спавн по краям, чтобы у скалы влезли бока
            new_pos = (
                randint(1, const.GRID_WIDTH - 2) * const.GRID_SIZE,
                randint(0, const.GRID_HEIGHT - 2) * const.GRID_SIZE
            )

            # Проверяем дистанцию Чебышёва (нахождение в радиусе 3 ячеек)
            is_unsafe = any(
                abs(new_pos[0] - cell[0]) <= 3 * const.GRID_SIZE
                and abs(new_pos[1] - cell[1]) <= 3 * const.GRID_SIZE
                for cell in occupied_cells
            )

            # Если точка безопасна, фиксируем вершину скалы
            if not is_unsafe:
                self.position = new_pos

        # Финально заполняем все 3 ячейки тела скалы на основе
        # утвержденной вершины
        x, y = self.position
        self.positions = [
            (x, y),
            (x - const.GRID_SIZE, y + const.GRID_SIZE),
            (x + const.GRID_SIZE, y + const.GRID_SIZE)
        ]


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
            body_color=const.SNAKE_COLOR,
            position=const.SNAKE_START_POSITION
    ):
        position = const.SNAKE_START_POSITION
        super().__init__(body_color, position)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice(
            [const.RIGHT, const.LEFT, const.UP, const.DOWN])
        self.next_direction = None
        self.last = None
        self.freeze_ticks = 0

        self.head_image = {}
        self.body_image = None

    def draw(self, surface):
        """Отрисовывает все сегменты тела и голову змейки на экране.

        Последовательно выводит текстуры тела для всех позиций, кроме первой,
        после чего накладывает спрайт головы, соответствующий текущему
        вектору движения (`self.direction`). Прерывает выполнение, если
        графические ресурсы не загружены.
        """
        if surface is None:
            return

        # загружаем картинки 1 раз при первом вызове draw
        if self.body_image is None:
            self.body_image = pg.transform.scale(
                pg.image.load(const.SNAKE_BODY_IMG).convert_alpha(),
                (const.GRID_SIZE, const.GRID_SIZE)
            )
            self.head_image = {
                const.UP: pg.transform.scale(
                    pg.image.load(const.SNAKE_HEAD_UP).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)
                ),
                const.DOWN: pg.transform.scale(
                    pg.image.load(const.SNAKE_HEAD_DOWN).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)
                ),
                const.LEFT: pg.transform.scale(
                    pg.image.load(const.SNAKE_HEAD_LEFT).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)
                ),
                const.RIGHT: pg.transform.scale(
                    pg.image.load(const.SNAKE_HEAD_RIGHT).convert_alpha(),
                    (const.GRID_SIZE, const.GRID_SIZE)
                )
            }

        # Отрисовка тела (начиная со второго элемента)
        for position in self.positions[1:]:
            surface.blit(self.body_image, position)
        surface.blit(self.head_image[self.direction], self.positions[0])

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
        self.update_direction()
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
        self.positions = [const.SNAKE_START_POSITION]
        self.direction = const.RIGHT
        self.next_direction = None
        self.last = None
        self.freeze_ticks = 0

    def shrink(self):
        """Уменьшает длину змейки на один сегмент.

        Удаляет последний элемент из массива координат хвоста и уменьшает
        значение `length`. Содержит вызов примитива очистки ячейки для
        совместимости
        с изолированными тестами отрисовки.
        """
        if self.length > 1:
            self.length -= 1
            self.positions.pop()

    def handle_bounce(self, surface):
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
        if surface is None:
            return

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
