# region imports
import numpy as np
import math
from scipy.optimize import fsolve
import random as rnd
# endregion

# region class definitions
class Fluid():
    #region constructor
    def __init__(self, mu=0.00089, rho=1000):
        """
        Initialize the Fluid object with default properties for water.

        Parameters:
        mu (float): Dynamic viscosity of the fluid in Pa·s (kg/(m·s)).
                    Default value for water at approximately 20 degrees Celsius.
        rho (float): Density of the fluid in kg/m^3. Default value for water
                     at approximately 4 degrees Celsius (maximum density).

        The kinematic viscosity (nu) is calculated by dividing the dynamic
        viscosity (mu) by the density (rho), as per the formula nu = mu / rho.

        Attributes:
        mu (float): Dynamic viscosity of the fluid.
        rho (float): Density of the fluid.
        nu (float): Kinematic viscosity of the fluid, derived from mu and rho.
        """
        self.mu = mu    # Dynamic viscosity
        self.rho = rho  # Density of the fluid
        self.nu = self.mu / self.rho  # Kinematic viscosity
    #endregion
class Node():
    #region constructor
    def __init__(self, Name='a', Pipes=[], ExtFlow=0):
        '''
        A node in a pipe network.
        :param Name: name of the node
        :param Pipes: a list of pipes connected to this node
        :param ExtFlow: any external flow into (+) or out (-) of this node in L/s
        '''
        self.name=Name
        self.pipes=Pipes
        self.extFlow=ExtFlow
    #endregion

    #region methods/functions
    def getNetFlowRate(self):
        '''
        Calculates the net flow rate into this node in L/s
        # :return:
        '''
        Qtot= self.extFlow  # Start with external flow
        for p in self.pipes:
            #retrieves the pipe flow rate (+) if into node (-) if out of node.  see class for pipe.
            Qtot+=p.getFlowIntoNode(self.name)
        return Qtot
    #endregion
class Loop():
    #region constructor
    def __init__(self, Name='A', Pipes=[]):
        '''
        Defines a loop in a pipe network.  Note: the pipes must be listed in order.  The traversal of a pipe loop
        will begin at the start node of Pipe[0] and move in the positive direction of that pipe.  Hence, loops
        can be either CW or CCW traversed, depending on which pipe you start with.  Should work fine either way.
        :param Name: name of the loop
        :param Pipes: a list/array of pipes in this loop
        '''
        self.name=Name
        self.pipes=Pipes
    #endregion

    #region methods/functions
    def getLoopHeadLoss(self):
        '''
        Calculates the net head loss as I traverse around the loop, in m of fluid.
        :return:
        '''
        deltaP=0 #initialize to zero
        startNode=self.pipes[0].startNode #begin at the start node of the first pipe
        for p in self.pipes:
            # calculates the head loss in the pipe considering loop traversal and flow directions
            phl=p.getFlowHeadLoss(startNode)
            deltaP+=phl
            startNode=p.endNode if startNode!=p.endNode else p.startNode #move to the next node
        return deltaP
    #endregion
