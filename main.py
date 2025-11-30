import pygame
import random


# Константы для настроек игры
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480  # Размеры игрового окна
GRID_SIZE = 20  # Размер одной клетки сетки
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE  # Ширина в клетках
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # Высота в клетках

# Направления движения змейки
MOVEMENTS = {
    'UP': (0, -1),      # Вверх
    'DOWN': (0, 1),     # Вниз
    'LEFT': (-1, 0),    # Влево
    'RIGHT': (1, 0)     # Вправо
}

# Цвета игры
BACKGROUND_COLOR = (0, 0, 0)          # Черный фон
BORDER_COLOR = (93, 216, 228)         # Голубая граница
APPLE_COLOR = (255, 0, 0)             # Красное яблоко
SNAKE_COLOR = (0, 255, 0)             # Зеленая змейка
GAME_SPEED = 10                       # Скорость игры


class GameEntity:
    """Базовый класс для всех игровых объектов."""
    
    def __init__(self, color=None):
        # Начальная позиция в центре экрана
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.color = color  # Цвет объекта
    
    def draw(self, surface):
        """Метод для отрисовки объекта на экране."""
        pass  # Будет переопределен в дочерних классах


class Food(GameEntity):
    """Класс для еды (яблока), которую собирает змейка."""
    
    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.spawn()  # Сразу создаем яблоко в случайном месте
    
    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле."""
        # Создаем прямоугольник для яблока
        cell_rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        # Рисуем заполненный прямоугольник (яблоко)
        pygame.draw.rect(surface, self.color, cell_rect)
        # Рисуем границу вокруг яблока
        pygame.draw.rect(surface, BORDER_COLOR, cell_rect, 1)
    
    def spawn(self, occupied_positions=None):
        """Создает яблоко в случайной позиции, не занятой змейкой."""
        if occupied_positions is None:
            occupied_positions = []
        
        # Ищем свободную позицию для яблока
        while True:
            # Случайные координаты в пределах сетки
            new_x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            new_y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (new_x, new_y)
            
            # Если позиция свободна - размещаем яблоко
            if new_position not in occupied_positions:
                self.position = new_position
                break


class PlayerSnake(GameEntity):
    """Класс для змейки, управляемой игроком."""
    
    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.body_parts = [self.position]  # Сегменты тела змейки
        self.size = 1  # Начальный размер змейки
        self.current_direction = MOVEMENTS['RIGHT']  # Начальное направление
        self.queued_direction = None  # Следующее направление (из очереди)
        self.previous_tail_position = None  # Позиция хвоста для очистки
    
    def draw(self, surface):
        """Отрисовывает змейку на игровом поле."""
        # Отрисовываем все сегменты тела кроме головы
        for segment in self.body_parts[:-1]:
            segment_rect = pygame.Rect(segment, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, segment_rect)
            pygame.draw.rect(surface, BORDER_COLOR, segment_rect, 1)
        
        # Отрисовываем голову змейки
        head_rect = pygame.Rect(self.body_parts[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)
        
        # Стираем старую позицию хвоста
        if self.previous_tail_position:
            tail_rect = pygame.Rect(
                self.previous_tail_position, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BACKGROUND_COLOR, tail_rect)
    
    def change_direction(self):
        """Обновляет направление движения змейки."""
        if self.queued_direction:
            self.current_direction = self.queued_direction
            self.queued_direction = None
    
    def move(self):
        """Перемещает змейку в текущем направлении."""
        # Получаем текущую позицию головы
        head_x, head_y = self.body_parts[0]
        move_x, move_y = self.current_direction
        
        # Вычисляем новую позицию головы с учетом телепортации через границы
        new_x = (head_x + move_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + move_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head_position = (new_x, new_y)
        
        # Добавляем новую голову
        self.body_parts.insert(0, new_head_position)
        
        # Удаляем хвост если змейка не выросла
        if len(self.body_parts) > self.size:
            self.previous_tail_position = self.body_parts.pop()
        else:
            self.previous_tail_position = None
        
        # Проверяем столкновение с собой
        if new_head_position in self.body_parts[1:]:
            self.respawn()  # Перезапускаем игру при столкновении
    
    def get_head_position(self):
        """Возвращает текущую позицию головы змейки."""
        return self.body_parts[0]
    
    def grow(self):
        """Увеличивает размер змейки при съедании яблока."""
        self.size += 1
    
    def respawn(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.body_parts = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.size = 1
        # Случайное начальное направление
        self.current_direction = random.choice(list(MOVEMENTS.values()))
        self.queued_direction = None
        self.previous_tail_position = None


class InputHandler:
    """Класс для обработки пользовательского ввода."""
    
    @staticmethod
    def process_events(snake):
        """Обрабатывает события клавиатуры."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Завершаем игру при закрытии окна
                pygame.quit()
                raise SystemExit
            
            elif event.type == pygame.KEYDOWN:
                # Обработка нажатий стрелок с проверкой противоположного направления
                if (event.key == pygame.K_UP and 
                        snake.current_direction != MOVEMENTS['DOWN']):
                    snake.queued_direction = MOVEMENTS['UP']
                elif (event.key == pygame.K_DOWN and 
                      snake.current_direction != MOVEMENTS['UP']):
                    snake.queued_direction = MOVEMENTS['DOWN']
                elif (event.key == pygame.K_LEFT and 
                      snake.current_direction != MOVEMENTS['RIGHT']):
                    snake.queued_direction = MOVEMENTS['LEFT']
                elif (event.key == pygame.K_RIGHT and 
                      snake.current_direction != MOVEMENTS['LEFT']):
                    snake.queued_direction = MOVEMENTS['RIGHT']


class GameController:
    """Главный контроллер, управляющий игровым процессом."""
    
    def __init__(self):
        # Инициализация pygame
        pygame.init()
        self.display_surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption('Змейка')  # Заголовок окна
        self.game_clock = pygame.time.Clock()  # Игровые часы для FPS
        
        # Создаем игровые объекты
        self.player = PlayerSnake()
        self.food = Food()
        self.input_handler = InputHandler()
    
    def run_game_loop(self):
        """Запускает главный игровой цикл."""
        while True:
            # Контроль скорости игры
            self.game_clock.tick(GAME_SPEED)
            
            # Обработка ввода пользователя
            self.input_handler.process_events(self.player)
            
            # Обновление направления движения
            self.player.change_direction()
            
            # Перемещение змейки
            self.player.move()
            
            # Проверка съедания яблока
            if self.player.get_head_position() == self.food.position:
                self.player.grow()  # Увеличиваем змейку
                # Создаем новое яблоко в свободном месте
                self.food.spawn(self.player.body_parts)
            
            # Отрисовка игрового состояния
            self.display_surface.fill(BACKGROUND_COLOR)  # Очистка экрана
            self.player.draw(self.display_surface)       # Отрисовка змейки
            self.food.draw(self.display_surface)         # Отрисовка яблока
            pygame.display.update()                      # Обновление экрана


def main():
    """Главная функция для запуска игры."""
    game = GameController()
    game.run_game_loop()


if __name__ == '__main__':
    main()
