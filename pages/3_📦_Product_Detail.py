"""
📦 Product Detail — Detailed product view with ML recommendations
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
from database import db_manager
from utils.visualizations import product_rating_breakdown, recommendation_comparison_chart

st.set_page_config(page_title="Product Detail | Smart Product Recommender", page_icon="📦", layout="wide")

st.markdown("""
<div style="margin-bottom: 24px;">
<h1 style="color: #FF9900; font-weight: 800;">📦 Product Detail</h1>
<p style="color: #8899A6;">View product info, reviews, and AI-powered recommendations.</p>
</div>
""", unsafe_allow_html=True)

# ─── Product Selector ────────────────────────────────────────────────────────
products_df = st.session_state.get("products_df")
hybrid_model = st.session_state.get("hybrid_model")

if products_df is None or hybrid_model is None:
    st.warning("⚠️ Please visit the main page first to initialize the system.")
    st.stop()

product_id = st.number_input("Enter Product ID", min_value=1, max_value=5000, value=1, step=1, key="product_id_input")

product = db_manager.get_product(product_id)

if product.empty:
    st.error("Product not found.")
    st.stop()

p = product.iloc[0]

# ─── Product Info ────────────────────────────────────────────────────────────
info_col, detail_col = st.columns([2, 3])

with info_col:
    model_str = f" · {p.get('model_variant')}" if p.get('model_variant') else ""
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 16px; padding: 24px;">
<div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #22252D, #2A2D35); border-radius: 12px; margin-bottom: 16px;">
<div style="font-size: 4rem;">📦</div>
</div>
<div style="padding: 3px 10px; border-radius: 15px; font-size: 0.7rem; font-weight: 600; background: rgba(0,168,225,0.15); color: #00A8E1; border: 1px solid rgba(0,168,225,0.3); display: inline-block; margin-bottom: 8px;">
{p.get('category', '')} · {p.get('sub_category', '')}
</div>
<div style="color: #00A8E1; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">
{p.get('brand', '')}{model_str}
</div>
<div style="margin-top: 20px; border-top: 1px solid #2A2D35; padding-top: 16px;">
<div style="color: #8899A6; font-size: 0.85rem; margin-bottom: 8px;">
🚚 <b>Delivery:</b> {p.get('delivery_days', 3)} days
</div>
<div style="color: #8899A6; font-size: 0.85rem; margin-bottom: 8px;">
💳 <b>EMI:</b> {"Available" if p.get('emi_available', 0) else "Not Available"}
</div>
<div style="color: {'#067D62' if p.get('availability', '') == 'In Stock' else '#FF9900' if 'Limited' in p.get('availability', '') else '#D93025'}; font-size: 0.85rem; font-weight: 600;">
📦 <b>Status:</b> {p.get('availability', 'In Stock')}
</div>
</div>
</div>
""", unsafe_allow_html=True)

with detail_col:
    stars = "⭐" * int(round(p.get("avg_rating", 0)))
    
    # Process platform data
    prices = {}
    urls = {}
    try:
        if p.get('platform_prices'):
            prices = json.loads(p.get('platform_prices'))
        if p.get('platform_urls'):
            urls = json.loads(p.get('platform_urls'))
    except:
        pass
        
    best_platform = p.get('best_platform', '')
    
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 16px; padding: 28px;">
<h2 style="color: #E8EAED; font-weight: 700; line-height: 1.4; margin-bottom: 12px;">
{p.get('title', '')}
</h2>
<div style="color: #FFA41C; font-size: 1.1rem; margin-bottom: 12px;">
{stars}
<span style="color: #8899A6; font-size: 0.9rem;">
{p.get('avg_rating', 0):.1f} out of 5 · {p.get('num_ratings', 0)} ratings
</span>
</div>
<div style="display: flex; align-items: flex-end; gap: 12px; margin: 16px 0;">
<div style="color: #067D62; font-size: 2.2rem; font-weight: 800; line-height: 1;">
₹{int(p.get('price', 0)):,}
</div>{f'<div style="text-decoration: line-through; color: #8899A6; font-size: 1.2rem; line-height: 1.4;">₹{int(p.get("original_price", 0)):,}</div>' if p.get('discount_percent', 0) > 0 else ''}{f'<div style="color: #FF9900; font-size: 1.2rem; font-weight: 800; line-height: 1.4;">{int(p.get("discount_percent", 0))}% OFF</div>' if p.get('discount_percent', 0) > 0 else ''}
</div>
<h4 style="color: #E8EAED; margin-top: 24px; margin-bottom: 12px;">⚖️ Where to Buy</h4>
<div style="border: 1px solid #2A2D35; border-radius: 8px; overflow: hidden;">
""", unsafe_allow_html=True)
    
    # Render Platform Table Rows
    for plat, price in sorted(prices.items(), key=lambda x: x[1]):
        is_best = plat == best_platform
        bg_color = "rgba(0, 168, 225, 0.05)" if is_best else "transparent"
        border_col = "#00A8E1" if is_best else "transparent"
        badge = '<span style="background: #FF9900; color: #131722; font-size: 0.6rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; margin-left: 8px;">Best Price</span>' if is_best else ''
        
        st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: {bg_color}; border-left: 4px solid {border_col}; border-bottom: 1px solid #2A2D35;">
<div style="display: flex; align-items: center;">
<span style="font-weight: 600; color: #E8EAED;">{plat}</span>{badge}
</div>
<div style="display: flex; align-items: center; gap: 16px;">
<span style="color: #067D62; font-weight: 700; font-size: 1.1rem;">₹{int(price):,}</span>
<a href="{urls.get(plat, '#')}" target="_blank" style="background: #FF9900; color: #131722; text-decoration: none; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">Buy Now</a>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
</div>
<div style="color: #8899A6; font-size: 0.9rem; line-height: 1.8; margin-top: 24px; padding-top: 16px; border-top: 1px solid #2A2D35;">
{p.get('description', 'No description available.')}
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Rating Breakdown ────────────────────────────────────────────────────────
ratings_data = db_manager.get_product_ratings(product_id)

if not ratings_data.empty:
    rb_col, rev_col = st.columns([1, 2])

    with rb_col:
        st.markdown("### 📊 Rating Breakdown")
        fig = product_rating_breakdown(ratings_data)
        st.plotly_chart(fig, use_container_width=True)

    with rev_col:
        st.markdown("### 💬 Recent Reviews")
        for _, review in ratings_data.head(5).iterrows():
            r_stars = "⭐" * int(review["rating"])
            st.markdown(f"""
