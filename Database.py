import sqlite3
from datetime import datetime
import hashlib

def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Create admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert sample admin (username: admin, password: admin123)
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    try:
        cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', 
                      ('admin', admin_password))
    except sqlite3.IntegrityError:
        pass
    
    # Insert sample students
    sample_students = [
        ('prajyot11', 'password123', 'Prajyot Main', '11'),
        ('riya10', 'password123', 'Riya Sharma', '10'),
        ('amit12', 'password123', 'Amit Kumar', '12'),
        ('priya11', 'password123', 'Priya Singh', '11'),
        ('rohan10', 'password123', 'Rohan Verma', '10')
    ]
    
    for username, password, name, class_ in sample_students:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('INSERT INTO students (username, password, name, class) VALUES (?, ?, ?, ?)',
                          (username, hashed_password, name, class_))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn
