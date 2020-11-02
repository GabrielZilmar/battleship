import socket
import threading
import struct
import random
import json
import util

def create_position():
    horizontal = random.randint(0, 1)
    return (horizontal, 1 - horizontal)

def position_boat(position, ship, ship_id, board):
    horizontal, vertical = position
    fit = False

    while not fit:
        row = random.randint(0, len(board) - 1)
        col = random.randint(0, len(board[0]) - 1)
    
        for s in range(ship['size']):
            r = row + s * vertical
            c = col + s * horizontal
            if (r >= len(board) or c >= len(board[0]) or board[r][c] != '-'):
                break
            elif s == ship['size'] - 1:
                fit = True

        if fit:
            for s in range(ship['size']):
                r = row + s * vertical
                c = col + s * horizontal
                board[r][c] = ship['symbol'] + str(ship_id)

def create_board(ships):
    board = [['-' for _ in range(10)] for _ in range(10)]

    for index, ship in ships.items():
        for i in range(ship['quantity']):
            position_boat(
                create_position(),
                ships[index],
                (i + 1),
                board
            )
    return board

def set_game(con):
    ships = {
        'A': {'symbol': 'a', 'name': 'Aircraft Carrier', 'size': 5, 'quantity': 1},
        'T': {'symbol': 't', 'name': 'Tanker', 'size': 4, 'quantity': 2},
        'D': {'symbol': 'd', 'name': 'Destroyers', 'size': 3, 'quantity': 3},
        'S': {'symbol': 's', 'name': 'Submarine', 'size': 2, 'quantity': 4}
    }

    enemy = create_board(ships)

    data_to_send = json.dumps(ships).encode()

    con.send(struct.pack('!I', 10))
    con.send(struct.pack('!I', 10))
    con.send(struct.pack('!I', len(data_to_send)))
    con.send(data_to_send)

    length, = struct.unpack('!I', con.recv(4))

    player = json.loads(con.recv(length).decode())

    boards = {'player': player, 'enemy': enemy}

    start(con, boards, 10, ships, 10)

def randomize():
    i = random.randint(0, 10 - 1)
    j = random.randint(0, 10 - 1)
    return (i, j)

def move(board, size, row, column):
    res = None

    if(row < 0 or row >= size or column < 0 or column >= size or board[row][column] == '*' or board[row][column] == 'x'):
        res = util.MoveStatus.INVALID
    elif board[row][column] == '-':
        res = util.MoveStatus.MISS
        board[row][column] = '*'
    else:
        res = util.MoveStatus.HIT
        board[row][column] = 'x'

    return res

def start(con, boards, size, ships, quantity):
    turn = util.Turn.PLAYER
    winner = util.Winner.NONE
    hits = {'player': 0, 'enemy': 0}

    hits_needed = 0
    for _, ship in ships.items():
        hits_needed += ship['quantity'] * ship['size']

    while winner == util.Winner.NONE:
        i = j = -1
        direction = step = None
        
        while turn == util.Turn.PLAYER:
            length, = struct.unpack('!I', con.recv(4))    
            i, j = json.loads(con.recv(length).decode()).values()
            res = move(boards['enemy'], size, i, j)

            con.send(struct.pack('!I', res.value))
            if res == util.MoveStatus.HIT:
                hits['player'] += 1
            elif res == util.MoveStatus.MISS:
                turn = util.Turn.ENEMY
            else:
                continue

            data = json.dumps(hits).encode()
            con.send(struct.pack('!I', len(data)))
            con.send(data)

            con.send(struct.pack('!I', turn.value))
            if hits['player'] == hits_needed:
                winner = util.Winner.PLAYER
                con.send(struct.pack('!I', winner.value))
                break
            else:
                con.send(struct.pack('!I', winner.value))
            
            i = -1
            j = -1

        while turn == util.Turn.ENEMY:
                if i != -1 and j != -1:
                    if not direction and not step:
                        direction = randomize()
                        step = random.randint(-1, 0) | 1

                    horizontal, vertical = direction
                    i = i + step * vertical
                    j = j + step * horizontal

                    print(step)
                    print((horizontal, vertical))
                    print((i, j))
                else:
                    i, j = randomize()
                    
                res = move(boards['player'], 10, i, j)
                
                data = json.dumps({'row': i, 'col': j}).encode()
                con.send(struct.pack('!I', len(data)))
                con.send(data)

                con.send(struct.pack('!I', res.value))
                if res == util.MoveStatus.HIT:
                    hits['enemy'] += 1
                elif res == util.MoveStatus.MISS:
                    turn = util.Turn.PLAYER
                    i = j = -1
                    direction = step = None
                else:
                    direction = randomize()
                    step = random.randint(-1, 0) | 1

                    if i < 0:
                        i = 0
                    elif i >= 10:
                        i = 10 - 1

                    if j < 0:
                        j = 0
                    elif j >= 10:
                        j = 10 - 1
                    continue
                    
                data = json.dumps(hits).encode()
                con.send(struct.pack('!I', len(data)))
                con.send(data)

                con.send(struct.pack('!I', turn.value))
                if hits['enemy'] == hits_needed:
                    winner = util.Winner.ENEMY
                    con.send(struct.pack('!I', winner.value))
                    break
                else:
                    con.send(struct.pack('!I', winner.value))

    con.close()

def start_server():
    HOST = util.get_address()
    PORT = int(input('Port: '))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))

    server.listen(5)

    print('Server stating...')
    print('Host: {}\t Port: {}'.format(HOST, PORT))

    while True:
        con, client = server.accept()
        print('{} connected.Preparing new game...'.format(client[0]))
        threading.Thread(target=set_game, args=(con, )).start()

if __name__ == '__main__':
    start_server()