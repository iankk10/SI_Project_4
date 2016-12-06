import pygame
from sprites import *
import random

pygame.init()

FONT = pygame.font.SysFont("helvetica", 15)
GAME_OVER_FONT = pygame.font.SysFont("helvetica", 30)


class Game(object):
    """ Init the Game object with a Snake on a 45x25 board and a piece of fruit """

    def __init__(self):
        self.done = False
        self.is_game_over = False
        self.game_display = pygame.display.set_mode((800, 450))
        self.clock = pygame.time.Clock()
        self.positions = set((x, y) for x in range(0, 45) for y in range(0, 25))
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
        self.wall_group.add(Wall(36, 16, 726, 4))
        # left
        self.wall_group.add(Wall(36, 16, 4, 406))
        # right
        self.wall_group.add(Wall(760, 16, 4, 408))
        # bottom
        self.wall_group.add(Wall(36, 420, 726, 4))
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
        score_text = FONT.render("Score: " + str(self.score), 1, (0, 0, 0))
        self.game_display.blit(score_text, (60, 427))

        if self.is_game_over:
            game_over_text = GAME_OVER_FONT.render("GAME OVER", 1, (0, 0, 0))
            game_over_rect = game_over_text.get_rect()
            # set to center of the screen
            game_over_rect.center = (800 / 2, 450 / 2)
            self.game_display.blit(game_over_text, game_over_rect)
            try_again_text = FONT.render("Press Space Bar to try again", 1, (0, 0, 0))
            try_again_rect = try_again_text.get_rect()
            try_again_rect.center = (800 / 2, game_over_rect.y + game_over_rect.height)
            self.game_display.blit(try_again_text, try_again_rect)

        pygame.display.flip()

    def update(self):
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

        # check for collisions
        self.check_for_collisions()

    def check_for_collisions(self):
        fruit_collision = pygame.sprite.collide_rect(self.snake.get_active_piece(), self.fruit)
        if fruit_collision:
            self.score += self.fruit.get_point_value()
            self.snake.max_size += self.fruit.get_size_value()
            self.fruit.play_eat_sound()
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

    def reset(self):
        pass


game = Game()
pygame.display.set_caption("Snake vs Pacman Ghosts")
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
        if event.key == pygame.K_SPACE and game.is_game_over:
            # start a new game
            game = Game()

    game.update()
    game.draw()

# required
pygame.quit()
quit()
