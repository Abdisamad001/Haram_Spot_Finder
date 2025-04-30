import sqlite3
import os
from datetime import datetime

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
    
    # spots table
    c.execute('''
        CREATE TABLE IF NOT EXISTS spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            count INTEGER,
            type TEXT,
            date TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
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

# Save detected spots
def save_spot(username, filename, count, type_):
  
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute(
        "INSERT INTO spots (username, filename, count, type, date) VALUES (?, ?, ?, ?, ?)",
        (username, filename, count, type_, date)
    )
    
    conn.commit()
    conn.close()

# Get user's spot history
def get_spots(username):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM spots WHERE username=? ORDER BY date DESC", (username,))
    results = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return results