# region imports
import numpy as np
import math
from scipy.optimize import fsolve
import random as rnd
# endregion

# region class definitions
class Fluid():
    def __init__(self, mu=0.00089, rho=1000):
        self.mu = mu
        self.rho = rho
        self.nu = self.mu / self.rho

class Node():
    def __init__(self, Name='a', Pipes=[], ExtFlow=0):
        self.name = Name
        self.pipes = Pipes
        self.extFlow = ExtFlow

    def getNetFlowRate(self):
        Qtot = self.extFlow
        for p in self.pipes:
            Qtot += p.getFlowIntoNode(self.name)
        return Qtot

class Loop():
    def __init__(self, Name='A', Pipes=[], pipe_network=None):
        self.name = Name
        self.pipes = Pipes
        self.pipe_network = pipe_network

    def getLoopHeadLoss(self):
        deltaP = 0
        startNode = self.pipe_network.getPipe(self.pipes[0]).startNode
        for pipe_name in self.pipes:
            p = self.pipe_network.getPipe(pipe_name)
            if p is None:
                raise ValueError(f'Pipe {pipe_name} does not exist in the network.')
            phl = p.getFlowHeadLoss(startNode)
            deltaP += phl
            startNode = p.endNode if startNode != p.endNode else p.startNode
        return deltaP

class Pipe():
    def __init__(self, Start='A', End='B', L=100, D=200, r=0.00025, fluid=Fluid()):
        self.startNode = min(Start, End)
        self.endNode = max(Start, End)
        self.length = L
        self.diameter = D / 1000.0
        self.roughness = r
        self.fluid = fluid
        self.area = math.pi * (self.diameter / 2) ** 2
        self.relativeRoughness = self.roughness / self.diameter
        self.volumetricFlowRate = 10
        self.velocity = self.calculate_velocity()
        self.reynoldsNumber = self.calculate_reynolds_number()

    def calculate_velocity(self):
        return self.volumetricFlowRate / (1000 * self.area)

    def calculate_reynolds_number(self):
        return (self.fluid.rho * self.velocity * self.diameter) / self.fluid.mu

    def FrictionFactor(self):
        Re = self.reynoldsNumber
        if Re <= 2000:
            return 64 / Re
        elif Re >= 4000:
            def CB(f):
                return 1 / np.sqrt(f) + 2.0 * np.log10(self.roughness / (3.7 * self.diameter) + 2.51 / (Re * np.sqrt(f)))
            f_turbulent, = fsolve(CB, 0.02)
            return f_turbulent
        else:
            f_laminar = 64 / Re
            def CB(f):
                return 1 / np.sqrt(f) + 2.0 * np.log10(self.roughness / (3.7 * self.diameter) + 2.51 / (Re * np.sqrt(f)))
            f_turbulent, = fsolve(CB, 0.02)
            mu_f = f_laminar + (f_turbulent - f_laminar) * (Re - 2000) / 2000
            sigma_f = 0.2 * mu_f
            return rnd.normalvariate(mu_f, sigma_f)

    def frictionHeadLoss(self):
        g = 9.81
        ff = self.FrictionFactor()
        hl = ff * (self.length / self.diameter) * (self.velocity ** 2) / (2 * g)
        return hl

    def getFlowHeadLoss(self, s):
        nTraverse = 1 if s == self.startNode else -1
        nFlow = 1 if self.volumetricFlowRate >= 0 else -1
        return nTraverse * nFlow * self.frictionHeadLoss()

    def Name(self):
        return f'{self.startNode}-{self.endNode}'

    def oContainsNode(self, node):
        return node == self.startNode or node == self.endNode

    def printPipeFlowRate(self):
        print(f'The flow in segment {self.Name()} is {self.volumetricFlowRate:.2f} L/s')

    def getFlowIntoNode(self, n):
        if n == self.startNode:
            return -self.volumetricFlowRate
        return self.volumetricFlowRate

