import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random
from collections import deque, Counter, defaultdict
from pprint import pprint


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
        self.assignedVars = deque()  # should perhaps refactor this to be more clear

        """ NORVIG CHECKING HELPER MEMORY"""
        # Create a value index tracker to:
        # 1) Track the count of each value (corresponding to the N - length of either set)
        # 2) Retrieve in constant time the index of the variable which must have a certain value

        self.N = self.gameboard.N

        rows = defaultdict(list)
        cols = defaultdict(list)
        blocks = defaultdict(list)

        for var in self.network.getVariables():
            if var not in rows[var.row]:
                rows[var.row].append(var)

            if var not in cols[var.col]:
                cols[var.col].append(var)

            if var not in blocks[var.block]:
                blocks[var.block].append(var)

        self.units = [rows, cols, blocks]

        # self.unit_domain_counts = {
        #     # corresponding to the count for each row
        #     "rows": defaultdict(Counter),
        #     "cols": defaultdict(Counter),
        #     "blocks": defaultdict(Counter)

        # }

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

        modified_var_domains = {}
        assignedVarsRecent = deque([self.assignedVars[0]])

        while assignedVarsRecent:
            var = assignedVarsRecent.popleft()

            for neighbor in self.network.getNeighborsOfVariable(var):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(var.getAssignment()):

                    self.trail.push(neighbor)
                    neighbor.removeValueFromDomain(var.getAssignment())
                    if neighbor.getDomain().size() == 1:
                        self.trail.push(neighbor)
                        neighbor.assignValue(neighbor.domain.values[0])
                        assignedVarsRecent.append(neighbor)

                        if not self.network.isConsistent():
                            return (modified_var_domains, False)

                    modified_var_domains[var] = var.getDomain()

        return (modified_var_domains, True)

    # =================================================================
    # Arc Consistency
    # =================================================================
    def arcConsistency(self):
        assigned = set()

        # self.assigned_cell_stack.append([])
        for c in self.network.constraints:  # optimize
            for v in c.vars:
                if v.isAssigned() and (v.row, v.col) not in assigned:
                    self.assignedVars.append(v)
                    value, row, col = v.getAssignment(), v.row, v.col
                    assigned.add((v.row, v.col))

        assignedVarsCopy = self.assignedVars.copy()

        while len(assignedVarsCopy) != 0:
            av = assignedVarsCopy.popleft()
            for neighbor in self.network.getNeighborsOfVariable(av):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(av.getAssignment()):
                    neighbor.removeValueFromDomain(av.getAssignment())
                    if neighbor.domain.size() == 1:
                        neighbor.assignValue(neighbor.domain.values[0])
                        assignedVarsCopy.append(neighbor)

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

    def norvigCheck(self):  # Good time for encapsulation
        if not self.network.isConsistent():
            return ({}, False)

        modified_var_domains = {}
        assignedVarsRecent = deque([self.assignedVars[0]])

        variables_assigned = {}

        modified_vars = []

        while assignedVarsRecent:
            var = assignedVarsRecent.popleft()

            for neighbor in self.network.getNeighborsOfVariable(var):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(var.getAssignment()):

                    self.trail.push(neighbor)
                    modified_vars.append(neighbor)

                    neighbor.removeValueFromDomain(var.getAssignment())
                    if neighbor.getDomain().size() == 1:
                        value = neighbor.domain.values[0]
                        self.trail.push(neighbor)
                        neighbor.assignValue(value)
                        variables_assigned[var] = value
                        assignedVarsRecent.append(neighbor)

                        if not self.network.isConsistent():
                            return (variables_assigned, False)

                        # values.add(neighbor.getAssignment())

                    # modified_var_domains[var] = var.getDomain()
        # print(values)

        # change the self variables in constraintnetwork back
        # find a different method

        # track the counts of each rows and cols
        # need to also backtrack the counts of each rows and cols and blocks

        # get the modified var domains

        # just check the modified var domains

        # count each row, each col, and each block
        # check the modified

        """
        Keep an array of hashmap of hashmaps in the class to keep track of domain counts of each row/col/block

        Update counts durin arc  consistency porrtion

        In Norvig, iterate over the modified domains of 
        to check all affected rows, columns and blocks

        how to reduce number of counts to check for counter[val] == 1

        Use the set of modified domains to backtrack this 


        
        """

        for units_type in self.units:  # O(NNq)

            # count the values in each unit (ex row)
            # should be able to do this at beginning and avoid repeated work

            units = list(units_type.values())

            # for unit in units_type.values():
            for unit_index in range(self.N):

                # optimize
                counter = Counter()
                # count the frequency of each value in domains in the unit
                for i in range(1, self.N+1):  # O(nq)
                    for val in units[unit_index][i-1].getDomain().values:
                        counter[val] += 1

                # find a value with a single possible location in this unit
                # find the only variable which it can be assigned to
                for i in range(1, self.N+1):  # O(nq)
                    if counter[i] == 1:
                        # find the one domain in unit that has i for a possible value

                        # optimize
                        for var in units[unit_index]:
                            if not var.isAssigned() and var.getDomain().contains(i):
                                self.trail.push(var)
                                var.assignValue(i)
                                variables_assigned[var] = i
                                if not self.network.isConsistent():
                                    return (variables_assigned, False)

        return (variables_assigned, True)

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
    """

    def getTournCC(self):
        # if self.N <= 16:
        #     return self.forwardChecking()

        return self.norvigCheck()

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

        """
        Potential Optimizations:
        Store this as a dict[set] in the class itself. Prevent recalculation and can update as board is solved.
        # track assigned and uniassigned varaibles
        # use itertools to use c instead
        """

        for v in self.network.variables:
            if not v.isAssigned() and v.getDomain().size() < min_domain_size:
                min_domain_size = v.getDomain().size()
                min_rem_vals_var = v

        return min_rem_vals_var

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with the smallest domain and affecting the most unassigned neighbors.
                If there are multiple variables that have the same smallest domain with the same number of unassigned neighbors, add them to the list of Variables.
                If there is only one variable, return the list of size 1 containing that variable.
    """

    def MRVwithTieBreaker(self):  # could use a heap
        # Get min domain size

        mrv_vars = [self.getMRV()]
        if mrv_vars[0] == None:
            return [None]

        max_deg = len(self.getUnassignedNeighbors(mrv_vars[0]))

        for v in self.network.variables:  # this is kind aslow
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
        """
        Potential Optimizations:
        Store this as a dict[set] in the class itself. Prevent recalculation and can update as board is solved.
        Tradeoff: Memory overhead
        """
        return [neighbor for neighbor in self.network.getNeighborsOfVariable(v) if not neighbor.isAssigned()]

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """

    def getTournVar(self):
        # if self.N <= 9:
        #     return self.getMRV()

        return self.MRVwithTieBreaker()

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
        """
        Potential optimizations:
        Bucket sort: O(nlogn) -> O(n)
        """

        domain = set(v.getDomain().values)
        value_knockout_count = Counter()  # (k: v) -- (Value: # Neighbors knocked out)

        # Count # of neighbors that match any of the values in the domain of v
        for v in self.network.getNeighborsOfVariable(v):
            for val in v.getDomain().values:
                if val in domain:
                    value_knockout_count[val] += 1

        # Alternatively, bucket sort is efficient because of the constrained domains of each value is maximally the max(width, height) of the board

        # print(value_knockout_count)
        lcv_sorted_counts = sorted(
            value_knockout_count.items(), key=lambda pair: pair[1])

        # Get just the values from the sorted pairs
        lcv_sorted_vals = [val for val, count in lcv_sorted_counts]

        return lcv_sorted_vals

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """

    def getTournVal(self, v):
        return self.getValuesLCVOrder()

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

            # Optimize later

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

            # while self.assigned_cell_stack[-1]:
            #     row, col, val = self.assigned_cell_stack[-1].pop()

            #     self.valueIndexTracker[val][0].add(row)
            #     self.valueIndexTracker[val][1].add(col)

            # self.assigned_cell_stack.pop()

            # undo the index removals with a stack

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
