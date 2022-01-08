import random
import copy
def isInside(pos):
    if pos[0] >= 0 and pos[0] < 8:
        if pos[1] >= 0 and pos[1] < 8:
            return True
    return False

class Piece:
    def __init__(self, game, position, color):
        self.position = position
        self.board = game.board
        self.game = game
        self.color = color
        self.rules = []
        self.first_move = True

    def check_for_self_check(self, pos):
        victim = 0
        if self.color == "B":
            color = 1
        else:
            color = 0
        tmp = self.board[pos[0]][pos[1]]
        if tmp != 0:
            if tmp.color != self.color:
                victim = tmp
                self.game.pieces[(color+1)%2].remove(victim)
                
        self.game.board[pos[0]][pos[1]] = self
        tmpPos = copy.deepcopy(self.position)
        self.board[self.position[0]][self.position[1]] = 0
        self.position = pos
        i = 1
        if self.game.next_to_move == "W":
            i = 0
        for piece in self.game.pieces[(i+1)%2]:
            for move in piece.get_possible_moves_no_check():
                if move == self.game.kings[i].position:
                    self.board[pos[0]][pos[1]] = tmp
                    self.position = tmpPos
                    self.board[self.position[0]][self.position[1]] = self
                    if victim != 0:
                        self.game.pieces[(color+1)%2].append(victim)
                    return True
        self.board[pos[0]][pos[1]] = tmp
        self.position = tmpPos
        self.board[self.position[0]][self.position[1]] = self
        if victim != 0:
            self.game.pieces[(color+1)%2].append(victim)
        return False

    def tick(self):
        return False

    def move(self, position):
        self.position = position
        self.first_move = False

    def get_possible_moves_no_check(self):
        possible_moves = []
        board = self.board
        for direction in self.rules:
            for move in direction:
                pos = [self.position[0] + move[0], self.position[1] + move[1]]
                if not (isInside(pos)):
                    continue
                if (board[pos[0]][pos[1]] != 0):
                    if (board[pos[0]][pos[1]].color != self.color): 
                        possible_moves.append(pos)         
                    break
                else:
                    possible_moves.append(pos)
        return possible_moves

    def get_possible_moves(self):
        if self.game.promotee:
            return
        possible_moves = []
        board = self.board
        for direction in self.rules:
            for move in direction:
                pos = [self.position[0] + move[0], self.position[1] + move[1]]
                
                if not (isInside(pos)):
                    continue
                if (board[pos[0]][pos[1]] != 0):
                    if (board[pos[0]][pos[1]].color != self.color and not self.check_for_self_check(pos)): 
                        possible_moves.append(pos)
                    break
                elif(not self.check_for_self_check(pos)):
                    possible_moves.append(pos)
        return possible_moves

