# Patient Records / Intake Analyzer!
# Python + Streamlit 
# Focus: patient intake data quality and basic healthcare operations reporting. From my experience with EHR's, I became very interested in expanding on how technology has been modernizing to adapt to today's health industry, where risk goes beyond just corporate docmuments; rather, it directly impacts the lives of patients.

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Patient Intake Analyzer",
    page_icon="🩺",
    layout="wide"
)

st.title("Patient Records / Intake Analyzer")

st.caption(
    "Analyze patient intake records, flag missing or inconsistent data, "
    "group reported symptoms, and summarize triage activity."
)

st.info(
    "Portfolio demonstration only — this project does not provide "
    "medical diagnoses or clinical recommendations."
)


# ---------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------

sample_data = pd.DataFrame(
    [
        {
            "patient_id": "P001",
            "age": 34,
            "symptoms": "fever cough fatigue",
            "triage_minutes": 18,
            "insurance": "Yes"
        },
        {
            "patient_id": "P002",
            "age": 67,
            "symptoms": "chest pain shortness of breath",
            "triage_minutes": 9,
            "insurance": "Yes"
        },
        {
            "patient_id": "P003",
            "age": 22,
            "symptoms": "rash itching",
            "triage_minutes": 26,
            "insurance": "No"
        },
        {
            "patient_id": "P004",
            "age": 145,
            "symptoms": "headache dizziness",
            "triage_minutes": 31,
            "insurance": "Yes"
        },
        {
            "patient_id": "P005",
            "age": 41,
            "symptoms": "abdominal pain nausea",
            "triage_minutes": 21,
            "insurance": ""
        },
        {
            "patient_id": "P006",
            "age": 29,
            "symptoms": "sore throat cough",
            "triage_minutes": 15,
            "insurance": "Yes"
        }
    ]
)


# ---------------------------------------------------------
# SIMPLE SYMPTOM GROUPING
# ---------------------------------------------------------

SYMPTOM_GROUPS = {
    "Respiratory": ["cough", "shortness of breath", "sore throat"],
    "Cardiac": ["chest pain", "palpitations"],
    "Neurological": ["headache", "dizziness"],
    "Gastrointestinal": ["abdominal pain", "nausea", "vomiting"],
    "Dermatological": ["rash", "itching"],
    "General": ["fever", "fatigue"]
}


def classify_symptoms(text):
    """Group reported symptoms into a broad category."""

    text = str(text).lower()

    for category, keywords in SYMPTOM_GROUPS.items():

        if any(keyword in text for keyword in keywords):
            return category

    return "Other"


# ---------------------------------------------------------
# BASIC RECORD VALIDATION
# ---------------------------------------------------------

def check_record(row):
    """Flag common intake data issues."""

    issues = []

    if pd.isna(row["patient_id"]) or str(row["patient_id"]).strip() == "":
        issues.append("Missing patient ID")

    if pd.isna(row["age"]):
        issues.append("Missing age")

    elif row["age"] < 0 or row["age"] > 120:
        issues.append("Invalid age")

    if pd.isna(row["symptoms"]) or str(row["symptoms"]).strip() == "":
        issues.append("Missing symptoms")

    if pd.isna(row["insurance"]) or str(row["insurance"]).strip() == "":
        issues.append("Missing insurance")

    return ", ".join(issues) if issues else "Valid"


# ---------------------------------------------------------
# DATA INPUT
# ---------------------------------------------------------

st.sidebar.header("Data Options")

uploaded_file = st.sidebar.file_uploader(
    "Upload patient intake CSV",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom intake data loaded.")
else:
    df = sample_data.copy()
    st.sidebar.info("Using sample intake data.")


required_columns = {
    "patient_id",
    "age",
    "symptoms",
    "triage_minutes",
    "insurance"
}

if not required_columns.issubset(df.columns):
    st.error("The uploaded file is missing one or more required columns.")
    st.stop()


# Clean numeric fields
df["age"] = pd.to_numeric(df["age"], errors="coerce")

df["triage_minutes"] = pd.to_numeric(
    df["triage_minutes"],
    errors="coerce"
)


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

df["symptom_category"] = (
    df["symptoms"]
    .apply(classify_symptoms)
)

df["record_status"] = (
    df.apply(check_record, axis=1)
)

flagged_records = (
    df["record_status"] != "Valid"
)


# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------

st.subheader("Intake Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Records Analyzed",
    len(df)
)

col2.metric(
    "Valid Records",
    int((~flagged_records).sum())
)

col3.metric(
    "Flagged Records",
    int(flagged_records.sum())
)

valid_ages = df["age"].where(
    df["age"].between(0, 120)
)

col4.metric(
    "Average Patient Age",
    f"{valid_ages.mean():.1f}"
)


# ---------------------------------------------------------
# TRIAGE METRICS
# ---------------------------------------------------------

st.subheader("Triage Summary")

t1, t2 = st.columns(2)

t1.metric(
    "Average Triage Time",
    f"{df['triage_minutes'].mean():.1f} min"
)

t2.metric(
    "Cases Over 30 Minutes",
    int((df["triage_minutes"] > 30).sum())
)


# ---------------------------------------------------------
# SYMPTOM BREAKDOWN
# ---------------------------------------------------------

st.subheader("Reported Symptom Categories")

symptom_summary = (
    df["symptom_category"]
    .value_counts()
    .rename_axis("Category")
    .to_frame("Patients")
)

st.dataframe(
    symptom_summary,
    use_container_width=True
)

st.bar_chart(
    symptom_summary["Patients"]
)


# ---------------------------------------------------------
# RECORD REVIEW
# ---------------------------------------------------------

st.subheader("Patient Record Review")

st.dataframe(
    df[
        [
            "patient_id",
            "age",
            "symptoms",
            "symptom_category",
            "triage_minutes",
            "insurance",
            "record_status"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# FLAGGED RECORDS
# ---------------------------------------------------------

with st.expander("View records that need review"):

    flagged_df = df[
        flagged_records
    ]

    if flagged_df.empty:
        st.write("No records currently require review.")

    else:
        st.dataframe(
            flagged_df[
                [
                    "patient_id",
                    "age",
                    "symptoms",
                    "insurance",
                    "record_status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


st.divider()

st.caption(
    "Healthcare informatics portfolio project focused on "
    "patient intake validation and operational reporting."
)
st.dataframe(df[["patient_id","age","symptoms","symptom_category","triage_minutes","validation_status"]], use_container_width=True)
