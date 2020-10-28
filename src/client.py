import socket

def connect():
    HOST = '127.0.0.1'    
    PORT = 5000          

    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest = (HOST, PORT)
        tcp.connect(dest)
        print 'Press CTRL+X to EXIT\n'
    except:
        print 'The server is down.'
        return

    msg = raw_input()
    while msg <> '\x18':
        if(msg == ':q'):
            return
        tcp.send (msg)
        msg = raw_input()

    tcp.close()
    return

if __name__ == "__main__":
    connect()