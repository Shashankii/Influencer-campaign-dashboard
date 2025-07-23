import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Influencer Campaign Dashboard", layout="wide")
st.title("📊 HealthKart Influencer Campaign Dashboard")

# Load CSVs
influencers = pd.read_csv("data/influencers.csv")
posts = pd.read_csv("data/posts.csv")
tracking = pd.read_csv("data/tracking_data.csv")
payouts = pd.read_csv("data/payouts.csv")

# Sidebar filter: platform
st.sidebar.header("🔍 Filters")
platforms = influencers["platform"].unique().tolist()
selected_platform = st.sidebar.selectbox("Select Platform", ["All"] + platforms)

if selected_platform != "All":
    influencers = influencers[influencers["platform"] == selected_platform]

# Merge data
merged = tracking.merge(influencers, left_on="influencer_id", right_on="id")
merged = merged.merge(payouts, on="influencer_id")

# Check column presence for debugging (optional)
# st.write("Merged columns:", merged.columns.tolist())

# Calculate ROAS
merged["ROAS"] = merged["revenue"] / merged["total_payout"]

# Top influencers table
st.subheader("🏆 Top Influencers by ROAS")
top_influencers = merged.groupby("name")[["revenue", "total_payout"]].sum()
top_influencers["ROAS"] = top_influencers["revenue"] / top_influencers["total_payout"]
top_influencers = top_influencers.sort_values("ROAS", ascending=False).reset_index()
st.dataframe(top_influencers)

# Campaign Performance Table
st.subheader("📈 Campaign Performance")

# Handle missing 'orders' column
campaign_summary = merged.groupby("campaign").agg({
    "revenue": "sum",
    "total_payout": "sum"
})

if 'orders' in merged.columns:
    campaign_summary["orders"] = merged.groupby("campaign")["orders"].sum()

campaign_summary["ROAS"] = campaign_summary["revenue"] / campaign_summary["total_payout"]
st.dataframe(campaign_summary.reset_index())


import plotly.express as px

# Bar Chart: Revenue by Top Influencers
st.subheader("💰 Revenue by Influencers")
rev_chart = top_influencers.sort_values("revenue", ascending=False)
fig1 = px.bar(
    rev_chart,
    x="name",
    y="revenue",
    color="name",
    title="Influencer Revenue",
    labels={"name": "Influencer", "revenue": "Revenue Earned"},
    height=400
)
st.plotly_chart(fig1, use_container_width=True)

# Bar Chart: ROAS by Campaign
st.subheader("📊 ROAS by Campaign")
fig2 = px.bar(
    campaign_summary.reset_index(),
    x="campaign",
    y="ROAS",
    color="campaign",
    title="ROAS per Campaign",
    labels={"campaign": "Campaign", "ROAS": "Return on Ad Spend"},
    height=400
)
st.plotly_chart(fig2, use_container_width=True)


# ---- CSV Export Buttons ----
st.subheader("📤 Export Data")

# Convert to CSV
top_csv = top_influencers.to_csv(index=False).encode("utf-8")
campaign_csv = campaign_summary.reset_index().to_csv(index=False).encode("utf-8")

# Buttons
st.download_button(
    label="⬇️ Download Top Influencers (CSV)",
    data=top_csv,
    file_name="top_influencers.csv",
    mime="text/csv"
)

st.download_button(
    label="⬇️ Download Campaign Summary (CSV)",
    data=campaign_csv,
    file_name="campaign_summary.csv",
    mime="text/csv"
)
