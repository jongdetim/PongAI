import os
import sys

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

import pygame
import numpy as np
import neat
# import visualize
# import graphviz
from game.pong import *

window_size = (800, 600)

leaky_relu = lambda x: max(0.01*x, x)

# Define the fitness function for evaluating the fitness of each genome
def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        print("genome:", genome)
        
        # Create a new neural network for this genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Initialize the game and play a game using the neural network
        game = Game(*window_size, render=True)
        while not game.done:
            # Get the current state of the game
            state = game.get_game_state()
            print("game state:", state)

            # Feed the state through the neural network to get the action
            action = net.activate(state)
            print("genome output:", action)
            action = np.argmax(action)

            # Take the action in the game
            game.run_one_frame(input=action, dt=1000/60, render=True, tickrate=60)

        # set the fitness of the genome (in this case, the score of the game)
        genome.fitness = game.score1
        # only works for left paddle!!

# Load the NEAT configuration file
config_path = "./neat/neat.ini"
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
config.genome_config.add_activation('leakyrelu', leaky_relu)


# Create a new population of genomes using the configuration
population = neat.Population(config)

# Add a reporter to output the progress of the algorithm during training
stats = neat.StatisticsReporter()
population.add_reporter(stats)

# initialize pygame
pygame.init()

# Run the NEAT algorithm for up to 100 generations
winner = population.run(evaluate_genomes, 100)

# Use the best genome found during training to play a game of Pong
net = neat.nn.FeedForwardNetwork.create(winner, config)
pygame.init()

render = True
game = Game(*window_size, render=render)
running = True
while running:
    state = game.get_game_state()
    action = net.activate(state)
    running = game.run_one_frame(input=action, dt=1000/60, render=render, tickrate=60)
