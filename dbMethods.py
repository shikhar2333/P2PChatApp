from datetime import datetime
import pymysql
import time
import serverUtils as sUtils

class DBMethods:
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='password',
                                 db='chatapp', cursorclass=pymysql.cursors.DictCursor)

    @staticmethod
    def register(username, hashed_password):
        conn = DBMethods.connection
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", [username])

                if not cursor.fetchone():
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                                   (username, hashed_password))
                    conn.commit()
                    return True
                else:
                    return False
        except Exception as e:
            print("addUserToDB Error:", e)
            return False

    @staticmethod
    def login(username, hashed_password):
        conn = DBMethods.connection
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", [username])
                user = cursor.fetchone()
                if user is not None:
                    if user["password"] == hashed_password:
                        return sUtils.encodeJWT(username)

        except Exception as e:
            print("getUserFromDB Error:", e)

    @staticmethod
    def closeConnection():
        DBMethods.connection.close()

    @staticmethod
    def is_username_valid(username):
        conn = DBMethods.connection
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", [username])
                user = cursor.fetchone()
                if user is None:
                    return False
                return True
        except Exception as e:
            print("getUserFromDB Error:", e)