"""
🧪 Model Evaluation — ML metrics dashboard with side-by-side model comparison
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.evaluator import ModelEvaluator
from utils.visualizations import model_performance_radar

st.set_page_config(page_title="Model Evaluation | Smart Product Recommender", page_icon="🧪", layout="wide")

st.markdown("""
<div style="margin-bottom: 24px;">
<h1 style="color: #FF9900; font-weight: 800;">🧪 Model Evaluation</h1>
<p style="color: #8899A6;">
Comprehensive ML metrics — Precision, Recall, RMSE, MAP, Coverage & Novelty.
<br>This section demonstrates rigorous model evaluation with train/test splits.
</p>
</div>
""", unsafe_allow_html=True)

hybrid_model = st.session_state.get("hybrid_model")
products_df = st.session_state.get("products_df")
ratings_df = st.session_state.get("ratings_df")

if hybrid_model is None or products_df is None or ratings_df is None:
    st.warning("⚠️ Please visit the main page first to initialize the system.")
    st.stop()

# ─── Configuration ───────────────────────────────────────────────────────────
st.markdown("### ⚙️ Evaluation Configuration")

config_col1, config_col2, config_col3 = st.columns(3)

with config_col1:
    k_value = st.slider("K (top-K recommendations)", 5, 20, 10, key="k_eval")

with config_col2:
    test_size = st.slider("Test set size", 0.1, 0.3, 0.2, 0.05, key="test_size")

with config_col3:
    relevance_threshold = st.slider("Relevance threshold", 3.0, 5.0, 4.0, 0.5,
                                     help="Minimum rating to consider relevant",
                                     key="rel_thresh")

st.divider()

# ─── Run Evaluation ──────────────────────────────────────────────────────────
if st.button("🚀 Run Full Evaluation", type="primary", use_container_width=True):
    evaluator = ModelEvaluator(
        test_size=test_size,
        relevance_threshold=relevance_threshold,
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(pct, text):
        progress_bar.progress(pct)
        status_text.text(text)

    with st.spinner("Running comprehensive evaluation..."):
        results = evaluator.full_evaluation(
            hybrid_model=hybrid_model,
            cf_model=hybrid_model.cf_model,
            ratings_df=ratings_df,
            products_df=products_df,
            k=k_value,
            progress_callback=update_progress,
        )

    progress_bar.progress(1.0)
    status_text.text("✅ Evaluation complete!")

    st.session_state["eval_results"] = results

# ─── Display Results ─────────────────────────────────────────────────────────
results = st.session_state.get("eval_results")

if results:
    st.markdown("---")
    st.markdown("### 📊 Evaluation Results")

    # ── SVD Metrics Cards ────────────────────────────────────────────
    svd_results = results.get("SVD (Collaborative)", {})
    ucf_results = results.get("User-User CF", {})

    st.markdown("#### 🤝 Collaborative Filtering — SVD")

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        rmse_val = svd_results.get("rmse", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">RMSE</div>
<div style="color: #FF9900; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{rmse_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Lower is better</div>
</div>
""", unsafe_allow_html=True)

    with m2:
        mae_val = svd_results.get("mae", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">MAE</div>
<div style="color: #00A8E1; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{mae_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Lower is better</div>
</div>
""", unsafe_allow_html=True)

    with m3:
        prec_val = svd_results.get(f"precision@{k_value}", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Precision@{k_value}</div>
<div style="color: #067D62; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{prec_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Higher is better</div>
</div>
""", unsafe_allow_html=True)

    with m4:
        recall_val = svd_results.get(f"recall@{k_value}", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Recall@{k_value}</div>
<div style="color: #FFA41C; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{recall_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Higher is better</div>
</div>
""", unsafe_allow_html=True)

    with m5:
        cov_val = svd_results.get("coverage", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Coverage</div>
<div style="color: #E31C3D; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{cov_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Higher is better</div>
</div>
""", unsafe_allow_html=True)

    with m6:
        nov_val = svd_results.get("novelty", "N/A")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1A1D23 0%, #22252D 100%); border: 1px solid #2A2D35; border-radius: 12px; padding: 20px; text-align: center;">
<div style="color: #8899A6; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Novelty</div>
<div style="color: #9C27B0; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{nov_val}</div>
<div style="color: #8899A6; font-size: 0.7rem;">Higher is better</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── User-User CF ─────────────────────────────────────────────────
    st.markdown("#### 🧑‍🤝‍🧑 User-User Collaborative Filtering")
    ucf_col1, ucf_col2, ucf_col3 = st.columns(3)
    with ucf_col1:
        st.metric("RMSE", ucf_results.get("rmse", "N/A"))
    with ucf_col2:
        st.metric("MAE", ucf_results.get("mae", "N/A"))
    with ucf_col3:
        st.metric("Predictions", ucf_results.get("n_predictions", "N/A"))

    st.divider()

    # ── Radar Chart ──────────────────────────────────────────────────
    st.markdown("### 🕸️ Model Comparison Radar")

    radar_data = {}
    for model_name, metrics in results.items():
        if isinstance(metrics.get("rmse"), (int, float)):
            radar_data[model_name] = metrics

    if radar_data:
        fig = model_performance_radar(radar_data)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Raw Results Table ────────────────────────────────────────────
    st.markdown("### 📋 Detailed Results")

    for model_name, metrics in results.items():
        with st.expander(f"📌 {model_name}", expanded=False):
            for key, value in metrics.items():
                st.markdown(f"**{key}**: `{value}`")

    # ── Metric Explanations ──────────────────────────────────────────
    st.divider()
    st.markdown("### 📖 Metric Explanations")

    with st.expander("What do these metrics mean?", expanded=False):
        st.markdown("""
| Metric | Description | Good Value |
|--------|-------------|------------|
| **RMSE** | Root Mean Squared Error — measures rating prediction error | < 1.0 |
| **MAE** | Mean Absolute Error — average prediction error magnitude | < 0.8 |
| **Precision@K** | Of the top-K recommended, how many are actually relevant? | > 0.2 |
| **Recall@K** | Of all relevant items, how many appear in top-K? | > 0.1 |
| **MAP@K** | Mean Average Precision — overall ranking quality | > 0.1 |
| **Coverage** | What fraction of the catalog gets recommended? | > 0.5 |
| **Novelty** | How surprising/non-obvious are recommendations? | > 5.0 |
""")

else:
    st.markdown("""
<div style="text-align: center; padding: 80px 20px; color: #8899A6;">
<div style="font-size: 4rem; margin-bottom: 16px;">🧪</div>
<div style="font-size: 1.2rem; margin-bottom: 8px;">No evaluation results yet</div>
<div style="font-size: 0.9rem;">Click <b>"Run Full Evaluation"</b> above to compute comprehensive ML metrics with train/test splits.</div>
</div>
""", unsafe_allow_html=True)
