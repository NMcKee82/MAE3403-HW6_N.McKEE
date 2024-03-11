#region imports
from scipy.optimize import fsolve
from Fails.HW6_1_OOP import Resistor, VoltageSource, Loop
#endregion

#region class definitions
class ResistorNetwork():
    #region constructor
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        This is the constructor for the network and it defines fields for Loops, Resistors and Voltage Sources.
        You can populate these lists manually or read them in from a file.
        """
        #create some instance variables that are logical parts of a resistor network
        self.Loops = []  # initialize an empty list of loop objects in the network
        self.Resistors = []  # initialize an empty a list of resistor objects in the network
        self.VSources = []  # initialize an empty a list of source objects in the network
    #endregion

class ResistorNetwork2(ResistorNetwork):
    def __init__(self):
        """
        Initialize the ResistorNetwork2 object. This calls the constructor of the superclass (ResistorNetwork)
        to ensure all the initialization done there is also applied here.
        """
        super().__init__()  # Call the superclass constructor to initialize inherited properties

    # Example of an overridden method
    def AnalyzeCircuit(self):
        """
        Override the AnalyzeCircuit method to implement a different analysis strategy or to extend the existing one.
        """
        # You could call the superclass method with super().AnalyzeCircuit() if you want to include its behavior.
        # Or you can define a new behavior specific to this subclass.
        print("Analyze circuit with modified approach in ResistorNetwork2.")
        # Assuming the method to solve the network remains largely the same,
        # but ensuring the updated network components are considered.
        super().AnalyzeCircuit()  # Optionally include original behavior if still relevant

    # Example of a new method specific to ResistorNetwork2
    def NewMethodSpecificToResistorNetwork2(self):
        """
        This is an example of a method that is specific to the ResistorNetwork2 class and does not exist in the ResistorNetwork class.
        """
        pass  # Implement the functionality here


    #region methods/functions
    def BuildNetworkFromFile(self, filename):
        """
        This function reads the lines from a file and processes the file to populate the fields
        for Loops, Resistors and Voltage Sources
        :param filename: string for file to process
        :return: nothing
        """
        FileTxt = open(filename,"r").read().split('\n')  # reads from file and then splits the string at the new line characters
        LineNum = 0  # a counting variable to point to the line of text to be processed from FileTxt
        # erase any previous
        self.Resistors = []
        self.VSources = []
        self.Loops = []
        LineNum = 0
        lineTxt = ""
        FileLength = len(FileTxt)
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()
            if len(lineTxt) <1:
                pass # skip
            elif lineTxt[0] == '#':
                pass  # skips comment lines
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            LineNum+=1
        pass

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file starting after detecting '<resistor>' in the text file.
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        R = Resistor()  # Instantiate a new resistor object with default parameters.
        N += 1  # <Resistor> was detected, so move to next line in Txt
        txt = Txt[N].lower().strip()  # Convert the line to lowercase and remove leading/trailing spaces
        while "resistor" not in txt:
            if "name" in txt:
                R.Name = txt.split('=')[1].strip()  # Extracts and assigns the resistor's name from the file.
            if "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())  # Extracts and assigns the resistor's resistance value from the file.
            N+=1
            if N >= len(Txt): break  # Avoid index out of range
            txt = Txt[N].lower().strip()

        self.Resistors.append(R)  # append the resistor object to the list of resistors
        print(f"Added Resistor: {R.Name} with Resistance: {R.Resistance}")
        return N

    def MakeVSource (self, N, Txt):
        """
        Make a voltage source object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a voltage source object
        """
        VS=VoltageSource()
        N+=1
        txt = Txt[N].lower()
        while "source" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N+=1
            txt=Txt[N].lower()

        self.VSources.append(VS)
        return N

    def MakeLoop(self, N, Txt):
        """
        Make a Loop object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        L=Loop()
        N+=1
        txt = Txt[N].lower()
        while "loop" not in txt:
            if "name" in txt:
                L.Name = txt.split('=')[1].strip()
            if "nodes" in txt:
                txt=txt.replace(" ","")
                L.Nodes = txt.split('=')[1].strip().split(',')
            N+=1
            txt=Txt[N].lower()

        self.Loops.append(L)
        return N

    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the resistor network.
        1. KCL:  The total current flowing into any node in the network is zero.
        2. KVL:  When traversing a closed loop in the circuit, the net voltage drop must be zero.
        :return: a list of the currents in the resistor network
        """
        # need to set the currents to that Kirchoff's laws are satisfied

        i0 = [1.0, 1.0, 1.0]  # Initial guess for the currents, assuming there are three currents to solve for
        i = fsolve(self.GetKirchoffVals,i0)
        # print output to the screen
        print("I1 = {:0.1f}".format(i[0]))
        print("I2 = {:0.1f}".format(i[1]))
        print("I3 = {:0.1f}".format(i[2]))
        return i

    def GetKirchoffVals(self, i):
        """
        This function uses Kirchoff Voltage and Current laws to analyze this specific circuit.
        KVL: The net voltage drop for a closed loop in a circuit should be zero.
        KCL: The net current flow into a node in a circuit should be zero.
        :param i: a list of currents relevant to the circuit.
        :return: a list of loop voltage drops and node currents.
        """

        resistors = ['ad', 'bc', 'cd', 'ce']  # List of resistors to set currents for
        currents = [i[0], i[0], i[2], i[1]]  # Corresponding currents for each resistor
        error_found = False

        for resistor_name, current in zip(resistors, currents):
            resistor = self.GetResistorByName(resistor_name)
            if resistor is not None:
                resistor.Current = current
            else:
                print(f"Error: Resistor '{resistor_name}' not found.")
                error_found = True  # Mark that an error was found

        # If an error was found, handle it appropriately
        if error_found:
            print("One or more errors were found in processing the resistors.")
            return None  # Or handle the error differently

        # Calculate net current into node c and continue with KVL calculation
        Node_c_Current = sum([i[0], i[1], -i[2]])
        KVL = self.GetLoopVoltageDrops()  # Get the voltage drops for the loops
        KVL.append(Node_c_Current)  # Add the net current equation for node c

        return KVL

    def GetElementDeltaV(self, name):
        """
        Need to retrieve either a resistor or a voltage source by name.
        :param name: The name of the element to find.
        :return: The voltage change across the element, or None if not found.
        """
        for r in self.Resistors:
            if name == r.Name:
                return -r.DeltaV()
            if name[::-1] == r.Name:
                return -r.DeltaV()
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return v.Voltage

        # If the element is not found, print a warning and return None
        print(f"Warning: Element named '{name}' not found.")
        return None

    def GetLoopVoltageDrops(self):
        """
        This calculates the net voltage drop around a closed loop in a circuit based on the
        current flowing through resistors (cause a drop in voltage regardless of direction of traversal) or
        the value of the voltage source that have been set up as positive based on the direction of traversal.
        :return: net voltage drop for all loops in the network.
        """
        loopVoltages=[]
        for L in self.Loops:
            # Traverse loops in order of nodes and add up voltage drops between nodes
            loopDeltaV=0
            for n in range(len(L.Nodes)):
                if n == len(L.Nodes)-1:
                    name = L.Nodes[0] + L.Nodes[n]
                else:
                    name = L.Nodes[n]+L.Nodes[n+1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        """
        A way to retrieve a resistor object from self.Resistors based on resistor name.
        :param name: The name of the resistor to find.
        :return: The resistor object with the specified name, or None if not found.
        """
        for r in self.Resistors:
            if r.Name.lower() == name.lower():
                return r
        print(f"Warning: Resistor named '{name}' not found.")
        return None
    #endregion

class Loop():
    #region constructor
    def __init__(self):
        """
        Defines a loop as a list of node names.
        """
        self.Nodes = []
    #endregion

class Resistor():
    #region  constructor
    def __init__(self, R=1.0, i=0.0, name='ab'):
        """
        Defines a resistor to have a self.Resistance, self.Current, and self.Name instance variables.
        :param R: resistance in Ohm
        :param i: current in amps
        :param name: name of resistor by alphabetically ordered pair of node names
        """
        # Assigning passed resistance value to the resistor's resistance property.
        self.Resistance = R
        # Assigning passed current value to the resistor's current property.
        self.Current = i
        # Assigning passed name to the resistor's name property, identifying the resistor by the nodes it connects.
        self.Name = name
    #endregion

    #region methods/functions
    def DeltaV(self):
        """
        Calculates voltage change across resistor.
        :return: the signed value of voltage drop.  Voltage drop > 0 in direction of positive current flow.
        """
        return self.Current*self.Resistance
    #endregion

class VoltageSource():
    #region constructor
    def __init__(self, V=12.0, name='ab'):
        """
        Define a voltage source with instance variables of self.Voltage = V, self.Name = name
        :param V: The voltage
        :param name: the name of voltage source.  The voltage source naming convention is to use the nodes such as 'ab'
        where the order of the nodes goes in the direction of positive voltage change as I traverse the loop from a to b.
        """
        self.Voltage = V
        self.Name=name
    #endregion

#endregion

# region Function Definitions
def main():
    """
    This program solves for the unknown currents in the circuit of the homework assignment.
    :return: nothing
    """
    Net = ResistorNetwork2()  # Instantiate a ResistorNetwork2 object instead
    Net.BuildNetworkFromFile(
        "ResistorNetwork_2.txt")  # This should now correctly refer to an instance of ResistorNetwork2
    ivals = Net.AnalyzeCircuit()

    # After calling BuildNetworkFromFile in the main function
    for resistor in Net.Resistors:
        print(resistor.Name)

# endregion

# region function calls
if __name__=="__main__":
    main()
# endregion