class Pawn(Piece):
    def __init__(self, board,  position, color):
        Piece.__init__(self, board, position, color)
        if self.color == "B":
            self.rules = [[[0,-1], [0,-2]]]
            self.aggresive_move = [[1, -1], [-1, -1]]
        else:
            self.rules = [[[0,1], [0,2]]]
            self.aggresive_move = [[1, 1], [-1, 1]]

        self.type = "Pawn"
        self.enPassant = None
        self.enPassantTarget = None

    def check_promotion(self):
        if self.color == "B" and self.position[1] == 0:
            return True
        elif self.color == "W" and self.position[1] == 7:
            return True
        else:
            return False

    def tick(self):
        if self.enPassant:
            print(self.color)
            print("removed")
            self.enPassant = None
            self.enPassantTarget = None
        return self.check_promotion()
    
    def get_possible_moves(self):
        if self.game.promotee:
            return
        possible_moves = []
        board = self.board
        for direction in self.rules:
            for move in direction:
                pos = [self.position[0] + move[0], self.position[1] + move[1]]
                if not (isInside(pos)):
                    continue
                if self.check_for_self_check(pos):
                    continue
                if (board[pos[0]][pos[1]] != 0):
                    break
                else:
                    possible_moves.append(pos)

        for move in self.aggresive_move:
            pos = [self.position[0] + move[0], self.position[1] + move[1]]
            if not (isInside(pos)):
                    continue
            if self.check_for_self_check(pos):
                    continue
            if (board[pos[0]][pos[1]] != 0):
                if (board[pos[0]][pos[1]].color != self.color and not self.check_for_self_check(pos)):
                    possible_moves.append(pos)
        if self.enPassant:
            pos = [self.position[0] + self.enPassant[0], self.position[1] + self.enPassant[1]]
            if (isInside(pos)):
                if (board[pos[0]][pos[1]] == 0):
                    if not self.check_for_self_check(pos):
                        possible_moves.append(pos)
        return possible_moves
   
    def check_for_en_passant(self, position):
        if not (isInside([position[0]+1, position[1]])):
            return
        if self.board[position[0]+1][position[1]] != 0:
            piece = self.board[position[0]+1][position[1]]
            if piece.type == "Pawn" and piece.color != self.color:
                if piece.color == "B":
                    piece.enPassant = [-1,-1]
                    piece.enPassantTarget = self
                else:
                    piece.enPassant = [-1,1]
                    piece.enPassantTarget = self
        if not (isInside([position[0]-1, position[1]])):
            return
        if self.board[position[0]-1][position[1]] != 0:
            piece = self.board[position[0]-1][position[1]]
            if piece.type == "Pawn" and piece.color != self.color:
                if piece.color == "B":
                    piece.enPassant = [+1,-1]
                    piece.enPassantTarget = self
                else:
                    piece.enPassant = [+1,1]
                    piece.enPassantTarget = self
    
    def move(self, position):
        color = 0
        if self.color =="B":
            color = 1
        if abs(self.position[1] - position[1]) == 2:
            self.check_for_en_passant(position)
        if self.enPassant:
            if position == [self.position[0] + self.enPassant[0], self.position[1] + self.enPassant[1]]:
                self.game.board[self.enPassantTarget.position[0]][self.enPassantTarget.position[1]] = 0
                self.game.pieces[(color+1)%2].remove(self.enPassantTarget)
        Piece.move(self, position)
        self.new_rules()


    def get_possible_moves_no_check(self):
        possible_moves = []
        board = self.board
        for direction in self.rules:
            for move in direction:
                pos = [self.position[0] + move[0], self.position[1] + move[1]]
                if not (isInside(pos)):
                    continue
                if (board[pos[0]][pos[1]] == 0):
                    possible_moves.append(pos)
        for move in self.aggresive_move:
            pos = [self.position[0] + move[0], self.position[1] + move[1]]
            if not (isInside(pos)):
                    continue
            if (board[pos[0]][pos[1]] != 0):
                if (board[pos[0]][pos[1]].color != self.color):
                    possible_moves.append(pos)
        return possible_moves

    def new_rules(self):
        if self.color == "B":
            self.rules = [[[0,-1]]]
            self.aggresive_move = [[1, -1], [-1, -1]]
        else:
            self.rules = [[[0,1]]]
            self.aggresive_move = [[1, 1], [-1, 1]]

class Knight(Piece):
    def __init__(self, board, position, color):
        Piece.__init__(self, board, position, color)
        self.rules = [[2,1], [1,2], [-1, -2], [1, -2], [-1, 2], [-2, 1], [-2, -1], [2, -1]]
        self.type = "Knight"

    def get_possible_moves(self):
        if self.game.promotee:
            return
        possible_moves = []
        board = self.board
        for move in self.rules:
            pos = [self.position[0] + move[0], self.position[1] + move[1]]
            if not (isInside(pos)):
                continue
            if self.check_for_self_check(pos):
                continue
            if (board[pos[0]][pos[1]] == 0 or board[pos[0]][pos[1]].color != self.color):
                possible_moves.append(pos)
        return possible_moves
    
    def get_possible_moves_no_check(self):
        possible_moves = []
        board = self.board
        for move in self.rules:
            pos = [self.position[0] + move[0], self.position[1] + move[1]]
            if not (isInside(pos)):
                continue
            if (board[pos[0]][pos[1]] == 0 or board[pos[0]][pos[1]].color != self.color):
                possible_moves.append(pos)
        return possible_moves

class Rook(Piece):
    def __init__(self, game, position, color):
        Piece.__init__(self, game, position, color)
        self.rules = []
        self.rules.append([[x, 0] for x in range(1,8)])
        self.rules.append([[0, y] for y in range(1,8)])
        self.rules.append([[0, -y] for y in range(1,8)])
        self.rules.append([[-y, 0] for y in range(1,8)])
        self.type = "Rook"

