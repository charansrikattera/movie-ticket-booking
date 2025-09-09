import sqlite3
import time

# Function to retry executing a command when the database is locked
def execute_with_retry(cursor, command, params=(), retries=5, delay=1):
    for i in range(retries):
        try:
            cursor.execute(command, params)
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                time.sleep(delay)
            else:
                raise
    raise sqlite3.OperationalError("Max retries reached. The database is still locked.")

# Connect to SQLite database with a timeout
def get_db_connection():
    return sqlite3.connect('C:/Users/Administrator/PycharmProjects/VirtusaMovieTicketBookingStreamlit/movieDB.db', timeout=10)

# Clear existing tables and create new structure
def reset_database():
    conn = get_db_connection()
    c = conn.cursor()

    # Drop existing tables if they exist
    try:
        execute_with_retry(c, 'DROP TABLE IF EXISTS users;')
        execute_with_retry(c, 'DROP TABLE IF EXISTS movies;')
        execute_with_retry(c, 'DROP TABLE IF EXISTS theaters;')
        execute_with_retry(c, 'DROP TABLE IF EXISTS bookings;')
    except sqlite3.OperationalError as e:
        print(f"Error while dropping tables: {e}")
        conn.close()
        return

    # Create new tables
    try:
        execute_with_retry(c, '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                phone TEXT,
                role TEXT NOT NULL
            );
        ''')

        execute_with_retry(c, '''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                theater_id INTEGER,
                timings TEXT,
                seats TEXT,
                FOREIGN KEY(theater_id) REFERENCES theaters(id)
            );
        ''')

        execute_with_retry(c, '''
            CREATE TABLE IF NOT EXISTS theaters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                owner_id INTEGER,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
        ''')

        execute_with_retry(c, '''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                theater_id INTEGER,
                timing TEXT,
                seats TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(movie_id) REFERENCES movies(id),
                FOREIGN KEY(theater_id) REFERENCES theaters(id)
            );
        ''')

        # Insert admin user
        execute_with_retry(c, '''
            INSERT INTO users (username, password, phone, role)
            VALUES ('admin123', 'admin123', '0000000000', 'admin')
            ON CONFLICT(username) DO NOTHING;
        ''')

        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Error while creating tables or inserting admin: {e}")
    finally:
        conn.close()

# Ensure the database is reset and new structure is created
reset_database()
