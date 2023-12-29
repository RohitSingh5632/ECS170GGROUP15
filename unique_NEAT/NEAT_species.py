import random
import copy

import NEAT_genome as G
speciesID = 0

class Species:
    
    def __init__(self, first_member):
        global speciesID
        self.ID = speciesID
        speciesID += 1
        self.members = [first_member]
        self.shared_fitness = 0
        self.rep_genome = first_member
        self.stagnation = 0
        self.prev_best = 0
    
    def select_parents(self):
        #print(len(self.members))
        #for g in self.members:
         #   print(str(round(g.fitness, 3)) + ", ",end="")
        #print(len(self.members))
        if len(self.members) > 1:
            #parent1 = random.choice(self.members)
            #parent2 = random.choice(self.members)
            
            #parent1
            cumulative_fitness = 0
            threshold = random.uniform(0, self.shared_fitness)
            parent1 = None
            for g in self.members:
                #print(g.fitness)
                adj_fitness = g.fitness / len(self.members)
                cumulative_fitness += adj_fitness
                #print((cumulative_fitness, threshold, self.shared_fitness, g))
                if cumulative_fitness >= threshold:
                    parent1 = g
            #parent2
            cumulative_fitness = 0
            threshold = random.uniform(0, self.shared_fitness)
            parent2 = None
            for g in self.members:
                adj_fitness = g.fitness / len(self.members)
                cumulative_fitness += adj_fitness
                #print((cumulative_fitness, threshold, self.shared_fitness, g, True))
                if cumulative_fitness >= threshold:
                    parent2 = g
            
        else:
            return self.members[0], self.members[0]  
        return parent1, parent2
    
    def crossover(self, g1, g2):
        offspring_nodes = []
        offspring_conns = []
        genes1 = g1.connectionGenes
        genes2 = g2.connectionGenes
        #determine which genome is larger
        if len(genes1) > len(genes2):
            small = g2
            large = g1
        else:
            small = g1
            large = g2
       # print(g1.connectionGenes)
       # print(g2.connectionGenes)
        i = 0
        j = 0
        #add connection genes to offspring
        while i < len(small.connectionGenes) and j < len(large.connectionGenes):
            conn1 = small.connectionGenes[i]
            conn2 = large.connectionGenes[j]
 
            #when matching genes have mismatching enabled states, take the enabled gene
            if conn1.innovNum == conn2.innovNum:
                if conn1.enabled == conn2.enabled:
                    if random.random() >= 0.5:
                        offspring_conns.append(conn1)
                    else:
                        offspring_conns.append(conn2)
                else:
                    if conn1.enabled == True:
                        offspring_conns.append(conn1)
                    else:
                        offspring_conns.append(conn2)
                i += 1
                j += 1
            elif conn1.innovNum < conn2.innovNum:
                if small.fitness > large.fitness:
                    offspring_conns.append(conn1)
                i += 1
            else:
                if large.fitness > small.fitness:
                    offspring_conns.append(conn2)
                j += 1
        for k in range(j, len(large.connectionGenes)):
            conn2 = large.connectionGenes[k]
            offspring_conns.append(conn2)
        
        #add nodes to nodeGenes
        node_record = []

        for node in g1.nodeGenes:
            if node.innovNum not in node_record:
                offspring_nodes.append(node)
                node_record.append(node.innovNum)
        for node in g2.nodeGenes:
            if node.innovNum not in node_record:
                offspring_nodes.append(node)
                node_record.append(node.innovNum)
        for conn in offspring_conns:
            if conn.In.innovNum not in node_record:
                offspring_nodes.append(conn.In)
                node_record.append(conn.In.innovNum)
            if conn.Out.innovNum not in node_record:
                offspring_nodes.append(conn.Out)
                node_record.append(conn.Out.innovNum)
        if g1.biasNode not in offspring_nodes:
            offspring_nodes.append(g1.biasNode)
        offspring_nodes2 = copy.deepcopy(offspring_nodes)
        offspring_conns2 = copy.deepcopy(offspring_conns)
        offspring = G.Genome(child_genes = (offspring_nodes2, offspring_conns2))
       # print(offspring.connectionGenes)
       # print("--------")
        return offspring