class Bishop(Piece):
    def __init__(self, game, position, color):
        Piece.__init__(self, game, position, color)
        self.rules = []
        self.rules.append([[x, x] for x in range(1,8)])
        self.rules.append([[x, -x] for x in range(1,8)])
        self.rules.append([[-x, x] for x in range(1,8)])
        self.rules.append([[-x, -x] for x in range(1,8)])
        self.type = "Bishop"

class Queen(Bishop):
    def __init__(self, game, position, color):
        Bishop.__init__(self, game, position, color)
        self.rules.append([[0, y] for y in range(1,8)])
        self.rules.append([[x, 0] for x in range(1,8)])
        self.rules.append([[0, -y] for y in range(1,8)])
        self.rules.append([[-y, 0] for y in range(1,8)])
        self.type = "Queen"
       
class King(Piece):
    def __init__(self, game, position, color):
        Piece.__init__(self, game, position, color)
        if color == "B":
            color = 1
        else:
            color =0
        self.rules = [[[1, 1]], [[1, 0]], [[1, -1]], [[-1,0]], [[-1, -1]], [[-1, 1]], [[0, 1]], [[0,-1]]]
        self.type = "King"
        self.rooks = [piece for piece in self.game.pieces[color] if piece.type == "Rook"]
        self.king_pos = []
        self.rook_pos = []
        self.rokade = []
    
    def check_between(self, rook):
        color = 0
        if self.color == "B":
            color = 1
        diff = rook.position[0] - self.position[0] 
        one = int(diff/abs(diff))
        for i in range(one, diff, one):
            if self.game.board[self.position[0]+i][self.position[1]] != 0:
                return False
            else:
                self.game.board[self.position[0]+i][self.position[1]] = self
            for piece in self.game.pieces[(color+1)%2]:
                if piece.type == "King":
                    continue
                if [self.position[0]+i,self.position[1]] in piece.get_possible_moves():
                    self.game.board[self.position[0]+i][self.position[1]] = 0
                    return False
            self.game.board[self.position[0]+i][self.position[1]] = 0
        return True
        
    def check_rokade(self):
        self.king_pos = []
        self.rook_pos = []
        self.rokade = []
        flag = False
        if self.first_move:
            for rook in self.rooks:
                if rook.first_move and self.check_between(rook):
                    direction = int((rook.position[0]-self.position[0]) / abs(self.position[0] - rook.position[0]))
                    position = [self.position[0]+direction*2, self.position[1]]
                    if self.check_for_self_check(position):
                        continue
                    self.rokade.append(rook)
                    self.king_pos.append(position)
                    position = [self.position[0]+direction*1, self.position[1]]
                    self.rook_pos.append(position)
                    flag = True
        return flag
    
    def get_possible_moves(self):
        first_moves = super().get_possible_moves()
        if self.check_rokade():
            first_moves.extend(self.king_pos)
        return first_moves

    def move(self, position):
        super().move(position)
        if position in self.king_pos:
            index = self.king_pos.index(position)
            rook = self.rokade[index]
            rook_pos = self.rook_pos[index]
            self.game.move([rook.position, rook_pos], self.color, True)
        

