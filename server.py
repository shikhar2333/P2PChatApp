import re
from threading import Thread
import time
from dbMethods import DBMethods
import serverUtils as sUtils
import gensafeprime
import group
from methods import *
import uuid

CONNECTED_CLIENTS = []
MAX_CLIENTS = 10
GROUPS = {}
USER_GROUPS = {}
GROUP_NONCE = {}

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

def sendb(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def get_client_socket(username):
    for client_dic in CONNECTED_CLIENTS:
        for dict_username, dict_socket in client_dic.items():
            if dict_username == username:
                return dict_socket

def send_group_nonce(u_name):
    socket_send = get_client_socket(u_name)
    if u_name not in USER_GROUPS.keys():
        send(socket_send, "Error: User is not part of any group")
        return
    groups = USER_GROUPS[u_name]
    for gname in groups:
        gnonce = GROUP_NONCE[gname]
        send(socket_send, "Random Nonce " + gname + " "+ gnonce)


def send_group_message(uname, gname, encrypted_message):
    gnonce = bytes(uname + " " + GROUP_NONCE[gname] + " ", "UTF-8")
    print("Group message: ", encrypted_message)
    for user in GROUPS[gname]:
        if user == uname:
            continue
        socket_send = get_client_socket(user)
        sendb(socket_send, gnonce + encrypted_message)

def get_jwt(req):
    if req[0] == 'login':
        return DBMethods.login(req[1], req[2])
    elif req[0] == 'register':
        if DBMethods.register(req[1], req[2]):
            return DBMethods.login(req[1], req[2])
    elif req[0] == '/verify':
        if sUtils.decodeJWT(req[1]) is not None:
            return req[1]    

def check_error(data):
    try:
        data = data.decode()
        return True
    except UnicodeDecodeError:
        # print("Unicode error")
        return False
def listenToClient(client_socket, client_address):
    while True:
        # try:
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
                        # try:
                        data = receive(client_socket)
                        f = check_error(data)
                        if f and data:
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
                                joingroup(client_socket, GROUPS, gdecoded, username, USER_GROUPS, GROUP_NONCE)
                            elif decoded == "LIST\n":
                                gdata = receive(client_socket)
                                gdecoded = gdata.decode()
                                listgroup(client_socket, GROUPS, gdecoded)
                            elif decoded == "CREATE":
                                gdata = receive(client_socket)
                                gdecoded = gdata.decode()
                                groupname = gdecoded.split(" ")[1]
                                GROUP_NONCE[groupname] = get_rand_nonce()
                                creategroup(client_socket, GROUPS, gdecoded, username, USER_GROUPS)
                            elif "Port" in decoded:  
                                u_name = decoded.split(" ")[-1]
                                dict_socket = get_client_socket(u_name)
                                send(dict_socket, decoded)
                            elif "GROUP" in decoded:
                                u_name = decoded.split(" ")[1]
                                send_group_nonce(u_name)
                            elif "Error" in decoded:
                                # send_group_message(username, decoded, b'')
                                pass
                            else:
                                pass
                        elif not f:
                            space_idx = data.index(b' ')
                            gname = data[:space_idx].decode()
                            encrypted_message = data[space_idx + 1:]
                            send_group_message(username, gname, encrypted_message)
                        # except Exception as e_:
                        #     print("Client disconnected:", e_)
                        #     CONNECTED_CLIENTS.remove(client_dic)
                        #     client_socket.close()
                        #     return False
                else:
                    send(client_socket, "<DECLINED>")
            else:
                send(client_socket, "<DECLINED>")
        else:
            print("Client disconnected")
            client_socket.close()
            return False

        # except Exception as e:
        #     print(e)
        #     print("Client disconnected")
        #     client_socket.close()
        #     return False

if __name__ == '__main__':
    main()