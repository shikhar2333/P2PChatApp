import socket
from threading import Thread
import time
import json
import struct


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(bytes(data, "UTF-8"))

def receive(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

def joingroup(client_socket,GROUPS,gdecoded,username):
    send(client_socket,"JOIN")
    # client_socket.sendall(bytes("JOIN", "UTF-8"))
    groupname = gdecoded.split(' ')[1]
    if groupname not in GROUPS.keys():
        GROUPS[str(groupname)]=[]
    
    if username in set(GROUPS[str(groupname)]):
        send(client_socket, "You are already added to group")
    else:
        GROUPS[str(groupname)].append(username)
        send(client_socket, "You are added to group")

def listgroup(client_socket,GROUPS,gdecoded):
    send(client_socket,"LIST")
    if len(GROUPS):
        data = json.dumps(GROUPS)
        send(client_socket,data)
    else:
        send(client_socket,"Error")

def creategroup(client_socket,GROUPS,gdecoded, username):
    groupname = gdecoded.split(' ')[1]
    send(client_socket,"CREATE")
    if groupname in GROUPS.keys():
        send(client_socket,"Error: Group already exists")
    else:    
        GROUPS[str(groupname)]=[]
        GROUPS[str(groupname)].append(username)
        send(client_socket,"Group Created")
