from classes import *
import pickle

def store_board(B):
  ## Stores board into file
  file_name = B.file_name
  new_file = open(f'{file_name}.txt', 'w')
  new_file.close()
  with open(f'{file_name}.txt', 'wb') as file:
    pickle.dump(B, file)
    new_file.close()
  
def load_board(file_name):
  ## loads board from file
  try:
    file = open(f'{file_name}.txt', 'rb')
    B = pickle.load(file)
    file.close()
    return B
  except:
    print('< Error > File not found')
    return None
  
def convert_pgn(B, pgn):
  pgn = pgn.split(' ')
  letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
  moves = []
  next_player = 'W'
  for i in pgn:
    if pgn.index(i) %3 != 0:
      prom = ''
      i = i.replace('x', '')
      i = i.replace('N', 'H')
      i = i.replace('+', '')
      i = i.replace('#', '')
      piece = ''
      if 'O' in i:
        piece = i
       # print(piece)
        moves.append(piece)
      else:
        if '=' in i:
          s = i.split('=')
          prom = str(s[1])
          i = s[0]
        piece+= i[-2:].upper() # E6
        i = i.replace(i[-2:], '')
        if i == '':
          piece = 'px'+piece #pxE6
        else:
          if i in letters:
            piece = 'p' + i[0].upper() +piece 
          else: piece = i[0].lower() + 'x'+piece
        #print(piece+prom)
        moves.append(piece+prom)
      if next_player =='W': next_player = 'B'
      else: next_player = 'W'
  return moves

def user_move(board, v_m, c_m):
  loop = True
  while loop:
    try:
      moves = []
      count = 0
      print('>> Possible moves for Player: ', board.turn)
      for m in v_m:
        if m.P.piece not in moves:
          moves.append(m.P.piece)
          print(f'> {count} {m.P.emoji} {m.P.piece} at {convert_letters(m.old_coor)}')
          count+=1
      new_count = count
      if len(c_m) == 0:
        print('<> * No king swap moves avaliable *')
      else: 
        try:
          for C in c_m:
            print(f'<> {new_count} {C[1].P.emoji} {C[1].P.piece} swaps with {C[0].P.emoji} {C[0].P.piece}')
            new_count+=1
        except:
          print(f'<> {new_count} {c_m[0][1].P.emoji} {c_m[0][1].P.piece} swaps with {c_m[0][0].P.emoji} {c_m[0][0].P.piece}')

      temp = int(input('\nEnter number from selection: '))
      if temp > count -1 :
        if new_count!= count:
          _move = c_m[int(temp - count)][1]
        else:
          _move = c_m[int(temp - count)][1]
      else:
        _move =  moves[temp]
        moves = []
        count = 0
        for m in v_m:
          if m.P.piece == _move:
            moves.append(m)
            if m.valid_kill != None:
              print(f'<> {count} {m.P.emoji} {m.P.piece} moves to {convert_letters(m.new_coor)} * Captures: {m.valid_kill.emoji} {m.valid_kill.piece} *')
            else: 
              print(f'> {count} {m.P.emoji} {m.P.piece} moves to {convert_letters(m.new_coor)}')
            count+=1
        _move = moves[int(input('\nEnter number from selection: '))]
      loop = False
        
    except Exception as e:
      print(f'* Error code : {e} *')
      print('* Invalid input, try again *\n')
  
  move, castle_move = board.move_in_valid_moves(_move.P.type, _move.P.colour, _move.old_coor, _move.new_coor)
  if castle_move:
    for M in move:
      board.move_piece(M.P, M.new_coor[0], M.new_coor[1], M.pgn)
    board.tutorial(move, False)
  else:
    board.move_piece(move.P, move.new_coor[0], move.new_coor[1], move.pgn)
    board.tutorial(move, False)

def login():
  choice = input('''
Welcome ! 

|0| > New game (just press Enter)
1 > Load game from file
2 > Load game from PGN

Enter a number to begin game :  ''')
  if choice == '1':
    B = load_board(input('Enter file name: '))
    if B == None:
      login()
    game(B)
  elif choice == '2': PGN_game(create_board_set())
  else: game(None)
  
