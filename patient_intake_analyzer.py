import pandas as pd
import streamlit as st

st.set_page_config(page_title="Patient Records / Intake Analyzer", layout="wide")
st.title("Patient Records / Intake Analyzer")
st.caption("Validates records, flags missing or inconsistent fields, classifies symptoms, and summarizes intake metrics.")

sample = pd.DataFrame([
    {"patient_id":"P001","age":34,"symptoms":"fever cough fatigue","triage_minutes":18,"insurance":"Yes","phone":"4045550101"},
    {"patient_id":"P002","age":67,"symptoms":"chest pain shortness of breath","triage_minutes":9,"insurance":"Yes","phone":"4045550102"},
    {"patient_id":"P003","age":22,"symptoms":"rash itching","triage_minutes":26,"insurance":"No","phone":""},
    {"patient_id":"P004","age":145,"symptoms":"headache dizziness","triage_minutes":31,"insurance":"Yes","phone":"4045550104"},
    {"patient_id":"P005","age":41,"symptoms":"abdominal pain nausea","triage_minutes":21,"insurance":"","phone":"4045550105"},
])

GROUPS = {
    "Respiratory":["cough","shortness of breath","sore throat"],
    "Cardiac":["chest pain","palpitations"],
    "Neurological":["headache","dizziness","migraine"],
    "Gastrointestinal":["abdominal pain","nausea","vomiting"],
    "Dermatological":["rash","itching"],
    "General":["fever","fatigue"],
}

def symptom_group(text):
    t = str(text).lower()
    scores = {g: sum(k in t for k in kws) for g,kws in GROUPS.items()}
    return "Other" if max(scores.values()) == 0 else max(scores, key=scores.get)

def validate(row):
    issues = []
    if not str(row["patient_id"]).strip(): issues.append("Missing patient ID")
    if pd.isna(row["age"]): issues.append("Missing age")
    elif row["age"] < 0 or row["age"] > 120: issues.append("Age outside expected range")
    if not str(row["symptoms"]).strip(): issues.append("Missing symptoms")
    if pd.isna(row["triage_minutes"]) or row["triage_minutes"] < 0: issues.append("Invalid triage time")
    if not str(row["insurance"]).strip(): issues.append("Missing insurance status")
    if not str(row["phone"]).strip(): issues.append("Missing phone")
    return "; ".join(issues) if issues else "Valid"

uploaded = st.file_uploader("Optional: upload a patient intake CSV", type=["csv"])
df = pd.read_csv(uploaded) if uploaded else sample.copy()
required = {"patient_id","age","symptoms","triage_minutes","insurance","phone"}
if not required.issubset(df.columns):
    st.error("CSV is missing required intake columns.")
    st.stop()

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["triage_minutes"] = pd.to_numeric(df["triage_minutes"], errors="coerce")
df["symptom_category"] = df["symptoms"].apply(symptom_group)
df["validation_status"] = df.apply(validate, axis=1)
flagged = df["validation_status"] != "Valid"

c1,c2,c3,c4 = st.columns(4)
c1.metric("Records analyzed", len(df))
c2.metric("Valid records", int((~flagged).sum()))
c3.metric("Flagged records", int(flagged.sum()))
c4.metric("Avg. triage time", f"{df['triage_minutes'].mean():.1f} min")

st.subheader("Operational Metrics")
st.write(f"Average patient age: {df['age'].where(df['age'].between(0,120)).mean():.1f}")
st.write(f"Median triage time: {df['triage_minutes'].median():.1f} minutes")

st.subheader("Symptom Classification")
counts = df["symptom_category"].value_counts().to_frame("patients")
st.dataframe(counts, use_container_width=True)
st.bar_chart(counts)

st.subheader("Validation Results")
st.dataframe(df[["patient_id","age","symptoms","symptom_category","triage_minutes","validation_status"]], use_container_width=True)
