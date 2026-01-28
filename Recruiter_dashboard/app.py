import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Recruiter Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STYLE_DIR = os.path.join(BASE_DIR, "style")
DB_PATH = os.path.join(DATA_DIR, "recruiter_dashboard.db")

# ==================================================
# DB
# ==================================================
def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

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

def seed_demo_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applications")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    base_date = datetime.today()
    rows = []

    for i in range(180):
        rows.append((
            f"CAND{i:04d}",
            f"Candidate {i}",
            f"user{i}@example.com",
            f"9{i:09d}",
            f"JOB{random.randint(1,6)}",
            (base_date - timedelta(days=random.randint(0,400))).strftime("%Y-%m-%d"),
            random.choice(["LinkedIn", "Indeed", "Referral"]),
            random.choice(["ATS", "Career Page"])
        ))

    cur.executemany(
        "INSERT INTO applications VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows
    )
    conn.commit()
    conn.close()

# 🚨 REQUIRED INIT
create_tables()
seed_demo_data()

# ==================================================
# CSS (SAFE LOAD)
# ==================================================
def load_css():
    css_path = os.path.join(STYLE_DIR, "ui.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data(show_spinner=False)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM applications", conn)
    conn.close()
    df["application_date"] = pd.to_datetime(df["application_date"])
    return df

apps = load_data()

# ==================================================
# SYNTHETIC ENRICHMENT (UNCHANGED BEHAVIOR)
# ==================================================
random.seed(42)

EDUCATION = ["Graduate", "Post-Graduate"]
EXPERIENCE_YEARS = [0, 1, 2, 3, 5, 7, 10]
SKILLS = ["Python", "SQL", "Excel", "Power BI", "ML", "Marketing", "Sales"]
ROLES = ["Analyst", "Senior Analyst", "Consultant", "Manager"]

def exp_bucket(x):
    if x == 0:
        return "Fresher"
    elif x <= 3:
        return "Early Career (1–3 yrs)"
    elif x <= 7:
        return "Experienced (4–7 yrs)"
    return "Senior (8+ yrs)"

apps["education"] = apps["candidate_record_id"].apply(lambda _: random.choice(EDUCATION))
apps["experience_years"] = apps["candidate_record_id"].apply(lambda _: random.choice(EXPERIENCE_YEARS))
apps["experience_bucket"] = apps["experience_years"].apply(exp_bucket)
apps["resume_skills"] = apps["candidate_record_id"].apply(
    lambda _: set(random.sample(SKILLS, random.randint(2,4)))
)
apps["current_role"] = apps["candidate_record_id"].apply(lambda _: random.choice(ROLES))

# ==================================================
# PAGINATION (RESTORED UX)
# ==================================================
def pagination_ui(df, key):
    if df.empty:
        st.info("No records to display.")
        st.stop()

    page_size = st.selectbox(
        "Rows per page", [10, 25, 50], index=1, key=f"{key}_size"
    )

    total_pages = max(1, (len(df) - 1) // page_size + 1)

    if f"{key}_page" not in st.session_state:
        st.session_state[f"{key}_page"] = 1

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", key=f"{key}_prev") and st.session_state[f"{key}_page"] > 1:
            st.session_state[f"{key}_page"] -= 1
    with col3:
        if st.button("Next ➡️", key=f"{key}_next") and st.session_state[f"{key}_page"] < total_pages:
            st.session_state[f"{key}_page"] += 1
    with col2:
        st.markdown(
            f"<p style='text-align:center;'>Page <b>{st.session_state[f'{key}_page']}</b> of <b>{total_pages}</b></p>",
            unsafe_allow_html=True
        )

    start = (st.session_state[f"{key}_page"] - 1) * page_size
    return df.iloc[start:start + page_size]

# ==================================================
# KPIs
# ==================================================
total_applications = len(apps)
unique_candidates = apps["email"].nunique()
job_openings = apps["job_id"].nunique()
repeat_emails = (
    apps.groupby("email").size().reset_index(name="cnt")
)
repeat_emails = repeat_emails[repeat_emails["cnt"] > 1]["email"]

# ==================================================
# AI — INTENT SCORE (UNCHANGED)
# ==================================================
def compute_intent_score(row):
    days_since = (datetime.today() - row["Last_Applied"]).days
    recency_score = max(0, 100 - days_since)
    resume_score = 100 if row["Resume_Updated"] else 30
    freq_score = min(row["Times_Applied"] * 25, 100)
    return round(0.4*recency_score + 0.35*resume_score + 0.25*freq_score, 1)

# ==================================================
# RESUME DIFF (UNCHANGED)
# ==================================================
def resume_diff(prev, latest):
    changes = []

    if prev["resume_skills"] != latest["resume_skills"]:
        added = latest["resume_skills"] - prev["resume_skills"]
        removed = prev["resume_skills"] - latest["resume_skills"]
        if added:
            changes.append(f"Skills added: {', '.join(added)}")
        if removed:
            changes.append(f"Skills removed: {', '.join(removed)}")

    if prev["experience_bucket"] != latest["experience_bucket"]:
        changes.append(
            f"Experience updated: {prev['experience_bucket']} → {latest['experience_bucket']}"
        )

    if prev["current_role"] != latest["current_role"]:
        changes.append(
            f"Role changed: {prev['current_role']} → {latest['current_role']}"
        )

    return changes

# ==================================================
# SIDEBAR (RESTORED LOOK & FEEL)
# ==================================================
st.sidebar.title("📊 Navigation Bar")
page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Candidate Segmentation",
        "Repeat Applicants",
        "Role & Skills Alignment",
        "Candidate Lookup",
    ],
    label_visibility="collapsed"
)

