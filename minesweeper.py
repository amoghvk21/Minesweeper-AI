import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        i = cell[0]
        j = cell[1]
        if count != 0:
            self.knowledge.append(Sentence([(i-1, j+1), (i, j+1), (i+1, j+1), (i-1, j), (i+1, j), (i-1, j-1), (i, j-1), (i+1, j-1)], count))
            change = True
            while (change == True) and (len(self.knowledge) != 1):
                change = False            
                for x in range(len(self.knowledge)):
                    for y in range(len(self.knowledge)):
                        # Creates new sentances with the knowledge pairs
                        s1 = self.knowledge[x]
                        s2 = self.knowledge[y]
                        if (s2.cells.issubset(s1.cells)) or (s1.cells.issubset(s2.cells)):
                            s = s2.cells.symmetric_difference(s1.cells)
                            c = abs(s2.count - s1.count)
                            if self.knowledge.count(Sentence(s, c)) == 0:
                                self.knowledge.append(Sentence(s, c))
                                change = True
                
                # Remove elements from the sentences if they are known to be safe
                for x in range(len(self.knowledge)):
                    s = self.knowledge[x].cells
                    s = list(s)
                    for ele in s:
                        if ele in self.safes:
                            self.knowledge[x].cells.remove(ele)

                # Remove elements from the sentences if they are known to be a mine
                for x in range(len(self.knowledge)):
                    s = self.knowledge[x].cells
                    s = list(s)
                    for ele in s:
                        if ele in self.mines:
                            self.knowledge[x].cells.remove(ele)
                            self.knowledge[x].count -= 1                    

        else:
            
            temp = []

            temp.append((i-1, j+1))
            temp.append((i, j+1))
            temp.append((i+1, j+1))
            temp.append((i-1, j))
            temp.append((i+1, j))
            temp.append((i-1, j-1))
            temp.append((i, j-1))
            temp.append((i+1, j-1))

            for i in temp:
                if (i[0] >= 0) and (i[0] <= 7) and (i[1] >= 0) and (i[1] <= 7):
                    self.safes.add(i)

            del temp

        # Mark any new mines if the sentence explicitly says so
        for s in self.knowledge:
            if len(s.cells) == s.count:
                l = list(s.cells)
                for x in l:
                    self.mines.add(x)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        # return an element from a list of safe cells that is not in the moves made set
        if len(self.safes) > 1:
            l = list(self.safes)
            for ele in l:
                if ele not in self.moves_made:
                    self.moves_made.add(ele)
                    return ele
            return None
        else:
            return None
        

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        if (len(self.safes) > 0) and (not self.safes.issubset(self.moves_made)):
            while True:
                move = random.sample(self.safes, 1)[0]
                if (move not in self.moves_made) and (move not in self.mines):
                    return move
        else:
            while True:
                i = random.randrange(0, 8)
                j = random.randrange(0, 8)
                if ((i, j) not in self.moves_made) and ((i, j) not in self.mines):
                    return (i, j)
