from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker()
OUT_DIR = Path("data/sources")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_csv(filename, platform, n=1000):
    rows = []
    for _ in range(n):
        rows.append({
            "candidate_record_id": fake.uuid4(),
            "full_name": fake.name(),
            "email": fake.email(),
            "phone": fake.msisdn(),
            "job_id": f"JOB-{random.randint(100,120)}",
            "application_platform": platform,
            "application_date": (
                datetime.today() - timedelta(days=random.randint(0, 365))
            ).strftime("%Y-%m-%d")
        })
    pd.DataFrame(rows).to_csv(OUT_DIR / filename, index=False)

generate_csv("ats.csv", "ATS")
generate_csv("linkedin.csv", "LinkedIn")
generate_csv("job_portal.csv", "JobPortal")

print("✅ Synthetic CSVs generated")
