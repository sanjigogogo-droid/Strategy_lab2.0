import os
import sqlite3
import pandas as pd

# --------------------------------------------------
# PATH SETUP (DEPLOYMENT SAFE)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "applications.db")

# --------------------------------------------------
# CONNECTION
# --------------------------------------------------
def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)  # ensure folder exists
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

# --------------------------------------------------
# TABLE CREATION (RUN ONCE AT START)
# --------------------------------------------------
def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        candidate_record_id TEXT,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        job_id TEXT,
        application_date TEXT,
        application_platform TEXT,
        source_system TEXT
    )
    """)

    conn.commit()
    conn.close()

# --------------------------------------------------
# INSERT DATA
# --------------------------------------------------
def load_to_db(df: pd.DataFrame):
    conn = get_connection()
    df.to_sql("applications", conn, if_exists="append", index=False)
    conn.close()

# --------------------------------------------------
# READ DATA
# --------------------------------------------------
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM applications", conn)
    conn.close()
    return df

# --------------------------------------------------
# COUNT RECORDS
# --------------------------------------------------
def count_records():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applications")
    count = cur.fetchone()[0]
    conn.close()
    return count
