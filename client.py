import socket
import threading
from server import SERVER_ADDRESS, SERVER_PORT, AUTH_OK, CHOICE_OK, DISCONNECT


def authorization(server):
    for i in range(3):
        msg = server.recv(1024)
        msg = msg.decode('utf-8')
        if msg == AUTH_OK:
            print('\nAuth success!\n')
            return True
        username = input(msg)
        print(username)
        server.send(username.encode('utf-8'))
    print('\nAuthorization failed!\n')
    return False


def choose_client(server):
    while True:
        msg = server.recv(1024).decode('utf-8')
        print('Choose fun: ', msg)
        if msg == CHOICE_OK:
            break

        response = input(msg).encode('utf-8')
        server.send(response)


def receive(server):
    while True:
        msg = server.recv(1024).decode('utf-8')
        if msg == DISCONNECT:
            print('Disconnected from server!')
            break


if __name__ == '__main__':
    server_socket = socket.socket()
    try:
        server_socket.connect((SERVER_ADDRESS, SERVER_PORT))

        msg = server_socket.recv(1024)
        msg = msg.decode('utf-8')
        print('Inbox: {0}'.format(msg))

        if authorization(server_socket):
            choose_client(server_socket)

            recv_thread = threading.Thread(
                target=receive, args=(server_socket,))
            recv_thread.daemon = True
            recv_thread.start()

            while True:
                out_msg = input('Your msg: ')
                server_socket.send(out_msg.encode('utf-8'))
                if out_msg == 'q':
                    break

        server_socket.close()

    except KeyboardInterrupt:
        server_socket.close()
        print("\nHow rude of you!\n")

    except Exception as e:
        server_socket.close()
        print('\nException: {0}'.format(e))
