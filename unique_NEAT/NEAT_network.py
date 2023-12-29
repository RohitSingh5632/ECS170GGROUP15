import queue


class Network:
    
    def __init__(self, genome):
        self.connections = genome.connectionGenes
        self.nodes = genome.nodeGenes
        self.adjList = self.createList(self.nodes, self.connections)
        
    def createList(self, nodes, connections):
        adjDict = {}
        for node in nodes:
            ID = node.innovNum
            adjDict[ID] = []
            for conn in connections:
                inNode = conn.In.innovNum
                outNode = conn.Out.innovNum
                if (outNode == ID or inNode == ID) and conn.enabled == True:
                    adjDict[ID].append(conn)
        return adjDict
    """
    def forwardProp(self, inputs, genome, max_iterations = 100):
        #reset activations
        for node in self.nodes:
            node.activation = 0
            node.prev_activation = 0
        genome.biasNode.activation = 1
        #set input values of input nodes
        for i in range(len(inputs)):
            val = inputs[i]
            genome.inputNodes[i].activation = val
        
        for iterations in range(max_iterations):
            for key in self.adjList:
                for conn in self.adjList[key]:
                    inNode = conn.In
                    outNode = conn.Out
                    outNode.activation += inNode.activation * conn.weight
                    outNode.activation = outNode.activationFxn()
                    outNode.prev_activation = outNode.activation
            
            converged = True
            for node in self.nodes:
                if abs(node.activation - node.prev_activation) > 0.01:
                    converged = False
            if converged == True:
                print(iterations)
                return
    """
    def forwardProp(self, inputs, genome):
        count = 0
        #reset activations and processed values
        for node in self.nodes:
            node.activation = 0
            node.processed = False
        for conn in self.connections:
            conn.processed = False
        #biasNode should always be active
        genome.biasNode.activation = 1
            
        #set input values of input nodes
        for i in range(len(inputs)):
            val = inputs[i]
            genome.inputNodes[i].activation = val
        inputNodes = genome.inputNodes
        Q = queue.Queue()
        #add all input connections
        for node in inputNodes:
            ID = node.innovNum
            #inputs nodes with no recurrent connections will already have an output value
            if self.incomingConns(node) == False:
                node.processed = True
            #add the outgoing connections of each input node to Q
            for conn in self.adjList[ID]:
                if conn.In.innovNum == ID:
                    Q.put(conn)
        #add all bias connections to Q
        if genome.biasNode.innovNum in self.adjList:
            for conn in self.adjList[genome.biasNode.innovNum]:
                Q.put(conn)

        #iterate through Q until no connections are left to process
        while Q.empty() == False:
            if count >= 200:
                #self.printAdjList()
                #genome.printGenome()
                print(True)
                return
            #get a connection from the Queue
            currConn = Q.get()
            inNode = currConn.In
            outNode = currConn.Out
            #check if outNode is already processed and update values accordingly
            if outNode.processed == True:
                #iterate over all recurrent connections
                for conn in self.adjList[outNode.innovNum]:
                    if conn.Out == outNode and conn.In.processed == True and conn.processed == False:
                        try:
                            outNode.recurrentActivation += conn.weight * conn.In.activation
                        except:
                            print((conn.In.innovNum, conn.Out.innovNum, conn.enabled))
                        #ensure that output nodes are processed correctly
                        if conn.Out.type == 2:
                            outNode.activation = outNode.activationFxn()
            else:
                #factor in recurrent activation
                outNode.activation += outNode.recurrentActivation
                #update outNode activation based on actviated inputNodes from all incoming connections
                for conn in self.adjList[outNode.innovNum]:
                    if conn.In.processed == True and conn.Out == outNode and conn.processed == False:
                        try:
                            outNode.activation += conn.weight * conn.In.activation
                        except:
                            print(((conn.In.innovNum, conn.In.activation), (conn.Out.innovNum, conn.Out.activation), conn.enabled, conn.weight, conn.innovNum))
                        for j in range(len(self.connections)):
                            if self.connections[j].innovNum == conn.innovNum:
                                self.connections[j].processed = True
                    #add all outgoing connections from outnode to the Q
                    if conn.In == outNode:
                        Q.put(conn)
                    #make current outNode processed
                    outNode.activation = outNode.activationFxn()
                    outNode.processed = True
            count += 1
        
    
    def incomingConns(self, node):
        ID = node.innovNum
        #check if node has any incoming connections
        for conn in self.adjList[ID]:
            if conn.Out.innovNum == ID:
                return True
        return False

    def printAdjList(self):
        for key in self.adjList:
            lists = self.adjList[key]
            print(str(key) + ": ",end="")
            for conn in lists:
                print(str((conn.In.innovNum, conn.Out.innovNum, round(conn.weight, 3))) + ", ",end="")
            print("")
        print("------------")
        
  

    
"""
class Network:
    
    def __init__(self, genome):
        self.layers = self.build_layers(genome)
    
    
    
    #
    def build_layers(self, genome):
        simplified_conns = []
        for conn in genome.connectionGenes:
            simplified_conn = (conn.In, conn.Out)
            simplified_conns.append(simplified_conn)
            
        inputs = set(genome.inputNodes)
        while True:
        canidates = set()
        for (i, o) in simplified_conns:
            if i in inputs and o not in inputs:
                canidates.add(o)
        t = set()
"""
