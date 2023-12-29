import numpy as np
import random
import math
import numpy as np

import NEAT_network as NN

np.seterr(all="ignore")

connectionInnovation = 0
nodeInnovation = 0

toggle_chance = 0.05
split_conn_chance = 0.05
add_conn_chance = 0.1
weight_mutation_chance = 0.4
weight_perturbation_chance = 0.9

split_history = {}
connection_history = {}

#2 inputs; 1 output
def XOR(x1, x2):
    if x1 == x2:
        return 0
    return 1

class Genome:

    def __init__(self, In = None, Out = None, child_genes = None):
        self.inputNodes = []
        self.hiddenNodes = []
        self.outputNodes = []
        self.biasNode = None
        
        if In == None and Out == None and child_genes != None:
            self.nodeGenes = child_genes[0] 
            #needs to be in sorted order based on innovationNum for proper crossover to occur
            self.connectionGenes = child_genes[1] 
        else:
            self.nodeGenes, self.connectionGenes = self.initNetwork(In, Out)
        
        #assign nodes to lists by type
        for node in self.nodeGenes:
            if node.type == 0:
                self.inputNodes.append(node)
            elif node.type == 1:
                self.hiddenNodes.append(node)
            elif node.type == 2:
                self.outputNodes.append(node)
            elif node.type == 3:
                self.biasNode = node
                
        #create the network using nodes and connections
        self.network = NN.Network(self)
        #assign each genome an individual fitness
        self.fitness = 0

    def initNetwork(self, In, Out):
        global nodeInnovation, connectionInnovation
        initNodeGenes = []
        initConnectionGenes = []
        #initiate all input nodes
        for g in range(In):
            nodeGene = NodeGene(0, nodeInnovation)
            initNodeGenes.append(nodeGene)
            nodeInnovation += 1
        #initiate all output layers
        for h in range(Out):
            nodeGene = NodeGene(2, nodeInnovation)
            initNodeGenes.append(nodeGene)
            nodeInnovation += 1
        #create connections
        
        for i in range(In):
            for j in range(Out):
                w = random.uniform(-1, 1)
                connectionGene = ConnectionGene(initNodeGenes[i], initNodeGenes[In + j], w, connectionInnovation)
                initConnectionGenes.append(connectionGene)
        
        #create a bias node
        biasNodeGene = NodeGene(3, nodeInnovation)
        nodeInnovation += 1
        initNodeGenes.append(biasNodeGene)
        return initNodeGenes, initConnectionGenes
        
    def printGenome(self):
        for node in self.nodeGenes:
            print(str(node.innovNum) + ", ",end="")
        print("")
        for conn in self.connectionGenes:
            print(str((conn.In.innovNum, conn.Out.innovNum, round(conn.weight, 3), conn.enabled, conn.innovNum)) + ", ",end="")
        print("")
        print("-----------------")

    def sort(self):
        #sort connections
        temp = []
        for conn in self.connectionGenes:
            temp.append((conn.innovNum, conn))
        sorted_temp = sorted(temp, key = lambda x : x[0])
        new_list = []
        for conn in sorted_temp:
            new_list.append(conn[1])
        self.connectionGenes = new_list
        #sort nodes
        temp = []
        for node in self.nodeGenes:
            temp.append((node.innovNum, node))
        sorted_temp = sorted(temp, key = lambda x : x[0])
        new_list = []
        for node in sorted_temp:
            new_list.append(node[1])
        self.nodeGenes = new_list
            
        
    def mutate(self):
        
        global add_conn_chance, split_conn_chance, weight_mutation_chance, weight_perturbation_chance
        #first check for add connection genome mutation
        if add_conn_chance >= random.random():
            self.addConnection()
        #second check for connection split mutation
        if split_conn_chance >= random.random():
            self.splitConnection()
        #apply mutations occuring on a per gene basis
        idx = 0
        l = len(self.connectionGenes)
        while idx < l:
            conn = self.connectionGenes[idx]            
            #third check for toggle
            if toggle_chance >= random.random():
                #if conn.split == False:
                if conn.enabled == True:
                    conn.enabled = False
                else:                    
                    conn.enabled = True
            #fourth check for weight mutation or perturbation 
            elif weight_mutation_chance >= random.random():
                conn.weight = random.uniform(-5, 5)
            elif weight_perturbation_chance >= random.random():
                conn.weight += random.uniform(-0.1, 0.1)
            idx += 1
        self.network = NN.Network(self)

    #splits a given connection into two connections connected by a new node
    def splitConnection(self):
        global nodeInnovation, connectionInnovation
        if len(self.connectionGenes) == 0:
            return
        conn = random.choice(self.connectionGenes)
        if conn.enabled == False:
            return
        #dont split bias nodes
        if conn.In.type == 3:
            return
        conn.enabled = False
       # conn.split = True
        #create a new hiddenNode and map it to any matching already existing structures ID
        newNode = None
        split_conn = (conn.In.innovNum, conn.Out.innovNum)
        if split_conn in split_history:
            newNode = NodeGene(1, split_history[split_conn])
        else:
            newNode = NodeGene(1, nodeInnovation)
            split_history[split_conn] = nodeInnovation
            nodeInnovation += 1
        self.nodeGenes.append(newNode)
        self.hiddenNodes.append(newNode)
        #create connection from conn input node to newNode; weight = 1
        newConn1 = ConnectionGene(conn.In, newNode, 1, connectionInnovation)
        self.connectionGenes.append(newConn1)
        #create connection from newNode to conn output node; weight = conn.weight
        newConn2 = ConnectionGene(newNode, conn.Out, conn.weight, connectionInnovation)
        self.connectionGenes.append(newConn2)
        self.network = NN.Network(self)
    #randomly finds 2 unconnected nodes and connects them    
    def addConnection(self):
        global connectionInnovation
        l = len(self.nodeGenes)
        count = 0
        while True:
            if count >= 100:
                break
            count += 1
            #pick 2 random Nodes
            randNode1 = random.choice(self.nodeGenes)
            randNode2 = random.choice(self.nodeGenes)
            #check if they're the same
            if (
            #no conns between input nodes
            (randNode1.type == 0 and randNode2.type == 0) or 
            #no conns between output nodes
            (randNode1.type == 2 and randNode2.type == 2) or
            #no conns between bias nodes
            (randNode1.type == 3 and randNode2.type == 3) or
            #no conns from input to bias
            (randNode1.type == 0 and randNode2.type == 3) or 
            #no conns from bias to input
            (randNode1.type == 3 and randNode2.type == 0) or
            #no conns from hidden to input
            (randNode1.type == 1 and randNode2.type == 0) or
            #no conns from output to hidden
            (randNode1.type == 2 and randNode2.type == 1) or
            #no conns from output to input
            (randNode1.type == 2 and randNode2.type == 0)):
                continue
            #check if the bias is an output and swap if true
            if randNode2.type == 3:
                temp = randNode1
                randNode1 = randNode2
                randNode2 = temp
            nodes = (randNode1, randNode2)
            #add newConnection to the genome if it doesn't already exist
            unique = True
            for conn in self.connectionGenes:
                if nodes[0].innovNum == conn.In.innovNum and nodes[1].innovNum == conn.Out.innovNum:
                    unique = False
            if unique == True:
                #print((nodes[0].innovNum, nodes[1].innovNum))
                #create new Connection or are both in the same input/output layer
                w = random.uniform(-1, 1)
                newConnection = ConnectionGene(randNode1, randNode2, w, connectionInnovation)
                self.connectionGenes.append(newConnection)
                self.network = NN.Network(self)        
                break
    #called during game to determine each move of snake
    """
    def predict(self, inputs, curr_dir):
        for i in range(5):
            self.network.forwardProp(inputs, self)
            self.softmax()
        best_activation = -1
        best_idx = random.randrange(4)
        
        #determine output node with highest activation
        for i in range(len(self.outputNodes)):
            if self.outputNodes[i].activation > best_activation:
                best_activation = self.outputNodes[i].activation
                best_idx = i
        
        #return move
        if best_idx == 0:
            return (-1, 0)
        elif best_idx == 1:
            return (0, 1)
        elif best_idx == 2:
            return (-1, 0)
            #best_idx == 3
        else:
            return (0, -1)
    """
    
    def predict(self, inputs, curr_dir):
        for g in self.nodeGenes:
            g.recurrentActivation = 0
        for i in range(5):
            self.network.forwardProp(inputs, self)
            self.softmax()
        best_activation = 0
        best_idx = random.randrange(3)
        
        #determine output node with highest activation
        for i in range(len(self.outputNodes)):
            if self.outputNodes[i].activation > best_activation:
                best_activation = self.outputNodes[i].activation
                best_idx = i
                
        #return direction associated with activated node
        #heading up
        #moving up
        if curr_dir == (-1, 0):
            #move left (left)
            if best_idx == 0:
                return (0, -1), 1
            #move forward (up)
            elif best_idx == 1:
                return (-1, 0), 0
            #move right (right)
            elif best_idx == 2:
                return (0, 1), 1
        #moving right
        elif curr_dir == (0, 1):
            #move left (up)
            if best_idx == 0:
                return (-1, 0), 1
            #move forward (right)
            elif best_idx == 1:
                return (0, 1), 0
            #move right (down)
            elif best_idx == 2:
                return (1, 0), 1
        #moving down
        elif curr_dir == (1, 0):
            #move left (right)
            if best_idx == 0:
                return (0, 1), 1
            #move forward (down)
            elif best_idx == 1:
                return (1, 0), 0
            #move right (left)
            elif best_idx == 2:
                return (0, -1), 1
        #moving left
        elif curr_dir == (0, -1):
            #move left (down)
            if best_idx == 0:
                return (1, 0), 1
            #move forward (left)
            elif best_idx == 1:
                return (0, -1), 0
            #move right (up)
            elif best_idx == 2:
                return (-1, 0), 1

    def softmax(self):
        activations = []
        for node in self.outputNodes:
            activations.append(node.activation)
        activations2 = np.array(activations)
        exp_data = np.exp(activations2 - np.max(activations2, axis=0))  # Subtract max for numerical stability
        score = exp_data / np.sum(exp_data, axis=0, keepdims=True)
        for i in range(len(self.outputNodes)):
            self.outputNodes[i].activation = score[i]
    
    def evaluate(self):
        fitness = 4
        for i in range(2):
            for j in range(2):
                #reset recurrent activations for next test
                for node in self.nodeGenes:
                    node.recurrentActivation = 0
                #evaluate genome for given input for certain amount of cycles
                for k in range(5):
                    self.network.forwardProp([i, j], self)
                if XOR(i, j) == 1:  
                    fitness -= (self.outputNodes[0].activation - 1)**2
                else:
                    fitness -= (self.outputNodes[0].activation - 0)**2
        self.fitness = max(0, fitness)
        #self.fitness = max(0, fitness - 0.5 * math.log(len(self.hiddenNodes))


    
