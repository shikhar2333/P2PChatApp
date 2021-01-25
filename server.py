import re
from threading import Thread
import time
from dbMethods import DBMethods
import serverUtils as sUtils
import gensafeprime
import group
from methods import *

def get_generator(p):
    one = 1
    gen = 0
    while one == 1:
        gen = randint(2, p-2)
        one = pow(gen, 2, p)
    return gen

CONNECTED_CLIENTS = []
MAX_CLIENTS = 10
GROUPS = {}

def main():
    global server_socket

    try:
        print('Starting ChatApp Server')

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", 5003))
        server_socket.listen(MAX_CLIENTS)

        while True:
            print("Waiting for " + ("a" if len(CONNECTED_CLIENTS) < 1 else "another") + " connection...")

            client_socket = None
            try:
                client_socket, client_address = server_socket.accept()
                Thread(target=listenToClient, args=[client_socket, client_address]).start()

            except KeyboardInterrupt:
                if client_socket:
                    client_socket.close()
                break
            print("Connection acquired: {0}".format(str(client_address)))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        exit(-1)
    finally:
        server_socket.close()
        print('PythonChat Server cleanup and exit...done!')
        exit(0)

def get_client_socket(username):
    for client_dic in CONNECTED_CLIENTS:
        for dict_username, dict_socket in client_dic.items():
            if dict_username == username:
                return dict_socket


def get_jwt(req):
    if req[0] == 'login':
        return DBMethods.login(req[1], req[2])
    elif req[0] == 'register':
        if DBMethods.register(req[1], req[2]):
            return DBMethods.login(req[1], req[2])
    elif req[0] == '/verify':
        if sUtils.decodeJWT(req[1]) is not None:
            return req[1]    

def listenToClient(client_socket, client_address):
    while True:
        try:
            data = receive(client_socket)
            if data:
                request = re.split(" +", data.decode())
                if request:
                    jwt = get_jwt(request)
                    if jwt:
                        decoded_jwt = sUtils.decodeJWT(jwt)
                        print('Login success')
                        username = decoded_jwt.get('username')
                        client_dic = {username: client_socket}
                        CONNECTED_CLIENTS.append(client_dic)
                        send(client_socket, "<ACCEPTED>")
                        while True:
                            try:
                                data = receive(client_socket)
                                if data:
                                    decoded = data.decode()
                                    if decoded == "SEND":
                                        dict_socket = get_client_socket(username)
                                        decoded = receive(dict_socket).decode()
                                        if "start" in decoded:
                                            u_name = decoded.split(" ")[1]
                                            dict_socket = get_client_socket(u_name)
                                            send(dict_socket, decoded)
                                    elif decoded == "JOIN":
                                        gdata = receive(client_socket)
                                        gdecoded = gdata.decode()
                                        joingroup(client_socket, GROUPS, gdecoded, username)
                                    elif decoded == "LIST\n":
                                        gdata = receive(client_socket)
                                        gdecoded = gdata.decode()
                                        listgroup(client_socket, GROUPS, gdecoded)
                                    elif decoded == "CREATE":
                                        gdata = receive(client_socket)
                                        gdecoded = gdata.decode()
                                        creategroup(client_socket, GROUPS, gdecoded, username)
                                    elif "Port" in decoded:  
                                        u_name = decoded.split(" ")[-1]
                                        dict_socket = get_client_socket(u_name)
                                        send(dict_socket, decoded)
                                    else:
                                        pass
                                else:
                                    raise error()
                            except Exception as e_:
                                print("Client disconnected:", e_)
                                CONNECTED_CLIENTS.remove(client_dic)
                                client_socket.close()
                                return False
                    else:
                        send(client_socket, "<DECLINED>")
                else:
                    send(client_socket, "<DECLINED>")
            else:
                print("Client disconnected")
                client_socket.close()
                return False

        except Exception as e:
            print(e)
            print("Client disconnected")
            client_socket.close()
            return False

if __name__ == '__main__':
    main()