class Pipe():
    #region constructor
    def __init__(self, Start='A', End='B', L=100, D=200, r=0.00025, fluid=Fluid()):
        """
        Initializes a Pipe object representing a segment of a pipe network.

        Parameters:
        Start (str): The starting node (identifier) of the pipe.
        End (str): The ending node (identifier) of the pipe.
        L (float): The length of the pipe in meters.
        D (float): The inner diameter of the pipe in millimeters.
        r (float): The roughness of the pipe's inner surface in meters.
        fluid (Fluid): The fluid object representing the fluid within the pipe.

        The pipe's properties, such as its diameter in meters, area, relative roughness,
        initial volumetric flow rate (Q), velocity (vel), and Reynolds number (Re),
        are calculated upon initialization.

        Attributes:
        startNode (str): The identifier for the start node, ensuring it's the minimum of Start and End.
        endNode (str): The identifier for the end node, ensuring it's the maximum of Start and End.
        length (float): Length of the pipe in meters.
        diameter (float): Inner diameter of the pipe in meters.
        area (float): Cross-sectional area of the pipe in square meters.
        relativeRoughness (float): The relative roughness of the pipe.
        volumetricFlowRate (float): Initial guess for the pipe's volumetric flow rate in L/s.
        velocity (float): Fluid velocity within the pipe in m/s.
        reynoldsNumber (float): Reynolds number for flow within the pipe.
        roughness (float): Roughness of the pipe's inner surface in meters.
        fluid (Fluid): The fluid flowing through the pipe.
        """
        self.startNode = min(Start, End)  # Alphabetically lower label is startNode
        self.endNode = max(Start, End)  # Alphabetically higher label is endNode
        self.length = L
        self.diameter = D / 1000.0  # Convert diameter from mm to m
        self.roughness = r
        self.fluid = fluid  # Fluid object representing the fluid in the pipe

        # Additional properties
        self.area = math.pi * (self.diameter / 2) ** 2  # Cross-sectional area of the pipe
        self.relativeRoughness = self.roughness / self.diameter  # Relative roughness
        self.volumetricFlowRate = 10  # Initial guess for flow rate in L/s (to be solved)
        self.velocity = self.calculate_velocity()  # Velocity, Q = A * v, Q in L/s needs conversion
        self.reynoldsNumber = self.calculate_reynolds_number()  # Reynolds number for flow within the pipe

    def calculate_velocity(self):
        """
        Calculate the fluid velocity based on the volumetric flow rate and pipe's cross-sectional area.

        Returns:
        float: The velocity of fluid in the pipe in m/s.
        """
        self.velocity = self.volumetricFlowRate / (1000 * self.area)  # Convert flow rate from L/s to m^3/s for calculation
        return self.velocity

    def calculate_reynolds_number(self):
        """
        Calculate the Reynolds number for the fluid flow based on the velocity, pipe diameter, and fluid properties.

        Returns:
        float: The Reynolds number.
        """
        self.reynoldsNumber = (self.fluid.rho * self.velocity * self.diameter) / self.fluid.mu
        return self.reynoldsNumber


    def FrictionFactor(self):
        """
        This function calculates the friction factor for a pipe based on the
        notion of laminar, turbulent and transitional flow.
        :return: the (Darcy) friction factor
        """
        # update the Reynolds number and make a local variable Re
        Re = self.reynoldsNumber
        if Re <= 2000:
            return 64 / Re
        elif Re >= 4000:
            # Correct indentation for the definition of the CB function
            def CB(f):
                return 1 / math.sqrt(f) + 2.0 * np.log10(
                    self.roughness / (3.7 * self.diameter) + 2.51 / (Re * math.sqrt(f)))

            f_turbulent, = fsolve(CB, 0.02)
            return f_turbulent
        else:
            # Transitional flow, assuming linear interpolation between laminar and turbulent
            f_laminar = 64 / Re

            def CB(f):
                return 1 / math.sqrt(f) + 2.0 * np.log10(
                    self.roughness / (3.7 * self.diameter) + 2.51 / (Re * math.sqrt(f)))

            f_turbulent, = fsolve(CB, 0.02)
            mu_f = f_laminar + (f_turbulent - f_laminar) * (Re - 2000) / 2000
            sigma_f = 0.2 * mu_f
            return rnd.normalvariate(mu_f, sigma_f)

    def frictionHeadLoss(self):  # calculate headloss through a section of pipe in m of fluid
        '''
        Use the Darcy-Weisbach equation to find the head loss through a section of pipe.
        '''
        g = 9.81  # m/s^2
        ff = self.FrictionFactor()
        hl = ff * (self.length / self.diameter) * (self.velocity ** 2) / (2 * g)
        return hl

    def getFlowHeadLoss(self, s):
        '''
        Calculate the head loss for the pipe.
        :param s: the node i'm starting with in a traversal of the pipe
        :return: the signed headloss through the pipe in m of fluid
        '''
        #while traversing a loop, if s = startNode I'm traversing in same direction as positive pipe
        nTraverse= 1 if s==self.startNode else -1
        #if flow is positive sense, scalar =1 else =-1
        nFlow = 1 if self.volumetricFlowRate >= 0 else -1
        return nTraverse*nFlow*self.frictionHeadLoss()

    def Name(self):
        '''
        Gets the pipe name.
        :return:
        '''
        return f'{self.startNode}-{self.endNode}'

    def oContainsNode(self, node):
        #does the pipe connect to the node?
        return node == self.startNode or node == self.endNode

    def printPipeFlowRate(self):
        print(f'The flow in segment {self.Name()} is {self.volumetricFlowRate:.2f} L/s')


    def getFlowIntoNode(self, n):
        '''
        determines the flow rate into node n
        :param n: a node object
        :return: +/-Q
        '''
        if n == self.startNode:
            return -self.volumetricFlowRate
        return self.volumetricFlowRate
    #endregion

