import sys

from crossword import *
import queue
import math
import time

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }
        self.copy_of_domains = dict()  # = domains  # ----------------------------- My copy of domains

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        self.copy_of_domains = self.domains
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # print(self.domains)
        for key in self.domains:
            # print(key, "---->")
            # print(self.domains[key])
            # type(key) -> <class 'crossword.Variable'>
            words_to_delete = []
            for word in self.domains[key]:
                if len(word) != key.length:
                    words_to_delete.append(word)
            for word_to_delete in words_to_delete:
                self.domains[key].remove(word_to_delete)
            # print(self.domains[key])

        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # print("hello in revise!!!!!!!!!")

        if self.crossword.overlaps[x, y] is None:
            return False  # ??????

        values_to_delete = []
        for value in self.domains[x]:
            word_for_this_value_exist = False
            for word in self.domains[y]:
                if value[self.crossword.overlaps[x, y][0]] == word[self.crossword.overlaps[x, y][1]]:
                    word_for_this_value_exist = True
            if not word_for_this_value_exist:
                values_to_delete.append(value)

        if not values_to_delete:
            return False
        while values_to_delete:
            self.domains[x].remove(values_to_delete[0])
            values_to_delete.pop(0)
        return True

        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        '''
        #print("neighbords Variable(1, 12, 'down', 7)::")
        #print(self.crossword.neighbors(Variable(1, 12, 'down', 7)))
        #for i in self.crossword.overlaps:
        #    print(i, "--",self.crossword.overlaps[i]) 
        '''  '''
        print("BeFORE: ",self.domains)
        for i in self.domains:
            print(i, "--->",self.domains[i])
        # '''
        # DO QUEUE A) arcs arcs is list, q is queue
        if arcs is None:
            arcs = []
            for keyx in self.domains:
                for keyy in self.domains:
                    if keyx != keyy:
                        arcs.append((keyx, keyy))
        elif not arcs:
            return True #????????????????????????????????????????????????????

        q = queue.Queue()
        for tuple in arcs:
            q.put(tuple)
        # print("LIST QUEUE", list(q.queue))

        #  AC-3 ALGORITHM
        while not q.empty():
            (X, Y) = q.get()
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                for Z in self.crossword.neighbors(X):
                    if Z == Y:
                        continue
                    q.put((Z, X))

        '''print("AFTER: ")
        for i in self.domains:
            print(i, "--->",self.domains[i])'''
        return True

        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for key in self.domains:
            if key not in assignment.keys():
                return False
        return True
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #  print("CONSISTENT")

        # all values are distinct
        all_values = set()
        for key in assignment:
            all_values.add(assignment[key])  # set have unique values
        if len(all_values) != len(assignment):  # if we add the same value there will be 1
            return False

        #  correct length
        for key in assignment:
            if len(assignment[key]) != key.length:
                return False

        # and there are no conflicts between neighboring variables.
        q = queue.Queue()
        for key in assignment:
            for neighbor in self.crossword.neighbors(key):
                if neighbor in assignment.keys():
                    q.put((key, neighbor))

        while not q.empty():
            (x, y) = q.get()
            # if assignment[x] == assignment[y]: CHECKED
            #    return False
            if self.crossword.overlaps[x, y] is None:
                continue
            (lx, ly) = self.crossword.overlaps[x, y]  # lx- letter in x word [0,1,2,3,4]
            if assignment[x][lx] != assignment[y][ly]:  # same letter must be in cross
                return False
            ''' # every key have one value not more words in my case 
            for word in assignment[x]:
                for word_neighbor in assignment[y]:
                    if word[self.crossword.overlaps[x, y][0]] != word_neighbor[self.crossword.overlaps[x, y][1]]:
                        return False
                    if word == word_neighbor:
                        return False ##### różne słowa???
            '''

        return True
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # self.crossword.neighbors(var)  # set of neighbors
        # assignment[var]  # set of words for this variable
        # print("ORDER DOMAIN VALUES--- Var: ", var)

        words_counts = dict()
        for word in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                # Note that any variable present in assignment already has a value,
                # and therefore should n’t be counted
                # when computing the number of values ruled out for neighboring unassigned variables.
                if neighbor in assignment:
                    continue

                (letter_var, letter_neighbor) = self.crossword.overlaps[var, neighbor]
                letter = word[letter_var]
                for word_neighbor in self.domains[neighbor]:
                    if word_neighbor[letter_neighbor] != letter:
                        count += 1
            words_counts[word] = count

        sorted_words = sorted(words_counts.items(), key=lambda x: x[1], reverse=True)
        # print("Sorted words: ", sorted_words)  # [('ANYBODY', 944), ('PACKAGE', 941),...........

        words_list = []
        for word in sorted_words:
            words_list.append(word[0])
        return words_list

        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # print("SELECT UNASSIGNED VARIABKE")
        '''
        minimum=len(self.crossword.words)#math.inf # good?? 1000? max value? infinity how many words
        for value in self.domains:
            if len(self.domains[value])<minimum:
                minimum=len(self.domains[value])
        min_values=[]
        for value in self.domains:
            if len(self.domains[value])==minimum:
                min_values.append(value)

        if len(min_values)==1:
            return min_values[0]
        minimum=len(self.crossword.words)
        for value in min_values:
            if len(self.crossword.neighbors(value))<minimum:
                minimum=len(self.crossword.neighbors(value))
        for value in min_values:
            if len(self.crossword.neighbors(value))==minimum:
                return value #first value which is ok

        #raise NotImplementedError
        '''
        # Choose the variable with the minimum number of remaining values in its domain.
        num_val_dict = dict()  # dictionary with number of value
        for key in self.domains:
            if key in assignment.keys():
                continue
            else:
                num_val_dict[key] = len(self.domains[key])
        if not num_val_dict:  # if there is no value which isn't in assignment
            return False

        # if only one key, we don't need to sort
        if len(num_val_dict) == 1:
            return list(num_val_dict.keys())[0]

        # this will be list of tuple!!
        sort_dict = sorted(num_val_dict.items(), key=lambda x: x[1], reverse=False)
        if sort_dict[0][1] != sort_dict[1][1]:  # if there is not tie
            return sort_dict[0][0]

        # TIE
        min_value = sort_dict[0][1]
        min_values = []
        for tuple_key_value in sort_dict:
            if tuple_key_value[1] == min_value:
                min_values.append(tuple_key_value[0])

        # If there is a tie, choose the variable with the highest degree.
        num_neig_dict = dict()
        for min_value in min_values:
            num_neig_dict[min_value] = len(self.crossword.neighbors(min_value))
        sorted_dict = sorted(num_neig_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_dict[0][0]

    def Inference(self, assignment):
        """
        Get assignment -> do a queue (X,Y). Every key in assignment -> Y

        def ac3(self, arcs=None):
        This function takes an optional argument called arcs, representing an initial list of arcs to process.
        """

        arcs = []
        for key in assignment:
            for neighbor in self.crossword.neighbors(key):
                if neighbor in assignment:
                    continue
                arcs.append((neighbor, key))

        return self.ac3(arcs)


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # FUNCTION BACKTRACK
        '''
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        # print("VAR: ", var, " --> ", len(self.domains[var]))
        for value in self.order_domain_values(var, assignment):
            assignment[var]=value
            if self.consistent(assignment):  # if value consistent with assignment
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)  # if value NOT consistent with assignment
        # print("BEFORE BACKTRACK IS NONE ",assignment)
        self.print(assignment)
        return None
        '''
        # BACKTRACK WITH INFERENCE

        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):

                if not self.Inference(assignment):
                    self.domains=self.copy_of_domains
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            self.domains = self.copy_of_domains
            assignment.pop(var)
        # print("BEFORE BACKTRACK IS NONE ",assignment)
        self.print(assignment)
        return None


def main():
    start_time = time.time()
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
