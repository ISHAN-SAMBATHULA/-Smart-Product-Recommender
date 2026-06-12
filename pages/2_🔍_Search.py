"""
🔍 Search — Full-text product search with filters
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import db_manager

st.set_page_config(page_title="Search | Smart Product Recommender", page_icon="🔍", layout="wide")

st.markdown("""
<div style="margin-bottom: 24px;">
<h1 style="color: #FF9900; font-weight: 800;">🔍 Product Search</h1>
<p style="color: #8899A6;">Search across 5,000+ products with powerful filters.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "Search products",
        placeholder="Try: wireless headphones, yoga mat, coffee maker...",
        key="search_input",
        label_visibility="collapsed",
    )
with col2:
    search_type = st.selectbox("Search in:", ["Local Database", "Live Web (Amazon.in)"], label_visibility="collapsed")

# ─── Filters ─────────────────────────────────────────────────────────────────
with st.expander("🎛️ Advanced Filters", expanded=True):
    filter_cols = st.columns(4)

    with filter_cols[0]:
        categories = db_manager.get_categories()
        category = st.selectbox("Category", ["All"] + categories, key="search_cat")

    with filter_cols[1]:
        price_range = st.slider("Price Range (₹)", 0, 200000, (0, 200000), step=500, key="price_range")

    with filter_cols[2]:
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, step=0.5, key="min_rating")

    with filter_cols[3]:
        sort_by = st.selectbox("Sort By", [
            ("relevance", "Most Relevant"),
            ("discount", "Best Deals (Discount %)"),
            ("rating", "Highest Rated"),
            ("price_low", "Price: Low to High"),
            ("price_high", "Price: High to Low"),
            ("newest", "Newest First"),
        ], format_func=lambda x: x[1], key="sort_by")
        
    platform_filter = st.selectbox("Best Price On Platform", ["All", "Amazon", "Flipkart", "Meesho", "Croma", "Myntra", "JioMart"], key="platform_filter")

# ─── Search Results ──────────────────────────────────────────────────────────
if search_type == "Local Database":
    results = db_manager.search_products(
        query=search_query if search_query else None,
        category=category if category != "All" else None,
        min_price=price_range[0] if price_range[0] > 0 else None,
        max_price=price_range[1] if price_range[1] < 200000 else None,
        min_rating=min_rating if min_rating > 0 else None,
        platform=platform_filter if platform_filter != "All" else None,
        sort_by=sort_by[0],
        limit=60,
    )
else:
    with st.spinner("Scraping live prices from Amazon India..."):
        from data.live_api import search_live_products
        results = search_live_products(search_query)
        if results.empty:
            st.warning("Amazon blocked the scraper with a CAPTCHA. Please try again later or use the Local Database.")

st.markdown(f"""
<div style="color: #8899A6; margin: 16px 0; font-size: 0.9rem;">
    Showing <b style="color: #FF9900;">{len(results)}</b> results
    {f'for "<b style="color:#E8EAED;">{search_query}</b>"' if search_query else ''}
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
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;">
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
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
<div>
<span style="color: #067D62; font-size: 1.4rem; font-weight: 700;">
₹{int(row.get('price', 0)):,}
</span>{f'<br><span style="text-decoration: line-through; color: #8899A6; font-size: 0.85rem;">₹{int(row.get("original_price", 0)):,}</span> <span style="color: #FF9900; font-size: 0.85rem; font-weight: bold;">({int(row.get("discount_percent", 0))}%)</span>' if row.get("discount_percent", 0) > 0 else ''}
</div>{f'<span style="padding: 4px 8px; border-radius: 4px; background: #FF9900; color: #1A1D23; font-weight: bold; font-size: 0.7rem;">Best on {row.get("best_platform", "")}</span>' if row.get("best_platform") else ''}
</div>
{f'<div style="margin-top: 16px;"><a href="{row.get("url")}" target="_blank" style="display: block; text-align: center; background: #FF9900; color: #131722; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">Buy on Amazon</a></div>' if row.get("url") else ''}
</div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<div style="text-align: center; padding: 60px 20px; color: #8899A6;">
<div style="font-size: 3rem; margin-bottom: 16px;">🔍</div>
<div style="font-size: 1.1rem;">No products found. Try a different search or adjust filters.</div>
</div>
""", unsafe_allow_html=True)
