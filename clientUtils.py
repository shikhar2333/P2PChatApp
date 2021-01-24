import hashlib

def get_hashed_password(username, password):
    return hashlib.md5((username + password).encode()).hexdigest()

def send_login_command(socket, p_user, p_pass):
    login_cmd = "login " + p_user + " " + get_hashed_password(p_user, p_pass)
    socket.send(bytes(login_cmd, "UTF-8"))
    try:
        data = socket.recv(1024)
        if data:
            if data.decode() == "<ACCEPTED>":
                return "<ACCEPTED>"
            elif data.decode() == "<FAILED LOGIN ATTEMPTS>":
                return "<FAILED LOGIN ATTEMPTS>"
            else:
                return False
    except Exception:
        return False


def send_register_command(socket, p_user, p_pass):
    register_cmd = "register " + p_user + " " + get_hashed_password(p_user, p_pass)
    socket.send(bytes(register_cmd, "UTF-8"))

    try:
        data = socket.recv(1024)
        if data:
            return "<ACCEPTED>" if data.decode() == "<ACCEPTED>" else False
    except Exception:
        return False
