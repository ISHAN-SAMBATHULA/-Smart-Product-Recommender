"""
Hybrid Recommendation Engine
Combines Content-Based and Collaborative Filtering for superior recommendations.
"""

import numpy as np
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.content_based import ContentBasedRecommender
from models.collaborative import CollaborativeFilteringRecommender
from database import db_manager


class HybridRecommender:
    """
    Weighted Hybrid Recommender System.
    
    Combines Content-Based and Collaborative Filtering scores:
        score_hybrid = α × score_content + (1 - α) × score_collaborative
    
    Handles cold-start:
        - New users (no ratings): falls back to content-based / popularity
        - New items (no interactions): falls back to content-based
    
    Attributes:
        alpha: Weight for content-based score (0 = pure CF, 1 = pure content)
    """

    def __init__(self, alpha=0.4):
        """
        Args:
            alpha: Blending weight. 0.0 = pure collaborative, 1.0 = pure content.
                   Default 0.4 favors collaborative (which is usually better for
                   users with enough history).
        """
        self.alpha = alpha
        self.content_model = ContentBasedRecommender()
        self.cf_model = CollaborativeFilteringRecommender(n_factors=50, n_neighbors=20)
        self.products_df = None
        self.is_fitted = False

    def fit(self, products_df, ratings_df):
        """
        Fit both sub-models.
        
        Args:
            products_df: DataFrame with product attributes
            ratings_df: DataFrame with [user_id, product_id, rating]
        """
        self.products_df = products_df

        # Fit content-based model on product features
        self.content_model.fit(products_df)

        # Fit collaborative filtering on user-item interactions
        self.cf_model.fit(ratings_df)

        self.is_fitted = True
        return self

    def get_recommendations(self, user_id, n=10, alpha=None):
        """
        Get hybrid recommendations for a user.
        
        Args:
            user_id: User ID
            n: Number of recommendations
            alpha: Override default alpha (optional)
            
        Returns:
            DataFrame with recommendations and score breakdown
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        blend = alpha if alpha is not None else self.alpha

        # Get user's rated products
        user_ratings = db_manager.get_user_ratings(user_id)
        rated_products = {}
        if not user_ratings.empty:
            rated_products = dict(zip(user_ratings["product_id"], user_ratings["rating"]))

        # Cold start: no rating history
        if not rated_products:
            return self._cold_start_recommendations(n)

        # ─── Content-Based Scores ────────────────────────────────────
        content_scores = self.content_model.get_content_scores_for_user(
            rated_products, n=n * 3
        )
        content_dict = dict(content_scores)

        # ─── Collaborative Filtering Scores ──────────────────────────
        cf_scores = self.cf_model.get_cf_scores_for_user(
            user_id, n=n * 3
        )
        cf_dict = dict(cf_scores)

        # ─── Combine Scores ─────────────────────────────────────────
        all_candidates = set(content_dict.keys()) | set(cf_dict.keys())
        all_candidates -= set(rated_products.keys())  # Exclude already rated

        hybrid_scores = []
        for pid in all_candidates:
            c_score = content_dict.get(pid, 0.0)
            cf_score = cf_dict.get(pid, 0.0)
            h_score = blend * c_score + (1 - blend) * cf_score
            hybrid_scores.append({
                "product_id": pid,
                "hybrid_score": round(h_score, 4),
                "content_score": round(c_score, 4),
                "cf_score": round(cf_score, 4),
            })

        hybrid_scores.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_scores = hybrid_scores[:n]

        if not top_scores:
            return self._cold_start_recommendations(n)

        # Merge with product info
        result_df = pd.DataFrame(top_scores)
        products_info = self.products_df[
            self.products_df["product_id"].isin(result_df["product_id"])
        ][["product_id", "title", "category", "sub_category", "brand", "price", "avg_rating", "num_ratings"]]

        result_df = result_df.merge(products_info, on="product_id", how="left")
        return result_df

    def _cold_start_recommendations(self, n):
        """Fallback for users with no rating history — recommend popular products."""
        top = db_manager.get_top_products(n=n)
        if top.empty:
            return pd.DataFrame()
        top["hybrid_score"] = np.linspace(1.0, 0.5, len(top))
        top["content_score"] = 0.0
        top["cf_score"] = 0.0
        return top[["product_id", "title", "category", "sub_category", "brand",
                     "price", "avg_rating", "num_ratings",
                     "hybrid_score", "content_score", "cf_score"]]

    def get_similar_products(self, product_id, n=10):
        """Passthrough to content-based model for item-item similarity."""
        if not self.is_fitted:
            return pd.DataFrame()
        return self.content_model.get_similar_products(product_id, n=n)

    def explain_recommendation(self, user_id, product_id):
        """
        Explain why a product was recommended to a user.
        
        Returns:
            Dict with explanation components
        """
        user_ratings = db_manager.get_user_ratings(user_id)
        if user_ratings.empty:
            return {"reason": "Popular product", "type": "popularity"}

        rated_products = dict(zip(user_ratings["product_id"], user_ratings["rating"]))

        # Find which rated products are most similar
        similar_rated = []
        for rated_pid, rating in rated_products.items():
            sim = self.content_model.get_similarity_score(rated_pid, product_id)
            if sim > 0.1:
                product_info = self.products_df[self.products_df["product_id"] == rated_pid]
                if not product_info.empty:
                    similar_rated.append({
                        "product_id": rated_pid,
                        "title": product_info.iloc[0]["title"],
                        "your_rating": rating,
                        "similarity": round(sim, 3),
                    })

        similar_rated.sort(key=lambda x: x["similarity"], reverse=True)

        return {
            "reason": "Based on your ratings and similar user preferences",
            "type": "hybrid",
            "similar_products_you_liked": similar_rated[:3],
            "content_weight": self.alpha,
            "cf_weight": 1 - self.alpha,
        }
