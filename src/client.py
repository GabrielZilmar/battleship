import socket
import struct
import json
import util

def show(ships, num_ships, boards, hits):
    column = 'A'
    print('Enemy Border\t\t\t\tPlayer Board')

    enemy_rows = '  '.join([str(i) for i in range(1, num_ships + 1)])
    player_rows = '   '.join([str(i) for i in range(1, num_ships + 1)])
    print('  {}\t\t  {}'.format(enemy_rows, player_rows))

    for enemy_row, player_row in zip(boards['enemy'], boards['player']):
        player_row = list(map(
            lambda x: '- ' if x == '-' else x,
            player_row
        ))
        print(column + ' ' + '  '.join(enemy_row) + '\t\t' +
              column + ' ' + '  '.join(player_row))
        column = chr(ord(column) + 1)
        

    print('The enemy has {} hit(s) out of 30'.format(hits['enemy']))
    print('You have {} hits(s) out of 30\n'.format(hits['player']))

    for _, ship in ships.items():
        print('-> {}: {}'.format(ship['symbol'], ship['name']))
    print('-> -: Invalid position')
    print('-> *: Fail')
    print('-> x: Hit\n')

def get_row(board_size):
    row = 'A'
    valid_pos = False
    while not valid_pos:
        try:
            row = (input('Choice a row (A-J): '))
            row = row.upper()

            if ord(row) < ord('A') or ord(row) >= ord('A') + board_size:
                raise Exception()

            valid_pos = True
        except Exception:
            print('Invalid. Try again.')

    return ord(row) - ord('A')

def get_column(board_size):
    column = 0
    valid_pos = False
    while not valid_pos:
        try:
            column = int(input('Choice a column (1-10): '))

            if column < 1 or column >= 1 + board_size:
                raise Exception()
            
            valid_pos = True
        except ValueError:
            print('Invalid value.')
        except Exception:
            print('Out of limit.')

    return column - 1

def get_direction():
    valid_dir = False
    while not valid_dir:
        try:
            d = input('Insert a direction (Horizontal: H, Vertical: V): ')
            d = d.upper()

            if d not in ['H', 'V']:
                raise Exception()

            valid_dir = True
        except Exception:
            print('Insert a direction (Horizontal: H, Vertical: V): ')
            
    return 1 if d == 'H' else 0

def get_coord(board_size):
    i = get_row(board_size)
    j = get_column(board_size)

    return (i, j)

def place_ship(board, board_size, ship, ship_number):
    fit = False
    positions = []
    
    while not fit:
        row, col = get_coord(board_size)
        direction = get_direction()
        
        for s in range(ship['size']):
            r = row + s * (1 - direction)
            c = col + s * direction

            if (r >= len(board) or c >= len(board[0]) or
                board[r][c] != '-'):
                
                break
            elif s == ship['size'] - 1:
                fit = True
                positions = [(row + (1 - direction) * i,
                              col + direction * i)
                             for i in range(ship['size'])]

        if not fit:
            print('Invalid position!')

    for i, j in positions:
        board[i][j] = ship['symbol'] + str(ship_number)

def new_board(ships, num_ships, board_size):
    enemy_board = [['-' for _ in range(board_size)]
                   for _ in range(board_size)]
    player_board = [['-' for _ in range(board_size)]
                    for _ in range(board_size)]

    for key, ship in ships.items():
        for i in range(ship['quantity']):
            place_ship(player_board, board_size, ships[key], (i + 1))
            show(
                ships, num_ships,
                {'player': player_board, 'enemy': enemy_board},
                {'player': 0, 'enemy': 0}
            )
    
    return player_board

def set_game():
    host = input('Insert the host: ')
    port = int(input('Insert the port: '))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    board_size, = struct.unpack('!I', client.recv(4))
    num_ships, = struct.unpack('!I', client.recv(4))
    
    length, = struct.unpack('!I', client.recv(4))
    ships = json.loads(client.recv(length).decode())

    enemy_board = [['-' for _ in range(board_size)]
                   for _ in range(board_size)]

    player_board = new_board(ships, num_ships, board_size)

    boards = {'player': player_board, 'enemy': enemy_board}

    data = json.dumps(boards['player']).encode()
    client.send(struct.pack('!I', len(data)))
    client.send(data)
    
    print('\n\nGame started!')
    start(client, ships, num_ships, boards, board_size)

def start(conn, ships, num_ships, boards, board_size):
    turn = util.Turn.PLAYER
    winner = util.Winner.NONE
        
    while winner == util.Winner.NONE:
        if turn == util.Turn.PLAYER:
            i, j = get_coord(board_size)
            data = json.dumps({'row': i, 'col': j}).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)

            data, = struct.unpack('!I', conn.recv(4))
            res = util.MoveStatus(data)

            print('Your result: {}'.format(
                util.MoveResult[res]
            ))

            if res == util.MoveStatus.HIT:
                boards['enemy'][i][j] = 'x'
            elif res == util.MoveStatus.MISS:
                boards['enemy'][i][j] = '*'

        else:
            length, = struct.unpack('!I', conn.recv(4))
            i, j = json.loads(conn.recv(length).decode()).values()
            
            data, = struct.unpack('!I', conn.recv(4))
            res = util.MoveStatus(data)

            print('Enemy result: {}'.format(
                util.MoveResult[res]
            ))
            
            if res == util.MoveStatus.HIT:
                boards['player'][i][j] = 'x '
            elif res == util.MoveStatus.MISS:
                boards['player'][i][j] = '* '

        if res != util.MoveStatus.INVALID:
            length, = struct.unpack('!I', conn.recv(4))
            hits = json.loads(conn.recv(length).decode())

            input('Enter to continue...')
            show(ships, num_ships, boards, hits)

            data, = struct.unpack('!I', conn.recv(4))
            turn = util.Turn(data)
            
            data, = struct.unpack('!I', conn.recv(4))
            winner = util.Winner(data)

    if winner == util.Winner.PLAYER:
        print('Win')
    else:
        print('Lose')
        
if __name__ == '__main__':
    set_game()