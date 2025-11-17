import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1010",
    "database": "registration_db"
}

def get_server_connection():
    # connect to MySQL server without specifying database (used to create DB if missing)
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

def get_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

def ensure_database():
    conn = None
    cursor = None
    try:
        conn = get_server_connection()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_table():
    ensure_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            firstname VARCHAR(100) NOT NULL,
            lastname VARCHAR(100) NOT NULL,
            enrollnumber VARCHAR(50) NOT NULL UNIQUE,
            dob DATE NOT NULL,
            mobile VARCHAR(15) NOT NULL,
            gmail VARCHAR(100) NOT NULL,
            address TEXT NOT NULL,
            qualification VARCHAR(50) NOT NULL,
            photo LONGBLOB,
            photo_filename VARCHAR(255),
            resume LONGBLOB,
            resume_filename VARCHAR(255),
            resume_mimetype VARCHAR(100),
            signature LONGBLOB,
            signature_filename VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL DEFAULT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
