from socket_server.server import Server

if __name__ == '__main__':
    print('socket server is starting...')

    server = Server(host='0.0.0.0', port=65432, timeout=30)
    server.start()

    pass
