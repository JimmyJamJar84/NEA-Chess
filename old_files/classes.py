from piece_validation import *

class Move:
  def __init__(self, P, new_coor, valid_kill):
    self.P = P # Piece object of peice being moved
    self.new_coor = new_coor
    self.new_x = new_coor[0]
    self.new_y = new_coor[1]
    self.old_coor = [P.old_x, P.old_y]
    self.valid_kill =  valid_kill # Piece object of piece being captured
    self.pgn = ''
    try: # If valid_kill is not None ..
      self.material_gain = self.valid_kill.value
    except AttributeError: #.. Else
      self.material_gain = 0
    self.material_loss = 0
    self.piece_table_gain = 0

class Square: 
  def __init__(self, x, y, value, Piece, square_values):
    self.y = y
    self.x = x
    self.value = value # value to display ong the board e.g Wp5
    self.Piece = Piece # Piece object
    self.s_values = square_values[1] # Dictionary
    self.reversed_s_values = square_values[0] # Dictionary
    try:
      self.emoji = Piece.emoji # Symbol to display on board
    except AttributeError:
      self.emoji = 'x'

  def get_square_values(self, colour): # Returns dictionary of values for that square
    if colour == 'B':
      return self.reversed_s_values
    elif colour == 'W':
      return self.s_values

  def get_square_value(self, colour, type): # Returns single integer value
    if colour == 'B':
      return (self.reversed_s_values).get(type)
    elif colour == 'W':
      return (self.s_values).get(type)

