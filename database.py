import sqlite3
import hashlib
import pandas as pd

DB_PATH = "database/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            movie_id INTEGER,
            rating INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                      (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
                  (username, hash_password(password)))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None



def save_rating(user_id, movie_id, rating):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if user_id is None:
        raise ValueError("User ID cannot be None when saving a rating.")
    
    try:
        cursor.execute("""
            INSERT INTO user_ratings (user_id, movie_id, rating)
            VALUES (?, ?, ?)
        """, (user_id, movie_id, rating))
        conn.commit()
    except Exception as e:
        print(f"Error saving rating: {e}")
    finally:
        conn.close()

def get_user_ratings(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT movie_id, rating, timestamp FROM user_ratings WHERE user_id = ?", 
                          conn, params=(user_id,))
    conn.close()
    return df

def get_rating_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_ratings WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

init_db()