def game(board):
  if board == None:
    board = create_board_set()
    board.turn = 'W'
    board.file_name = input('Enter a new file name for this game: ')
    if board.file_name == '' or board.file_name == 'piece_validation' or board.file_name == 'classes' or board.file_name == 'main':
      game(None)
    print(f'File name : {board.file_name}\n')
    choice = input('Is this a game against another human? (y or |n|): ')
    if choice == 'y':
      board.human_game = True
  board.valid_moves()
  board.enable_pre_tutorials, board.enable_tutorials = True, True
  while True:
    print(f"\n< < Player: {board.turn}'s turn > >\n")
    
    board.print_board()
    if board.turn == board.human_player:
      user_move(board, board.valid_white_moves, board.white_castles)
    else:
      if board.human_game:
        user_move(board, board.valid_black_moves, board.black_castles)
      else:
        evaluate(board)

    
    store_board(board)
    choice = input(f'''* Game saved to : {board.file_name} *
< It is now player: {board.get_next_turn()}'s turn >

|0| > Next turn
1 > Return to login page
2 > Print PGN of current game
3 > Change game against human to: {not board.human_game}
4 > Undo previous move
-1 > Forfeit

''')
    if choice == '1':
      login()
    elif choice == '-1':
      board.end_game()
      login()
    elif choice == '2':
      input(f'\nPGN: {board.pgn}\n')
    elif choice == '3':
      board.human_game = not board.human_game
    elif choice == '4':
      loop = True
      while loop:
        board.undo_move()
        board.next_turn()
        board.valid_moves()
        undo_more = input(f"""* Previous move has been undone *
 
Player: {board.get_next_turn()}'s' turn
Would you like to undo another move? (|y| or n): """)
        if undo_more == 'n':
          loop = False
    
    board.next_turn()
    board.valid_moves()
    

def evaluate(B):
  highest_score = -999
  for opponent_m in B.valid_white_moves:
    if opponent_m.valid_kill != None:
      for comp_move in B.valid_black_moves:
        if comp_move.valid_kill != opponent_m.P:
          comp_move.material_loss = opponent_m.valid_kill.value
    
  for m in B.valid_black_moves:
    S = B.board[ B.find_square(m.new_coor) ]
    square_value = S.get_square_value('B', m.P.type)
    m.piece_table_gain = square_value
    m.evaluation_score = m.piece_table_gain + m.material_gain - (m.material_loss*2)
    print(f'{m.P.piece} Total: {m.evaluation_score} ({m.piece_table_gain}, {m.material_gain}, {m.material_loss*2}) { m.new_coor}')

  for m in B.valid_black_moves:
    if m.evaluation_score > highest_score:
      highest_score = m.evaluation_score
      best_move = m

  B.move_piece(best_move.P, best_move.new_coor[0], best_move.new_coor[1], best_move.pgn)
  B.tutorial(best_move, False)

def AI_random_move(board, v_m):
    import random
    ind = random.choice(v_m.valid_black_moves)
    board.print_board(v_m.all_valid_moves)
    board.move_piece(ind.Piece, ind.new_coor[0], ind.new_coor[1])
    board.print_board(v_m.all_valid_moves)

def PGN_game(board):
  continue_game = 'n'
  board.file_name = 'PGN_game'
  pgn = input('\nEnter PGN: ')
  choice = input(f'Approximate length of PGN = {round(len(pgn) / 12)+1} pairs of moves\nWould you like to skip to the last move made from the PGN? (y or |n|): ')
  if choice == 'y':
    skip = True
    board.enable_pre_tutorials = False
    board.enable_tutorials = False
  else:
    skip = False
  pgn_moves = convert_pgn(board, pgn)
  board.valid_moves()
  for pgn in pgn_moves:
    if not skip:
      print(f"< Player: {board.turn}'s turn >")
    if pgn == 'O-O' or pgn == 'O-O-O':
      print(board.castle_moves)
      
      board.move_castle_moves(pgn, True)
    else:
      if pgn[-1].isalpha():
        print(pgn[:4])
        board.promotion_type = pgn[-1].lower()
        pgn = pgn[:4] 
      coor = pgn[2:]
      if coor.isalnum():
        for M in board.all_valid_moves:
          if M.P.colour == board.turn and M.P.type == pgn[0] and M.new_coor == convert_letters(coor):
            if pgn[0] == 'p' and pgn[1] != 'x':
              if convert_letters(pgn[1]) == M.old_coor[0]:
                board.move_piece( M.P, M.new_coor[0], M.new_coor[1], pgn)
                board.tutorial(M, False)
            else:
              board.move_piece( M.P, M.new_coor[0], M.new_coor[1], pgn)
              board.tutorial(M, False)
    board.next_turn()
    board.valid_moves()
    if not skip:
      board.print_board()
      continue_game = input(f'Next turn: Player {board.turn}\nWould you like to continue the game from here? (y or |n|): ')
    if continue_game == 'y':
      print('File saved as "PGN_game"')
      game(board)
  board.print_board()
  choice = input(f'''\n* End of PGN *
Next turn: Player {board.turn}
Would you like to continue the game? (y or |n|): ''')
  if choice == 'y' :
    game(board)
  else:
    login()

