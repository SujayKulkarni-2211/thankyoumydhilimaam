import sqlite3

def init_db():
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()




def add_image(filename, name, message):
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO images (filename, name, message)
        VALUES (?, ?, ?)
    ''', (filename, name, message))
    conn.commit()
    conn.close()

def get_images():
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename, name, message FROM images')
    images = cursor.fetchall()
    conn.close()
    return images

import sqlite3

def delete_entry_by_id(db_path, table_name, entry_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute('BEGIN TRANSACTION;')
        
        # Delete the entry with the specific ID
        cursor.execute(f"""
            DELETE FROM {table_name}
            WHERE id = ?
        """, (entry_id,))
        
        # Commit the transaction
        conn.commit()
        print(f"Deleted entry with ID: {entry_id}.")
    
    except sqlite3.Error as e:
        # Rollback in case of an error
        conn.rollback()
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        conn.close()

# Usage
# delete_entry_by_id('images.db', 'images', 13)

