# Necessary imports 
import pygame
import random
import os
import neat
pygame.font.init()  # init font


WINDOW = pygame.display.set_mode((960, 720))
pygame.display.set_caption("AI Learns to play Jumping game")
gravity = 20
generation = 0

player_img = pygame.transform.scale2x(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/player.png").convert_alpha())
tree_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/tree.png").convert_alpha(), (60,120))
ground_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/base.png").convert_alpha(), (960, 150))
background_img = pygame.transform.scale(pygame.image.load("/Users/jake.langlois/Desktop/MLJumpingGame/images/background.png").convert_alpha(), (960, 720))


# Represents the cube that is the player and its methods
class Player:
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
    WIDTH = ground_img.get_width()
    IMG = ground_img

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

def draw_window(window, players, trees, score, ground, generation, tree_index):
    # Generation 0 DNE
    if generation == 0:
        generation = 1
    
    # Draw background onto the screen
    window.blit(background_img, (0, 0))

    # Draws the floor onto the screen
    ground.draw(WINDOW)

    for tree in trees:
        tree.draw(WINDOW)
    
    for player in players:
        # Draws Players COME BACK TO ADD VISION LINES
        player.draw(WINDOW)
    
    # Draws the score of the game
    score_label = pygame.font.SysFont("comicsans", 50).render("Score: " + str(score),1,(255,255,255))
    window.blit(score_label, (480, 50))

    # Draws the number of generations so far
    score_label = pygame.font.SysFont("comicsans", 50).render("Gens: " + str(generation-1),1,(255,255,255))
    window.blit(score_label, (10, 10))

    # Draws number of players alive
    score_label = pygame.font.SysFont("comicsans", 50).render("Alive: " + str(len(players)),1,(255,255,255))
    window.blit(score_label, (10, 50))

    pygame.display.update()

def eval_genomes(genomes, config):
    # Initialize necessary variables
    global WINDOW, generation
    window = WINDOW
    generation += 1

    # Create a list of genomes, their associated neural networks, and 
    # Players that will be using the neural networks to play
    ge = []
    players = []
    networks = []

    for genome_id, genome in genomes:
        genome.fitness = 0 # genomes start with no "skill"
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        players.append(Player(300, 570))
        ge.append(genome)

    ground = Ground(570)
    trees = [Tree(800)]
    score = 0

    clock = pygame.time.Clock()

    run = True

    while run and len(players) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        tree_index = 0
        
        for x, player in enumerate(players):
            ge[x].fitness += 0.1 # increases skill of each player for every frame they live
            player.move()
        
            # Sends Player information about its location and the nearest tree 
            output = networks[players.index(player)].activate((player.x, abs(trees[tree_index].x - player.x), 60))


            if output[0] > 0.5:
                player.jump()
            
        ground.move()

        rem = []
        add_tree = False
        for tree in trees:
            tree.move()
            for player in players:
                if tree.collision(player, window):
                    ge[players.index(player)].fitness -= 1
                    networks.pop(players.index(player))
                    ge.pop(players.index(player))
                    players.pop(players.index(player))
                
            if tree.x < 10:
                rem.append(tree)
                
            if not tree.hopped and tree.x < player.x:
                tree.hopped = True
                add_tree = True
                
        if add_tree:
            score += 1
            for genome in ge:
                genome.fitness += 5
                trees.append(Tree(800))

        for r in rem:
            trees.remove(r)

        draw_window(WINDOW, players, trees, score, ground, generation, tree_index)

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 20 generations.
    winner = p.run(eval_genomes, 20)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
        


        
        



    

        


