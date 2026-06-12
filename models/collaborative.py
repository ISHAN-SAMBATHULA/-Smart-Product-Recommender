"""
Collaborative Filtering Engine
Implements User-User CF, Item-Item CF, and SVD-based Matrix Factorization.
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class CollaborativeFilteringRecommender:
    """
    Collaborative Filtering with three strategies:
    
    1. User-User CF: Find similar users → aggregate their ratings
    2. Item-Item CF: Find similar items by co-rating patterns
    3. SVD Matrix Factorization: Decompose user-item matrix into latent factors
    
    The SVD approach is default as it handles sparsity best and scales well.
    """

    def __init__(self, n_factors=50, n_neighbors=20):
        """
        Args:
            n_factors: Number of latent factors for SVD decomposition
            n_neighbors: Number of neighbors for KNN-based CF
        """
        self.n_factors = n_factors
        self.n_neighbors = n_neighbors

        # SVD components
        self.svd = TruncatedSVD(n_components=n_factors, random_state=42)
        self.user_factors = None
        self.item_factors = None

        # KNN components
        self.user_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        self.item_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)

        # Data
        self.ratings_matrix = None
        self.ratings_matrix_filled = None
        self.user_ids = None
        self.product_ids = None
        self.user_mean_ratings = None
        self.global_mean = 0.0

        # Index mappings
        self.user_to_idx = {}
        self.product_to_idx = {}
        self.idx_to_user = {}
        self.idx_to_product = {}

        self.is_fitted = False

    def fit(self, ratings_df):
        """
        Fit the collaborative filtering model.
        
        Args:
            ratings_df: DataFrame with columns [user_id, product_id, rating]
        """
        # Build pivot table (user x product)
        self.ratings_matrix = ratings_df.pivot_table(
            index='user_id', columns='product_id', values='rating'
        )

        self.user_ids = self.ratings_matrix.index.tolist()
        self.product_ids = self.ratings_matrix.columns.tolist()

        # Index mappings
        self.user_to_idx = {uid: i for i, uid in enumerate(self.user_ids)}
        self.product_to_idx = {pid: i for i, pid in enumerate(self.product_ids)}
        self.idx_to_user = {i: uid for uid, i in self.user_to_idx.items()}
        self.idx_to_product = {i: pid for pid, i in self.product_to_idx.items()}

        # Compute user means for normalization
        self.user_mean_ratings = self.ratings_matrix.mean(axis=1)
        self.global_mean = ratings_df['rating'].mean()

        # Fill NaN with 0 for matrix operations
        self.ratings_matrix_filled = self.ratings_matrix.fillna(0)
        matrix_values = self.ratings_matrix_filled.values

        # ─── SVD Factorization ───────────────────────────────────────
        # R ≈ U · Σ · V^T
        self.user_factors = self.svd.fit_transform(matrix_values)
        self.item_factors = self.svd.components_.T  # (n_products x n_factors)

        # ─── KNN models ─────────────────────────────────────────────
        # User-User similarity
        if len(self.user_ids) > 1:
            self.user_knn.fit(matrix_values)
        # Item-Item similarity
        if len(self.product_ids) > 1:
            self.item_knn.fit(matrix_values.T)

        self.is_fitted = True
        return self

    def predict_rating(self, user_id, product_id, method='svd'):
        """
        Predict a user's rating for a product.
        
        Args:
            user_id: User ID
            product_id: Product ID
            method: 'svd', 'user_cf', or 'item_cf'
            
        Returns:
            Predicted rating (float, clipped to 1-5)
        """
        if not self.is_fitted:
            return self.global_mean

        user_idx = self.user_to_idx.get(user_id)
        prod_idx = self.product_to_idx.get(product_id)

        if user_idx is None or prod_idx is None:
            return self.global_mean

        if method == 'svd':
            pred = np.dot(self.user_factors[user_idx], self.item_factors[prod_idx])
            return float(np.clip(pred, 1, 5))

        elif method == 'user_cf':
            return self._predict_user_cf(user_idx, prod_idx)

        elif method == 'item_cf':
            return self._predict_item_cf(user_idx, prod_idx)

        return self.global_mean

    def _predict_user_cf(self, user_idx, prod_idx):
        """User-based collaborative filtering prediction."""
        user_vector = self.ratings_matrix_filled.values[user_idx].reshape(1, -1)
        try:
            distances, indices = self.user_knn.kneighbors(user_vector)
        except Exception:
            return self.global_mean

        neighbor_ratings = []
        neighbor_sims = []
        for i, neighbor_idx in enumerate(indices[0]):
            if neighbor_idx == user_idx:
                continue
            rating = self.ratings_matrix.iloc[neighbor_idx, prod_idx]
            if pd.notna(rating):
                sim = 1 - distances[0][i]  # cosine distance to similarity
                neighbor_ratings.append(rating)
                neighbor_sims.append(max(sim, 0.001))

        if not neighbor_ratings:
            return self.global_mean

        weighted_sum = sum(r * s for r, s in zip(neighbor_ratings, neighbor_sims))
        sim_sum = sum(neighbor_sims)
        pred = weighted_sum / sim_sum
        return float(np.clip(pred, 1, 5))

    def _predict_item_cf(self, user_idx, prod_idx):
        """Item-based collaborative filtering prediction."""
        item_vector = self.ratings_matrix_filled.values[:, prod_idx].reshape(1, -1)
        try:
            distances, indices = self.item_knn.kneighbors(item_vector)
        except Exception:
            return self.global_mean

        sim_ratings = []
        sim_scores = []
        for i, neighbor_item_idx in enumerate(indices[0]):
            if neighbor_item_idx == prod_idx:
                continue
            rating = self.ratings_matrix.iloc[user_idx, neighbor_item_idx]
            if pd.notna(rating):
                sim = 1 - distances[0][i]
                sim_ratings.append(rating)
                sim_scores.append(max(sim, 0.001))

        if not sim_ratings:
            return self.global_mean

        weighted_sum = sum(r * s for r, s in zip(sim_ratings, sim_scores))
        sim_sum = sum(sim_scores)
        pred = weighted_sum / sim_sum
        return float(np.clip(pred, 1, 5))

    def get_user_recommendations(self, user_id, n=10, method='svd'):
        """
        Get top-N product recommendations for a user.
        
        Args:
            user_id: User ID
            n: Number of recommendations
            method: 'svd', 'user_cf', or 'item_cf'
            
        Returns:
            List of (product_id, predicted_rating) tuples
        """
        if not self.is_fitted:
            return []

        user_idx = self.user_to_idx.get(user_id)
        if user_idx is None:
            return []

        # Get products the user hasn't rated
        user_ratings = self.ratings_matrix.iloc[user_idx]
        unrated_mask = user_ratings.isna()
        unrated_products = user_ratings[unrated_mask].index.tolist()

        if not unrated_products:
            return []

        if method == 'svd':
            # Fast: compute all predictions at once via dot product
            all_preds = np.dot(self.user_factors[user_idx], self.item_factors.T)
            predictions = []
            for pid in unrated_products:
                pidx = self.product_to_idx.get(pid)
                if pidx is not None:
                    pred = float(np.clip(all_preds[pidx], 1, 5))
                    predictions.append((pid, pred))
        else:
            # Slower: predict one by one
            predictions = []
            for pid in unrated_products[:200]:  # Limit for performance
                pred = self.predict_rating(user_id, pid, method)
                predictions.append((pid, pred))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def get_similar_users(self, user_id, n=10):
        """Find users most similar to the given user."""
        if not self.is_fitted:
            return []

        user_idx = self.user_to_idx.get(user_id)
        if user_idx is None:
            return []

        user_vector = self.ratings_matrix_filled.values[user_idx].reshape(1, -1)
        try:
            distances, indices = self.user_knn.kneighbors(user_vector, n_neighbors=min(n + 1, len(self.user_ids)))
        except Exception:
            return []

        results = []
        for i, neighbor_idx in enumerate(indices[0]):
            if neighbor_idx == user_idx:
                continue
            uid = self.idx_to_user[neighbor_idx]
            sim = round(1 - distances[0][i], 4)
            results.append((uid, sim))

        return results[:n]

    def get_cf_scores_for_user(self, user_id, candidate_ids=None, n=10):
        """
        Get collaborative filtering scores for a user (used by hybrid model).
        
        Returns:
            List of (product_id, score) tuples, scores normalized to 0-1
        """
        recs = self.get_user_recommendations(user_id, n=max(n, 50), method='svd')

        if candidate_ids is not None:
            candidate_set = set(candidate_ids)
            recs = [(pid, score) for pid, score in recs if pid in candidate_set]

        # Normalize scores to 0-1 range
        if recs:
            max_score = max(s for _, s in recs)
            min_score = min(s for _, s in recs)
            range_score = max_score - min_score if max_score != min_score else 1.0
            recs = [(pid, (s - min_score) / range_score) for pid, s in recs]

        return recs[:n]
