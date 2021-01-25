# import socket
import time
from sys import argv
import clientUtils as cUtils
import gui
from random import randint
from getpass import getpass
from pyDes import *
from methods import *

SERVER_PORT = 5003
p = 307662152597849524039519709992560403259
g = 174657925435224939675987965147035581892
initial_value_bits = "\0\0\0\0\0\0\0\0"
class LoginGUI:
    def __init__(self):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
        self.client_socket.connect((argv[1] if len(argv) > 1 else "localhost", SERVER_PORT))  # Connect to the socket
        self.username = None
        self.roll = None
        self.comm_server_socket = None
        self.comm_server_port = None
        self.message = None
        self.p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secret_number = None
        self.recv_public_key = None
        def login_or_register(should_login):
            print('Enter Name:')
            user = str(input())
            print('Enter Roll No:')
            roll_no = int(input())
            self.roll = roll_no
            password = getpass(prompt="Enter Password: ")
            if not user or not password:
                print('Please fill in all required fields!')
            else:
                server_login_cb(self, should_login, user, roll_no, password)

        def login_on_click():
            login_or_register(True)

        def register_on_click():
            login_or_register(False)
        
        while True:
            print('Press 1 to login')
            print('Press 2 to register')
            val = str(input())
            if val=='1':
                login_on_click()

            elif val=='2':
                register_on_click()
            else:
                pass
    
    def sendb(self, sock, data):
        length = len(data)
        sock.sendall(struct.pack('!I', length))
        sock.sendall(data)

    def decrypt(self, encrypted_message):
        shared_secret_key = pow(self.recv_public_key, self.secret_number, p)
        print("Secret number: ", self.secret_number)
        print("Shared secret key: ", shared_secret_key)
        key = shared_secret_key.to_bytes(24, byteorder='little')
        k = triple_des(key, CBC, initial_value_bits, pad=None, padmode=PAD_PKCS5)
        decrypted_message = k.decrypt(encrypted_message, padmode=PAD_PKCS5)
        return decrypted_message

    def encrypt(self):
        shared_secret_key = pow(self.recv_public_key, self.secret_number, p)
        print("Secret number: ", self.secret_number)
        print("Shared secret key: ", shared_secret_key)
        key = shared_secret_key.to_bytes(24, byteorder='little')
        k = triple_des(key, CBC, initial_value_bits, pad=None, padmode=PAD_PKCS5)
        encrypted_message = k.encrypt(self.message)
        return encrypted_message
        
    def start_comm_server(self, max_clients):
        self.comm_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.comm_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.comm_server_socket.bind(("", self.comm_server_port))
        self.comm_server_socket.listen(max_clients)
    
    def listen_to_peers(self):
        peer_socket, peer_addr = self.comm_server_socket.accept()
        with peer_socket:
            print("Connected by: ", peer_addr)
            while True:
                # data = peer_socket.recv(1024)
                data = receive(peer_socket)
                if not data:
                    break
                # print("Is received key none: ", self.recv_public_key)
                if not self.recv_public_key:
                    self.recv_public_key = int.from_bytes(data, byteorder='little')
                    print("Received key: ", self.recv_public_key)
                    self.secret_number =  randint(p - 1000, p)
                    public_key = pow(g, self.secret_number, p)
                    print("Public key to send: ", public_key)
                    public_key = public_key.to_bytes(24, byteorder='little')
                    # peer_socket.send(public_key)
                    self.sendb(peer_socket, public_key)
                else:
                    decrypted_message = self.decrypt(data)
                    decrypted_message = decrypted_message.decode("UTF-8")
                    final_message = decrypted_message.split(" ", 2)[2]
                    print("Decrypted message: ", final_message)
                    self.recv_public_key = None
                    break                
        # print("Exited While")

    def recv_from_comm_server(self, comm_server_port):
        self.p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_socket.connect(("localhost", comm_server_port))
        self.secret_number = randint(p -1000, p)
        public_key = pow(g, self.secret_number, p)
        print("Public key to send: ", public_key)
        public_key = public_key.to_bytes(24, byteorder='little')
        # self.p2p_socket.send(public_key)
        self.sendb(self.p2p_socket, public_key)
        while True:
            # data = self.p2p_socket.recv(1024)
            data = receive(self.p2p_socket)
            if not data:
                break
            try:
                self.recv_public_key = int.from_bytes(data, byteorder='little')
                print("Received key: ", self.recv_public_key)
                break
            except Exception as e:
                print(e)
                break
        
        encrypted_message = self.encrypt()
        print("Encrypted message: ", encrypted_message)
        # self.p2p_socket.send(encrypted_message)
        self.sendb(self.p2p_socket, encrypted_message)
        # print("Is socket closing")
        self.recv_public_key = None
        self.p2p_socket.close()

def server_login_cb(client_object, should_login, p_user, p_roll, p_pass):

    client_socket = client_object.client_socket
    if should_login:
        p_user = p_user + str(p_roll)
        log_attempt = cUtils.send_login_command(client_socket, p_user, p_pass)
        print("Login Status: %s" % log_attempt)
        print("-"*80)
        if log_attempt == "<ACCEPTED>":
            client_object.username = p_user
            gui.start_gui(client_object)
        else:
            print("Invalid username or password.")
    else:
        p_user = p_user + str(p_roll)
        log_attempt = cUtils.send_register_command(client_socket, p_user, p_pass)
        print("Login Status: %s" % log_attempt)
        print("-"*80)
        if log_attempt == "<ACCEPTED>":
            client_object.username = p_user
            gui.start_gui(client_object)
        else:
            print("That username is already in use.")

def main():
    print('Starting ChatApp Client')
    LoginGUI()



if __name__ == '__main__':
    main()