"""
📊 Analytics — Data visualizations and insights dashboard
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db_manager
from utils.visualizations import (
    rating_distribution_chart,
    category_distribution_chart,
    top_products_chart,
    price_vs_rating_scatter,
    user_activity_chart,
    ratings_over_time_chart,
)

st.set_page_config(page_title="Analytics | Smart Product Recommender", page_icon="📊", layout="wide")

st.markdown("""
<div style="margin-bottom: 24px;">
<h1 style="color: #FF9900; font-weight: 800;">📊 Analytics Dashboard</h1>
<p style="color: #8899A6;">Explore data patterns, trends, and insights across the product catalog.</p>
</div>
""", unsafe_allow_html=True)

# ─── Load Data ───────────────────────────────────────────────────────────────
products_df = st.session_state.get("products_df")
ratings_df = st.session_state.get("ratings_df")

if products_df is None or ratings_df is None:
    st.warning("⚠️ Please visit the main page first to initialize the system.")
    st.stop()

# ─── Key Metrics ─────────────────────────────────────────────────────────────
stats = db_manager.get_stats()

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("📦 Products", f"{stats['total_products']:,}")
m2.metric("👤 Users", f"{stats['total_users']:,}")
m3.metric("⭐ Reviews", f"{stats['total_ratings']:,}")
m4.metric("📊 Avg Rating", f"{stats['avg_rating']}")
m5.metric("🏷️ Categories", stats['categories'])
m6.metric("🏢 Brands", stats['brands'])

st.divider()

# ─── Charts Grid ─────────────────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    st.plotly_chart(rating_distribution_chart(ratings_df), use_container_width=True)

with chart2:
    st.plotly_chart(user_activity_chart(ratings_df), use_container_width=True)

st.divider()

# Category treemap
st.plotly_chart(category_distribution_chart(products_df), use_container_width=True)

st.divider()

chart3, chart4 = st.columns(2)

with chart3:
    st.plotly_chart(top_products_chart(products_df, n=15), use_container_width=True)

with chart4:
    st.plotly_chart(price_vs_rating_scatter(products_df), use_container_width=True)

st.divider()

# Timeline
st.plotly_chart(ratings_over_time_chart(ratings_df), use_container_width=True)

st.divider()

# ─── Category Statistics Table ───────────────────────────────────────────────
st.markdown("### 📋 Category Statistics")

cat_stats = products_df.groupby("category").agg(
    Products=("product_id", "count"),
    Avg_Price=("price", "mean"),
    Avg_Rating=("avg_rating", "mean"),
    Total_Reviews=("num_ratings", "sum"),
    Top_Brand=("brand", lambda x: x.value_counts().index[0] if len(x) > 0 else "N/A"),
).round(2).reset_index()

cat_stats.columns = ["Category", "Products", "Avg Price (₹)", "Avg Rating", "Total Reviews", "Top Brand"]
cat_stats = cat_stats.sort_values("Total Reviews", ascending=False)

st.dataframe(
    cat_stats,
    use_container_width=True,
    height=500,
    column_config={
        "Avg Price (₹)": st.column_config.NumberColumn(format="₹%d"),
        "Avg Rating": st.column_config.NumberColumn(format="%.2f ⭐"),
        "Total Reviews": st.column_config.NumberColumn(format="%d"),
    }
)
