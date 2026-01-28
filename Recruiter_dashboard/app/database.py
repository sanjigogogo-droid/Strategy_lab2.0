import sqlite3

DB_PATH = "data/recruiter_dashboard.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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

def load_to_db(df):
    conn = get_connection()
    df.to_sql("applications", conn, if_exists="append", index=False)
    conn.close()

def count_records():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applications")
    count = cur.fetchone()[0]
    conn.close()
    return count