def create_board_set():
  Pieces = []
  Squares = []
  BOARD_LIST = [[1, 1, 'Wr1'], [2, 1, 'Wh1'], [3, 1, 'Wb1'], [4, 1, 'Wq1'], [5, 1, 'Wk1'], [6, 1, 'Wb2'], [7, 1, 'Wh2'], [8, 1, 'Wr2'], [1, 2, 'Wp1'], [2, 2, 'Wp2'], [3, 2, 'Wp3'], [4, 2, 'Wp4'], [5, 2, 'Wp5'], [6, 2, 'Wp6'], [7, 2, 'Wp7'], [8, 2, 'Wp8'], [1, 3, 'xxx'], [2, 3, 'xxx'], [3, 3, 'xxx'], [4, 3, 'xxx'], [5, 3, 'xxx'], [6, 3, 'xxx'], [7, 3, 'xxx'], [8, 3, 'xxx'], [1, 4, 'xxx'], [2, 4, 'xxx'], [3, 4, 'xxx'], [4, 4, 'xxx'], [5, 4, 'xxx'], [6, 4, 'xxx'], [7, 4, 'xxx'], [8, 4, 'xxx'], [1, 5, 'xxx'], [2, 5, 'xxx'], [3, 5, 'xxx'], [4, 5, 'xxx'], [5, 5, 'xxx'], [6, 5, 'xxx'], [7, 5, 'xxx'], [8, 5, 'xxx'], [1, 6, 'xxx'], [2, 6, 'xxx'], [3, 6, 'xxx'], [4, 6, 'xxx'], [5, 6, 'xxx'], [6, 6, 'xxx'], [7, 6, 'xxx'], [8, 6, 'xxx'], [1, 7, 'Bp1'], [2, 7, 'Bp2'], [3, 7, 'Bp3'], [4, 7, 'Bp4'], [5, 7, 'Bp5'], [6, 7, 'Bp6'], [7, 7, 'Bp7'], [8, 7, 'Bp8'], [1, 8, 'Br1'], [2, 8, 'Bh1'], [3, 8, 'Bb1'], [4, 8, 'Bq1'], [5, 8, 'Bk1'], [6, 8, 'Bb2'], [7, 8, 'Bh2'], [8, 8, 'Br2']]
  s_value, reversed_s_value = get_piece_square_table()
  for square in BOARD_LIST:
    ind = BOARD_LIST.index(square)
    values = {}
    reversed_values = {}
    for type, table in s_value.items():
      values.update({type: table[ind]})
    for type, table in reversed_s_value.items():
      reversed_values.update({type: table[ind]})
    both_values = [values, reversed_values]
    if square[2] =='xxx':
      Squares.append(Square(square[0], square[1], square[2], None, both_values))
    else:
      type = square[2][1] 
      if type == 'p':
        piece = Pawn(square[0], square[1], square[2])
      elif type == 'r':
        piece = Rook(square[0], square[1], square[2])
      elif type == 'b':
        piece = Bishop(square[0], square[1], square[2])
      elif type == 'q':
        piece = Queen(square[0], square[1], square[2])
      elif type == 'k':
        piece = King(square[0], square[1], square[2])
      elif type== 'h':
        piece = Horse(square[0], square[1], square[2])
      piece.__init__(square[0], square[1], square[2])
      Pieces.append(piece)
      Squares.append(Square(square[0], square[1], square[2], piece, both_values))
  return Board(Squares, Pieces)

def get_piece_square_table():
    return {
'p': [0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0],
'h': [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50],
'b': [-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-10,-10,-10,-10,-10,-20],
'r': [  0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0],
'q': [-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20],
'k':[-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20] }, {'p': [0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0],
 'h': [-50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50],
  'b': [-20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20],
'r': [0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0],
  'q':[-20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20],
  'k': [ 20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30] }

print('    < Jamie Grey - Computing NEA >')
login()
