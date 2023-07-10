import os
import sys
import multiprocessing

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

import pygame
import numpy as np
import neat
# import visualize
# import graphviz
from game.pong import *

window_size = (800, 600)

def leaky_relu(x):
    return max(0.01*x, x)

def custom_init(genome_config, _):
    # Disable connections from the last input node
    num_inputs = genome_config.num_inputs
    num_hidden = genome_config.num_hidden
    num_outputs = genome_config.num_outputs

    last_input_node = num_inputs - 1

    for j in range(num_hidden, num_hidden + num_outputs):
        genome_config.init_connectivity[(last_input_node, j)] = 0.0

# Define the fitness function for evaluating the fitness of each genome
def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        # print("genome:", genome)
        # quit()
        
        # Create a new neural network for this genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Initialize the game and play a game using the neural network
        game = Game(*window_size, render=False, player2=GodPaddle(750 - 10, 0, 10, 600, Game.WHITE, False), vsync=False)
        while not game.done:
            # Get the current state of the game
            state = game.get_scaled_game_state()
            # print("game state:", state)

            # Feed the state through the neural network to get the action
            action = net.activate(state[0:5])
            # print("genome output:", action)
            
            # take highest value output neuron index
            action = np.argmax(action)

            # Take the action in the game
            game.run_one_frame(bot_input=action, dt=1000/60, render=False, tickrate=10000000000000)

        # set the fitness of the genome
        genome.fitness = game.paddle1.hits
        print(game.paddle1.hits)
        # only works for left paddle!! and counts the amount of hits, not the actual game score.

# Define the fitness function for evaluating the fitness of each genome
def evaluate_genome(genome, config):        
    # Create a new neural network for this genome
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    
    pygame.init()

    # Initialize the game and play a game using the neural network
    game = Game(*window_size, render=False, player2=GodPaddle(750 - 10, 0, 10, 600, Game.WHITE, False), vsync=False)
    while not game.done:
        # Get the current state of the game
        state = game.get_scaled_game_state()
        # print("game state:", state)

        # Feed the state through the neural network to get the action
        action = net.activate(state[0:5])
        # print("genome output:", action)
        
        # take highest value output neuron index
        action = np.argmax(action)

        # Take the action in the game
        game.run_one_frame(bot_input=action, dt=1000/60, render=False, tickrate=1000000000000000)

    # pygame.display.quit()

    # set the fitness of the genome
    # print(game.paddle1.hits)
    return game.paddle1.hits
    # only works for left paddle!! and counts the amount of hits, not the actual game score.

def run():
    # Load the NEAT configuration file
    config_path = "./neat/config.ini"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    config.genome_config.add_activation('leakyrelu', leaky_relu)

    # Set the custom initialization function. this sets all connections to the last input node to 0. this is the paddle2 position
    # config.genome_config.init_type = custom_init

    # Create a new population of genomes using the configuration
    population = neat.Population(config)

    # Add a reporter to output the progress of the algorithm during training
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.StdOutReporter(True))

    # initialize pygame
    pygame.init()

    # Run the NEAT algorithm for up to x generations
    # winner = population.run(evaluate_genomes, 20)

    # Run the NEAT algorithm on multiple cores for up to x generations
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), evaluate_genome)
    winner = population.run(pe.evaluate, 30)

    print("winner fitness:", winner.fitness)
    print(winner)

    # Use the best genome found during training to play a game of Pong
    net = neat.nn.FeedForwardNetwork.create(winner, config)

    render = True
    pygame.display.quit()
    game = Game(*window_size, render=render)

    while not game.done:
        state = game.get_scaled_game_state()
        action = net.activate(state[0:5])
        action = np.argmax(action)
        game.run_one_frame(bot_input=action, dt=1000/60, render=render, tickrate=60)

if __name__ == "__main__":
    run()