class PipeNetwork():
    def __init__(self, Pipes=[], Loops=[], Nodes=[], fluid=Fluid()):
        self.loops = Loops
        self.nodes = Nodes
        self.pipes = Pipes
        self.Fluid = fluid

    def findFlowRates(self):
        N = len(self.pipes)
        Q0 = np.full(N, 10)
        def fn(q):
            for i, pipe in enumerate(self.pipes):
                pipe.volumetricFlowRate = q[i]
                pipe.calculate_velocity()
                pipe.calculate_reynolds_number()
            qNet = self.getNodeFlowRates()
            lhl = self.getLoopHeadLosses()
            return np.concatenate((qNet, lhl))
        flow_rates, info, ier, mesg = fsolve(fn, Q0, full_output=True)
        if ier != 1:
            print(f"Solution not found: {mesg}")
        return flow_rates

    def getNodeFlowRates(self):
        return [node.getNetFlowRate() for node in self.nodes]

    def getLoopHeadLosses(self):
        return [loop.getLoopHeadLoss() for loop in self.loops]

    def getPipe(self, name):
        for p in self.pipes:
            if name == p.Name():
                return p
        return None

    def getNodePipes(self, node):
        l = []
        for p in self.pipes:
            if p.oContainsNode(node):
                l.append(p)
        return l

    def nodeBuilt(self, node):
        for n in self.nodes:
            if n.name == node:
                return True
        return False

    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def buildNodes(self):
        for p in self.pipes:
            if not self.nodeBuilt(p.startNode):
                self.nodes.append(Node(p.startNode, self.getNodePipes(p.startNode), 0))
            if not self.nodeBuilt(p.endNode):
                self.nodes.append(Node(p.endNode, self.getNodePipes(p.endNode), 0))

    def printPipeFlowRates(self):
        for p in self.pipes:
            p.printPipeFlowRate()

    def printNetNodeFlows(self):
        for n in self.nodes:
            print(f'net flow into node {n.name} is {n.getNetFlowRate():0.2f}')

    def printLoopHeadLoss(self):
        for l in self.loops:
            print(f'head loss for loop {l.name} is {l.getLoopHeadLoss():0.2f}')

# endregion

# region function definitions
def main():
    water = Fluid(mu=0.00089, rho=1000)

    pipes = [
        Pipe('a', 'b', 250, 300, 0.00025, water),
        Pipe('a', 'c', 100, 200, 0.00025, water),
        Pipe('b', 'e', 100, 200, 0.00025, water),
        Pipe('c', 'd', 125, 200, 0.00025, water),
        Pipe('c', 'f', 100, 150, 0.00025, water),
        Pipe('d', 'e', 125, 200, 0.00025, water),
        Pipe('d', 'g', 100, 150, 0.00025, water),
        Pipe('e', 'h', 100, 150, 0.00025, water),
        Pipe('f', 'g', 125, 250, 0.00025, water),
        Pipe('g', 'h', 125, 250, 0.00025, water)
    ]

    PN = PipeNetwork(pipes, fluid=water)
    PN.buildNodes()

    PN.getNode('a').extFlow = 60
    PN.getNode('d').extFlow = -30
    PN.getNode('f').extFlow = -15
    PN.getNode('h').extFlow = -15

    loops = [
        Loop('A', ['a-b', 'b-e', 'e-d', 'd-c', 'c-a'], PN),
        Loop('B', ['c-d', 'd-g', 'g-f', 'f-c'], PN),
        Loop('C', ['d-e', 'e-h', 'h-g', 'g-d'], PN)
    ]
    PN.loops = loops

    PN.findFlowRates()

    PN.printPipeFlowRates()
    print('\nCheck node flows:')
    PN.printNetNodeFlows()
    print('\nCheck loop head loss:')
    PN.printLoopHeadLoss()

if __name__ == "__main__":
    main()
