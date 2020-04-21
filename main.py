import os
import sys
import pygame
import time
import random
from pygame.locals import *


snakepartsPlayer = []
snakepartsEnemy = []

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
            for i in range(0, snakepartsPlayer.__len__()):
                if snakepartsPlayer[i].rect.colliderect(apple.rect):
                    good_location = False
            for i in range(0, snakepartsEnemy.__len__()):
                if snakepartsEnemy[i].rect.colliderect(apple.rect):
                    good_location = False

    def get_apple_spawn_location(self):
        return [random.randrange(0, width, standardSize), random.randrange(0, height, standardSize)]


class SnakePart:
    standardStep = 30
    lastPosition = None

    def __init__(self, picture, is_ki):
        self.isKI = is_ki
        self.picture = picture
        self.image = pygame.image.load(picture)
        self.rect = self.image.get_rect()
        if not self.isKI:
            snakepartsPlayer.append(self)
        else:
            snakepartsEnemy.append(self)

    def build_tail(self):
        self.tail = SnakeTail(self.picture, self.isKI)
        self.tail.move(self.lastPosition)


class SnakeHead(SnakePart):
    speed = [0, 0]
    length = 1
    direction = -1  # 0 = UP, 1 = RIGHT, 2 = DOWN, 3 == LEFT, -1 = STANDING

    def __init__(self, picture, starting_location, is_ki):
        super().__init__(picture, is_ki)
        self.rect.topleft = starting_location

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
        self.rect = self.rect.move(self.speed)

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

    def calculate_direction(self, apple_target):
        # Calculates the optimal direction for the AI snake
        options = [0, 0, 0, 0]  # options[x] shows the weight for this direction
        x = self.rect.topleft[0]
        y = self.rect.topleft[1]
        min_x = 0
        max_x = width - standardSize
        min_y = 0
        max_y = height - standardSize
        apple_x = apple_target.rect.topleft[0]
        apple_y = apple_target.rect.topleft[1]

        # Removing the illegal option by giving it a weight of -10000
        for i in range(0, 5):
            if not self.check_movement_legality(i):
                options[i] -= 10000

        # Heavily discouraging the option to move into a wall by giving it a weight of -1000
        if x == min_x:
            options[3] -= 1000
        if x == max_x:
            options[1] -= 1000
        if y == min_y:
            options[0] -= 1000
        if y == max_y:
            options[2] -= 1000

        # Encouraging the option to move closer to the apple, by giving a positive weight of 50
        if x > apple_x:
            options[3] += 50
        elif x < apple_x:
            options[1] += 50
        if y > apple_y:
            options[0] += 50
        elif y < apple_y:
            options[2] += 50

        print("Best option: ", str(options.index(max(options))))
        return options.index(max(options))


class SnakeTail(SnakePart):
    def __init__(self, picture, is_ki):
        SnakePart.__init__(self, picture, is_ki)
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

starting_location_player = (0, 0)
snake = SnakeHead("redSnake.png", starting_location_player, False)

starting_location_enemy = (width - standardSize, height - standardSize)
enemy = SnakeHead("greenSnake.png", starting_location_enemy, True)

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

    # Checking if enough time has passed to move, only checks when player started moving
    if not tempDirection == -1:
        if time.time() - lastUpdate >= minTimeBetweenMovement:
            print("We are moving now")
            lastUpdate = time.time()
            # Move player snake
            if snake.check_movement_legality(tempDirection):
                snake.direction = tempDirection
            snake.set_speed()
            snake.move()

            # Move enemy snake
            enemy.direction = enemy.calculate_direction(apple)
            print("Moving towards: ", str(enemy.direction))
            enemy.set_speed()
            enemy.move()

            # Check apple collision
            if snake.rect.colliderect(apple.rect):
                apple.spawn_apple()
                snake.append_snake()
            if enemy.rect.colliderect(apple.rect):
                apple.spawn_apple()
                enemy.append_snake()

    # Checking if the player has touched the border of the screen
    if snake.rect.left < 0 or snake.rect.right > width:
        game.stop_game("Verloren!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))
    if snake.rect.top < 0 or snake.rect.bottom > height:
        game.stop_game("Verloren!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))

    # Checking if the enemy has touched the border of the screen
    if enemy.rect.left < 0 or enemy.rect.right > width:
        game.stop_game("Gewonnen!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))
    if enemy.rect.top < 0 or enemy.rect.bottom > height:
        game.stop_game("Gewonnen!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))

    # Checking if a head touched player tail
    for x in range(1, snakepartsPlayer.__len__()):
        if snakepartsPlayer[0].rect.colliderect(snakepartsPlayer[x]):
            game.stop_game("Verloren!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))
        if snakepartsEnemy[0].rect.colliderect(snakepartsPlayer[x]):
            game.stop_game("Gewonnen!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))

    # Checking if a head touched enemy tail
    for x in range(1, snakepartsEnemy.__len__()):
        if snakepartsEnemy[0].rect.colliderect(snakepartsEnemy[x]):
            game.stop_game("Gewonnen!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))
        if snakepartsPlayer[0].rect.colliderect(snakepartsEnemy[x]):
            game.stop_game("Verloren!" + " Schlangenlänge: " + str(snakepartsPlayer.__len__() - 1))

    # TODO: CHECK SNAKE Head2Head COLLISION

    # Drawing
    screen.fill(background)
    screen.blit(apple.image, apple.rect)
    for x in range(0, snakepartsPlayer.__len__()):
        screen.blit(snakepartsPlayer[x].image, snakepartsPlayer[x].rect)
    for x in range(0, snakepartsEnemy.__len__()):
        screen.blit(snakepartsEnemy[x].image, snakepartsEnemy[x].rect)
    pygame.display.flip()

# TODO: SHOW WINNER AND SCORE
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