class PipeNetwork():
    #region constructor
    def __init__(self, Pipes=[], Loops=[], Nodes=[], fluid=Fluid()):
        """
        Initialize the PipeNetwork object that represents the entire pipe network.

        The network is composed of a collection of pipes, nodes, and loops that
        are interrelated. This class facilitates the analysis of the pipe network
        by providing methods to find flow rates in pipes given constraints of mass
        conservation at nodes and zero net pressure drops in the loops.

        Parameters:
        Pipes (list of Pipe objects): A list of all the pipe segments in the network.
        Loops (list of Loop objects): A list of loops in the network, each loop is
                                      a closed path of pipe segments.
        Nodes (list of Node objects): A list of nodes in the network where pipes connect.
        fluid (Fluid object): The fluid that flows through the pipe network.

        Attributes:
        loops (list of Loop objects): Loops within the pipe network.
        nodes (list of Node objects): Nodes within the pipe network.
        pipes (list of Pipe objects): Pipes within the pipe network.
        Fluid (Fluid object): The fluid within the pipe network.
        """
        self.loops = Loops
        self.nodes = Nodes
        self.pipes = Pipes
        self.Fluid = fluid

    def findFlowRates(self):
        """
        Analyzes the pipe network to find the flow rates in each pipe segment.

        This method leverages the fsolve function from scipy.optimize to solve the
        non-linear equations that arise from the conservation of mass at nodes and
        the zero net pressure drop requirement in loops.

        Returns:
        numpy.ndarray: An array of the solved flow rates for each pipe in the network.
        """
        # The number of equations is equal to the number of nodes plus the number of loops
        N = len(self.nodes) + len(self.loops)
        # Initial guess for the flow rates in the pipes (L/s)
        Q0 = np.full(N, 10)

        def fn(q):
            """
            The callback function for fsolve that represents the system of equations
            to be solved. The equations are based on mass conservation at nodes and
            pressure loss in loops.

            Parameters:
            q (numpy.ndarray): An array of guessed flow rates for the pipes.

            Returns:
            numpy.ndarray: An array containing the mass conservation at each node
                           and pressure losses for each loop.
            """
            # Update the flow rate in each pipe object with the current guess
            for i, pipe in enumerate(self.pipes):
                pipe.Q = q[i]

            # Calculate the net flow rates at the nodes
            qNet = self.getNodeFlowRates()
            # Calculate the net head loss for the loops
            lhl = self.getLoopHeadLosses()
            # Concatenate the flow rates and head loss to form the system of equations
            return np.concatenate((qNet, lhl))

        # Use fsolve to find the flow rates that satisfy all equations
        flow_rates = fsolve(fn, Q0)
        return flow_rates

    def getNodeFlowRates(self):
        """
        Calculates the net flow rate at each node in the pipe network.

        The net flow rate at a node is the sum of the flow rates in pipes going into
        and out of the node. This should be zero for mass conservation.

        Returns:
        list: A list of net flow rates for each node, ideally all zeroes.
        """
        return [node.getNetFlowRate() for node in self.nodes]

    def getLoopHeadLosses(self):
        """
        Calculates the net head loss around each loop in the pipe network.

        According to the principle of energy conservation in a loop, the sum of
        head losses and gains around any closed loop should be zero.

        Returns:
        list: A list of net head losses for each loop, ideally all zeroes.
        """
        return [loop.getLoopHeadLoss() for loop in self.loops]

    def getPipe(self, name):
        #returns a pipe object by its name
        for p in self.pipes:
            if name == p.Name():
                return p

    def getNodePipes(self, node):
        #returns a list of pipe objects that are connected to the node object
        l=[]
        for p in self.pipes:
            if p.oContainsNode(node):
                l.append(p)
        return l

    def nodeBuilt(self, node):
        #determines if I have already constructed this node object (by name)
        for n in self.nodes:
            if n.name==node:
                return True
        return False

    def getNode(self, name):
        #returns one of the node objects by name
        for n in self.nodes:
            if n.name==name:
                return n

    def buildNodes(self):
        #automatically create the node objects by looking at the pipe ends
        for p in self.pipes:
            if self.nodeBuilt(p.startNode)==False:
                #instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.startNode,self.getNodePipes(p.startNode)))
            if self.nodeBuilt(p.endNode)==False:
                #instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.endNode,self.getNodePipes(p.endNode)))

    def printPipeFlowRates(self):
        for p in self.pipes:
            p.printPipeFlowRate()

    def printNetNodeFlows(self):
        for n in self.nodes:
            print('net flow into node {} is {:0.2f}'.format(n.name, n.getNetFlowRate()))

    def printLoopHeadLoss(self):
        for l in self.loops:
            print('head loss for loop {} is {:0.2f}'.format(l.name, l.getLoopHeadLoss()))
    #endregion
