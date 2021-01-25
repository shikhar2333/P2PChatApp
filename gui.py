import os
from threading import Thread
# import socket
from sys import argv
import re
import select  
import sys
import random
from dbMethods import DBMethods
from methods import *

SERVER_PORT = 5003
def start_gui(client_object):
    client_socket = client_object.client_socket
    def on_closing():
        client_socket.close()
        sys.exit(1)

    while True:
        sockets_list = [sys.stdin, client_socket]
        read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])
        for socks in read_sockets:  
            if socks == client_socket:
                data = receive(client_socket)
                data = data.decode('UTF-8')
                client_server_port = client_object.comm_server_port
                start_server = "start server"
                if start_server in data:
                    while not client_server_port:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        comm_port = random.randint(5004, 10000)
                        result = sock.connect_ex(('localhost', comm_port))
                        if result:
                            client_object.comm_server_port = comm_port
                            client_object.start_comm_server(9)
                            break
                    username = data.split(" ")[-1]
                    print("Communication server port: ", client_object.comm_server_port)
                    Thread(target=client_object.listen_to_peers).start()
                    port = "Port "+str(client_object.comm_server_port)+" "+username
                    send(client_socket, port)
                elif "Port" in data:
                    comm_port = int(data.split(" ")[1])
                    client_object.recv_from_comm_server(comm_port)
                elif data == "JOIN":
                    data = receive(client_socket)
                    decode = data.decode()
                    print(decode)
                elif data == "CREATE":
                    data = receive(client_socket)
                    decode = data.decode()
                    print(decode)
                elif data == "LIST":
                    data = receive(client_socket)
                    if data:
                        data = data.decode('utf-8')
                        if data == "Error":
                            print('No Group Exists')
                        else:
                            data_loaded = json.loads(data)
                            for gname,user in data_loaded.items():
                                print(gname,len(user))
            else:  
                message = sys.stdin.readline()  
                req_sent = message.split(" ")
                send(client_socket, req_sent[0])
                if len(req_sent)>=3 and req_sent[0] == "SEND":
                    sent_usr = req_sent[1]
                    client_object.message = message
                    if DBMethods.is_username_valid(sent_usr):
                        start_server = "Tell " + sent_usr + " to start server for " + client_object.username
                        send(client_socket, start_server)
                    else:
                        print("Username doesn't exist")
                elif req_sent[0] == "JOIN":
                    send(client_socket, message)
                elif req_sent[0] == "LIST\n":
                    send(client_socket, message)
                elif req_sent[0] == "CREATE":
                    send(client_socket, message)
                else:
                    pass
