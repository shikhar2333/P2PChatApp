import re
from socket import *
from threading import Thread
import time
from dbMethods import DBMethods
import serverUtils as sUtils


CONNECTED_CLIENTS = []
MAX_CLIENTS = 10
arrayOfStoredMessages = []
GROUPS = []

class messageObject:
    def __init__(self, sender, recipient, message):
        self.sender = sender
        self.recipient = recipient
        self.message = message

    def getSender(self):
        return self.sender

    def getRecipient(self):
        return self.recipient

    def getMessage(self):
        return self.message

def main():
    global server_socket

    try:
        print('Starting ChatApp Server')

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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
    while 1:
        try:
            data = client_socket.recv(1024)
            
            if data is not None:
                request = re.split(" +", data.decode())
                if request is not None:
                    jwt = get_jwt(request)
                    if jwt is not None:
                        decoded_jwt = sUtils.decodeJWT(jwt)
                        print('Login success')
                        username = decoded_jwt.get('username')
                        client_dic = {username: client_socket}
                        CONNECTED_CLIENTS.append(client_dic)
                        client_socket.send(bytes("<ACCEPTED>", "UTF-8"))
                        # sendUserLists()
                        for x in arrayOfStoredMessages:
                            if x.getRecipient() == username:
                                client_socket.send(bytes("SEND " + x.getMessage(), "UTF-8"))
                                arrayOfStoredMessages.remove(x)

                        while True:
                            try:
                                data = client_socket.recv(1024)
                                if data:
                                    decoded = data.decode()
                                    request = re.split(" +", decoded)
                                    if "start" in decoded:
                                        u_name = decoded.split(" ")[1]
                                        dict_socket = get_client_socket(u_name)
                                        dict_socket.send(bytes((decoded), "UTF-8"))
                                    elif "Port" in decoded:  
                                        u_name = decoded.split(" ")[-1]
                                        dict_socket = get_client_socket(u_name)
                                        dict_socket.send(bytes((decoded), "UTF-8"))
                                    # elif request[0] == 'SEND':
                                    #     hasSent = False
                                    #     # start a communincation server on Client B
                                        
                                    #     for client_dict in CONNECTED_CLIENTS:
                                    #         for dict_username, dict_socket in client_dict.items():
                                    #             if dict_username == request[1]:
                                    #                 hasSent = True
                                    #                 # dict_socket.send(bytes(("Message from " + username + ": " + decoded),"UTF-8"))
                                    #                 dict_socket.send(bytes(("Start server " + username),"UTF-8"))

                                    #     if not hasSent:
                                    #         storedMessage = messageObject(sender=username, recipient=request[1],
                                    #                                       message=" ".join(request).split(" ", 1)[1])
                                    #         arrayOfStoredMessages.append(storedMessage)
                                    #         print("storedMessage: " + storedMessage.getMessage())
                                    elif request[0] == '/something':
                                        dict_socket.send(bytes("I did something", "UTF-8"))
                                    
                                    elif request[0] == 'JOIN':
                                        if request[1] not in GROUPS.keys():
                                            GROUPS[str(request[1])]=[]
                                            dict_socket.send(bytes("Group Created", "UTF-8"))
                                        
                                        GROUPS[str(request[1])].append(username)
                                        dict_socket.send(bytes("You are added to group", "UTF-8"))


                                    elif request[0] == 'CREATE':
                                        if request[1] in GROUPS.keys():
                                            dict_socket.send(bytes("Group already exists", "UTF-8"))
                                        else:    
                                            GROUPS[str(request[1])]=[]
                                            dict_socket.send(bytes("Group Created", "UTF-8"))
                                    
                                    elif request[0] == 'LIST':
                                        if request[1] in GROUPS.keys():
                                            for i in GROUPS[request[1]]:
                                                print(i)
                                        else:
                                            dict_socket.send(bytes("No group exists with this name", "UTF-8"))
                                        
                                    else:
                                        for client_dict in CONNECTED_CLIENTS:
                                            for dict_username, dict_socket in client_dict.items():
                                                dict_socket.send(bytes((username + ": " + decoded), "UTF-8"))
                                else:
                                    raise error()
                            except Exception as e_:
                                print("Client disconnected:", e_)
                                CONNECTED_CLIENTS.remove(client_dic)
                                client_socket.close()
                                # sendUserLists()
                                return False
                    else:
                        client_socket.send(bytes("<DECLINED>", "UTF-8"))    
                else:
                    client_socket.send(bytes("<DECLINED>", "UTF-8"))
            else:
                print("Client disconnected")
                client_socket.close()
                return False

        except Exception as e:
            print(e)
            print("Client disconnected")
            client_socket.close()
            return False

def sendUserLists():
    usernameList = []
    for client_dict in CONNECTED_CLIENTS:
        for dict_username, dict_socket in client_dict.items():
            usernameList.append(dict_username)
    for client_dict in CONNECTED_CLIENTS:
        for dict_username, dict_socket in client_dict.items():
            dict_socket.send(bytes(("/userlist " + " ".join(usernameList)), "UTF-8"))

if __name__ == '__main__':
    main()