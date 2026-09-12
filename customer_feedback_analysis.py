# Customer Feedback Analysis Tool!
# Built with Python + Streamlit 
# Goal: turn raw customer reviews into quick, useful service/product insights. This was inspired by my experience doing structured feedback missions for TOPBOX, teaching me the importance of simple quality feedback and how every company can benefit from visualizing such data.
import re
from collections import Counter

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Customer Feedback Analysis Tool",
    page_icon="💬",
    layout="wide"
)

st.title("Customer Feedback Analysis Tool")
st.caption(
    "Analyze customer reviews by topic, rating, recurring keywords, "
    "and potential service issues."
)


# ---------------------------------------------------------
# SAMPLE DATA
# This lets the app work immediately, but users can also
# upload their own CSV later.
# ---------------------------------------------------------

sample_data = pd.DataFrame(
    [
        {
            "review": "Delivery was two days late, but the shoes arrived in perfect condition.",
            "rating": 4
        },
        {
            "review": "The quality is excellent and the fit is very comfortable.",
            "rating": 5
        },
        {
            "review": "The price felt high compared with similar products.",
            "rating": 3
        },
        {
            "review": "Customer support responded quickly and helped process my return.",
            "rating": 5
        },
        {
            "review": "The package arrived damaged and the material had a visible defect.",
            "rating": 2
        },
        {
            "review": "Great value for the price and shipping was faster than expected.",
            "rating": 5
        },
        {
            "review": "Support took too long to respond to my refund request.",
            "rating": 2
        },
        {
            "review": "The product is comfortable, but delivery tracking was inaccurate.",
            "rating": 3
        },
        {
            "review": "The sizing was inconsistent and I had to exchange the product.",
            "rating": 2
        },
        {
            "review": "Fast delivery, good quality, and the discount made it a great purchase.",
            "rating": 5
        },
    ]
)


# ---------------------------------------------------------
# REVIEW CATEGORIES
# Simple keyword-based tagging keeps the logic transparent
# while still giving useful results.
# ---------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Shipping": [
        "shipping", "delivery", "delivered", "late",
        "delay", "package", "arrived", "tracking"
    ],

    "Product Quality": [
        "quality", "broken", "defect", "damaged",
        "material", "fit", "size", "sizing",
        "comfortable", "durable"
    ],

    "Pricing": [
        "price", "pricing", "expensive", "cheap",
        "cost", "value", "discount", "refund"
    ],

    "Customer Support": [
        "support", "service", "agent", "representative",
        "help", "response", "return", "exchange"
    ]
}


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def clean_text(text):
    """Basic text cleanup so keyword matching is more consistent."""
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_categories(review):
    """
    Return every category mentioned in the review.

    I kept this multi-label instead of forcing every review
    into one bucket because real customer feedback usually
    touches more than one issue.
    """

    cleaned_review = clean_text(review)
    detected = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in cleaned_review for keyword in keywords):
            detected.append(category)

    return detected if detected else ["Other"]


def primary_category(review):
    """
    Pick the strongest category based on keyword matches.

    This gives us one main category for charts while still
    keeping the multi-category tags separately.
    """

    cleaned_review = clean_text(review)

    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(
            1 for keyword in keywords
            if keyword in cleaned_review
        )

        category_scores[category] = score

    best_category = max(category_scores, key=category_scores.get)

    if category_scores[best_category] == 0:
        return "Other"

    return best_category


def assign_priority(rating):
    """
    Simple service-priority flag.

    Lower ratings get surfaced faster so a customer service
    team could focus on the most urgent feedback first.
    """

    if rating <= 2:
        return "High"
    elif rating == 3:
        return "Medium"
    else:
        return "Low"


def extract_common_terms(review_series, top_n=12):
    """Find recurring useful words across all customer reviews."""

    stop_words = {
        "the", "and", "a", "an", "to", "of", "is",
        "was", "were", "it", "my", "for", "with",
        "in", "on", "but", "this", "that", "very",
        "had", "has", "have", "i", "they", "we",
        "you", "from", "at", "too", "as"
    }

    words = []

    for review in review_series.astype(str):

        cleaned_review = clean_text(review)

        words.extend(
            word
            for word in cleaned_review.split()
            if len(word) > 2 and word not in stop_words
        )

    return Counter(words).most_common(top_n)


# ---------------------------------------------------------
# DATA INPUT
# ---------------------------------------------------------

st.sidebar.header("Data Options")