class NodeGene: 

    def __init__(self, t, innov):
        self.innovNum = innov
        #0 = input; 1 = hidden; 2 = output; 3 = bias
        self.type = t
        if self.type == 3:
            self.activation = 1
        else:
            self.activation = 0
        self.processed = False
        self.recurrentActivation = 0

    def activationFxn(self):
        #print(self.activation)
        if self.type == 1 or self.type == 0:
            return (1 / (1 + np.exp(-self.activation)))
            #return max(0, self.activation)
        elif self.type == 2:
            return self.activation
            #return (1 / (1 + np.exp(-self.activation)))

class ConnectionGene:
    
    def __init__(self, initIn, initOut, w, innov):
        #input node in connection
        self.In = initIn
        #output node in connection
        self.Out = initOut
        #random starting weight between -1 and 1
        self.weight = w
        #boolean to determine if a node is active in a network
        self.enabled = True
        #boolean to determine if a node was processed in the network during forwardProp
        self.processed = False
        #boolean to determine if a node was split and thus inelgiable for renabling
        self.split = False
        #assign and increment global innovation counter
        #unique global identifier for a gene
        global connection_history, connectionInnovation
        if (self.In.innovNum, self.Out.innovNum) in connection_history:
            self.innovNum = connection_history[(self.In.innovNum, self.Out.innovNum)]
        else:
            self.innovNum = innov
            connection_history[(self.In.innovNum, self.Out.innovNum)] = innov
            connectionInnovation += 1


            

