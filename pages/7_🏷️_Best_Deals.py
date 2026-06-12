"""
🏷️ Best Deals — Discover top discounts across platforms
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db_manager

st.set_page_config(page_title="Best Deals | Smart Product Recommender", page_icon="🏷️", layout="wide")

st.markdown("""
<div style="margin-bottom: 24px;">
<h1 style="color: #FF9900; font-weight: 800;">🏷️ Best Deals Today</h1>
<p style="color: #8899A6;">Find the highest discounts across multiple e-commerce platforms.</p>
</div>
""", unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────────────
filter_cols = st.columns(3)

with filter_cols[0]:
    categories = db_manager.get_categories()
    category = st.selectbox("Category", ["All"] + categories, key="deals_cat")

with filter_cols[1]:
    platform = st.selectbox("Best Price On Platform", ["All", "Amazon", "Flipkart", "Meesho", "Croma", "Myntra", "JioMart"], key="deals_plat")

with filter_cols[2]:
    min_discount = st.slider("Minimum Discount %", 10, 90, 30, step=10, key="min_discount")

# ─── Search Results ──────────────────────────────────────────────────────────
results = db_manager.get_best_deals(
    limit=60,
    category=category if category != "All" else None,
    min_discount=min_discount,
    platform=platform if platform != "All" else None
)

st.markdown(f"""
<div style="color: #8899A6; margin: 16px 0; font-size: 0.9rem;">
    Showing <b style="color: #FF9900;">{len(results)}</b> top deals
</div>
""", unsafe_allow_html=True)

if not results.empty:
    # Grid layout
    cols = st.columns(3)
    for i, (_, row) in enumerate(results.iterrows()):
        with cols[i % 3]:
            stars = "⭐" * int(round(row.get("avg_rating", 0)))
            pid = row["product_id"]

            st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease; position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; right: 0; background: #FF9900; color: #1A1D23; padding: 4px 12px; border-bottom-left-radius: 12px; font-weight: 800; font-size: 0.85rem;">
{int(row.get('discount_percent', 0))}% OFF
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="padding: 3px 10px; border-radius: 15px; font-size: 0.7rem; font-weight: 600; background: rgba(0,168,225,0.15); color: #00A8E1; border: 1px solid rgba(0,168,225,0.3);">
{row.get('category', '')}
</span>
<span style="color: #8899A6; font-size: 0.75rem;">ID: {pid}</span>
</div>
<div style="color: #00A8E1; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">
{row.get('brand', '')}
</div>
<div style="color: #E8EAED; font-size: 0.95rem; font-weight: 600; margin: 8px 0; line-height: 1.5; min-height: 50px;">
{str(row.get('title', ''))[:80]}
</div>
<div style="color: #FFA41C; margin: 8px 0;">
{stars} <span style="color:#8899A6; font-size:0.8rem;">
({row.get('avg_rating', 0):.1f}) · {row.get('num_ratings', 0)} reviews</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 12px;">
<div>
<span style="text-decoration: line-through; color: #8899A6; font-size: 0.85rem;">₹{int(row.get("original_price", 0)):,}</span>
<br>
<span style="color: #067D62; font-size: 1.4rem; font-weight: 700;">
₹{int(row.get('price', 0)):,}
</span>
</div>{f'<span style="padding: 4px 8px; border-radius: 4px; background: rgba(0,168,225,0.15); color: #00A8E1; border: 1px solid rgba(0,168,225,0.3); font-weight: bold; font-size: 0.7rem;">Best on {row.get("best_platform", "")}</span>' if row.get("best_platform") else ''}
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<div style="text-align: center; padding: 60px 20px; color: #8899A6;">
<div style="font-size: 3rem; margin-bottom: 16px;">🏷️</div>
<div style="font-size: 1.1rem;">No deals found matching your criteria.</div>
</div>
""", unsafe_allow_html=True)
