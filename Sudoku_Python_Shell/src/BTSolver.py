import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random
from collections import deque, Counter


class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__(self, gb, trail, val_sh, var_sh, cc):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

        # track assigned variables here
        self.assignedVars = deque()
        self.arcConsistency()

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck(self):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: a tuple of a dictionary and a bool. The dictionary contains all MODIFIED variables, mapped to their MODIFIED domain.
                The bool is true if assignment is consistent, false otherwise.
    """

    def forwardChecking(self):
        if not self.network.isConsistent():
            return ({}, False)
        # self.arcConsistency()
        # most recently

        # self.assignedVars = deque()
        # for c in self.network.constraints:
        #     for v in c.vars:
        #         if v.isAssigned():
        #             self.assignedVars.append(v)

        modified_var_domains = {}

        while self.assignedVars:
            var = self.assignedVars.popleft()

            for neighbor in self.network.getNeighborsOfVariable(var):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(var.getAssignment()):

                    self.trail.push(neighbor)
                    neighbor.removeValueFromDomain(var.getAssignment())
                    if neighbor.getDomain().size() == 1:
                        self.trail.push(neighbor)
                        neighbor.assignValue(neighbor.domain.values[0])
                        self.assignedVars.append(neighbor)

                        if not self.network.isConsistent():
                            return (modified_var_domains, False)

                    modified_var_domains[var] = var.getDomain()

        return (modified_var_domains, True)

    # =================================================================
        # Arc Consistency
        # =================================================================
    def arcConsistency(self):
        # self.assignedVars = []
        for c in self.network.constraints:
            for v in c.vars:
                if v.isAssigned():
                    self.assignedVars.append(v)
        while len(self.assignedVars) != 0:
            av = self.assignedVars.popleft()
            for neighbor in self.network.getNeighborsOfVariable(av):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(av.getAssignment()):
                    neighbor.removeValueFromDomain(av.getAssignment())
                    if neighbor.domain.size() == 1:
                        neighbor.assignValue(neighbor.domain.values[0])
                        self.assignedVars.append(neighbor)

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: a pair of a dictionary and a bool. The dictionary contains all variables 
		        that were ASSIGNED during the whole NorvigCheck propagation, and mapped to the values that they were assigned.
                The bool is true if assignment is consistent, false otherwise.
    """

    def norvigCheck(self):
        return ({}, False)

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
    """

    def getTournCC(self):
        return False

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable(self):  # optimize
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """

    def getMRV(self):  # optimize by calculating at start
        min_domain_size = float("inf")
        min_rem_vals_var = None

        for v in self.network.variables:
            if not v.isAssigned() and v.getDomain().size() < min_domain_size:
                min_domain_size = v.getDomain().size()
                min_rem_vals_var = v
        # print(min_rem_vals_var)
        return min_rem_vals_var

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with the smallest domain and affecting the  most unassigned neighbors.
                If there are multiple variables that have the same smallest domain with the same number of unassigned neighbors, add them to the list of Variables.
                If there is only one variable, return the list of size 1 containing that variable.
    """

    def MRVwithTieBreaker(self):
        # Get min domain size

        mrv_vars = [self.getMRV()]
        if mrv_vars[0] == None:
            return [None]

        max_deg = len(self.getUnassignedNeighbors(mrv_vars[0]))

        for v in self.network.variables:
            deg = len(self.getUnassignedNeighbors(v))

            if mrv_vars[0].getDomain().size() == v.getDomain().size():
                if deg > max_deg:
                    # reset
                    mrv_vars = [v]
                    max_deg = deg
                elif deg == max_deg:
                    # append
                    mrv_vars.append(v)

        return mrv_vars

    def getUnassignedNeighbors(self, v):  # this is a custom function
        return [neighbor for neighbor in self.network.getNeighborsOfVariable(v) if not neighbor.isAssigned()]

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """

    def getTournVar(self):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder(self, v):
        values = v.domain.values
        return sorted(values)

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """

    def getValuesLCVOrder(self, v):
        domain = set(v.getDomain().values)
        value_knockout_count = Counter()  # (Value, # Neighbors knocked out)

        # Count # of neighbors that match any of the values in the domain of v
        for v in self.network.getNeighborsOfVariable(v):
            for val in v.getDomain().values:
                if val in domain:
                    value_knockout_count[val] += 1

        # Alternatively, bucket sort is efficient because of the constrained domains of each value is maximally the max(width, height) of the board

        # print(value_knockout_count)
        lcv_sorted_counts = sorted(
            value_knockout_count.items(), key=lambda p: p[1])

        # Get just the values from the sorted pairs
        lcv_sorted_vals = [val for val, count in lcv_sorted_counts]

        return lcv_sorted_vals

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """

    def getTournVal(self, v):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve(self, time_left=600):
        if time_left <= 60:
            return -1

        start_time = time.time()
        if self.hassolution:
            return 0

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if (v == None):
            # Success
            self.hassolution = True
            return 0

        # Attempt to assign a value
        for i in self.getNextValues(v):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push(v)

            # Assign the value
            v.assignValue(i)

            self.assignedVars.appendleft(v)  # changed

            # Propagate constraints, check consistency, recur
            if self.checkConsistency():
                elapsed_time = time.time() - start_time
                new_start_time = time_left - elapsed_time
                if self.solve(time_left=new_start_time) == -1:
                    return -1

            # If this assignment succeeded, return
            if self.hassolution:
                return 0

            # Otherwise backtrack
            self.trail.undo()

        return 0

    def checkConsistency(self):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()[1]

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()[1]

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable(self):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()[0]

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues(self, v):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder(v)

        if self.valHeuristics == "tournVal":
            return self.getTournVal(v)

        else:
            return self.getValuesInOrder(v)

    def getSolution(self):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
