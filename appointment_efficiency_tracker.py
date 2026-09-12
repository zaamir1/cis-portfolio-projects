# Appointment Efficiency Tracker
# Python + Streamlit portfolio project
# Goal: identify delays, incomplete records, and workflow bottlenecks. I wanted to be able to explore the depths of IT in healthcare after working at a local clinic during summer and realizing how regulated the data really was in real time.

import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Appointment Efficiency Tracker",
    page_icon="📅",
    layout="wide"
)

st.title("Appointment Efficiency Tracker")

st.caption(
    "Analyze appointment and intake workflows to identify delays, "
    "incomplete records, and potential operational bottlenecks."
)


# ---------------------------------------------------------
# SAMPLE APPOINTMENT DATA
# Built in so the dashboard works immediately.
# Users can also upload their own CSV.
# ---------------------------------------------------------

sample_data = pd.DataFrame(
    [
        {
            "appointment_id": "A001",
            "scheduled_time": "2026-09-01 09:00",
            "arrival_time": "2026-09-01 08:55",
            "intake_start": "2026-09-01 09:02",
            "intake_end": "2026-09-01 09:14",
            "status": "Completed",
            "forms_complete": "Yes"
        },
        {
            "appointment_id": "A002",
            "scheduled_time": "2026-09-01 09:30",
            "arrival_time": "2026-09-01 09:42",
            "intake_start": "2026-09-01 09:49",
            "intake_end": "2026-09-01 10:14",
            "status": "Completed",
            "forms_complete": "No"
        },
        {
            "appointment_id": "A003",
            "scheduled_time": "2026-09-01 10:00",
            "arrival_time": "2026-09-01 09:58",
            "intake_start": "2026-09-01 10:04",
            "intake_end": "2026-09-01 10:18",
            "status": "Completed",
            "forms_complete": "Yes"
        },
        {
            "appointment_id": "A004",
            "scheduled_time": "2026-09-01 10:30",
            "arrival_time": "",
            "intake_start": "",
            "intake_end": "",
            "status": "No Show",
            "forms_complete": "No"
        },
        {
            "appointment_id": "A005",
            "scheduled_time": "2026-09-01 11:00",
            "arrival_time": "2026-09-01 10:52",
            "intake_start": "2026-09-01 11:05",
            "intake_end": "2026-09-01 11:39",
            "status": "Completed",
            "forms_complete": "Yes"
        },
        {
            "appointment_id": "A006",
            "scheduled_time": "2026-09-01 11:30",
            "arrival_time": "2026-09-01 11:28",
            "intake_start": "2026-09-01 11:32",
            "intake_end": "2026-09-01 11:43",
            "status": "Completed",
            "forms_complete": "Yes"
        },
    ]
)


# ---------------------------------------------------------
# DATA INPUT
# ---------------------------------------------------------

st.sidebar.header("Data Options")

uploaded_file = st.sidebar.file_uploader(
    "Upload appointment CSV",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom appointment data loaded.")
else:
    df = sample_data.copy()
    st.sidebar.info("Using sample appointment data.")


required_columns = {
    "appointment_id",
    "scheduled_time",
    "arrival_time",
    "intake_start",
    "intake_end",
    "status",
    "forms_complete"
}

if not required_columns.issubset(df.columns):
    st.error("Uploaded file is missing one or more required columns.")
    st.stop()


# ---------------------------------------------------------
# CLEAN + PREPARE DATA
# ---------------------------------------------------------

time_columns = [
    "scheduled_time",
    "arrival_time",
    "intake_start",
    "intake_end"
]

for column in time_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )


# Calculate workflow timing metrics
df["arrival_delay_min"] = (
    df["arrival_time"] - df["scheduled_time"]
).dt.total_seconds() / 60

df["wait_to_intake_min"] = (
    df["intake_start"] - df["arrival_time"]
).dt.total_seconds() / 60

df["intake_duration_min"] = (
    df["intake_end"] - df["intake_start"]
).dt.total_seconds() / 60


# ---------------------------------------------------------
# DATA QUALITY + BOTTLENECK LOGIC
# ---------------------------------------------------------

df["incomplete_record"] = (
    df["forms_complete"]
    .astype(str)
    .str.strip()
    .str.lower()
    .ne("yes")
)


def identify_bottleneck(row):
    """Flag workflow issues that may slow down patient processing."""

    issues = []

    if pd.notna(row["arrival_delay_min"]) and row["arrival_delay_min"] > 10:
        issues.append("Late arrival")

    if pd.notna(row["wait_to_intake_min"]) and row["wait_to_intake_min"] > 10:
        issues.append("Long intake wait")

    if pd.notna(row["intake_duration_min"]) and row["intake_duration_min"] > 25:
        issues.append("Long intake process")

    if row["incomplete_record"]:
        issues.append("Incomplete forms")

    return ", ".join(issues) if issues else "No major issue"


