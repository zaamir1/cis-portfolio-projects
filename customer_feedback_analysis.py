import re
from collections import Counter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Feedback Analysis Tool", layout="wide")
st.title("Customer Feedback Analysis Tool")
st.caption("Categorizes reviews, summarizes ratings, and identifies recurring customer themes.")

KEYWORDS = {
    "Shipping": ["shipping","delivery","delivered","late","delay","package","arrived"],
    "Product Quality": ["quality","broken","defect","damaged","durable","material","fit","comfortable"],
    "Pricing": ["price","pricing","expensive","cheap","cost","value","refund","discount"],
    "Support": ["support","service","agent","representative","help","response","return"],
}

sample = pd.DataFrame([
    {"review":"Delivery was two days late, but the shoes arrived in perfect condition.","rating":4},
    {"review":"The product quality is excellent and the fit is very comfortable.","rating":5},
    {"review":"Price felt high compared with similar products.","rating":3},
    {"review":"Customer support responded quickly and helped with my return.","rating":5},
    {"review":"The package arrived damaged and the material had a defect.","rating":2},
    {"review":"Great value for the price and shipping was faster than expected.","rating":5},
    {"review":"Support took too long to respond to my refund request.","rating":2},
])

def classify(text):
    t = str(text).lower()
    scores = {cat: sum(k in t for k in kws) for cat, kws in KEYWORDS.items()}
    return "Other" if max(scores.values()) == 0 else max(scores, key=scores.get)

uploaded = st.file_uploader("Optional: upload a CSV with review and rating columns", type=["csv"])
df = pd.read_csv(uploaded) if uploaded else sample.copy()
if not {"review","rating"}.issubset(df.columns):
    st.error("CSV must contain review and rating columns.")
    st.stop()

df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["category"] = df["review"].apply(classify)

c1,c2,c3 = st.columns(3)
c1.metric("Reviews analyzed", len(df))
c2.metric("Average rating", f"{df['rating'].mean():.2f}/5")
c3.metric("Low-rated reviews", int((df["rating"] <= 2).sum()))

summary = df.groupby("category").agg(review_count=("review","size"), average_rating=("rating","mean"))
summary["average_rating"] = summary["average_rating"].round(2)
st.subheader("Category Summary")
st.dataframe(summary, use_container_width=True)
st.bar_chart(summary["review_count"])

stop = {"the","and","a","an","to","of","is","was","it","my","for","with","in","on","but","this","that"}
words = []
for text in df["review"].astype(str):
    words += re.findall(r"[A-Za-z']+", text.lower())
terms = Counter(w for w in words if len(w) > 2 and w not in stop)
st.subheader("Recurring Terms")
st.dataframe(pd.DataFrame(terms.most_common(10), columns=["term","mentions"]), use_container_width=True)

st.subheader("Detailed Analysis")
st.dataframe(df[["review","rating","category"]], use_container_width=True)
