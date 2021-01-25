import os
from threading import Thread
import socket
from sys import argv
import re
import select  
import sys
import random
from dbMethods import DBMethods

SERVER_PORT = 5003
# COMM_SERVER_PORT = 5004

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
                data = client_socket.recv(1024)
                data = data.decode('UTF-8')
                # request = data.split(' ', 3)
                # command = request[3].split(' ',2)
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
                    client_socket.send(bytes(("Port "+str(client_object.comm_server_port)+" "+username), "UTF-8"))
                elif "Port" in data:
                    comm_port = int(data.split(" ")[1])
                    # Thread(target=client_object.recv_from_comm_server, args=[comm_port]).start()
                    client_object.recv_from_comm_server(comm_port)
                else:
                    pass
            else:  
                message = sys.stdin.readline()  
                client_object.message = message
                split_message = message.split(" ")
                if len(split_message) >= 3:
                    is_send = split_message[0]
                    if is_send == "SEND":
                        sent_usr = split_message[1]
                        if DBMethods.is_username_valid(sent_usr):
                            start_server = "Tell " + sent_usr + " to start server for " + client_object.username
                            client_socket.send(bytes((start_server), "UTF-8"))
                        else:
                            print("Username doesn't exist")
                    
                # sys.stdout.write("You to " + sent_usr +" :")
                # msg = message.split(' ',2)[2]
                # sys.stdout.write(msg)  
                # sys.stdout.flush()
