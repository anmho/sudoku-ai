import Variable
import Constraint
import SudokuBoard
from math import floor

"""
    CSP representation of the problem. Contains the variables, constraints, and
    many helpful accessors.
"""


class ConstraintNetwork:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__(self, sboard=None):
        self.constraints = []
        self.variables = []

        if sboard != None:
            board = sboard.board
            temp = []
            value = 0

            for i in range(sboard.N):
                for j in range(sboard.N):
                    value = board[i][j]
                    domain = []
                    if value == 0:
                        d = 1
                        while d <= sboard.N:
                            domain.append(d)
                            d += 1
                    else:
                        domain.append(value)

                    block = int(
                        ((floor(i/sboard.p) * sboard.p) + floor(j/sboard.q)))
                    temp.append(Variable.Variable(domain, i, j, block))

            # Change this so that this class does not have to be modified
            self.rows = dict()
            self.cols = dict()
            self.blocks = dict()

            self.units = [self.rows,
                          self.cols,
                          self.blocks]

            for v in temp:
                row = v.row
                col = v.col
                block = v.block

                if not (row in self.rows.keys()):
                    self.rows[row] = []
                if not (col in self.cols.keys()):
                    self.cols[col] = []
                if not (block in self.blocks.keys()):
                    self.blocks[block] = []

                self.rows[row].append(v)
                self.cols[col].append(v)
                self.blocks[block].append(v)

            for v in temp:
                self.addVariable(v)

            for e in self.rows:
                c = Constraint.Constraint()
                for v in self.rows[e]:
                    c.addVariable(v)
                self.addConstraint(c)

            for e in self.cols:
                c = Constraint.Constraint()
                for v in self.cols[e]:
                    c.addVariable(v)
                self.addConstraint(c)

            for e in self.blocks:
                c = Constraint.Constraint()
                for v in self.blocks[e]:
                    c.addVariable(v)
                self.addConstraint(c)

    # ==================================================================
    # Modifiers
    # ==================================================================

    def addConstraint(self, c):
        if c not in self.constraints:
            self.constraints.append(c)

    def addVariable(self, v):
        if v not in self.variables:
            self.variables.append(v)

    # ==================================================================
    # Accessors
    # ==================================================================

    def getConstraints(self):
        return self.constraints

    def getVariables(self):
        return self.variables

    # Returns all variables that share a constraint with v
    def getNeighborsOfVariable(self, v):
        neighbors = set()

        for c in self.constraints:
            if c.contains(v):
                for x in c.vars:
                    neighbors.add(x)

        neighbors.remove(v)
        return list(neighbors)

    # Returns true is every constraint is consistent
    def isConsistent(self):
        for c in self.constraints:
            if not c.isConsistent():
                return False

        return True

    # Returns a list of constraints that contains v
    def getConstraintsContainingVariable(self, v):
        """
            @param v variable to check
            @return list of constraints that contains v
        """
        outList = []
        for c in self.constraints:
            if c.contains(v):
                outList.append(c)
        return outList

    """
        Returns the constraints that contain variables whose domains were
        modified since the last call to this method.

        After getting the constraints, it will reset each variable to
        unmodified

        Note* The first call to this method returns the constraints containing
        the initialized variables.
    """

    def getModifiedConstraints(self):
        mConstraints = []
        for c in self.constraints:
            if c.isModified():
                mConstraints.append(c)

        for v in self.variables:
            v.setModified(False)

        return mConstraints

    # ==================================================================
    # String Representation
    # ==================================================================

    def __str__(self):
        output = str(len(self.variables)) + " Variables: {"
        delim = ""

        for v in self.variables:
            output += delim + v.name
            delim = ","
        output += "}"

        output += "\n" + str(len(self.constraints)) + " Constraints:"
        delim = "\n"
        for c in self.constraints:
            output += delim + str(c)

        output += "\n"
        for v in self.variables:
            output += str(v) + "\n"

        return output

    # ==================================================================
    # Sudoku Board Representation
    # ==================================================================

    def toSudokuBoard(self, p, q):
        n = p*q
        board = [[0 for j in range(n)] for i in range(n)]
        row = 0
        col = 0
        for v in self.variables:
            board[row][col] = v.getAssignment()
            col += 1
            if col == n:
                col = 0
                row += 1
        return SudokuBoard.SudokuBoard(p, q, board=board)
