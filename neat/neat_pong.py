import pygame
import neat

from game import *

# Define the fitness function for evaluating the fitness of each genome
def evaluate_genome(genome, config):
    # Create a new neural network for this genome
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Initialize the game and play a game using the neural network
    game = Game()
    while not game.done:
        # Get the current state of the game
        state = game.get_game_state()

        # Feed the state through the neural network to get the action
        action = net.activate(state)

        # Take the action in the game
        game.run_one_frame(input=action, dt=1000/60, render=render, tickrate=60)

    # Return the fitness of the genome (in this case, the score of the game)
    return game.score

# Load the NEAT configuration file
config_path = "./neat/neat.ini"
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

# Create a new population of genomes using the configuration
population = neat.Population(config)

# Add a reporter to output the progress of the algorithm during training
stats = neat.StatisticsReporter()
population.add_reporter(stats)

# Run the NEAT algorithm for up to 100 generations
winner = population.run(evaluate_genome, 100)

# Use the best genome found during training to play a game of Pong
net = neat.nn.FeedForwardNetwork.create(winner, config)
pygame.init()
window_size = (800, 600)
render = False
game = Game(*window_size, render=render)
running = True
while running:
    state = game.get_game_state()
    action = net.activate(state)
    running = game.run_one_frame(input=action, dt=1000/60, render=render, tickrate=60)
