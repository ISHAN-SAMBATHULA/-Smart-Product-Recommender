"""
🏠 Home — Trending & Top-Rated Products
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db_manager

st.set_page_config(page_title="Home | Smart Product Recommender", page_icon="🏠", layout="wide")

st.markdown("""
<div style="margin-bottom: 32px;">
<h1 style="color: #FF9900; font-weight: 800;">🏠 Discover Products</h1>
<p style="color: #8899A6;">Explore trending, top-rated, and popular products across all categories.</p>
</div>
""", unsafe_allow_html=True)

# ─── Trending Products ──────────────────────────────────────────────────────
st.markdown("### 🔥 Trending Now")
trending = db_manager.get_trending_products(n=12)

if not trending.empty:
    cols = st.columns(4)
    for i, (_, row) in enumerate(trending.iterrows()):
        with cols[i % 4]:
            stars = "⭐" * int(round(row.get("avg_rating", 0)))
            st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 16px; margin-bottom: 12px; transition: all 0.3s ease;">
<div style="display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 0.7rem; font-weight: 600; background: rgba(0,168,225,0.15); color: #00A8E1; border: 1px solid rgba(0,168,225,0.3); margin-bottom: 8px;">
{row.get('category', '')}
</div>
<div style="color: #E8EAED; font-size: 0.85rem; font-weight: 600; margin: 6px 0; line-height: 1.4; min-height: 40px;">
{str(row.get('title', ''))[:55]}...
</div>
<div style="color: #FFA41C; font-size: 0.85rem;">{stars} ({row.get('num_ratings', 0)})</div>
<div style="color: #067D62; font-size: 1.2rem; font-weight: 700; margin-top: 6px;">
₹{int(row.get('price', 0)):,}
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Top Rated by Category ──────────────────────────────────────────────────
st.markdown("### 🏆 Top Rated by Category")

categories = db_manager.get_categories()
selected_cat = st.selectbox("Filter by category", ["All"] + categories, key="home_cat")

if selected_cat == "All":
    top = db_manager.get_top_products(n=16)
else:
    top = db_manager.get_top_products(category=selected_cat, n=16)

if not top.empty:
    cols = st.columns(4)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i % 4]:
            stars = "⭐" * int(round(row.get("avg_rating", 0)))
            st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
<div style="color: #00A8E1; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">
{row.get('brand', '')} · {row.get('category', '')}
</div>
<div style="color: #E8EAED; font-size: 0.85rem; font-weight: 600; margin: 8px 0; line-height: 1.4;">
{str(row.get('title', ''))[:55]}
</div>
<div style="color: #FFA41C;">{stars} <span style="color:#8899A6; font-size:0.8rem;">
({row.get('avg_rating', 0):.1f}) · {row.get('num_ratings', 0)} reviews</span>
</div>
<div style="color: #067D62; font-size: 1.2rem; font-weight: 700; margin-top: 8px;">
₹{int(row.get('price', 0)):,}
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("No products found in this category.")
