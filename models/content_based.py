"""
Content-Based Filtering Engine
Recommends products based on item feature similarity using TF-IDF + Cosine Similarity.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.preprocessor import build_product_features


class ContentBasedRecommender:
    """
    Content-Based Filtering using TF-IDF vectorization and cosine similarity.
    
    Approach:
        1. Combine product features (title, description, category, brand) into 
           a weighted text representation.
        2. Apply TF-IDF vectorization to convert text to numerical features.
        3. Compute pairwise cosine similarity between all products.
        4. For any product, return the top-K most similar products.
    """

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self.products_df = None
        self.product_id_to_idx = {}
        self.is_fitted = False

    def fit(self, products_df):
        """
        Fit the model: vectorize product features and compute similarity matrix.
        
        Args:
            products_df: DataFrame with columns [product_id, title, description, category, brand, sub_category]
        """
        self.products_df = products_df.reset_index(drop=True)
        self.product_id_to_idx = {
            pid: idx for idx, pid in enumerate(self.products_df["product_id"])
        }

        # Build combined feature strings with weighting
        features = build_product_features(self.products_df)

        # TF-IDF vectorization
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(features)

        # Compute cosine similarity (only compute on demand for large datasets)
        # For 5000 products, the full matrix is ~200MB — manageable
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

        self.is_fitted = True
        return self

    def get_similar_products(self, product_id, n=10, exclude_same_category=False):
        """
        Get top-N similar products for a given product.
        
        Args:
            product_id: ID of the query product
            n: Number of recommendations to return
            exclude_same_category: If True, excludes products from the same category

        Returns:
            DataFrame with columns [product_id, title, category, price, avg_rating, similarity_score]
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if product_id not in self.product_id_to_idx:
            return pd.DataFrame()

        idx = self.product_id_to_idx[product_id]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort by similarity descending, skip self
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [(i, score) for i, score in sim_scores if i != idx]

        if exclude_same_category:
            query_cat = self.products_df.iloc[idx]["category"]
            sim_scores = [
                (i, score) for i, score in sim_scores
                if self.products_df.iloc[i]["category"] != query_cat
            ]

        top_indices = sim_scores[:n]

        results = []
        for i, score in top_indices:
            row = self.products_df.iloc[i]
            results.append({
                "product_id": row["product_id"],
                "title": row["title"],
                "category": row["category"],
                "sub_category": row.get("sub_category", ""),
                "brand": row.get("brand", ""),
                "price": row["price"],
                "avg_rating": row["avg_rating"],
                "num_ratings": row["num_ratings"],
                "similarity_score": round(score, 4),
            })

        return pd.DataFrame(results)

    def get_similarity_score(self, product_id_a, product_id_b):
        """Get similarity score between two products."""
        if not self.is_fitted:
            return 0.0
        idx_a = self.product_id_to_idx.get(product_id_a)
        idx_b = self.product_id_to_idx.get(product_id_b)
        if idx_a is None or idx_b is None:
            return 0.0
        return float(self.similarity_matrix[idx_a][idx_b])

    def get_content_scores_for_user(self, user_rated_products, candidate_ids=None, n=10):
        """
        Get content-based recommendations for a user based on their rating history.
        Aggregates similarity scores from all products the user has rated highly.
        
        Args:
            user_rated_products: Dict {product_id: rating}
            candidate_ids: Optional list of candidate product IDs to score
            n: Number of recommendations
            
        Returns:
            List of (product_id, score) tuples
        """
        if not self.is_fitted:
            return []

        rated_ids = set(user_rated_products.keys())
        
        # Weight by user rating (normalize to 0-1)
        scores = np.zeros(len(self.products_df))
        total_weight = 0

        for pid, rating in user_rated_products.items():
            if pid in self.product_id_to_idx:
                idx = self.product_id_to_idx[pid]
                weight = (rating - 1) / 4.0  # Normalize 1-5 to 0-1
                scores += weight * self.similarity_matrix[idx]
                total_weight += weight

        if total_weight > 0:
            scores /= total_weight

        # Build results excluding already-rated products
        results = []
        for i, score in enumerate(scores):
            pid = self.products_df.iloc[i]["product_id"]
            if pid not in rated_ids:
                if candidate_ids is None or pid in candidate_ids:
                    results.append((pid, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:n]
