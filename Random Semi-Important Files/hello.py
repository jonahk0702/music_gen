#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:20:42 2023

@author: maridel
"""

import os
import random
import music21
from music21 import stream, duration, midi

# Defining a function to extract the melody and chord progression from the midi files
def extract_features(filename):
    # Load the MIDI file into a music21 Stream object
    midi = music21.converter.parse(filename)
    
    # Extract the melody from the MIDI file
    melody = midi.parts[0].flat.notes
    
    # Extract the chord progression from the MIDI file
    chords = []
    for measure in midi.parts[1].measures(1, len(midi.parts[1])):
        chord = measure.chordify()
        chords.extend(chord.flat.getElementsByClass(music21.chord.Chord))
    
    return melody, chords

# Get features from midi dataset
midi_dir = "/Users/maridel/Desktop/music_gen/data/midi_dataset"

old_music = []
for file in os.listdir(midi_dir):
    if file.endswith(".mid") or file.endswith(".midi"):
        filename = os.path.join(midi_dir, file)
        melody, chords = extract_features(filename)
        sequence = [note.nameWithOctave for note in melody] + [chord.normalOrder for chord in chords]
        old_music.append(sequence)

# Define Fitness Function(s)
def evaluate_fitness(sequence):
    # Compute the number of matching notes and chords between the generated sequence and the original music
    matches = sum(1 for note in sequence if note in old_music)
    
    # Compute the total length of the generated sequence and the original music
    total_length = len(sequence) + sum(len(s) for s in old_music)
    
    # Check if total_length is greater than zero to avoid zero division error
    if total_length > 0:
        # Compute the fitness score as the ratio of matching notes and chords to the total length
        fitness_score = matches / total_length
    else:
        # If total_length is zero, set the fitness score to zero
        fitness_score = 0
        
    return fitness_score

def calculate_fitness(population):
    """
    Calculate the fitness score for each individual in the population
    """
    fitness_scores = []
    for individual in population:
        # Convert the individual to a music sequence
        sequence = individual
        # Evaluate the fitness of the sequence using the evaluate_fitness() function
        fitness_score = evaluate_fitness(sequence)
        
        # Append the fitness score to the list of fitness scores
        fitness_scores.append(fitness_score)
        
    return fitness_scores

# Starting Genetic Algorithm
POPULATION_SIZE = 100
MUTATION_RATE = 0.1
GENERATIONS = 50
length = len(old_music)

# Define function and parameters to generate random music
def generate_sequence(length):
    sequence = [random.choice(old_music) for j in range(length)]
    return sequence

def generate_population(length):
    population = []
    for i in range(POPULATION_SIZE):
        sequence = generate_sequence(length)
        population.append(sequence)

    return population

# Selection function
def select_parents(population, fitness_fn):
    # Sort the population based on fitness score in descending order
    sorted_population = sorted(population, key=fitness_fn, reverse=True)
    # Select the top performers to be parents for the next generation
    top_performers = sorted_population[:int(len(sorted_population)/2)]
    return top_performers

# Crossover function
def crossover(parent1, parent2):
    # Check that the length of the parent sequences is greater than zero
    if len(parent1) == 0 or len(parent2) == 0:
        return parent1, parent2
    
    # Combine the parents' sequences
    combined_sequence = parent1 + parent2
    # Randomly shuffle the combined sequence
    random.shuffle(combined_sequence)
    # Select a random crossover point
    crossover_point = random.randint(1, len(parent1)-1)
    # Perform crossover to create offspring
    offspring1 = combined_sequence[:crossover_point] + parent1[crossover_point:]
    offspring2 = combined_sequence[crossover_point:] + parent2[:crossover_point]
    return offspring1, offspring2


# Mutation function
def mutate(sequence, mutation_rate):
    # Check if sequence is empty and return as is
    if len(sequence) == 0:
        return sequence
    # Determine number of mutations based on mutation rate
    num_mutations = max(1, int(mutation_rate * len(sequence)))
    # Randomly select positions to mutate
    mutation_positions = random.sample(range(len(sequence)), num_mutations)
    # Mutate selected positions
    for position in mutation_positions:
        sequence[position] = random.choice(NOTES)
    return sequence
    
    
def run_genetic_algorithm(population_size, mutation_rate, generations):
    # Generate initial population
    population = generate_population(length)

    # Iterate through generations
    for i in range(generations):
        # Calculate fitness scores for each individual
        fitness_scores = calculate_fitness(population)

        # Select parents for next generation
        parents = select_parents(population, lambda x: evaluate_fitness(x))

        # Create new population by performing crossover and mutation
        offspring = []
        for j in range(population_size - len(parents)):
            parent1, parent2 = random.choices(parents, k=2)
            child1, child2 = crossover(parent1, parent2)
            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)
            offspring.append(child1)
            offspring.append(child2)

        # Combine parents and offspring to form next generation
        population = parents + offspring

    # Calculate fitness scores for final population
    fitness_scores = calculate_fitness(population)

    # Select the best individual in the final population
    best_individual = max(population, key=lambda x: evaluate_fitness(x))

    return best_individual    
    