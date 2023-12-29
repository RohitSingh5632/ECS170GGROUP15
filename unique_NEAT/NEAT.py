import pickle
import queue
import NEAT_population as P
import NEAT_snake2 as snake
from NEAT_network import Network
from NEAT_genome import Genome, NodeGene, ConnectionGene
import random


def find_best_genomeXOR(population):
    for s in population.species:
        #show best_genome results on task
        for i in range(2):
            for j in range(2):
                #reset recurrent activations
                for node in s.rep_genome.nodeGenes:
                    node.recurrentActivation = 0
                #evaluate for certain number of cycles
                for k in range(5):
                    s.rep_genome.network.forwardProp([i, j], s.rep_genome)
                print(str((i, j)) + ", ", end="")
                for node in s.rep_genome.outputNodes:
                    print(str(node.activation) + ", ", end="")
                print("")
        print("------------------------")
    for g in population.genomes:
        g.evaluate()
    best_genome = max(population.genomes, key = lambda x : x.fitness)
    best_genome.network.printAdjList()    
    best_genome.printGenome()
    print(best_genome.fitness)
    save(best_genome)


    
    

def save(genome):
    with open('NEAT_bestGenome', 'wb') as file:
        pickle.dump(genome, file)
    print("Genome saved to files!")
            
def load(file):
    genome = None    
    with open("NEAT_bestGenome", 'rb') as file:
        genome = pickle.load(file)
    return genome
    

def find_best_genome(population):
    for s in population.species:
        best_genome = max(s.members, key = lambda x : x.fitness)
        best_genome.fitness = snake.train_food_direction(s.rep_genome, True)
        #best_genome.network.printAdjList()
        #best_genome.printGenome()
        print(s.rep_genome.fitness)
    for g in population.genomes:
        g.fitness = snake.train_food_direction(g, True)
    best_genome = max(population.genomes, key = lambda x : x.fitness)
    best_genome.network = Network(best_genome)
    best_genome.network.printAdjList()    
    best_genome.printGenome()
    print(best_genome.fitness)
    save(best_genome)

def NEAT(loading):
    if loading == True:
        seed_genome = load("NEAT_bestGenome")
        population = P.Population(100, (15, 3), seed_genome)
        population.evolve(1000)
        find_best_genome(population)
    else:
        population = P.Population(100, (15, 3))
        population.evolve(1000)
        find_best_genome(population)

loading = False
for i in range(10):
    print("##########################")
    print(i)
    if loading == False:        
        NEAT(False)
        loading = True
    else:
        NEAT(True)

#population = P.Population(1000, (2, 1))
#population.evolve(100)
#find_best_genomeXOR(population)


#best = load("NEAT_bestGenome")
#best.fitness = snake.train_food_direction(best, True)
#print(best.fitness)