# endregion

# region function definitions
def main():
    '''
    This program analyzes flows in a given pipe network based on the following:
    1. The pipe segments are named by their endpoint node names:  e.g., a-b, b-e, etc.
    2. Flow from the lower letter to the higher letter of a pipe is considered positive.
    3. Pressure decreases in the direction of flow through a pipe.
    4. At each node in the pipe network, mass is conserved.
    5. For any loop in the pipe network, the pressure loss is zero
    Approach to analyzing the pipe network:
    Step 1: build a pipe network object that contains pipe, node, loop and fluid objects
    Step 2: calculate the flow rates in each pipe using fsolve
    Step 3: output results
    Step 4: check results against expected properties of zero head loss around a loop and mass conservation at nodes.
    :return:
    '''
    # Instantiate a Fluid object to define the working fluid as water
    water = Fluid(mu=0.00089, rho=1000)  # Water properties

    # Instantiate Pipe objects for the network
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

    # Create the PipeNetwork object
    PN = PipeNetwork(Pipes=pipes, fluid=water)

    # Automatically generate Node objects from Pipe objects
    PN.buildNodes()

    # Manually update the external flow of certain nodes
    PN.getNode('a').extFlow = 60
    PN.getNode('d').extFlow = -30
    PN.getNode('f').extFlow = -15
    PN.getNode('h').extFlow = -15

    # Define Loops with the pipes involved
    loops = [
        Loop('A', [PN.getPipe('a-b'), PN.getPipe('b-e'), PN.getPipe('d-e'), PN.getPipe('c-d'), PN.getPipe('a-c')]),
        Loop('B', [PN.getPipe('c-d'), PN.getPipe('d-g'), PN.getPipe('f-g'), PN.getPipe('c-f')]),
        Loop('C', [PN.getPipe('d-e'), PN.getPipe('e-h'), PN.getPipe('g-h'), PN.getPipe('d-g')])
    ]

    # Add loops to the PipeNetwork
    PN.loops.extend(loops)

    # Find flow rates
    PN.findFlowRates()

    # Output results
    PN.printPipeFlowRates()
    print('\nCheck node flows:')
    PN.printNetNodeFlows()
    print('\nCheck loop head loss:')
    PN.printLoopHeadLoss()


if __name__ == "__main__":
    main()
# endregion
