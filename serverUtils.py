import os
import jwt  # pip install PyJWT

jwt_key = "yr2e7GEU6x5a9k9ratfXz32w8uBRLO"  # Could be any ASCII key


def cls():
    # nt (windows) = cls | unix = clear
    os.system('cls' if os.name == 'nt' else 'clear')


def encodeJWT(client_username):
    """
    Returns a JWT with a payload of the client's username

    :param client_username: The username of the client to be embedded into the JWT
    :return: A JWT
    """
    return jwt.encode({'username': client_username}, jwt_key, algorithm='HS256')


def decodeJWT(client_jwt):
    """
    Returns a dictionary payload if successfully decoded, otherwise None is returned

    :param client_jwt: The JWT to decode (passed in from the client)
    :return: Client payload, or None
    """
    try:
        return jwt.decode(client_jwt, jwt_key, algorithms=['HS256'])
    except jwt.DecodeError:
        return None