class Board:
  def __init__(self, Squares, Pieces):
    self.board = Squares # List of square objects
    self.Pieces = Pieces # List of Piece objects
    self.valid_pieces = [] # Pieces that could be moved
    self.taken_pieces = [] 
    self.Kings = self.find_type_pieces('k')
    self.check_mate = False
    self.in_check = False
    self.direction = 1 # Direction the board is facing (1 or -1)
    self.turn = 'W'
    self.human_player = 'W' # Colour of the user playing against the computer
    self.human_game = False # Is the game human to humam (True) or human to computer (False)
    self.move_num = 1 # Number of move pairs made - used for generating PGN
    self.pgn = '' # PGN of entire game
    self.file_name = '' 
    self.previous_move = None
    self.move_history = [] # List of Moves that have been made
    self.promotion_type = None
    self.enable_tutorials = True
    self.enable_pre_tutorials = True
    self.disabled_tutorials = []

  def tutorial(self, M, pre_tutorial):
    valid_kill = 'No piece captured'
    if (pre_tutorial == True and self.enable_pre_tutorials == False) or (pre_tutorial == False and self.enable_tutorials == False) or (M == []):
      return None
    if pre_tutorial == True:
      turn = self.get_next_turn()
      temp = 'could perform'
      temp2 = 'next '
    else:
      turn = self.turn
      temp = 'has just performed'
      temp2 = ''
    move_name = ''
    try: # M is the Move object
      if M.pgn in self.disabled_tutorials:
        return None
      if M.valid_kill != None:
        valid_kill = M.valid_kill.piece
      if M.P.type == 'p' and (M.old_coor[1] == 2 or M.old_coor[1] == 7) and (M.new_y == 4 or M.new_y == 5) and pre_tutorial == False:
        move_name = 'two step'
      elif M.P.type == 'p' and (M.new_y == 8 or M.new_y == 1):
        move_name = 'promotion'
      elif M.P.type == 'p' and valid_kill[1] == 'P':
        move_name =  'en passant'
      else:
        return None
      turn = M.P.colour
      print(f'''< Info > Player: {turn} {temp} a * {move_name} * move on their {temp2} turn
      
Details: {M.P.piece} moves from {convert_letters(M.old_coor)} to {convert_letters(M.new_coor)}.
Captured piece? : {valid_kill}
''')
      
    except AttributeError: # M is a list of moves, one for king one for rook
      if M[0].pgn in self.disabled_tutorials:
        return None
      turn = M[0].P.colour
      move_name = 'castling'
      print(f'''< Info > Player: {turn} {temp} a king swap move on their {temp2}turn
      
Rook: {M[0].P.piece} moves from {convert_letters(M[0].old_coor)} to {convert_letters(M[0].new_coor)}
King: {M[1].P.piece} moves from {convert_letters(M[1].old_coor)} to {convert_letters(M[1].new_coor)}
''')
    choice = input('''Would you like to learn more about this move? 
    
> 0 Yes
> 1 Disable tutorials for this specific move
> 2 Disable all tutorials
> |3| No

''')

    if choice == '1' and move_name != 'castling':
      (self.disabled_tutorials).append(M.pgn)
    elif choice == '1' and move_name == 'castling':
      (self.disabled_tutorials).append(M[0].pgn)
    elif choice == '2':
      self.enable_pre_tutorials = False
      self.enable_tutorials = False
    elif choice == '0':
      if move_name == 'promotion':
        print(f'''\n\n>> Pawn Promotion:

When a player moves a pawn (> {M.P.piece}) to the other end of the board (in this case at row (> {M.new_y})), 
the player can 'promote' it to any type of piece they wish.
This means a player could have more than one queen.

Tactics: Most people promote their pawn to a queen as this is the most powerful piece in the game
, however, in complicated end games a knight may be more suitable 
(since a queen can not perform a knights actions).

Conditions: Must be a pawn that is on the last row.''')

      elif move_name == 'en passant':
        print(f'''\n\n>> En Passant:
  
When a player moves a pawn (> {M.valid_kill.piece}) forward two places 
and one of their opponents pawns (> {M.P.piece}) is directly and horizontally adjacent to 
the destination square of the moved pawn, this allows the opponent to capture it en passant (in passing).
The opponent does this by moving their pawn to the square that the players pawn had skipped over (to square > {M.new_coor}).
  
Tactics: This means that a player can not skip past their opponents pawn without being vulnerable to attack.

Conditions: This move must be made immediately after a player has moved a pawn forward two places.''')

      elif move_name == 'two step':
        print(f'''\n\n>> Two-step pawn move:

When a players pawn (> {M.P.piece}) has not been moved (is on their home row > {M.old_coor[1]}), 
this means that they can move it foward two places instead of one if they choose to do so.

Tactics: This helps the player to control the centre of the board, 
and allows them to move pieces that can not jump over the pawns (like rooks and bishops).

Conditions: Pawn must be on its home row and 
there must not be any piece in the first or second square up from the home row.''')

      elif move_name == 'castling':
        print(f'''\n\n>> Castling (king swap):

A unique move that invloves moving a players king (> {M[0].P.piece}) and rook (> {M[1].P.piece}) at the same time.
Once in every game, a player can perform a king swap where the players king moves two places to 
the left or right and the chosen rook is moves to the square the king skipped over.

Tactics: This helps protect a player's king by moving it closer to a corner 
behind a set of pawns (if they haven't been moved yet). 
It also moves their rook closer to the centre of the row, 
making it more useful instead of it being stuck behind a set of pawns.

Conditions: Can only be performed once per game for each player.
The players king must not be in check.
Any of the squares that the king moves over (including the one it is on) 
must have no pieces and must not be covered by an opponents piece.''')

      input('\n\nPress Enter to continue with game\n')

  def next_turn(self):
    if self.turn == 'W':
      self.turn = 'B'
    elif self.turn == 'B':
      self.turn = 'W'

  def get_next_turn(self):
    if self.turn == 'W':
      return 'B'
    elif self.turn == 'B':
      return 'W'

  def find_type_pieces(self, type):
    pieces = []
    for P in self.Pieces:
      if P.type == type:
          pieces.append(P)
    return pieces

  def find_piece(self, piece):
    for P in self.Pieces:
      if P.piece == piece:
        return P
    print('piece not found')

  def find_square(self, coor):
    for S in self.board:
      if [S.x, S.y] == coor:
        return (self.board).index(S)

  def __update_square(self, S, P, value, emoji):
    if P != False: 
      S.Piece = P
    if value != False: 
      S.value = value
    if emoji != False: 
      S.emoji = emoji

  def get_direction(self, colour):
    if colour == self.human_player:
      return self.direction
    else:
      return - self.direction

  def __remove_piece(self, piece): # Removes Piece object from list of Piece objects and the Square object it is on
    for P in self.Pieces:
      if P == piece:
        self.Pieces.remove(P)
        self.taken_pieces.append(P.piece)
        break
    for S in self.board:
      if S.Piece == piece:
        S.Piece = None

  # def board_as_a_list(self):
  #   board_list = []
  #   for S in self.board:
  #     board_list.append([S.x, S.y, S.value])
  #   return board_list

  def move_castle_moves(self, pgn, execute):
    # Error handling for castling moves
    if self.turn == 'W':
      castles = self.white_castles
    elif self.turn == 'B':
      castles = self.black_castles
    try:
      if execute:
        self.move_piece(castles[0].P, castles[0].new_x, castles[0].new_y, pgn)
        self.move_piece(castles[1].P, castles[1].new_x, castles[1].new_y, pgn)
        self.tutorial(castles, False)
      else:
        temp = castles[0].P
        return castles
    except AttributeError:
      for arr in castles:
        if execute :
          if arr[0].pgn == pgn:
            self.move_piece(arr[0].P, arr[0].new_x, arr[0].new_y, pgn)
            self.move_piece(arr[1].P, arr[1].new_x, arr[1].new_y, pgn)
            self.tutorial(arr, False)
            return None
        else: 
          return arr
  
  def __find_squares_inbetween(self, king, attacker):
    # Finds Squares between the king and the attacker
    Squares = []
    x_dir=1 
    y_dir=1 
    if king.old_x < attacker.old_x:
      x_dir=-1 
    if king.old_y < attacker.old_y: 
      y_dir=-1 
    if attacker.type == 'b' or attacker.type == 'q':
      for z in range(abs(attacker.old_x - king.old_x)):
        Squares.append(self.find_square([attacker.old_x + z*x_dir, attacker.old_y+ z*y_dir]))
    if attacker.type == 'r' or attacker.type == 'q':
      if attacker.old_x == king.old_x:
        for y in range(abs(attacker.old_y - king.old_y)):
          Squares.append(self.find_square([attacker.old_x, attacker.old_y+ y*y_dir]))
      elif attacker.old_y == king.old_y:
        for x in range(abs(attacker.old_x - king.old_x)):
          Squares.append(self.find_square([attacker.old_x +x*x_dir, attacker.old_y]))
    return Squares

  def end_game(self):
    self.print_board()
    if self.in_check == False:
      print(f'\n\n < Player: {self.human_player} has forfeited >')
    else:
      check_mated = (self.in_check).valid_kill.colour
      print(f'\n\n< King: {check_mated} in check mate >\n')
    print('\n\n Game Ended')
    input()
    
  def __game_in_check(self, v_m):
    # returns the Move object which has a piece attacking a king
    for M in v_m:
      if M.valid_kill != None:
        if M.valid_kill.type == 'k':
          return M
    return False
        
  def __en_passant(self,P):
    # Generates a ghost piece behind a pawn that moved two places which can be captured by En Passant
    if P.colour == 'W':
      ghost_piece = Piece(P.old_x, 3, P.piece[0] + 'P' + P.piece[2])
      ind = self.find_square([P.old_x, 3])
    else:
      ghost_piece = Piece(P.old_x, 6, P.piece[0] + 'P' + P.piece[2])
      ind = self.find_square([P.old_x, 6])
    ghost_piece.value = 0
    (self.Pieces).append( ghost_piece )
    self.board[ind].Piece = ghost_piece
    self.board[ind].value =' Px'
    
  def __promote(self, P):
    print('\n< Promotion >')
    new_type = self.promotion_type
    if P.colour == 'W' and new_type == None:
      new_type = input(f'''
Pawn {P.piece} can be pormoted to one of the following
> ♕ Queen (q)
> ♖ Rook (r)
> ♗ Bishop (b)
> ♘ Knight / Horse (h)

Enter the type of peice you would like to promote {P.piece} to
(q, r, b or h): ''')
      if new_type not in ['q', 'r', 'b', 'h']:
        print('/nPlease try again, enter a valid option/n')
        self.promote(P)
    elif new_type == None:
      new_type = 'q'
    num = 0
    for p in self.find_type_pieces(new_type):
      if p.number > num:
        num = p.number + 1
    self.__remove_piece(P)
    new_P = Piece(P.old_x, P.old_y, P.piece[0] + new_type + str(num))
    (self.Pieces).append(new_P)
    ind = self.find_square([P.old_x, P.old_y])
    self.board[ind].Piece = new_P
    self.promotion_type = None
    return new_P

  def __add_PGN(self, pgn):
    if self.turn == 'W':
      self.pgn += str(self.move_num) + '. '
      self.move_num += 1
    self.pgn += pgn + ' '

  def print_board(self, state=' Before '):
    length = len(self.board)
    valid_pieces = self.valid_pieces
    for i in range(19):
      print('-', end='')
    print(state,end='')
    for i in range(19):
      print('-', end='')
    print('\n')
    for y in range(8,0, -1):
      print(f"|{y}", end='  ')
      for x in range(1,9):
        if y == 1:
          S = self.board[x-1]
          if S.Piece in valid_pieces:
            print(f"\033[32m{S.emoji+S.value}", end=' ')
          else:
            print(f"\033[0m{S.emoji+S.value}", end=' ')
        else:
          S = self.board[length + x-9]
          if S.Piece in valid_pieces:
            print(f"\033[32m{S.emoji+S.value}", end=' ')
          else:
            print(f"\033[0m{S.emoji+S.value}", end=' ')
      length -= 8
      print('\033[0m|\n')
    print('     ', end='')
    for k in LETTERS:
      print(k, end='    ')
    print('\n', end='')
    for i in range(45):
      print('-', end='')
    print('\n{ Taken Pieces: ', end='')
    if self.taken_pieces == []:
      print('None taken ', end='')
    for p in self.taken_pieces:
      print(p, end=', ')
    print('}\n')

  def move_piece(self, piece, move_x, move_y, pgn=''):
    enemy = None
    ind = self.find_square([move_x, move_y])
    ind2 = self.find_square([piece.old_x, piece.old_y])
    if piece.colour != (self.board[ind]).value[0]:
      enemy = (self.board[ind]).Piece
      if (self.board[ind]).value != 'xxx' :
        self.__remove_piece( self.find_piece( (self.board[ind]).Piece.piece) ) 

      if (self.board[ind]).value[1] == 'P':
        ind3 = self.find_square([move_x, piece.old_y ]) 
        self.Pieces.remove((self.find_piece( (self.board[ind3]).Piece.piece)))
        self.__update_square(self.board[ind3], None, 'xxx', 'x')
        (self.board[ind2]).emoji = 'x'

      for P in self.Pieces: # Enpassant
        if P.type == 'P' and P.colour == self.turn:
          print('> Removed : ', P.piece)
          ind4 = self.find_square([P.old_x, P.old_y])
          self.__update_square((self.board[ind4]), None, 'xxx', 'x')
          (self.Pieces).remove(P)

      if piece.type == 'p' :
        if abs( piece.old_y - move_y) == 2 :
          self.__en_passant(piece)
        elif move_y == 8 or move_y == 1:
          piece.promoted = True
          piece = self.__promote(piece)

      self.__update_square((self.board[ind]), piece, piece.piece, piece.emoji)
      self.__update_square((self.board[ind2]), None, 'xxx', 'x')

      self.previous_move = Move(piece, [move_x, move_y], enemy)
      self.move_history.append(self.previous_move)
      
      piece.old_y = move_y 
      piece.old_x =  move_x
      piece.y = move_y
      piece.x =  move_x
      piece.moved = True
      self.__add_PGN(pgn)
      print(f'\n>> Moved : {piece.piece} to {convert_letters([piece.x, piece.y])} ( PGN: {pgn} )')

      self.print_board(' After ')
    return enemy
  
  def undo_move(self):
    piece = self.previous_move.P
    old_x = self.previous_move.old_coor[0]
    old_y = self.previous_move.old_coor[1]
    new_x = self.previous_move.new_x
    new_y = self.previous_move.new_y
    piece_taken = self.previous_move.valid_kill
    ind = self.find_square([old_x, old_y])
    ind2 = self.find_square([new_x, new_y])
    if piece_taken != None:
      self.__update_square((self.board[ind2]), piece_taken, piece_taken.piece, piece_taken.emoji)
      self.Pieces.append(piece_taken)
      self.taken_pieces.remove(piece_taken.piece)
    self.__update_square((self.board[ind]), piece, piece.piece, piece.emoji)
    self.__update_square((self.board[ind2]), None, 'xxx', 'x')
  
    piece.old_y = old_y
    piece.old_x = old_x
    piece.y = old_y
    piece.x = old_x
    if len(self.move_history) != 0:
      self.move_history.pop()
    if len(self.move_history) != 0:
      self.previous_move = self.move_history[-1]
      print(f'\n>> Undo : {piece.piece} to {convert_letters([piece.x, piece.y])}')
    else:
      print('\n* No more moves to undo *')
    
    self.print_board('Undo')

  def valid_moves(self):
    self.valid_white_moves = []
    self.valid_black_moves = []
    self.king_moves = []
    self.valid_pieces = []
    self.all_valid_moves = []
    valid_moves = []
    for piece in self.Pieces:
      for Y in range(1,9):
        for X in range(1,9):
          valid = False
          ind = self.find_square([X, Y])      
          if piece.colour != (self.board[ind]).value[0]:  
            enemy = (self.board[ind]).Piece
            piece.y = Y
            piece.x = X
            # if piece.type == 'r':
            #   valid = piece.valid_rook(self)
            # elif piece.type == 'b':
            #   valid = piece.valid_bishop(self)
            # elif piece.type == 'q': 
            #   valid = piece.valid_queen(self)
            # elif piece.type == 'h':
            #   valid = piece.valid_horse(self)
            # elif piece.type == 'k': 
            #   valid = piece.valid_king(self)
            # elif piece.type == 'p':
            #   valid = piece.valid_pawn(self)
            valid = piece.validate_move(self)
            if enemy != None:
              if enemy.type == 'P' and enemy.colour == piece.colour:
                valid = False
            if piece.old_x == piece.x and piece.old_y == piece.y:
              valid = False

            if valid and piece.type == 'k':
              self.king_moves.append(Move(piece, [X, Y], enemy))
            elif valid:
              move = Move(piece, [X, Y], enemy)

              pgn = ''
              if piece.type != 'p':
                if piece.type == 'h': pgn += 'N'
                else: pgn += (piece.type).upper()
              coor = convert_letters(move.new_coor)
              pgn+= coor[0].lower() + str(coor[1])
              if piece.type == 'p' and (piece.y == 8 or piece.y == 1):
                pgn += '=Q'
              move.pgn = pgn

              valid_moves.append(move) 

    self.white_castles, self.black_castles = self.valid_castle()
    self.castle_moves = self.white_castles + self.black_castles
    if len(self.castle_moves) == 1:
      self.castle_moves = self.castle_moves[0]
  
    check_Move = self.__game_in_check(valid_moves) 
    if check_Move != False:
      self.in_check = check_Move
      king = check_Move.valid_kill
      print('>> King: ', king.piece, ' in check, Attacker: ', check_Move.P.piece)
      new_v_m = []
      for k_m in self.king_moves:
        if k_m.P == king:
          for M in valid_moves:
            if ((M.new_coor != k_m.new_coor and M.P.colour != k_m.P.colour) or k_m.valid_kill == check_Move.P) and (k_m not in new_v_m):
              new_v_m.append(k_m)
            elif M.P.colour != k_m.P.colour:
              #print(f'\n* King { king.piece} can not move to {M.new_coor}. Covered by: {M.P.piece} *\n')
              pass
              
      for m in valid_moves:
        if m.P.colour != king.colour or (self.find_square(m.new_coor) in self.__find_squares_inbetween(king, check_Move.P)):
          new_v_m.append(m)
        if m.valid_kill != None:
          if m.valid_kill == check_Move.P:
            new_v_m.append(m)
            
      valid_moves = new_v_m
    else:
      for k_m in self.king_moves:
        valid_moves.append(k_m)
      self.in_check = False

    for move in valid_moves:
      self.valid_pieces.append(move.P)
      if move.P.colour == 'W':
        self.valid_white_moves.append(move)
      elif move.P.colour == 'B':
        self.valid_black_moves.append(move)
      if move.P.colour == self.turn:
        self.tutorial(move, True)
    try:
      for moves in self.castle_moves:
        if moves[0].P.colour == self.turn:
          self.tutorial(moves, True)
    except:
      if self.castle_moves[0].P.colour == self.turn:
        self.tutorial(self.castle_moves, True)

    self.all_valid_moves = valid_moves 
    if len(self.valid_white_moves) == 0 or len(self.valid_black_moves) == 0:
      self.check_mate == True
      print('NO VALID MOVES')
      self.end_game()

  def move_in_valid_moves(self, piece, colour, old_coor, new_coor):
    if colour == 'W':
      for move in self.valid_white_moves:
        if piece == move.P.type and old_coor == move.old_coor and new_coor == move.new_coor:
          return move, False
    elif colour == 'B':
      for move in self.valid_black_moves:
        if piece == move.P.type and old_coor == move.old_coor and new_coor == move.new_coor:
          return move, False

    try:
      for move in self.castle_moves:
        m = move[1]
        if piece == m.P.type and old_coor == m.old_coor and new_coor == m.new_coor:
          return move, True
    except AttributeError:
      m = self.castle_moves[1]
      if piece == m.P.type and old_coor == m.old_coor and new_coor == m.new_coor:
        return self.castle_moves, True

    print('< Error > Move not in Valid_moves')
    return False, False

  def print_valid_moves(self ,v_m):
    for m in v_m:
      print(m.P.piece, m.old_coor, m.new_coor)

  def valid_castle(self): 
    white_castles = []
    black_castles = []
    kings = self.find_type_pieces('k')
    rooks = self.find_type_pieces('r')
    for rook_piece in rooks:
      valid = True
      for k in kings:
        if k.colour == rook_piece.colour:
          king_piece = k
      if rook_piece.old_x ==1 and king_piece.old_x ==5: # queen side sawp
        pgn = 'O-O-O'
        for i in range(1,4):
          ind = self.find_square([1 + i, rook_piece.old_y])
          if self.board[ind].value != 'xxx':
            valid = False
        if valid:
          rook_piece.x = 4
          king_piece.x = 3
      elif rook_piece.old_x == 8 and king_piece.old_x ==5: # king side swap
        pgn = 'O-O'
        for i in range(1,3):
          ind = self.find_square([5+i, rook_piece.old_y])
          if self.board[ind].value != 'xxx':
            valid = False
            # print('Piece in way: ', board.board[ind].value)
        if valid:
          rook_piece.x = 6
          king_piece.x = 7
      if valid and not (rook_piece.moved or king_piece.moved):
        moves = [ Move(rook_piece, [rook_piece.x, rook_piece.old_y], None) , Move(king_piece, [king_piece.x, king_piece.old_y], None)]
        king_piece.king_swap = True
        moves[0].pgn = pgn
        moves[1].pgn = pgn
  
        if king_piece.colour == 'W':
          white_castles.append(moves)
        else:
          black_castles.append(moves)
    return white_castles, black_castles
      

global LETTERS
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def convert_letters(value):
  if len(value) == 1:
    return LETTERS.index(value) + 1
  if (value[0]) in LETTERS:
    return [LETTERS.index(value[0])+1, int(value[1]) ]
  else:
    return [LETTERS[ value[0] -1 ], int(value[1]) ]
