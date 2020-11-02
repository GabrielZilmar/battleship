import socket
import enum

Turn = enum.Enum('Turn', 'ENEMY PLAYER')
MoveStatus = enum.Enum('MoveStatus', 'HIT MISS INVALID')
MoveResult = {
    MoveStatus.HIT: 'Hit',
    MoveStatus.MISS: 'Erro',
    MoveStatus.INVALID: 'Movimento Inválido',
}

Winner = enum.Enum('Winner', 'NONE SERVER PLAYER')

def get_address():
    try:
        address = socket.gethostbyname(socket.gethostname())
    except:
        address = None
    finally:
        if not address or address.startswith("127."):
            HOST = "8.8.8.8"
            PORT = 80
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((HOST, PORT))
            address = sock.getsockname()[0]
            sock.close()
            return address
