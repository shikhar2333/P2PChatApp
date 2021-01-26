import socket
from threading import Thread
import time
import json
import struct
import uuid

p = 307662152597849524039519709992560403259
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

def get_rand_nonce():
    rand_nonce = uuid.uuid4().bytes
    rand_nonce = int.from_bytes(rand_nonce, 'little')
    rand_nonce = str(rand_nonce % p)
    return rand_nonce
def joingroup(client_socket, GROUPS, gdecoded, username, user_groups, group_nonce):
    send(client_socket, "JOIN")
    groupname = gdecoded.split(' ')[1]
    if groupname not in group_nonce.keys():
        group_nonce[groupname] = get_rand_nonce()
    if username not in user_groups.keys():
        user_groups[username] = []
    if groupname not in GROUPS.keys():
        GROUPS[str(groupname)] = []
    if username in set(GROUPS[str(groupname)]):
        send(client_socket, "You are already added to group")
    else:
        GROUPS[str(groupname)].append(username)
        send(client_socket, "You are added to group")
        user_groups[username].append(groupname)

def listgroup(client_socket, GROUPS, gdecoded):
    send(client_socket, "LIST")
    if len(GROUPS):
        data = json.dumps(GROUPS)
        send(client_socket, data)
    else:
        send(client_socket, "Error")

def creategroup(client_socket, GROUPS, gdecoded, username, user_groups):
    groupname = gdecoded.split(' ')[1]
    send(client_socket, "CREATE")
    if groupname in GROUPS.keys():
        send(client_socket, "Error: Group already exists")
    else:    
        GROUPS[str(groupname)]=[]
        GROUPS[str(groupname)].append(username)
        if username not in user_groups.keys():
            user_groups[username] = []
        user_groups[username].append(groupname)
        send(client_socket, "Group Created")

    