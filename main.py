import pygame
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

MOVEMENTS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}

BACKGROUND_COLOR = (1, 1, 1)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
GAME_SPEED = 10


class GameEntity:
    def __init__(self, color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.color = color

    def draw(self, surface):
        pass


class Food(GameEntity):
    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.spawn()

    def draw(self, surface):
        cell_rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, cell_rect)
        pygame.draw.rect(surface, BORDER_COLOR, cell_rect, 1)

    def spawn(self, occupied_positions=None):
        if occupied_positions is None:
            occupied_positions = []

        while True:
            new_x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            new_y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (new_x, new_y)

            if new_position not in occupied_positions:
                self.position = new_position
                break


class PlayerSnake(GameEntity):
    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.body_parts = [self.position]
        self.size = 1
        self.current_direction = MOVEMENTS['RIGHT']
        self.queued_direction = None
        self.previous_tail_position = None

    def draw(self, surface):
        for segment in self.body_parts[:-1]:
            segment_rect = pygame.Rect(segment, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, segment_rect)
            pygame.draw.rect(surface, BORDER_COLOR, segment_rect, 1)

        head_rect = pygame.Rect(self.body_parts[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        if self.previous_tail_position:
            tail_rect = pygame.Rect(self.previous_tail_position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BACKGROUND_COLOR, tail_rect)

    def change_direction(self):
        if self.queued_direction:
            self.current_direction = self.queued_direction
            self.queued_direction = None

    def move(self):
        head_x, head_y = self.body_parts[0]
        move_x, move_y = self.current_direction

        new_x = (head_x + move_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + move_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head_position = (new_x, new_y)

        self.body_parts.insert(0, new_head_position)

        if len(self.body_parts) > self.size:
            self.previous_tail_position = self.body_parts.pop()
        else:
            self.previous_tail_position = None

        if new_head_position in self.body_parts[1:]:
            self.respawn()

    def get_head_position(self):
        return self.body_parts[0]

    def grow(self):
        self.size += 1

    def respawn(self):
        self.body_parts = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.size = 1
        self.current_direction = random.choice(list(MOVEMENTS.values()))
        self.queued_direction = None
        self.previous_tail_position = None


class InputHandler:
    @staticmethod
    def process_events(snake):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.current_direction != MOVEMENTS['DOWN']:
                    snake.queued_direction = MOVEMENTS['UP']
                elif event.key == pygame.K_DOWN and snake.current_direction != MOVEMENTS['UP']:
                    snake.queued_direction = MOVEMENTS['DOWN']
                elif event.key == pygame.K_LEFT and snake.current_direction != MOVEMENTS['RIGHT']:
                    snake.queued_direction = MOVEMENTS['LEFT']
                elif event.key == pygame.K_RIGHT and snake.current_direction != MOVEMENTS['LEFT']:
                    snake.queued_direction = MOVEMENTS['RIGHT']


class GameController:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Змейка')
        self.game_clock = pygame.time.Clock()

        self.player = PlayerSnake()
        self.food = Food()
        self.input_handler = InputHandler()

    def run_game_loop(self):
        while True:
            self.game_clock.tick(GAME_SPEED)

            self.input_handler.process_events(self.player)

            self.player.change_direction()

            self.player.move()

            if self.player.get_head_position() == self.food.position:
                self.player.grow()
                self.food.spawn(self.player.body_parts)

            self.display_surface.fill(BACKGROUND_COLOR)
            self.player.draw(self.display_surface)
            self.food.draw(self.display_surface)
            pygame.display.update()


def main():
    game = GameController()
    game.run_game_loop()


if __name__ == '__main__':
    main()