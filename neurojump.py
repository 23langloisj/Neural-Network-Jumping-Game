# Necessary imports for game
import pygame
import os
import random
import math
import sys
import neat

# Initalize game
pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Audio
boop_sound = pygame.mixer.Sound("COUNT5.wav")
death_sound = pygame.mixer.Sound("DEATH.wav")

# Player Sprite
PLAYER = pygame.transform.scale2x(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/player.png"))

# Backdrop Image
SKY = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/background.png"), (500, SCREEN_WIDTH))

# Obstacle Image
TREE = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/tree.png"), (60, 180))

# Grass Floor
BG = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/base.png"), (SCREEN_WIDTH, 150))

# Font
FONT = pygame.font.Font('freesansbold.ttf', 20)

# Represents a Player
class Player:
    # Constants for Player
    X_POS = 200
    Y_POS = 405
    JUMP_VEL = 8.5

    def __init__(self):
        self.image = PLAYER
        # Boolean flag determining if player should run
        self.dino_run = True
        # Boolean flag determining if player should jump
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        # Player is represented as a rect (think of as just a mxn area)
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, PLAYER.get_width(), PLAYER.get_height())
        # Each Player takes a random color because it looks cool
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Updates the location of the Player
    # If it needs to jump then have it jump and same for running
    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

    # If a player is jumping sets its velocity in the upward direction and adds it to position
    # Makes sure jumping velocity doesn't get too high
    def jump(self):
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    # Sets the position of the Player in the correct spot
    def run(self):
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

    # Draws the Player onto the screen
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        # Draws a line from each player to the center of the nearest tree obstacle
        for tree in trees:
            pygame.draw.line(SCREEN, self.color, (self.rect.x, self.rect.y + 20), tree.rect.center, 2)

# Reprents a Tree which is the obstacle of the game
class Tree:
    def __init__(self):
        self.image = TREE
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 295

    # Updates position of Tree and makes it scroll down the page
    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            trees.pop()

    # Draws the tree onto the given screen
    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)

# Funciton to calculate the euclidian distance between two points
def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)

# Evaluated fitness of each genome
def eval_genomes(genomes, config):
    # Global constants
    global game_speed, x_pos_bg, y_pos_bg, trees, players, ge, networks, score
    clock = pygame.time.Clock()
    score = 0

    # Initalize global constants
    # Setup array for the obstacles, players, genomes, and neural networks
    trees = []
    players = []
    ge = []
    networks = []

    # Constants determining the initial game speed and position of the floor
    x_pos_bg = 0
    y_pos_bg = 450
    game_speed = 20

    # Iterates through all genomes and feeds the neural network
    # All genomes start at a fitness level of zero
    for genome_id, genome in genomes:
        players.append(Player())
        ge.append(genome)
        network = neat.nn.FeedForwardNetwork.create(genome, config) # config file is 'config-feedforward.txt'
        networks.append(network)
        genome.fitness = 0 # starts at 0

    # Function to display the currents score of the players
    def display_score():
        global score, game_speed
        for i, player in enumerate(players):
            ge[i].fitness += 0.1
        score += 1
        # Slowly increases the speed / difficulty at which the game is played
        if score % 25 == 0:
            game_speed += 1
        for i, player in enumerate(players):
            ge[i].fitness += .25 * game_speed
        if game_speed >= 50:
            game_speed = 50
        text = FONT.render(f'Score:  {str(score)}', True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))

    # Function to display other informative statistics about the game
    def statistics():
        global players, game_speed, ge
        text_1 = FONT.render(f'Players Alive:  {str(len(players))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        SCREEN.blit(text_1, (50, 20))
        SCREEN.blit(text_2, (50, 50))
        SCREEN.blit(text_3, (50, 80))

    # Function that draws the ground on the screen and gives it the affect of motion
    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    # Pygame
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Creates the blue sky
        SCREEN.fill("#87CEEB")

        # Moves all the players and draws them on the screen
        for player in players:
            player.update()
            player.draw(SCREEN)

        # If all players die then break
        if len(players) == 0:
            break

        # if there are no obstacles then add one
        if len(trees) == 0:
            trees.append(Tree())

        # Iterates through all trees and draws them on screen then moves them towards the players
        for tree in trees:
            tree.draw(SCREEN)
            tree.update()
            for i, player in enumerate(players):
                if player.rect.colliderect(tree.rect):
                    ge[i].fitness -= 32 # punishes players for hitting the tree
                    # "kills" players that hit the tree
                    ge.pop(i) 
                    networks.pop(i)
                    players.pop(i)
                    death_sound.play()

        # Feeds the players information which the neural network will then decide whether or not to jump
        for i, player in enumerate(players):
            # network is given the y coordinate of the player, the distance between the player and the obstacle,
            # and the current speed at which the game is being played
            output = networks[i].activate((player.rect.y,
                                       distance((player.rect.x, player.rect.y),
                                        tree.rect.midtop), game_speed))
            
            # Using a tanh function so output values are between [-1, 1] if > 0 then network tells player to jump
            if output[0] > 0.5 and player.rect.y == player.Y_POS:
                player.dino_jump = True
                player.dino_run = False
                boop_sound.play()
                print("I will jump because my output is: " + str(output[0])) # Debugging statements
            print("I will not jump because my output is: " + str(output[0]))
            print("Game speed is currently: " + str(game_speed))

        # Execute all the functions to put together the game
        statistics()
        display_score()
        background()
        clock.tick(30)
        pygame.display.update()


# Configure the NEAT neural network
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
    pop.run(eval_genomes, 15)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)