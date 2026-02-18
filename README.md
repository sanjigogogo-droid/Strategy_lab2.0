Problem Statement: Recruiters source candidates from multiple platforms such as ATS systems, job portals, and professional networks. This fragmented ecosystem creates duplicate profiles, conflicting data fields, and incomplete candidate histories, forcing recruiters to manually reconcile information before making decisions. As hiring volumes scale, this inefficiency increases screening time, reduces productivity, and impacts time-to-shortlist.
The problem is to design a recruiter-facing MVP that consolidates candidate data into a unified view, detects duplicate and repeat applicants, surfaces resume changes, and provides explainable prioritization insights — all without requiring live integrations or production backend systems.

SCOPE:

•  Data Consolidation Scope
Aggregate and standardize candidate data from multiple simulated hiring platforms into a unified schema.
•  Identity & Duplication Scope
Detect and consolidate duplicate profiles while identifying legitimate repeat applicants.
•  Intelligence & AI Scope.                                                                                                           Analyse resume evolution and compute an explainable reapplication intent score based on behavioural signals.
•  Dashboard & Pilot Scope
Develop a recruiter-facing MVP dashboard with actionable insights, segmentation, and governance-ready summaries, using synthetic data for privacy-safe feasibility demonstration.

Objectives

•	Create a single source of truth for candidate information across platforms
•	Reduce recruiter effort spent on duplicate verification and manual reconciliation
•	Identify legitimate repeat applicants and highlight resume evolution
•	Implement an explainable AI-based reapplication intent score
•	Deliver a recruiter-friendly dashboard that improves time-to-shortlist
•	Ensure transparency, auditability, and pilot readiness
Methodology Used

1.	Data Simulation & Ingestion
o	Used synthetic datasets to replicate ATS, job portal, and network data
o	Manually ingested structured CSV files to simulate multi-source integration
2.	Data Standardization
o	Converted incoming data into a common schema
o	Cleaned and normalized key identifiers (email, phone, job ID, timestamps)
3.	Identity Resolution Logic
o	Applied deterministic matching using unique identifiers
o	Classified applications as unique, duplicate, or legitimate repeat entries
4.	Resume Change Detection
o	Compared historical application attributes (skills, experience, roles)

o	Flagged meaningful profile evolution

6.	Explainable AI Integration
o	Designed a weighted scoring model using:

	Recency

	Frequency

	Resume evolution

	Skill relevance

o	Generated transparent intent scores with reasoning
7.	Dashboard Development
8.	
o	Built interactive UI using Streamlit
o	Integrated pagination, filtering, segmentation, and real-time summaries
Results & Impact

•	Successfully unified 3,000+ synthetic candidate records into a consolidated view
•	Automated detection of duplicate and repeat applicants
•	Enabled resume change visibility across application timelines
•	Implemented an explainable AI-based reapplication intent scoring mechanism
•	Demonstrated improved recruiter prioritization and reduced manual verification effort
•	Delivered a pilot-ready prototype aligned with compliance and privacy constraints
Business Impact

•  Reduced screening redundancy

•  Faster time-to-shortlist

•  Improved recruiter productivity

•  Enhanced transparency in hiring decisions

•  Scalable architecture 


