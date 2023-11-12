class Piece(object):
  def __init__(self, x, y, piece):
    self.y = y
    self.x = x
    self.colour = piece[0]
    if piece[0] == 'W':
      self.opposite_colour = 'B'
    else:
      self.opposite_colour = 'W'
    self.piece = piece[0] +piece[1] + str(piece[2])
    self.type = piece[1]
    self.number = int(piece[2])
    self.old_y = y
    self.old_x = x
    self.moved = False
    self.emoji = None
    w_emojis = {'p':'♙', 'h':'♘', 'b':'♗', 'r':'♖', 'q':'♕', 'k':'♔'}
    b_emojis = {'p':'♟', 'h':'♞', 'b':'♝', 'r':'♜', 'q':'♛', 'k':'♚'}
    values = {'p':10, 'h':30, 'b':30, 'r':50, 'q':90, 'k':100} 
    for key, num in values.items():
        if self.type == key:
          self.value = num
            # if self.colour == 'W':
            #   self.value = num
            # else:
            #   self.value = -num
    if self.colour == 'W':
      for key, emoji in w_emojis.items():
        if self.type == key:
            self.emoji = emoji
    else:
      for key, emoji in b_emojis.items():
        if self.type == key:
            self.emoji = emoji
    # Special cases
    if self.type == 'p':
      self.en_passant = False
      self.promote = False
      self.two_step = False
    if self.type == 'k':
      self.king_swap = False
      self.in_check = False
      self.in_checkmate = False
      
  def killed(self):
    self.value = 0
    self.x = -1
    self.y = -1

  def validate_move(self, board):
    pass # Polymorphism 


class Pawn(Piece): # Inheriting from the Piece class
  def validate_move(self, board): 
    d = board.get_direction(str(self.colour))
    ind = board.find_square([self.old_x, self.old_y])
    if self.y == 0 or self.y == 9:  
      return False #### To prevent looping around the board
  
    if (self.x == self.old_x):
      if (self.moved == False) and ((board.board[ind + 8 * d]).value == 'xxx') and ((board.board[ind + 16 * d]).value == 'xxx') :  ## Pawn hasn't been moved and head on kill prevention
        if (self.old_y+ 2*d == self.y):
          self.two_step = True
        return (self.old_y+ 2*d == self.y) or (self.old_y+ d == self.y) ## Double or single step
    
      else: ## Single step
        return ( (self.old_y+ d == self.y) and (board.board[ind + 8 * d]).value == 'xxx')
    elif self.old_y+ d == self.y: # killing 
      if self.old_x != 1: # if not on left side of board
        left_kill = (board.board[ind + 7 * d])
        if (left_kill.x == self.x and left_kill.y == self.y) and (left_kill.value[0] != self.colour and left_kill.value != 'xxx') : 
          return True
      if self.old_x !=8: # if not on right side of board
        right_kill = (board.board[ind + 9 * d])
        if (right_kill.x == self.x and right_kill.y == self.y) and (right_kill.value[0] != self.colour and right_kill.value != 'xxx'):
          return True
      return False
    return False

class Rook(Piece):
  def validate_move(self, board):
    Valid = True
    d=1
    if self.old_y == self.y: # Moving horizontally
      if self.old_x > self.x: # If moving left
        d=-1
      for i in range(1, abs(self.old_x-self.x) +1):
        ind = board.find_square([self.old_x +i*d , self.y])
  
        if board.board[ind].value[0] == self.colour: # Piece is blocking final square
          Valid = False
          #print('item in the way: ', board.board[ind].value)
          break
        elif (board.board[ind].value[0] == self.opposite_colour): # Enemy self
          if (i == abs(self.old_x-self.x)  ): # If its the destination square
            break
          else: # Piece is blocking final square
            return False 
            
    elif self.old_x == self.x: # Moving vertically
        if self.old_y > self.y:
          d=-1 # If moving down
        for i in range( 1, abs(self.old_y-self.y) +1):
          ind = board.find_square([self.x , self.old_y +i*d])
          
          if board.board[ind].value[0] == self.colour:
            Valid = False
            #print('item in the way: ', board.board[ind].value)
            break
          elif (board.board[ind].value[0] == self.opposite_colour) :
            if (i == abs(self.old_y-self.y)  ): # last self 
              # print('kill')
              break
            else:
              return False
            #print('item in the way: ', board.board[ind].value)
              
    else: # Not a rook move
      Valid = False
    return Valid

class Bishop(Piece):
  def validate_move(self, board):
    Valid = True
    if (abs(self.x - self.old_x) != abs(self.y - self.old_y)):
      return False
    x=1
    y=1
    if self.x < self.old_x:
      x=-1 
    if self.y < self.old_y: 
      y=-1 
    for i in range( 1, abs(self.x - self.old_x) +1 ):
      ind = board.find_square([self.old_x + i*x , self.old_y + i*y])
  
      if board.board[ind].value[0] == self.colour:
        Valid = False
        break
      elif (board.board[ind].value[0] == self.opposite_colour):
        if (i == abs(self.x - self.old_x)): # last self
          break
        else: # Piece in way
          return False
  
    return Valid

class Queen(Piece):
  def validate_move(self, board):
    # rook and bishop combined
    if self.old_x == self.x or self.old_y == self.y:
      valid = Rook.validate_move(self, board)
    else:
      valid = Bishop.validate_move(self, board)
    return valid

class Horse(Piece):
  def validate_move(self, board):
    ox = self.old_x
    oy = self.old_y
    px = self.x
    py = self.y
  ## All possible L shapes
    if py == oy +2 and px == ox + 1:
      return True
    if py == oy -2 and px == ox + 1:
      return True
    if py == oy -2 and px == ox -1:
      return True
    if py == oy +2 and px == ox -1:
      return True
    if py == oy +1 and px == ox + 2:
      return True
    if py == oy -1 and px == ox + 2:
      return True
    if py == oy -1 and px == ox -2:
      return True
    if py == oy +1 and px == ox -2:
      return True
    return False

class King(Piece):
  def validate_move(self, board):
    if ( (abs(self.old_x - self.x) == 1 and abs(self.old_y-self.y) == 1) or
         (abs(self.old_x - self.x) == 1 and abs(self.old_y-self.y) == 0) or 
         (abs(self.old_x - self.x) == 0 and abs(self.old_y-self.y) == 1) ):
      return True
    return False