uploaded_file = st.sidebar.file_uploader(
    "Upload customer review CSV",
    type=["csv"],
    help="Your file should contain review and rating columns."
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom dataset loaded.")
else:
    df = sample_data.copy()
    st.sidebar.info("Using built-in sample customer feedback.")


# ---------------------------------------------------------
# VALIDATE INPUT
# ---------------------------------------------------------

required_columns = {"review", "rating"}

if not required_columns.issubset(df.columns):
    st.error(
        "The dataset must contain columns named "
        "`review` and `rating`."
    )
    st.stop()


# Make sure rating behaves like a number
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# Remove completely unusable rows
df = df.dropna(subset=["review", "rating"]).copy()


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

df["primary_category"] = df["review"].apply(primary_category)

df["topics_detected"] = df["review"].apply(
    lambda review: ", ".join(detect_categories(review))
)

df["priority"] = df["rating"].apply(assign_priority)


# ---------------------------------------------------------
# TOP-LEVEL METRICS
# ---------------------------------------------------------

st.subheader("Feedback Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Reviews Analyzed",
    len(df)
)

col2.metric(
    "Average Rating",
    f"{df['rating'].mean():.2f} / 5"
)

col3.metric(
    "High-Priority Reviews",
    int((df["priority"] == "High").sum())
)

col4.metric(
    "5-Star Reviews",
    int((df["rating"] == 5).sum())
)


# ---------------------------------------------------------
# CATEGORY PERFORMANCE
# ---------------------------------------------------------

st.subheader("Feedback by Category")

category_summary = (
    df.groupby("primary_category")
    .agg(
        Reviews=("review", "count"),
        Average_Rating=("rating", "mean")
    )
    .sort_values("Reviews", ascending=False)
)

category_summary["Average_Rating"] = (
    category_summary["Average_Rating"].round(2)
)

left_col, right_col = st.columns(2)

with left_col:
    st.dataframe(
        category_summary,
        use_container_width=True
    )

with right_col:
    st.bar_chart(
        category_summary["Reviews"]
    )


# ---------------------------------------------------------
# PRIORITY BREAKDOWN
# ---------------------------------------------------------

st.subheader("Customer Service Priority")

priority_counts = (
    df["priority"]
    .value_counts()
    .reindex(["High", "Medium", "Low"])
    .fillna(0)
)

st.bar_chart(priority_counts)


# ---------------------------------------------------------
# TREND / KEYWORD ANALYSIS
# ---------------------------------------------------------

st.subheader("Recurring Customer Themes")

common_terms = extract_common_terms(df["review"])

term_df = pd.DataFrame(
    common_terms,
    columns=["Keyword", "Mentions"]
)

if not term_df.empty:

    st.dataframe(
        term_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# QUICK INSIGHTS
# ---------------------------------------------------------

st.subheader("Quick Insights")

worst_category = (
    category_summary["Average_Rating"].idxmin()
    if not category_summary.empty
    else "N/A"
)

best_category = (
    category_summary["Average_Rating"].idxmax()
    if not category_summary.empty
    else "N/A"
)

low_rating_pct = (
    (df["rating"] <= 2).mean() * 100
)

insight_col1, insight_col2, insight_col3 = st.columns(3)

insight_col1.info(
    f"Lowest-rated category: **{worst_category}**"
)

insight_col2.success(
    f"Highest-rated category: **{best_category}**"
)

insight_col3.warning(
    f"{low_rating_pct:.1f}% of reviews are rated 2 stars or below."
)


# ---------------------------------------------------------
# REVIEW EXPLORER
# ---------------------------------------------------------

st.subheader("Review Explorer")

category_options = ["All"] + sorted(
    df["primary_category"].unique().tolist()
)

selected_category = st.selectbox(
    "Filter by category",
    category_options
)

if selected_category != "All":

    filtered_df = df[
        df["primary_category"] == selected_category
    ]

else:
    filtered_df = df


st.dataframe(
    filtered_df[
        [
            "review",
            "rating",
            "primary_category",
            "topics_detected",
            "priority"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# HIGH-PRIORITY FEEDBACK
# ---------------------------------------------------------

with st.expander("View high-priority customer feedback"):

    high_priority_df = df[
        df["priority"] == "High"
    ]

    if high_priority_df.empty:

        st.write("No high-priority reviews found.")

    else:

        st.dataframe(
            high_priority_df[
                [
                    "review",
                    "rating",
                    "primary_category",
                    "topics_detected"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

# ---------------------------------------------------------
# ---------------------------------------------------------

st.divider()

st.caption(
    "Python portfolio project focused on customer feedback analysis, "
    "basic text classification, data summarization, and operational insights."
)
