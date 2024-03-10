import pygame
import os
import random
import math
import sys
import neat

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

PLAYER = pygame.transform.scale2x(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/player.png"))

SKY = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/background.png"), (500, SCREEN_WIDTH))

TREE = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/tree.png"), (60, 180))

BG = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/base.png"), (SCREEN_WIDTH, 150))

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Player:
    X_POS = 200
    Y_POS = 405
    JUMP_VEL = 8.5

    def __init__(self):
        self.image = PLAYER
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, PLAYER.get_width(), PLAYER.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for tree in trees:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), tree.rect.center, 2)


class Tree:
    def __init__(self):
        self.image = TREE
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 295

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            trees.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)


def remove(index):
    players.pop(index)
    ge.pop(index)
    networks.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, trees, players, ge, networks, points
    clock = pygame.time.Clock()
    points = 0

    trees = []
    players = []
    ge = []
    networks = []

    x_pos_bg = 0
    y_pos_bg = 450
    game_speed = 20

    for genome_id, genome in genomes:
        players.append(Player())
        ge.append(genome)
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)
        genome.fitness = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))

    def statistics():
        global players, game_speed, ge
        text_1 = FONT.render(f'Players Alive:  {str(len(players))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        SCREEN.blit(text_1, (50, 20))
        SCREEN.blit(text_2, (50, 50))
        SCREEN.blit(text_3, (50, 80))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill("#87CEEB")

        for player in players:
            player.update()
            player.draw(SCREEN)

        if len(players) == 0:
            break

        if len(trees) == 0:
            trees.append(Tree())


        for tree in trees:
            tree.draw(SCREEN)
            tree.update()
            for i, player in enumerate(players):
                if player.rect.colliderect(tree.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, player in enumerate(players):
            output = networks[i].activate((player.rect.y,
                                       distance((player.rect.x, player.rect.y),
                                        tree.rect.midtop), game_speed))
            if output[0] > 0.5 and player.rect.y == player.Y_POS:
                player.dino_jump = True
                player.dino_run = False
                print("IM JUMPING CUS MY VALUE IS: " + str(output[0]))
            print("Im not jumping because my output is: " + str(output[0]))
            print("Game speed is currently: " + str(game_speed))

        statistics()
        score()
        background()
        clock.tick(30)
        pygame.display.update()


# Setup the NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)