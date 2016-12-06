import pygame
from sprites import *
import random
from math import hypot

pygame.init()


class Game(object):
    """ Init the Game object with a Snake on a 45x25 board and a piece of fruit """

    def __init__(self):
        self.done = False
        self.is_game_over = False
        self.game_display = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.positions = set((x, y) for x in range(0, 44) for y in range(0, 24))
        self.snake = Snake()
        self.snake.create_new_piece(2, self.positions)
        self.collision_group = pygame.sprite.Group()
        random_position = random.sample(self.positions, 1)[0]
        self.fruit = Game.create_new_fruit(OFFSET_X + (16 * random_position[0]), OFFSET_Y + (16 * random_position[1]))
        self.all_sprites_group = pygame.sprite.Group()
        self.all_sprites_group.add(self.fruit)
        # build walls
        self.wall_group = pygame.sprite.Group()
        # top
        self.wall_group.add(Wall(44, 16, 710, 4))
        # left
        self.wall_group.add(Wall(44, 16, 4, 390))
        # right
        self.wall_group.add(Wall(752, 16, 4, 392))
        # bottom
        self.wall_group.add(Wall(44, 404, 710, 4))
        self.frame_count = 0
        self.next_direction = 2
        self.score = 0

    @staticmethod
    def create_new_fruit(x, y):
        rand = random.randint(1, 10)
        # 20% to be ghost fruit
        if rand <= 2:
            return GhostFruit(x, y)
        else:
            return Fruit(x, y)

    def draw(self):
        self.frame_count += 1
        self.game_display.fill((255, 255, 255))
        self.clock.tick_busy_loop(30)
        self.snake.draw(self.game_display)
        self.all_sprites_group.draw(self.game_display)
        self.wall_group.draw(self.game_display)
        pygame.display.flip()

    def update(self):
        # check for collisions
        self.check_for_collisions()

        # normal game loop
        if not self.is_game_over:
            if self.frame_count == 4:
                self.snake.create_new_piece(self.next_direction, self.positions)
                self.frame_count = 0
            self.snake.update(self.next_direction)
            # updates fruit, checks if we need a new one if it's a GhostFruit
            need_new_fruit = self.fruit.update(self.snake.get_active_piece().rect)
            if need_new_fruit:
                self.all_sprites_group.remove(self.fruit)
                random_position = random.sample(self.positions, 1)[0]
                self.fruit = Game.create_new_fruit(OFFSET_X + (16 * random_position[0]),
                                                   OFFSET_Y + (16 * random_position[1]))
                self.all_sprites_group.add(self.fruit)

    def check_for_collisions(self):
        fruit_collision = pygame.sprite.collide_rect(self.snake.get_active_piece(), self.fruit)
        if fruit_collision:
            self.score += self.fruit.get_point_value()
            self.snake.max_size += self.fruit.get_size_value()
            self.all_sprites_group.remove(self.fruit)
            random_position = random.sample(self.positions, 1)[0]
            self.fruit = Game.create_new_fruit(OFFSET_X + (16 * random_position[0]),
                                               OFFSET_Y + (16 * random_position[1]))
            self.all_sprites_group.add(self.fruit)

        head_collision = self.snake.check_collision()
        if head_collision:
            self.is_game_over = True

        wall_collision = pygame.sprite.spritecollide(self.snake.get_active_piece(), self.wall_group, False, False)
        if wall_collision:
            self.is_game_over = True

    def set_next_direction(self, param):
        # snake cannot reverse direction
        if ((self.snake.current_direction() == 3 or self.snake.current_direction() == 4) and param in (1, 2)) or (
                    (self.snake.current_direction() == 1 or self.snake.current_direction() == 2) and param in (3, 4)):
            self.next_direction = param


# create colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# position vars
x_pos = 0
y_pos = 0
x_delta = 0
y_delta = 0
clock = pygame.time.Clock()

# create a surface

game = Game()
pygame.display.set_caption("Snake")
pygame.display.update()  # only updates portion specified
# default moving right
while not game.done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.done = True

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            game.set_next_direction(1)
        if event.key == pygame.K_RIGHT:
            game.set_next_direction(2)
        if event.key == pygame.K_UP:
            game.set_next_direction(3)
        if event.key == pygame.K_DOWN:
            game.set_next_direction(4)

    x_pos += x_delta
    y_pos += y_delta
    game.update()
    game.draw()

# required
pygame.quit()
quit()