<div style="background: #1A1D23; border: 1px solid #2A2D35; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
<span style="color: #00A8E1; font-weight: 600; font-size: 0.85rem;">
👤 {review.get('username', 'Anonymous')}
</span>
<span style="color: #8899A6; font-size: 0.75rem;">{review.get('review_date', '')}</span>
</div>
<div style="color: #FFA41C; font-size: 0.85rem;">{r_stars}</div>
<div style="color: #E8EAED; font-size: 0.85rem; margin-top: 6px; line-height: 1.5;">
{str(review.get('review_text', ''))[:200]}
</div>
<div style="color: #8899A6; font-size: 0.75rem; margin-top: 4px;">
👍 {review.get('helpful_votes', 0)} helpful
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Similar Products (Content-Based) ───────────────────────────────────────
st.markdown("### 👀 Customers Who Viewed This Also Viewed")
st.caption("*Content-Based Filtering — products with similar features*")

similar = hybrid_model.get_similar_products(product_id, n=8)

if not similar.empty:
    cols = st.columns(4)
    for i, (_, row) in enumerate(similar.iterrows()):
        with cols[i % 4]:
            s_stars = "⭐" * int(round(row.get("avg_rating", 0)))
            sim_pct = int(row.get("similarity_score", 0) * 100)
            st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
<span style="padding: 2px 8px; border-radius: 12px; font-size: 0.65rem; background: rgba(0,168,225,0.15); color: #00A8E1; border: 1px solid rgba(0,168,225,0.3);">
{row.get('category', '')}
</span>
<span style="padding: 2px 8px; border-radius: 12px; font-size: 0.65rem; background: rgba(255,153,0,0.15); color: #FF9900; border: 1px solid rgba(255,153,0,0.3);">
{sim_pct}% match
</span>
</div>
<div style="color: #E8EAED; font-size: 0.8rem; font-weight: 600; margin: 6px 0; line-height: 1.4; min-height: 36px;">
{str(row.get('title', ''))[:50]}
</div>
<div style="color: #FFA41C; font-size: 0.8rem;">{s_stars}</div>
<div style="color: #067D62; font-size: 1.1rem; font-weight: 700; margin-top: 6px;">
₹{int(row.get('price', 0)):,}
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("No similar products found.")

# ─── Personalized Recommendations (Hybrid) ──────────────────────────────────
st.divider()
st.markdown("### 🎯 Recommended For You")
st.caption("*Hybrid Engine — personalized based on your ratings and similar users*")

user_id = st.session_state.get("selected_user_id", 1)
recs = hybrid_model.get_recommendations(user_id, n=8)

if not recs.empty:
    # Score breakdown chart
    st.plotly_chart(recommendation_comparison_chart(recs), use_container_width=True)

    cols = st.columns(4)
    for i, (_, row) in enumerate(recs.iterrows()):
        with cols[i % 4]:
            r_stars = "⭐" * int(round(row.get("avg_rating", 0)))
            h_score = int(row.get("hybrid_score", 0) * 100)
            st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
<div style="padding: 2px 8px; border-radius: 12px; font-size: 0.65rem; background: rgba(255,153,0,0.15); color: #FF9900; border: 1px solid rgba(255,153,0,0.3); display: inline-block;">
Score: {h_score}%
</div>
<div style="color: #E8EAED; font-size: 0.85rem; font-weight: 600; margin: 8px 0; line-height: 1.4;">
{str(row.get('title', ''))[:55]}
</div>
<div style="color: #FFA41C; font-size: 0.8rem;">{r_stars}</div>
<div style="color: #067D62; font-size: 1.1rem; font-weight: 700; margin-top: 6px;">
₹{int(row.get('price', 0)):,}
</div>
</div>
""", unsafe_allow_html=True)