df["bottleneck"] = df.apply(
    identify_bottleneck,
    axis=1
)


# ---------------------------------------------------------
# SIMPLE EFFICIENCY SCORE
# 100 = clean workflow
# Points are deducted for common workflow problems.
# ---------------------------------------------------------

def calculate_efficiency_score(row):

    score = 100

    if pd.notna(row["arrival_delay_min"]) and row["arrival_delay_min"] > 10:
        score -= 15

    if pd.notna(row["wait_to_intake_min"]) and row["wait_to_intake_min"] > 10:
        score -= 20

    if pd.notna(row["intake_duration_min"]) and row["intake_duration_min"] > 25:
        score -= 20

    if row["incomplete_record"]:
        score -= 15

    if str(row["status"]).lower() == "no show":
        score -= 30

    return max(score, 0)


df["efficiency_score"] = df.apply(
    calculate_efficiency_score,
    axis=1
)


# ---------------------------------------------------------
# DASHBOARD METRICS
# ---------------------------------------------------------

completed = (
    df["status"]
    .astype(str)
    .str.lower()
    .eq("completed")
)

no_show = (
    df["status"]
    .astype(str)
    .str.lower()
    .eq("no show")
)

st.subheader("Operations Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Appointments",
    len(df)
)

col2.metric(
    "Completion Rate",
    f"{completed.mean() * 100:.1f}%"
)

col3.metric(
    "No-Show Rate",
    f"{no_show.mean() * 100:.1f}%"
)

col4.metric(
    "Average Efficiency Score",
    f"{df['efficiency_score'].mean():.0f}/100"
)


# ---------------------------------------------------------
# WORKFLOW TIMING
# ---------------------------------------------------------

st.subheader("Workflow Timing")

time1, time2, time3 = st.columns(3)

time1.metric(
    "Avg. Arrival Delay",
    f"{df.loc[completed, 'arrival_delay_min'].mean():.1f} min"
)

time2.metric(
    "Avg. Wait to Intake",
    f"{df.loc[completed, 'wait_to_intake_min'].mean():.1f} min"
)

time3.metric(
    "Avg. Intake Duration",
    f"{df.loc[completed, 'intake_duration_min'].mean():.1f} min"
)


# ---------------------------------------------------------
# BOTTLENECK SUMMARY
# ---------------------------------------------------------

st.subheader("Potential Bottlenecks")

issue_count = (
    df["bottleneck"]
    .value_counts()
    .rename_axis("Issue")
    .to_frame("Appointments")
)

st.dataframe(
    issue_count,
    use_container_width=True
)


# ---------------------------------------------------------
# QUICK OPERATIONS INSIGHTS
# ---------------------------------------------------------

st.subheader("Quick Insights")

flagged_records = (
    df["bottleneck"] != "No major issue"
).sum()

incomplete_records = (
    df["incomplete_record"]
).sum()

long_intakes = (
    df["intake_duration_min"] > 25
).sum()

i1, i2, i3 = st.columns(3)

i1.warning(
    f"{flagged_records} appointment(s) contain at least one workflow issue."
)

i2.info(
    f"{incomplete_records} appointment(s) have incomplete forms."
)

i3.info(
    f"{long_intakes} appointment(s) exceeded 25 minutes for intake."
)


# ---------------------------------------------------------
# APPOINTMENT EXPLORER
# ---------------------------------------------------------

st.subheader("Appointment-Level Analysis")

status_options = (
    ["All"]
    + sorted(df["status"].dropna().unique().tolist())
)

selected_status = st.selectbox(
    "Filter appointments by status",
    status_options
)

if selected_status != "All":
    filtered_df = df[
        df["status"] == selected_status
    ]
else:
    filtered_df = df


display_columns = [
    "appointment_id",
    "status",
    "forms_complete",
    "arrival_delay_min",
    "wait_to_intake_min",
    "intake_duration_min",
    "bottleneck",
    "efficiency_score"
]

st.dataframe(
    filtered_df[display_columns].round(1),
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# FLAGGED CASES
# ---------------------------------------------------------

with st.expander("View flagged appointments"):

    flagged_df = df[
        df["bottleneck"] != "No major issue"
    ]

    st.dataframe(
        flagged_df[display_columns].round(1),
        use_container_width=True,
        hide_index=True
    )


st.divider()

st.caption(
    "Python workflow analysis project focused on appointment scheduling, "
    "intake efficiency, record completeness, and healthcare operations."
)