# ==================================================
# OVERVIEW
# ==================================================
if page == "Overview":
    st.title("🧑‍💼 Recruiter Dashboard")
    st.caption("Unified, decision-ready view of candidate applications")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Job Openings", job_openings)
    c2.metric("Total Applications", total_applications)
    c3.metric("Unique Candidates", unique_candidates)
    c4.metric("Repeat Applicants", len(repeat_emails))

    df = (
        apps.groupby("email")
        .agg(
            Name=("full_name", "first"),
            Education=("education", "first"),
            Experience=("experience_bucket", "first"),
            Applications=("job_id", "count"),
        )
        .reset_index()
    )

    st.dataframe(pagination_ui(df, "overview"), use_container_width=True)

# ==================================================
# CANDIDATE SEGMENTATION
# ==================================================
if page == "Candidate Segmentation":
    st.title("👥 Candidate Segmentation")

    df = (
        apps.groupby("email")
        .agg(
            Name=("full_name", "first"),
            Education=("education", "first"),
            Experience=("experience_bucket", "first"),
            Applications=("job_id", "count"),
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)
    edu = col1.multiselect("Education", sorted(df["Education"].unique()))
    exp = col2.multiselect("Experience", sorted(df["Experience"].unique()))

    if edu:
        df = df[df["Education"].isin(edu)]
    if exp:
        df = df[df["Experience"].isin(exp)]

    st.dataframe(pagination_ui(df, "seg"), use_container_width=True)

# ==================================================
# REPEAT APPLICANTS (FULLY RESTORED)
# ==================================================
if page == "Repeat Applicants":
    st.title("🔁 Repeat Applicants")
    st.caption("AI-prioritized re-engagement candidates")

    repeat_df = (
        apps[apps["email"].isin(repeat_emails)]
        .groupby("email")
        .agg(
            Name=("full_name", "first"),
            Times_Applied=("job_id", "count"),
            First_Applied=("application_date", "min"),
            Last_Applied=("application_date", "max"),
        )
        .reset_index()
    )

    six_months_ago = datetime.today() - timedelta(days=180)
    repeat_df["Applied_Recently"] = repeat_df["Last_Applied"] >= six_months_ago
    repeat_df["Resume_Updated"] = repeat_df["Times_Applied"] > 1
    repeat_df["Intent_Score"] = repeat_df.apply(compute_intent_score, axis=1)

    t1, t2 = st.tabs(["🟢 Last 6 Months", "🟡 Older"])

    with t1:
        st.dataframe(
            pagination_ui(repeat_df[repeat_df["Applied_Recently"]], "recent"),
            use_container_width=True
        )

    with t2:
        st.dataframe(
            pagination_ui(repeat_df[~repeat_df["Applied_Recently"]], "older"),
            use_container_width=True
        )

    st.divider()
    st.subheader("📝 Resume Changes Since Last Application")

    selected = st.selectbox(
        "Select Candidate",
        repeat_df["email"],
        format_func=lambda e: f"{apps[apps['email']==e]['full_name'].iloc[0]} | {e}"
    )

    history = apps[apps["email"] == selected].sort_values("application_date")
    if len(history) >= 2:
        diffs = resume_diff(history.iloc[-2], history.iloc[-1])
        for d in diffs:
            st.markdown(f"• {d}")
    else:
        st.caption("Only one application on record.")

# ==================================================
# ROLE & SKILLS ALIGNMENT
# ==================================================
if page == "Role & Skills Alignment":
    st.title("🧩 Role & Skills Alignment")

    job = st.selectbox("Select Job ID", sorted(apps["job_id"].unique()))
    required = set(random.sample(SKILLS, 3))

    df = (
        apps[apps["job_id"] == job]
        .assign(Skill_Match=lambda d: d["resume_skills"].apply(lambda s: len(s & required)))
        .sort_values("Skill_Match", ascending=False)
    )

    st.caption(f"Required Skills: {', '.join(required)}")
    st.dataframe(
        pagination_ui(df[["full_name", "Skill_Match", "resume_skills"]], "skills"),
        use_container_width=True
    )

# ==================================================
# CANDIDATE LOOKUP
# ==================================================
if page == "Candidate Lookup":
    st.title("🔍 Candidate Lookup")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    job = st.text_input("Job ID")

    df = apps.copy()
    if name:
        df = df[df["full_name"].str.contains(name, case=False)]
    if email:
        df = df[df["email"].str.contains(email, case=False)]
    if phone:
        df = df[df["phone"].str.contains(phone, case=False)]
    if job:
        df = df[df["job_id"].str.contains(job, case=False)]

    st.dataframe(pagination_ui(df, "lookup"), use_container_width=True)
