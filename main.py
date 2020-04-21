import os
import sys
import pygame
import time
import random
from pygame.locals import *


class Apple:
    def __init__(self):
        self.image = pygame.image.load("apple.png")
        self.rect = self.image.get_rect().move(self.get_apple_spawn_location())

    def spawn_apple(self):
        good_location = False
        while not good_location:
            self.rect.topleft = self.get_apple_spawn_location()
            good_location = True
            # Respawning the apple if it touches any part of the snake
            for i in range(0, snakeparts.__len__()):
                if snakeparts[i].rect.colliderect(apple.rect):
                    good_location = False


    def get_apple_spawn_location(self):
        return [random.randrange(0, width, standardSize), random.randrange(0, height, standardSize)]


class SnakePart:
    standardStep = 30
    lastPosition = None

    def __init__(self, picture):
        self.picture = picture
        self.image = pygame.image.load(picture)
        self.rect = self.image.get_rect()
        snakeparts.append(self)

    def build_tail(self):
        self.tail = SnakeTail(self.picture)
        self.tail.move(self.lastPosition)


class SnakeHead(SnakePart):
    speed = [0, 0]
    length = 1
    direction = -1  # 0 = UP, 1 = RIGHT, 2 = DOWN, 3 == LEFT, -1 = STANDING

    def set_speed(self):
        if self.direction == 0:
            self.speed = [0, -self.standardStep]
        elif self.direction == 1:
            self.speed = [self.standardStep, 0]
        elif self.direction == 2:
            self.speed = [0, self.standardStep]
        elif self.direction == 3:
            self.speed = [-self.standardStep, 0]
        else:
            self.speed = [0, 0]

    def move(self):
        self.lastPosition = self.rect.topleft
        if self.length > 1:
            self.tail.move(self.lastPosition)
        self.rect = self.rect.move(snake.speed)

    def append_snake(self):
        self.length += 1

        if self.length == 2:
            self.build_tail()
        else:
            self.tail.append_snake()

    def check_movement_legality(self, planned_movement):
        if self.direction == 0:
            if planned_movement != 2:
                return True
        elif self.direction == 1:
            if planned_movement != 3:
                return True
        elif self.direction == 2:
            if planned_movement != 0:
                return True
        elif self.direction == 3:
            if planned_movement != 1:
                return True
        else:
            return True
        return False


class SnakeTail(SnakePart):
    def __init__(self, picture):
        SnakePart.__init__(self, picture)
        self.appended = False

    def move(self, position):
        self.lastPosition = self.rect.topleft
        if self.appended:
            self.tail.move(self.lastPosition)
        self.rect.topleft = position
        screen.blit(self.image, self.rect)

    def append_snake(self):
        if not self.appended:
            self.appended = True
            self.build_tail()
        else:
            self.tail.append_snake()


class GameState:
    gameRunning = False
    endMessage = ""

    def start_game(self):
        self.gameRunning = True

    def stop_game(self, message):
        self.gameRunning = False
        self.endMessage = message


pygame.init()

size = width, height = 660, 480
standardSize = 30
black = 0, 0, 0
red = 255, 0, 0
background = black

minTimeBetweenMovement = 1 / 6  # Time between 2 updates in seconds
lastUpdate = time.time()

snakeparts = []
snake = SnakeHead("redSnake.png")
apple = Apple()

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

tempDirection = -1

game = GameState()
game.start_game()

while game.gameRunning:

    # Checking all events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
            if event.key == K_UP:
                tempDirection = 0
            if event.key == K_DOWN:
                tempDirection = 2
            if event.key == K_RIGHT:
                tempDirection = 1
            if event.key == K_LEFT:
                tempDirection = 3

    # Checking if enough time has passed to move
    if time.time() - lastUpdate >= minTimeBetweenMovement:
        lastUpdate = time.time()
        if snake.check_movement_legality(tempDirection):
            snake.direction = tempDirection
        snake.set_speed()
        snake.move()
        if snake.rect.colliderect(apple.rect):
            apple.spawn_apple()
            snake.append_snake()

    # Checking if the snake has touched the border of the screen
    if snake.rect.left < 0 or snake.rect.right > width:
        game.stop_game("Game Over!" + " Your Score: " + str(snakeparts.__len__() - 1))
    if snake.rect.top < 0 or snake.rect.bottom > height:
        game.stop_game("Game Over!" + " Your Score: " + str(snakeparts.__len__() - 1))

    # Checking if the head of the snake touched a tail
    for x in range(1, snakeparts.__len__()):
        if snakeparts[0].rect.colliderect(snakeparts[x]):
            game.stop_game("Game Over!" + " Your Score: " + str(snakeparts.__len__() - 1))

    # Drawing
    screen.fill(background)
    screen.blit(apple.image, apple.rect)
    for x in range(0, snakeparts.__len__()):
        screen.blit(snakeparts[x].image, snakeparts[x].rect)
    pygame.display.flip()

if pygame.font:
    font = pygame.font.Font(None, 50)
    text = font.render(game.endMessage, 1, red)
    textpos = text.get_rect(centerx=int(screen.get_width() / 2), centery=int(screen.get_height() / 2))
    screen.blit(text, textpos)
    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
