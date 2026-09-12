import pandas as pd
import streamlit as st

st.set_page_config(page_title="Appointment Efficiency Tracker", layout="wide")
st.title("Appointment Efficiency Tracker")
st.caption("Measures scheduling and intake efficiency, flags incomplete records, and highlights workflow bottlenecks.")

sample = pd.DataFrame([
    {"appointment_id":"A001","scheduled_time":"2026-09-01 09:00","arrival_time":"2026-09-01 08:55","intake_start":"2026-09-01 09:02","intake_end":"2026-09-01 09:14","status":"Completed","forms_complete":"Yes"},
    {"appointment_id":"A002","scheduled_time":"2026-09-01 09:30","arrival_time":"2026-09-01 09:41","intake_start":"2026-09-01 09:46","intake_end":"2026-09-01 10:10","status":"Completed","forms_complete":"No"},
    {"appointment_id":"A003","scheduled_time":"2026-09-01 10:00","arrival_time":"2026-09-01 09:58","intake_start":"2026-09-01 10:04","intake_end":"2026-09-01 10:18","status":"Completed","forms_complete":"Yes"},
    {"appointment_id":"A004","scheduled_time":"2026-09-01 10:30","arrival_time":"","intake_start":"","intake_end":"","status":"No Show","forms_complete":"No"},
    {"appointment_id":"A005","scheduled_time":"2026-09-01 11:00","arrival_time":"2026-09-01 10:52","intake_start":"2026-09-01 11:03","intake_end":"2026-09-01 11:38","status":"Completed","forms_complete":"Yes"},
])

uploaded = st.file_uploader("Optional: upload an appointment workflow CSV", type=["csv"])
df = pd.read_csv(uploaded) if uploaded else sample.copy()
required = {"appointment_id","scheduled_time","arrival_time","intake_start","intake_end","status","forms_complete"}
if not required.issubset(df.columns):
    st.error("CSV is missing required appointment columns.")
    st.stop()

for col in ["scheduled_time","arrival_time","intake_start","intake_end"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

df["arrival_delay_min"] = (df["arrival_time"] - df["scheduled_time"]).dt.total_seconds()/60
df["wait_to_intake_min"] = (df["intake_start"] - df["arrival_time"]).dt.total_seconds()/60
df["intake_duration_min"] = (df["intake_end"] - df["intake_start"]).dt.total_seconds()/60
df["incomplete_record"] = df["forms_complete"].astype(str).str.lower().ne("yes")

def bottleneck(row):
    issues = []
    if pd.notna(row["arrival_delay_min"]) and row["arrival_delay_min"] > 10: issues.append("Late arrival")
    if pd.notna(row["wait_to_intake_min"]) and row["wait_to_intake_min"] > 10: issues.append("Intake wait >10 min")
    if pd.notna(row["intake_duration_min"]) and row["intake_duration_min"] > 25: issues.append("Long intake")
    if row["incomplete_record"]: issues.append("Incomplete record")
    return "; ".join(issues) if issues else "No major issue"

df["potential_bottleneck"] = df.apply(bottleneck, axis=1)
completed = df["status"].astype(str).str.lower().eq("completed")
no_show = df["status"].astype(str).str.lower().eq("no show")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Appointments", len(df))
c2.metric("Completion rate", f"{completed.mean()*100:.1f}%")
c3.metric("No-show rate", f"{no_show.mean()*100:.1f}%")
c4.metric("Incomplete records", int(df["incomplete_record"].sum()))

st.subheader("Efficiency Metrics")
st.write(f"Average arrival delay: {df.loc[completed,'arrival_delay_min'].mean():.1f} min")
st.write(f"Average wait to intake: {df.loc[completed,'wait_to_intake_min'].mean():.1f} min")
st.write(f"Average intake duration: {df.loc[completed,'intake_duration_min'].mean():.1f} min")

st.subheader("Appointment-Level Analysis")
cols = ["appointment_id","status","forms_complete","arrival_delay_min","wait_to_intake_min","intake_duration_min","potential_bottleneck"]
st.dataframe(df[cols].round(1), use_container_width=True)
