import pygame.mixer
import sys
import os
import random
from collections import deque
from math import hypot

pygame.mixer.init()

OFFSET_X = 40
OFFSET_Y = 20
BOO_SOUND = pygame.mixer.Sound(os.path.join(sys.path[0],
                                            "sounds", "boo.wav"))
FRUIT_EAT_SOUND = pygame.mixer.Sound(os.path.join(sys.path[0],
                                                  "sounds", "fruit_eat.wav"))
GHOST_EAT_SOUND = pygame.mixer.Sound(os.path.join(sys.path[0],
                                                  "sounds", "ghost_eat.wav"))


class Snake(object):
    def __init__(self):
        # inactive group is all pieces we can collide with
        self.inactive_group = pygame.sprite.Group()
        # active group includes first two pieces since you cannot collide with them
        self.active_group = pygame.sprite.Group()
        self.pieces_deque = deque()
        self.max_size = 10
        self.next_direction = 2
        self.is_first_piece = True

    def add_piece(self, piece, board_positions):
        """ Add a piece to the front of the snake """
        if len(self.active_group) < 2:
            # less than 2 active pieces, add the new piece to active group
            self.active_group.add(piece)
        elif len(self.active_group) == 2:
            # we have 2 pieces, need to remove the second
            current_second = self.pieces_deque[1]
            self.active_group.remove(current_second)
            self.inactive_group.add(current_second)
        self.pieces_deque.appendleft(piece)
        self.active_group.add(piece)
        # remove the position of the new piece from the active options, ignore the exception if we have a piece outside
        # the board -- this happens when you hit a wall
        try:
            board_positions.remove(piece.position)
        except KeyError as ignored:
            pass
        # if we have more than our max size, remove the last piece of the snake
        if len(self.pieces_deque) > self.max_size:
            piece_to_remove = self.pieces_deque.pop()
            board_positions.add(piece_to_remove.position)
            self.inactive_group.remove(piece_to_remove)

    def is_snake_full(self):
        """ Checks if the snake length is at capacity """
        return len(self.pieces_deque) == self.max_size

    def get_active_piece(self):
        """ Gets the currently active (front) snake piece """
        return self.pieces_deque[0]

    def get_last_piece(self):
        """ Gets the last piece in the current snake"""
        return self.pieces_deque[-1]

    def update(self, next_direction):
        """ Updates the snake, moving the active piece in the current direction, as well as takes input for the next
            direction """
        self.next_direction = next_direction
        self.get_active_piece().update()
        # need to animate last piece if we're at max size
        if len(self.pieces_deque) == self.max_size:
            second_to_last = self.pieces_deque[-2]
            last = self.pieces_deque[-1]
            direction = second_to_last.direction
            if direction == 1:
                last.rect = last.rect.move(-4, 0)
            elif direction == 2:
                last.rect = last.rect.move(4, 0)
            elif direction == 3:
                last.rect = last.rect.move(0, -4)
            else:
                last.rect = last.rect.move(0, 4)

    def draw(self, surface: pygame.Surface):
        """ Draws the snake """
        self.inactive_group.draw(surface)
        self.active_group.draw(surface)

    def get_pieces(self):
        """ Gets all pieces in the snake """
        return self.pieces_deque

    def create_new_piece(self, next_direction, board_positions):
        """ Creates a new piece for the snake with a given direction, updating the available board positions """
        if self.is_first_piece:
            self.is_first_piece = False
            new_piece = SnakePiece(2, OFFSET_X, OFFSET_Y)
        else:
            active_piece = self.get_active_piece()
            new_piece = SnakePiece(next_direction, active_piece.rect.x, active_piece.rect.y)
        self.add_piece(new_piece, board_positions)

    def current_direction(self):
        return self.get_active_piece().direction

    def check_collision(self):
        head_collision = pygame.sprite.groupcollide(self.active_group, self.inactive_group, False, False)
        return head_collision


class SnakePiece(pygame.sprite.Sprite):
    """ Class for each piece of snake. Provides the direction and center point
        For direction 1 = LEFT, 2 = RIGHT, 3 = UP, 4 = DOWN """

    def __init__(self, direction, x, y):
        super().__init__()
        self.direction = direction
        self.image = pygame.Surface([16, 16])
        self.image.fill((255, 238, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.progress = 0
        # Sets the final position on the board of the snake. Since we start in the previous position and animate out,
        # this is necessary
        if self.direction == 1:  # LEFT
            self.position = (int((x - OFFSET_X - 16) / 16), int((y - OFFSET_Y) / 16))
        elif self.direction == 2:  # RIGHT
            self.position = (int((x - OFFSET_X + 16) / 16), int((y - OFFSET_Y) / 16))
        elif self.direction == 3:  # UP
            self.position = (int((x - OFFSET_X) / 16), int((y - OFFSET_Y - 16) / 16))
        else:  # DOWN
            self.position = (int((x - OFFSET_X) / 16), int((y - OFFSET_Y + 16) / 16))

    def update(self):
        if self.progress < 4:
            self.progress += 1
            if self.direction == 1:
                self.rect = self.rect.move(-4, 0)
            elif self.direction == 2:
                self.rect = self.rect.move(4, 0)
            elif self.direction == 3:
                self.rect = self.rect.move(0, -4)
            else:
                self.rect = self.rect.move(0, 4)


class Fruit(pygame.sprite.Sprite):
    """ Class for a normal piece of fruit. Eating one increases score by 10 and increases Snake max length by 1 """

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(sys.path[0], "images", "fruit" + str(random.randint(0, 4)) + ".gif")).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_point_value(self):
        return 10

    def update(self, snake_rect):
        return False

    def get_size_value(self):
        return 1

    @staticmethod
    def play_eat_sound():
        FRUIT_EAT_SOUND.play()


class GhostFruit(Fruit):
    """ Class for a Ghost Fruit disguised as a real fruit. Eating one will decrease score by 10 and increase snake size
        by 5. Ghost Fruits appear as fruit until the snake is close to them, then they reveal as a ghost. If not eaten
        for a short time after being revealed, the ghost will disappear. """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.ghost_image = pygame.image.load(
            os.path.join(sys.path[0], "images", "ghost" + str(random.randint(1, 4)) + ".gif")).convert()
        self.revealed = False
        self.active_frames = 0

    def get_point_value(self):
        return -10

    def update(self, snake_rect):
        if self.revealed:
            self.active_frames += 1
        else:
            dist = hypot(self.rect.x - snake_rect.x, self.rect.y - snake_rect.y)
            if dist < 48 and not self.revealed:
                # play sound here
                self.image = self.ghost_image
                BOO_SOUND.play()
                self.revealed = True

        if self.active_frames == 32:
            return True
        else:
            return False

    def get_size_value(self):
        return 5

    @staticmethod
    def play_eat_sound():
        GHOST_EAT_SOUND.play()


class Wall(pygame.sprite.Sprite):
    def __init__(self, rect_x, rect_y, surface_width, surface_height):
        super().__init__()
        self.image = pygame.Surface([surface_width, surface_height])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = rect_x
        self.rect.y = rect_y
