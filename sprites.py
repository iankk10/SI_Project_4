import pygame
import sys
import os
import random
from collections import deque
from pygame import gfxdraw
from math import pi


class Snake(object):
    def __init__(self):
        # inactive group is all pieces we can collide with
        self.inactive_group = pygame.sprite.Group()
        # active group includes first two pieces since you cannot collide with them
        self.active_group = pygame.sprite.Group()
        self.pieces_deque = deque()
        self.max_size = 5
        self.add_piece(SnakePiece(2, 0, 0))
        self.next_direction = 2

    def add_piece(self, piece):
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
        # if we have more than our max size, remove the last piece of the snake
        if len(self.pieces_deque) > self.max_size:
            piece_to_remove = self.pieces_deque.pop()
            self.inactive_group.remove(piece_to_remove)

    def is_snake_full(self):
        return len(self.pieces_deque) == self.max_size

    def get_active_piece(self):
        return self.pieces_deque[0]

    def get_last_piece(self):
        return self.pieces_deque[-1]

    def update(self, next_direction):
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
        self.inactive_group.draw(surface)
        self.active_group.draw(surface)

    def get_pieces(self):
        return self.pieces_deque

    def create_new_piece(self, next_direction):
        active_piece = self.get_active_piece()
        new_piece = SnakePiece(next_direction, active_piece.rect.x, active_piece.rect.y)
        self.add_piece(new_piece)

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
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(sys.path[0], "images", "fruit" + str(random.randint(0, 4)) + ".gif")).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_point_value(self):
        return 10


class GhostFruit(Fruit):
    def get_point_value(self):
        return -10
