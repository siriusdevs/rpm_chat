"""Server for chat app, made for my beloved students."""

import socket
import threading
import time
from typing import List

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345
AUTH_OK = 'AUTH_OK'
CHOICE_OK = 'CHOICE_OK'
DISCONNECT = 'DISCONNECT'


def authorization(client: socket, users: List[str]):
    """Asks client for his name three times.

    Args:
        client: socket - the socket to send messages.
        users: List[str] - list of names already in use.
    Returns:
        str - name if auth ok, empty string if not.
    """
    for _ in range(3):
        client.send('Type you name: '.encode('utf-8'))
        msg = client.recv(1024)
        username = msg.decode('utf-8')
        print('username: ', username)
        if username and username not in users:
            client.send(AUTH_OK.encode('utf-8'))
            return username
    return ''


def new_client(client_socket: socket, username: str, recipient_socket: socket):
    """Main logic of workin with client. Finishes when receives 'q' from client.

    Args:
        client_socket: socket - the socket to receive messages.
        recipient_socket: socket - the socket to send messages.
        username: str - name of the client.
    """
    while True:
        msg = client_socket.recv(1024)
        msg = msg.decode('utf-8')
        if msg == 'q':
            break
        out_msg = 'From {1}: {0}'.format(msg, username)
        if recipient_socket:
            recipient_socket.send(out_msg.encode('utf-8'))
        else:
            print('No one hears {0}'.format(username))


def choose_client(client: socket, usernames: List[str]):
    """Choosing a client to chat with. Finishes when receives valid index.

    Args:
        client: socket - the socket to work with.
        usernames: List[str] - names that are already in use.
    Returns:
        str - name of the client to chat with.
    """
    time.sleep(1)
    if not len(usernames):
        client.send(CHOICE_OK.encode('utf-8'))
        return None
    indexes = range(1, len(usernames) + 1)
    iter_names = [(ind, name) for ind, name in zip(indexes, usernames)]
    while True:
        msg = 'Choose client to chat with: '
        msg += ' '.join(['{0[0]}. {0[1]}'.format(pair) for pair in iter_names])
        client.send(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        try:
            index = int(response) - 1
        except ValueError as error:
            print('[Choose_fun]: received invalid index', error)
        else:
            if 0 <= index < len(usernames):
                client.send(CHOICE_OK.encode('utf-8'))
                return usernames[index]
            else:
                last_index = len(usernames) - 1
                msg = '[Choose_fun]: got index {0} while {1} available'.format(recipient, last_index)
                print(msg)


if __name__ == '__main__':
    server_socket = socket.socket()
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    users = {}

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print('Connected {0[0]}:{0[1]}'.format(addr))

            msg = 'Connection success!'
            client_socket.send(msg.encode('utf-8'))

            username = authorization(client_socket, list(users.keys()))

            if username:
                recipient = choose_client(client_socket, list(users.keys()))
                users[username] = client_socket
                recipient_socket = users[recipient] if recipient else None
                args = client_socket, username, recipient_socket
                user_thread = threading.Thread(target=new_client, args=args)
                user_thread.start()

    except KeyboardInterrupt:
        server_socket.close()
        print('\nServer shut down.\n')

    except Exception as e:
        server_socket.close()
        print('\nException: {0}'.format(e))
