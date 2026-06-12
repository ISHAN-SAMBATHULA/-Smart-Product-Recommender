"""
Amazon Product Recommendation System
Main entry point — sets up the Streamlit app, initializes models, and manages state.
"""

import streamlit as st
import sys
import os

# Self-clean: Remove the unnecessary user profile page file
profile_page = os.path.join("pages", "4_👤_User_Profile.py")
if os.path.exists(profile_page):
    try:
        os.remove(profile_page)
    except Exception:
        pass

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import ensure_data_ready
from database import db_manager

# ─── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Product Recommender",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] {
font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar styling */
[data-testid="stSidebar"] {
background: linear-gradient(180deg, #131722 0%, #1A1D23 100%);
border-right: 1px solid #2A2D35;
}

/* Card styling */
.product-card {
background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%);
border: 1px solid #2A2D35;
border-radius: 12px;
padding: 20px;
margin: 10px 0;
transition: all 0.3s ease;
box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.product-card:hover {
border-color: #FF9900;
transform: translateY(-2px);
box-shadow: 0 8px 25px rgba(255, 153, 0, 0.15);
}

/* Metric card */
.metric-card {
background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%);
border: 1px solid #2A2D35;
border-radius: 12px;
padding: 24px;
text-align: center;
box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.metric-value {
font-size: 2.2rem;
font-weight: 800;
color: #FF9900;
margin: 8px 0;
}
.metric-label {
font-size: 0.85rem;
color: #8899A6;
text-transform: uppercase;
letter-spacing: 1px;
}

/* Hero section */
.hero-section {
background: linear-gradient(135deg, #131722 0%, #1E2330 50%, #232F3E 100%);
border-radius: 16px;
padding: 48px 40px;
margin-bottom: 32px;
border: 1px solid #2A2D35;
position: relative;
overflow: hidden;
}
.hero-section::before {
content: '';
position: absolute;
top: -50%;
right: -20%;
width: 400px;
height: 400px;
background: radial-gradient(circle, rgba(255,153,0,0.08) 0%, transparent 70%);
border-radius: 50%;
}
.hero-title {
font-size: 2.5rem;
font-weight: 800;
background: linear-gradient(135deg, #FF9900 0%, #FFC46B 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
margin-bottom: 12px;
}
.hero-subtitle {
color: #8899A6;
font-size: 1.1rem;
line-height: 1.6;
max-width: 600px;
}

/* Star rating */
.stars {
color: #FFA41C;
font-size: 1.1rem;
}

/* Badge */
.badge {
display: inline-block;
padding: 4px 12px;
border-radius: 20px;
font-size: 0.75rem;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.5px;
}
.badge-category {
background: rgba(0, 168, 225, 0.15);
color: #00A8E1;
border: 1px solid rgba(0, 168, 225, 0.3);
}
.badge-score {
background: rgba(255, 153, 0, 0.15);
color: #FF9900;
border: 1px solid rgba(255, 153, 0, 0.3);
}

/* Recommendation section */
.rec-header {
font-size: 1.3rem;
font-weight: 700;
color: #E8EAED;
margin: 24px 0 16px 0;
padding-bottom: 8px;
border-bottom: 2px solid #FF9900;
display: inline-block;
}

/* Scrollable section */
.scroll-section {
overflow-x: auto;
white-space: nowrap;
padding: 10px 0;
}

/* Price tag */
.price-tag {
font-size: 1.5rem;
font-weight: 700;
color: #067D62;
}

/* Streamlit overrides */
.stSelectbox label, .stSlider label, .stTextInput label {
color: #E8EAED !important;
font-weight: 500 !important;
}

div[data-testid="stMetricValue"] {
font-size: 1.8rem;
color: #FF9900;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
gap: 8px;
}
.stTabs [data-baseweb="tab"] {
border-radius: 8px;
padding: 8px 20px;
}
</style>
""", unsafe_allow_html=True)


# ─── Initialize Data ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔧 Generating dataset & training models...")
def initialize_system():
    """One-time initialization: generate data, fit models."""
    ensure_data_ready()

    products_df = db_manager.get_all_products()
    ratings_df = db_manager.get_all_ratings()

    from models.hybrid import HybridRecommender
    hybrid = HybridRecommender(alpha=0.4)
    hybrid.fit(products_df, ratings_df)

    return hybrid, products_df, ratings_df


# Initialize
hybrid_model, products_df, ratings_df = initialize_system()

# Store in session state for pages
st.session_state["hybrid_model"] = hybrid_model
st.session_state["products_df"] = products_df
st.session_state["ratings_df"] = ratings_df

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align: center; padding: 20px 0;">
<div style="font-size: 2.5rem;">🛒</div>
<div style="font-size: 1.2rem; font-weight: 700; color: #FF9900; margin-top: 8px;">
Smart Recommender
</div>
<div style="font-size: 0.75rem; color: #8899A6; margin-top: 4px;">
ML-Powered Product Discovery
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Silently set a default user context for recommendations
    if "selected_user_id" not in st.session_state:
        st.session_state["selected_user_id"] = 1

    st.markdown("""
<div style="padding: 12px; text-align: center; margin-top: 50px;">
<div style="font-size: 0.8rem; color: #8899A6;">
built by ishan with love ❤️
</div>
</div>
""", unsafe_allow_html=True)



# ─── Main Page Content ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
<div class="hero-title">🛒 Smart Product Recommender</div>
<div class="hero-subtitle">
A production-grade recommendation system powered by <b>Content-Based Filtering</b>,
<b>Collaborative Filtering (SVD)</b>, and a <b>Weighted Hybrid Engine</b> —
built to demonstrate real-world ML engineering.
</div>
</div>
""", unsafe_allow_html=True)



# ─── Algorithms Overview ────────────────────────────────────────────────────
st.markdown('<div class="rec-header">🧠 Recommendation Algorithms</div>', unsafe_allow_html=True)

algo_col1, algo_col2, algo_col3 = st.columns(3)

with algo_col1:
    st.markdown("""
<div class="product-card">
<h4 style="color: #00A8E1;">📝 Content-Based Filtering</h4>
<p style="color: #8899A6; font-size: 0.85rem; line-height: 1.6;">
Uses <b>TF-IDF vectorization</b> on product titles, descriptions, and categories.
Computes <b>cosine similarity</b> to find products with similar features.
</p>
<div class="badge badge-category">TF-IDF + Cosine Similarity</div>
</div>
""", unsafe_allow_html=True)

with algo_col2:
    st.markdown("""
<div class="product-card">
<h4 style="color: #067D62;">🤝 Collaborative Filtering</h4>
<p style="color: #8899A6; font-size: 0.85rem; line-height: 1.6;">
Leverages <b>user-item interaction data</b> with User-User CF, Item-Item CF,
and <b>SVD matrix factorization</b> to discover latent preference patterns.
</p>
<div class="badge badge-category">SVD + KNN</div>
</div>
""", unsafe_allow_html=True)

with algo_col3:
    st.markdown("""
<div class="product-card">
<h4 style="color: #FF9900;">🔀 Hybrid Engine</h4>
<p style="color: #8899A6; font-size: 0.85rem; line-height: 1.6;">
Combines both approaches: <b>α × content + (1-α) × collaborative</b>.
Handles cold-start users with automatic fallback to popularity-based ranking.
</p>
<div class="badge badge-score">Weighted Ensemble</div>
</div>
""", unsafe_allow_html=True)

# ─── Quick Recommendations ──────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="rec-header">🎯 Quick Recommendations for You</div>', unsafe_allow_html=True)

user_id = st.session_state.get("selected_user_id", 1)
recs = hybrid_model.get_recommendations(user_id, n=8)

if not recs.empty:
    cols = st.columns(4)
    for i, (_, row) in enumerate(recs.head(8).iterrows()):
        with cols[i % 4]:
            rating_stars = "⭐" * int(round(row.get("avg_rating", 0)))
            score_pct = int(row.get("hybrid_score", 0) * 100)
            st.markdown(f"""
<div class="product-card">
<div class="badge badge-category">{row.get('category', 'N/A')}</div>
<h4 style="color: #E8EAED; margin: 8px 0; font-size: 0.9rem; line-height: 1.4;">
{str(row.get('title', ''))[:60]}
</h4>
<div class="stars">{rating_stars}</div>
<div style="margin-top: 8px;">
<span class="price-tag">₹{int(row.get('price', 0)):,}</span>
</div>
<div style="margin-top: 8px;">
<span class="badge badge-score">Match: {score_pct}%</span>
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("Select a user from the sidebar to see personalized recommendations.")

# ─── Navigate ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="rec-header">📍 Explore</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    st.page_link("pages/2_🔍_Search.py", label="🔍 Search Products", icon="🔍")
    st.page_link("pages/3_📦_Product_Detail.py", label="📦 Product Details", icon="📦")
with nav_col2:
    st.page_link("pages/7_🏷️_Best_Deals.py", label="🏷️ Best Deals", icon="🏷️")
    st.page_link("pages/5_📊_Analytics.py", label="📊 Analytics", icon="📊")
with nav_col3:
    st.page_link("pages/6_🧪_Model_Evaluation.py", label="🧪 Model Evaluation", icon="🧪")
