from flask_login import UserMixin
from app import mysql
from werkzeug.security import check_password_hash


class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    @staticmethod
    def authenticate(username, password):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE username=%s AND password=%s", (username, password))
        data = cur.fetchone()
        cur.close()
        if data:
            return User(*data)
        return None

    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE id=%s", (user_id,))
        data = cur.fetchone()
        cur.close()
        if data:
            return User(*data)
        return None
