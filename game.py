# Necessary imports 
import pygame
import random
import os
import neat

WINDOW = pygame.display.set_mode((960, 720))
pygame.display.set_caption("AI Learns to play Jumping game")

player_img = pygame.transform.scale2x(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/player.png").convert_alpha())
tree_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/tree.png").convert_alpha(), (60,120))
base_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/base.png").convert_alpha(), (960, 150))
background_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/background.png").convert_alpha(), (960, 720))


# Represents the cube that is the player and its methods
class Player:
    gravity = 20
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.IMG = player_img
        self.in_air = False

    def jump(self):
        if not self.in_air:
            self.velocity = -42
            self.in_air = True
        
    def move(self):
        # for downward acceleration
        self.velocity += gravity

        self.y += self.velocity

        if self.y >= 550:
            self.velocity = 0
            self.y = 550
            self.in_air = False
            
    def draw(self, surface):
        surface.blit(self.IMG, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

class Tree:
    speed = 5

    def __init__(self, x):
        self.x = x
        self.bottom = 0
        self.IMG = tree_img
        self.hopped = False

    def move(self):
        self.x -= 7.5

    def draw(self, window):
        window.blit(self.IMG, (self.x, 460))

    # Returns if a collision occurs between this tree and the player
    def collision(self, player, window):
        player_mask = player.get_mask()
        tree_mask = pygame.mask.from_surface(self.IMG)
        offset = (self.x - player.x, 460 - player.y)
        result = player_mask.overlap(tree_mask, offset)

        if result:
            return True
        
        return False
        

# Represents the Ground that randomly spawns obstacles that the player
class Ground:
    speed = 7.5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    
    def move(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    
    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))

# pygame setup
pygame.init()
clock = pygame.time.Clock()
running = True
gravity = 3


# Player Info
player = Player(300, 550)

# Ground Info
ground = Ground(570)

# Tree Info
tree = Tree(800)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Draws background image onto game
    WINDOW.blit(background_img, (0, 0))
    
    # Draws the flooring of the game
    ground.draw(WINDOW)

    # Scrolls the floor to the left
    ground.move()

    # Draws Player and Handles them jumping
    player.draw(WINDOW)
    player.move()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and player.velocity == 0:
        player.jump()
    
    # Draws Obstacles and slides them towards player (Trees)
    tree.draw(WINDOW)
    tree.move()

    # Handles Collision Logic
    if tree.collision(player, WINDOW):
        print("HE HIT THE THING")


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()