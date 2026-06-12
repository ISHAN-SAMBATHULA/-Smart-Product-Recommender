"""
Data Visualizations — Interactive Plotly charts for the analytics dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ─── Color palette ──────────────────────────────────────────────────────────
COLORS = {
    "primary": "#FF9900",
    "secondary": "#232F3E",
    "accent": "#00A8E1",
    "success": "#067D62",
    "warning": "#FFA41C",
    "danger": "#E31C3D",
    "bg": "#0F1116",
    "card": "#1A1D23",
    "text": "#E8EAED",
    "muted": "#8899A6",
}

PLOTLY_TEMPLATE = "plotly_dark"
CATEGORY_COLORS = px.colors.qualitative.Set3


def rating_distribution_chart(ratings_df):
    """Interactive histogram of rating distribution."""
    fig = px.histogram(
        ratings_df, x="rating",
        nbins=5,
        color_discrete_sequence=[COLORS["primary"]],
        title="⭐ Rating Distribution",
        labels={"rating": "Rating", "count": "Number of Reviews"},
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        bargap=0.1,
        xaxis=dict(tickvals=[1, 2, 3, 4, 5]),
        font=dict(color=COLORS["text"]),
    )
    return fig


def category_distribution_chart(products_df):
    """Treemap of product categories."""
    cat_counts = products_df.groupby("category").agg(
        count=("product_id", "count"),
        avg_rating=("avg_rating", "mean"),
        avg_price=("price", "mean"),
    ).reset_index()

    fig = px.treemap(
        cat_counts,
        path=["category"],
        values="count",
        color="avg_rating",
        color_continuous_scale=["#E31C3D", "#FFA41C", "#067D62"],
        title="📦 Product Categories (size = count, color = avg rating)",
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
    )
    return fig


def top_products_chart(products_df, n=15):
    """Horizontal bar chart of top-rated products."""
    top = products_df.nlargest(n, "avg_rating")
    top = top.sort_values("avg_rating")

    # Truncate long titles
    top["short_title"] = top["title"].apply(lambda x: x[:40] + "..." if len(str(x)) > 40 else x)

    fig = px.bar(
        top,
        x="avg_rating",
        y="short_title",
        orientation="h",
        color="avg_rating",
        color_continuous_scale=["#FFA41C", "#FF9900", "#067D62"],
        title=f"🏆 Top {n} Highest Rated Products",
        labels={"avg_rating": "Average Rating", "short_title": "Product"},
        hover_data=["category", "brand", "num_ratings", "price"],
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=500,
        yaxis=dict(tickfont=dict(size=10)),
    )
    return fig


def price_vs_rating_scatter(products_df):
    """Scatter plot of price vs rating colored by category."""
    # Sample for performance
    sample = products_df.sample(n=min(1000, len(products_df)), random_state=42)

    fig = px.scatter(
        sample,
        x="price",
        y="avg_rating",
        color="category",
        size="num_ratings",
        size_max=15,
        opacity=0.7,
        title="💰 Price vs. Rating by Category",
        labels={"price": "Price ($)", "avg_rating": "Average Rating"},
        hover_data=["title", "brand"],
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=500,
    )
    return fig


def user_activity_chart(ratings_df):
    """Distribution of ratings per user."""
    user_counts = ratings_df.groupby("user_id").size().reset_index(name="num_ratings")

    fig = px.histogram(
        user_counts,
        x="num_ratings",
        nbins=30,
        color_discrete_sequence=[COLORS["accent"]],
        title="👤 User Activity Distribution",
        labels={"num_ratings": "Number of Ratings", "count": "Number of Users"},
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
    )
    return fig


def recommendation_comparison_chart(recommendations_df):
    """Compare hybrid vs content vs CF scores for recommended products."""
    if recommendations_df.empty:
        return go.Figure()

    top = recommendations_df.head(10).copy()
    top["short_title"] = top["title"].apply(lambda x: str(x)[:30] + "..." if len(str(x)) > 30 else str(x))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Content Score",
        x=top["short_title"],
        y=top["content_score"],
        marker_color=COLORS["accent"],
    ))
    fig.add_trace(go.Bar(
        name="CF Score",
        x=top["short_title"],
        y=top["cf_score"],
        marker_color=COLORS["success"],
    ))
    fig.add_trace(go.Bar(
        name="Hybrid Score",
        x=top["short_title"],
        y=top["hybrid_score"],
        marker_color=COLORS["primary"],
    ))

    fig.update_layout(
        barmode="group",
        title="🔀 Recommendation Score Breakdown",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        xaxis_tickangle=-45,
        height=450,
    )
    return fig


def model_performance_radar(metrics_dict):
    """
    Radar chart comparing model performance across metrics.
    
    Args:
        metrics_dict: Dict like {"Model A": {"precision": 0.3, "recall": 0.2, ...}, ...}
    """
    fig = go.Figure()

    metric_names = ["RMSE (inv)", "Precision@10", "Recall@10", "MAP@10", "Coverage", "Novelty"]

    for model_name, metrics in metrics_dict.items():
        values = [
            1 - min(metrics.get("rmse", 1.0), 2.0) / 2.0 if isinstance(metrics.get("rmse"), (int, float)) else 0.5,
            metrics.get("precision@10", 0),
            metrics.get("recall@10", 0),
            metrics.get("map@10", 0),
            metrics.get("coverage", 0),
            min(metrics.get("novelty", 0) / 15.0, 1.0),  # Normalize novelty
        ]
        # Close the polygon
        values.append(values[0])
        names = metric_names + [metric_names[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=names,
            name=model_name,
            fill='toself',
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=COLORS["muted"]),
            angularaxis=dict(gridcolor=COLORS["muted"]),
        ),
        title="📊 Model Performance Comparison",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=500,
    )
    return fig


def product_rating_breakdown(ratings_df):
    """Stacked bar showing rating breakdown for a product."""
    rating_counts = ratings_df["rating"].value_counts().sort_index()
    total = rating_counts.sum()

    colors = {5: "#067D62", 4: "#4CAF50", 3: "#FFA41C", 2: "#FF6D00", 1: "#E31C3D"}

    fig = go.Figure()
    for rating in [5, 4, 3, 2, 1]:
        count = rating_counts.get(rating, 0)
        pct = round(count / total * 100, 1) if total > 0 else 0
        fig.add_trace(go.Bar(
            x=[count],
            y=[f"{'⭐' * rating}"],
            orientation='h',
            name=f"{rating} star ({pct}%)",
            marker_color=colors[rating],
            text=f"{count} ({pct}%)",
            textposition='auto',
        ))

    fig.update_layout(
        barmode='stack',
        title="Rating Breakdown",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=250,
        showlegend=False,
        xaxis=dict(showgrid=False),
        margin=dict(l=80, r=20, t=40, b=20),
    )
    return fig


def user_preference_radar(profile):
    """Radar chart of user's category preferences."""
    if not profile or "top_categories" not in profile:
        return go.Figure()

    categories = list(profile["top_categories"].keys())
    values = [profile["top_categories"][c]["mean"] for c in categories]
    counts = [profile["top_categories"][c]["count"] for c in categories]

    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Avg Rating',
        line_color=COLORS["primary"],
        fillcolor='rgba(255, 153, 0, 0.2)',
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 5], gridcolor=COLORS["muted"]),
        ),
        title="🎯 Your Category Preferences",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=400,
    )
    return fig


def ratings_over_time_chart(ratings_df):
    """Line chart of ratings count over time."""
    if "review_date" not in ratings_df.columns:
        return go.Figure()

    df = ratings_df.copy()
    df["review_date"] = pd.to_datetime(df["review_date"])
    df["month"] = df["review_date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").agg(
        count=("rating", "count"),
        avg_rating=("rating", "mean"),
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=monthly["month"], y=monthly["count"], name="Reviews",
               marker_color=COLORS["primary"], opacity=0.7),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=monthly["month"], y=monthly["avg_rating"], name="Avg Rating",
                   line=dict(color=COLORS["accent"], width=3), mode="lines+markers"),
        secondary_y=True,
    )

    fig.update_layout(
        title="📅 Reviews Over Time",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        height=400,
    )
    fig.update_yaxes(title_text="Number of Reviews", secondary_y=False)
    fig.update_yaxes(title_text="Average Rating", secondary_y=True, range=[1, 5])
    return fig
