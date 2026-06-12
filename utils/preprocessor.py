"""
Text Preprocessor & Feature Engineering
"""

import re
import string
import numpy as np
import pandas as pd

# Common English stopwords (avoids nltk dependency)
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
    'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
    'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'through', 'during', 'before', 'after', 'above',
    'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
    't', 'can', 'will', 'just', 'don', 'should', 'now',
}


def clean_text(text):
    """Normalize text: lowercase, remove punctuation and stopwords."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 1]
    return " ".join(words)


def build_product_features(products_df):
    """
    Combine product text fields into a single feature string for TF-IDF.
    Weights: category (repeated 3x), brand (2x), title, description
    """
    features = []
    for _, row in products_df.iterrows():
        parts = []
        # Category weighted heavily
        cat = clean_text(str(row.get("category", "")))
        parts.extend([cat] * 3)
        # Sub-category
        sub = clean_text(str(row.get("sub_category", "")))
        parts.extend([sub] * 2)
        # Brand weighted
        brand = clean_text(str(row.get("brand", "")))
        parts.extend([brand] * 2)
        # Title
        parts.append(clean_text(str(row.get("title", ""))))
        # Description
        parts.append(clean_text(str(row.get("description", ""))))
        features.append(" ".join(parts))
    return features


def create_price_buckets(prices, n_buckets=5):
    """Bin prices into quantile-based buckets."""
    labels = ["Budget", "Economy", "Mid-Range", "Premium", "Luxury"]
    return pd.qcut(prices, q=n_buckets, labels=labels, duplicates='drop')


def create_rating_category(rating):
    """Categorize a numeric rating."""
    if rating >= 4.5:
        return "Excellent"
    elif rating >= 3.5:
        return "Good"
    elif rating >= 2.5:
        return "Average"
    elif rating >= 1.5:
        return "Below Average"
    else:
        return "Poor"


def build_user_profile(user_ratings_df):
    """Build a user preference profile from their rating history."""
    if user_ratings_df.empty:
        return {}

    profile = {
        "avg_rating": round(user_ratings_df["rating"].mean(), 2),
        "num_ratings": len(user_ratings_df),
        "rating_std": round(user_ratings_df["rating"].std(), 2) if len(user_ratings_df) > 1 else 0,
    }

    if "category" in user_ratings_df.columns:
        cat_ratings = user_ratings_df.groupby("category")["rating"].agg(["mean", "count"])
        profile["top_categories"] = cat_ratings.sort_values("count", ascending=False).head(5).to_dict("index")

    if "brand" in user_ratings_df.columns:
        brand_ratings = user_ratings_df.groupby("brand")["rating"].agg(["mean", "count"])
        profile["top_brands"] = brand_ratings.sort_values("count", ascending=False).head(5).to_dict("index")

    if "price" in user_ratings_df.columns:
        profile["avg_price_preference"] = round(user_ratings_df["price"].mean(), 2)
        profile["price_range"] = (
            round(user_ratings_df["price"].min(), 2),
            round(user_ratings_df["price"].max(), 2)
        )

    return profile
