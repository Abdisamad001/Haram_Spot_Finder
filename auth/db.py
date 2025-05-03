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
    
    # Check db_update
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exists = c.fetchone() is not None
    
    if users_exists:
        
        try:
           
            c.execute("SELECT contact FROM users LIMIT 1")
        except sqlite3.OperationalError:
            
            try:
                c.execute("ALTER TABLE users ADD COLUMN contact TEXT")
            except sqlite3.OperationalError:
                pass
                
        try:
            # name column
            c.execute("SELECT name FROM users LIMIT 1")
        except sqlite3.OperationalError:
            # Add name column 
            try:
                c.execute("ALTER TABLE users ADD COLUMN name TEXT")
            except sqlite3.OperationalError:
                pass
    else:
        # Create sers table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                name TEXT,
                contact TEXT
            )
        ''')
    
    # Space table
    c.execute('''
        CREATE TABLE IF NOT EXISTS space (
            space_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            capacity INTEGER,
            availability TEXT
        )
    ''')
    
    # Gate table
    c.execute('''
        CREATE TABLE IF NOT EXISTS gate (
            gate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            status TEXT
        )
    ''')
    
    # Haram Staff table
    c.execute('''
        CREATE TABLE IF NOT EXISTS haram_staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            contact TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Admin table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            authentication TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Model table
    c.execute('''
        CREATE TABLE IF NOT EXISTS model (
            sys_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            version TEXT,
            status TEXT
        )
    ''')
    
    # Allocation table
    c.execute('''
        CREATE TABLE IF NOT EXISTS allocation (
            alloc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            space_id INTEGER,
            user_id INTEGER,
            timestamp TEXT,
            FOREIGN KEY (space_id) REFERENCES space (space_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Gate monitoring table (staff <--> gates)
    c.execute('''
        CREATE TABLE IF NOT EXISTS gate_monitoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            gate_id INTEGER,
            timestamp TEXT,
            FOREIGN KEY (staff_id) REFERENCES haram_staff (staff_id),
            FOREIGN KEY (gate_id) REFERENCES gate (gate_id)
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


# Check if contact exists
def check_contact_exists(contact):
    if not contact:
        return False
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE contact=?", (contact,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Add user 
def add_user(username, password, name=None, contact=None):
    if not username or not password:
        raise Exception("Username and password are required")
        
    conn = sqlite3.connect(DB_PATH) 
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, password, name, contact) VALUES (?, ?, ?, ?)", 
                (username, password, name, contact))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    # sqlite error handling 
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        
        ## username and contact error
        if "UNIQUE constraint failed: users.username" in str(e):
            raise Exception("Username already exists")
        elif "UNIQUE constraint failed: users.contact" in str(e):
            raise Exception("Contact already exists")
        
        else:
            raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        conn.close()
        raise Exception(f"Error adding user: {str(e)}")

# admin record
def add_admin(name, authentication, user_id):
    if not name or not authentication or not user_id:
        raise Exception("All admin fields are required")
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO admin (name, authentication, user_id) VALUES (?, ?, ?)", 
                (name, authentication, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise Exception(f"Error adding admin: {str(e)}")

# Add haram staff record
def add_staff(name, role, contact, user_id):
    if not name or not role or not contact or not user_id:
        raise Exception("All staff fields are required")
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO haram_staff (name, role, contact, user_id) VALUES (?, ?, ?, ?)", 
                (name, role, contact, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise Exception(f"Error adding staff: {str(e)}")

# Add space record
def add_space(location, capacity, availability):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO space (location, capacity, availability) VALUES (?, ?, ?)", 
              (location, capacity, availability))
    conn.commit()
    conn.close()

# Add gate record
def add_gate(name, location, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO gate (name, location, status) VALUES (?, ?, ?)", 
              (name, location, status))
    conn.commit()
    conn.close()

# Add model record
def add_model(name, version, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO model (name, version, status) VALUES (?, ?, ?)", 
              (name, version, status))
    conn.commit()
    conn.close()


# # Add allocation record
# def add_allocation(space_id, user_id):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     timestamp = datetime
#     c.execute("INSERT INTO allocation (space_id, user_id, timestamp) VALUES (?, ?, ?)", 
#               (space_id, user_id, timestamp))
#     conn.commit()
#     conn.close()


# Add allocation record
def add_allocation(space_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO allocation (space_id, user_id, timestamp) VALUES (?, ?, ?)", 
              (space_id, user_id, timestamp))
    conn.commit()
    conn.close()

# Assign staff to monitor gate
def assign_gate_to_staff(staff_id, gate_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO gate_monitoring (staff_id, gate_id, timestamp) VALUES (?, ?, ?)", 
              (staff_id, gate_id, timestamp))
    conn.commit()
    conn.close()

# Verify the user and check user type
def authenticate_user(username, password):
    if not username or not password:
        return None
        
    conn = sqlite3.connect(DB_PATH)  
    c = conn.cursor()
    
    # First check if the user exists in the users table
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user_result = c.fetchone()
    
    if not user_result:
        conn.close()
        return None
        
    user_id = user_result[0]
    
    # Check if user is an admin
    c.execute("SELECT * FROM admin WHERE user_id=?", (user_id,))
    admin_result = c.fetchone()
    
    if admin_result:
        conn.close()
        return {'id': user_id, 'username': username, 'user_type': 'admin'}
    
    # Check if user is a haram staff
    c.execute("SELECT * FROM haram_staff WHERE user_id=?", (user_id,))
    staff_result = c.fetchone()
    
    if staff_result:
        conn.close()
        return {'id': user_id, 'username': username, 'user_type': 'haram_staff'}
    
    # Regular user
    conn.close()
    return {'id': user_id, 'username': username, 'user_type': 'user'}


# Original functions
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

def get_spots(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM spots WHERE username=? ORDER BY date DESC", (username,))
    results = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return results

# Get available spaces
def get_available_spaces():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM space")
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Get all gates
def get_all_gates():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM gate")
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Get user allocations
def get_user_allocations(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT a.*, s.location, s.capacity 
            FROM allocation a
            JOIN space s ON a.space_id = s.space_id
            WHERE a.user_id=?
            ORDER BY a.timestamp DESC
        """, (user_id,))
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Get gates monitored by staff
def get_staff_gates(staff_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT g.*, gm.timestamp 
            FROM gate g
            JOIN gate_monitoring gm ON g.gate_id = gm.gate_id
            WHERE gm.staff_id=?
            ORDER BY gm.timestamp DESC
        """, (staff_id,))
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Update space availability
def update_space_availability(space_id, availability):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE space SET availability=? WHERE space_id=?", (availability, space_id))
    conn.commit()
    conn.close()

# Update gate status
def update_gate_status(gate_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gate SET status=? WHERE gate_id=?", (status, gate_id))
    conn.commit()
    conn.close()

# Get all users
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM users")
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Get all staff
def get_all_staff():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT hs.*, u.username 
            FROM haram_staff hs
            JOIN users u ON hs.user_id = u.id
        """)
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        results = []
    
    conn.close()
    return results

# Get staff by user_id
def get_staff_by_user_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM haram_staff WHERE user_id=?", (user_id,))
        result = c.fetchone()
        
        if result:
            staff_data = dict(result)
        else:
            staff_data = None
    except:
        staff_data = None
    
    conn.close()
    return staff_data