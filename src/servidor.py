import socket
import thread

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

def connected(con, cliente):
    print 'Connected by', cliente

    while True:
        msg = con.recv(1024)
        if not msg: break
        print cliente, msg

    print 'End session with client', cliente
    con.close()
    thread.exit()
    

def connect():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    orig = (HOST, PORT)

    tcp.bind(orig)
    tcp.listen(1)

    while True:
        con, cliente = tcp.accept()
        thread.start_new_thread(connected, tuple([con, cliente]))

    tcp.close()

if __name__ == "__main__":
    connect()