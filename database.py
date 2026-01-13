import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",   # change if needed
        database="urcw_chatbot",
        auth_plugin="mysql_native_password"
    )
