import sqlite3


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
       CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
);
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
