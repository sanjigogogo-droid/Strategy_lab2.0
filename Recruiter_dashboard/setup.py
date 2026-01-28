from app.ingestion import ingest_all_sources
from app.database import create_tables, load_to_db, count_records
import os

def main():
    print("🚀 Starting setup")

    if os.path.exists("data/recruiter_dashboard.db"):
        os.remove("data/recruiter_dashboard.db")
        print("🗑 Existing database removed")

    print("📥 Ingesting data")
    df = ingest_all_sources()
    print(f"   → {len(df)} records ingested")

    print("🗄 Creating database")
    create_tables()

    print("⬆️ Loading data into database")
    load_to_db(df)

    print("✅ Setup complete")
    print(f"📊 Records in DB: {count_records()}")
    print("👉 Run: python3.11 -m streamlit run app.py")

if __name__ == "__main__":
    main()
