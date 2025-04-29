import sqlite3
import os

# Define the database path
DB_PATH = os.path.join("database", "users.db")  

# database directory
os.makedirs("database", exist_ok=True)

def create_users_table():
    conn = sqlite3.connect(DB_PATH)  
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Add user 
def add_user(username, password):
    conn = sqlite3.connect(DB_PATH) 
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Verify the user
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)  
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None