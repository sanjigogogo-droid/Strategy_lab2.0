import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Recruiter Dashboard", layout="wide")
DB_PATH = "data/recruiter_dashboard.db"

# ==================================================
# DB
# ==================================================
def get_connection():
    return sqlite3.connect(DB_PATH)

# ==================================================
# HELPERS
# ==================================================

def load_css():
    with open("style/ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def paginate(df, page_size, page_num):
    start = (page_num - 1) * page_size
    return df.iloc[start:start + page_size]

def pagination_ui(df, key):
    if df.empty:
        st.info("No records to display.")
        st.stop()

    # Page size
    page_size = st.selectbox(
        "Rows per page",
        [10, 25, 50],
        index=1,
        key=f"{key}_size"
    )

    total_pages = max(1, (len(df) - 1) // page_size + 1)

    # Initialize session state
    if f"{key}_page" not in st.session_state:
        st.session_state[f"{key}_page"] = 1

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", key=f"{key}_prev"):
            if st.session_state[f"{key}_page"] > 1:
                st.session_state[f"{key}_page"] -= 1

    with col3:
        if st.button("Next ➡️", key=f"{key}_next"):
            if st.session_state[f"{key}_page"] < total_pages:
                st.session_state[f"{key}_page"] += 1

    with col2:
        st.markdown(
            f"<p style='text-align:center; margin-top:6px;'>"
            f"Page <b>{st.session_state[f'{key}_page']}</b> of <b>{total_pages}</b>"
            f"</p>",
            unsafe_allow_html=True
        )

    start = (st.session_state[f"{key}_page"] - 1) * page_size
    return df.iloc[start:start + page_size]


# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM applications", conn)
    conn.close()
    df["application_date"] = pd.to_datetime(df["application_date"])
    return df

apps = load_data()

# ==================================================
# SYNTHETIC ENRICHMENT (NON-DESTRUCTIVE)
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
    else:
        return "Senior (8+ yrs)"

apps["education"] = apps["candidate_record_id"].apply(lambda _: random.choice(EDUCATION))
apps["experience_years"] = apps["candidate_record_id"].apply(lambda _: random.choice(EXPERIENCE_YEARS))
apps["experience_bucket"] = apps["experience_years"].apply(exp_bucket)
apps["resume_skills"] = apps["candidate_record_id"].apply(
    lambda _: set(random.sample(SKILLS, random.randint(2, 4)))
)
apps["current_role"] = apps["candidate_record_id"].apply(lambda _: random.choice(ROLES))

# ==================================================
# KPIs
# ==================================================
total_applications = len(apps)
unique_candidates = apps["email"].nunique()
job_openings = apps["job_id"].nunique()

application_counts = apps.groupby("email").size().reset_index(name="times_applied")
repeat_emails = application_counts[application_counts["times_applied"] > 1]["email"]

# ==================================================
# AI — REAPPLICATION INTENT SCORE
# ==================================================
def compute_intent_score(row):
    days_since = (datetime.today() - row["Last_Applied"]).days
    recency_score = max(0, 100 - days_since)
    resume_score = 100 if row["Resume_Updated"] else 30
    freq_score = min(row["Times_Applied"] * 25, 100)

    score = (
        0.4 * recency_score +
        0.35 * resume_score +
        0.25 * freq_score
    )
    return round(score, 1)

# ==================================================
# RESUME DIFF LOGIC (KEY ADDITION)
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
# SIDEBAR
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

    overview_df = (
        apps.groupby("email")
        .agg(
            Name=("full_name", "first"),
            Education=("education", "first"),
            Experience=("experience_bucket", "first"),
            Applications=("job_id", "count"),
        )
        .reset_index()
    )

    paged = pagination_ui(overview_df, "overview")
    st.dataframe(paged, width="stretch")


# ==================================================
# CANDIDATE SEGMENTATION
# ==================================================
if page == "Candidate Segmentation":
    st.title("👥 Candidate Segmentation")

    seg_df = (
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
    edu = col1.multiselect("Education", sorted(seg_df["Education"].unique()))
    exp = col2.multiselect("Experience", sorted(seg_df["Experience"].unique()))

    if edu:
        seg_df = seg_df[seg_df["Education"].isin(edu)]
    if exp:
        seg_df = seg_df[seg_df["Experience"].isin(exp)]

    paged = pagination_ui(seg_df, "seg")
    st.dataframe(paged, width="stretch")

# ==================================================
# REPEAT APPLICANTS (WITH RESUME CHANGE EXPLAINER)
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

    recent_df = repeat_df[repeat_df["Applied_Recently"]]
    older_df = repeat_df[~repeat_df["Applied_Recently"]]

    t1, t2 = st.tabs([
        f"🟢 Last 6 Months ({len(recent_df)})",
        f"🟡 Older ({len(older_df)})"
    ])

    with t1:
        paged = pagination_ui(recent_df, "recent")
        st.dataframe(paged, width="stretch")

    with t2:
        paged = pagination_ui(older_df, "older")
        st.dataframe(paged, width="stretch")

    st.divider()
    st.subheader("📝 Resume Changes Since Last Application")

    selected_email = st.selectbox(
        "Select Candidate",
        repeat_df["email"],
        format_func=lambda e: f"{apps[apps['email']==e]['full_name'].iloc[0]} | {e}"
    )

    history = apps[apps["email"] == selected_email].sort_values("application_date")

    if len(history) >= 2:
        prev = history.iloc[-2]
        latest = history.iloc[-1]
        diffs = resume_diff(prev, latest)

        if diffs:
            for d in diffs:
                st.markdown(f"• {d}")
        else:
            st.caption("No material resume changes detected.")
    else:
        st.caption("Only one application on record.")

# ==================================================
# ROLE & SKILLS ALIGNMENT
# ==================================================
if page == "Role & Skills Alignment":
    st.title("🧩 Role & Skills Alignment")

    job = st.selectbox("Select Job ID", sorted(apps["job_id"].unique()))
    required = set(random.sample(SKILLS, 3))

    eligible = (
        apps[apps["job_id"] == job]
        .assign(Skill_Match=lambda d: d["resume_skills"].apply(lambda s: len(s & required)))
        .sort_values("Skill_Match", ascending=False)
    )

    st.caption(f"Required Skills: {', '.join(required)}")
    paged = pagination_ui(
        eligible[["full_name", "Skill_Match", "resume_skills"]],
        "skills"
    )
    st.dataframe(paged, width="stretch")

# ==================================================
# CANDIDATE LOOKUP (NO VAGUE IDS)
# ==================================================
if page == "Candidate Lookup":
    st.title("🔍 Candidate Lookup")

    c1, c2, c3, c4 = st.columns(4)
    name_q = c1.text_input("Name")
    email_q = c2.text_input("Email")
    phone_q = c3.text_input("Phone")
    job_q = c4.text_input("Job ID")

    df = apps.copy()
    if name_q:
        df = df[df["full_name"].str.contains(name_q, case=False, na=False)]
    if email_q:
        df = df[df["email"].str.contains(email_q, case=False, na=False)]
    if phone_q:
        df = df[df["phone"].astype(str).str.contains(phone_q, na=False)]
    if job_q:
        df = df[df["job_id"].str.contains(job_q, case=False, na=False)]

    if df.empty:
        st.warning("No candidate found.")
        st.stop()

    selected = st.selectbox(
        "Select Candidate",
        df["email"].unique(),
        format_func=lambda e: f"{df[df['email']==e]['full_name'].iloc[0]} | {e}"
    )

    c = df[df["email"] == selected].iloc[0]

    st.markdown(f"""
    **Name:** {c['full_name']}  
    **Email:** {c['email']}  
    **Education:** {c['education']}  
    **Experience:** {c['experience_bucket']}  
    """)

    st.subheader("📜 Application History")
    st.table(
        apps[apps["email"] == selected]
        [["application_platform", "job_id", "application_date"]]
        .sort_values("application_date")
    )
