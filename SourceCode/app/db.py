import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # isi kalau kamu set password
        database="kasir_app",
        cursorclass=pymysql.cursors.DictCursor
    )