class Game():
    def __init__(self):
        self.pieces = [[], []]
        board = [ [0 for i in range(8)] for y in range(8) ]
        self.board = board
        self.kings = []
        self.future_board = copy.deepcopy(self.board)
        self.next_to_move = "W"
        self.promotee = None
        for i in range(8):
            piece = Pawn(self,[i,1], "W")
            self.board[i][1] = piece
            self.pieces[0].append(piece)
            piece = Pawn(self, [i, 6], "B")
            self.board[i][6] = piece
            self.pieces[1].append(piece)

        piece = Rook(self, [0,0], "W"); self.board[0][0] = piece; self.pieces[0].append(piece)
        piece = Rook(self,[7,0], "W"); self.board[7][0] = piece; self.pieces[0].append(piece)
        piece = Rook(self,[0,7], "B"); self.board[0][7] = piece; self.pieces[1].append(piece)
        piece = Rook(self,[7,7], "B"); self.board[7][7] = piece; self.pieces[1].append(piece)
        
        piece = Knight(self,[1,0], "W"); self.board[1][0] = piece; self.pieces[0].append(piece)
        piece = Knight(self,[6,0], "W"); self.board[6][0] = piece; self.pieces[0].append(piece)
        piece = Knight(self,[1,7], "B"); self.board[1][7] = piece; self.pieces[1].append(piece)
        piece = Knight(self,[6,7], "B"); self.board[6][7] = piece; self.pieces[1].append(piece)

        piece = Bishop(self,[2,0], "W"); self.board[2][0] = piece; self.pieces[0].append(piece)
        piece = Bishop(self,[5,0], "W"); self.board[5][0] = piece; self.pieces[0].append(piece)
        piece = Bishop(self,[2,7], "B"); self.board[2][7] = piece; self.pieces[1].append(piece)
        piece = Bishop(self,[5,7], "B"); self.board[5][7] = piece; self.pieces[1].append(piece)

        piece = King(self,[3,0], "W"); self.board[3][0] = piece; self.pieces[0].append(piece)
        self.kings.append(piece)
        piece = King(self,[3,7], "B"); self.board[3][7] = piece; self.pieces[1].append(piece)
        self.kings.append(piece)

        piece = Queen(self,[4,0], "W"); self.board[4][0] = piece; self.pieces[0].append(piece)
        piece = Queen(self,[4,7], "B"); self.board[4][7] = piece; self.pieces[1].append(piece)

    def printBoard(self):
        pBoard = [ [0 for x in range(8)] for y in range(8) ]
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == 0:
                    continue
                type = self.board[x][y].type
                color = self.board[x][y].color
                if type == "Pawn":
                    pBoard[x][y] = color +"P"
                elif type == "King":
                    pBoard[x][y] = color+"K"
                elif type == "Queen":
                    pBoard[x][y] = color+"Q"
                elif type == "Knight":
                    pBoard[x][y] = color+"H"
                elif type == "Bishop":
                    pBoard[x][y] = color+"B"
                elif type == "Rook":
                    pBoard[x][y] = color+"R"

        for y in range(8):
            string = "|"
            for x in range(8):
                string += str(pBoard[x][y]) + "|"
            print(string)

    def get_possible_moves(self, color):
        possible_moves = []
        for piece in self.pieces[color]:
            moves = piece.get_possible_moves()
            for move in moves:
                possible_moves.append([piece.position, move])
        return possible_moves
    
    def tick(self, color):
        promotee = None
        print("tick color", color)
        for piece in self.pieces[color]:
            promotion = piece.tick()
            if promotion:
                promotee = piece
        if promotee:
            return promotee
        return False

    def move(self, positions, color, no_change = False):
        if color =="B":
            color = 1
        else:
            color = 0
        piece = self.board[positions[0][0]][positions[0][1]]
        tmp = self.board[positions[1][0]][positions[1][1]]
        self.board[positions[1][0]][positions[1][1]] = piece
        self.board[positions[0][0]][positions[0][1]] = 0
        if tmp != 0:
            self.pieces[(color+1)%2].remove(tmp)
        print(color)
        piece.move(positions[1])
        promotee = self.tick(color)
        if promotee:
            self.promotee = promotee
        else:
            if not no_change and self.next_to_move == "B":
                self.next_to_move = "W"
            else:
                self.next_to_move = "B"
        
    def promote(self, typ):
        color = 0
        if self.promotee.color == "B":
            color = 1
        position = self.promotee.position
        self.pieces[color].remove(self.promotee)
        if typ == "Rook":
            piece = Rook(self, position, self.promotee.color); self.board[position[0]][position[1]] = piece; self.pieces[color].append(piece)
        elif typ == "Knight":
            piece = Knight(self,position, self.promotee.color); self.board[position[0]][position[1]] = piece; self.pieces[color].append(piece)
        elif typ == "Bishop":
            piece = Bishop(self,position, self.promotee.color); self.board[position[0]][position[1]] = piece; self.pieces[color].append(piece)
        elif typ == "Queen": 
            piece = Queen(self,position, self.promotee.color); self.board[position[0]][position[1]] = piece; self.pieces[color].append(piece)
        piece.first_move = False
        
        self.promotee = None
        if self.next_to_move == "B":
            self.next_to_move = "W"
        else:
            self.next_to_move = "B"

    def play_random(self):
        for i in range(1000):
            print(i)
            moves = self.get_possible_moves(i%2)
            move = random.choice(moves)
            self.move(move, i%2)
            self.printBoard()
            print("______________________________________________")

            
        
            
