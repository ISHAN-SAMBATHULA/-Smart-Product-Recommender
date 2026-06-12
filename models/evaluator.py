"""
Model Evaluation Engine
Computes Precision@K, Recall@K, RMSE, MAE, MAP, Coverage, and Novelty.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class ModelEvaluator:
    """
    Evaluates recommendation models with industry-standard metrics.
    
    Metrics:
        - Precision@K: Fraction of recommended items that are relevant
        - Recall@K: Fraction of relevant items that are recommended
        - RMSE: Root Mean Squared Error of rating predictions
        - MAE: Mean Absolute Error of rating predictions
        - MAP@K: Mean Average Precision at K
        - Coverage: Fraction of catalog that gets recommended
        - Novelty: Average inverse popularity of recommendations
    """

    def __init__(self, test_size=0.2, random_state=42, relevance_threshold=4.0):
        """
        Args:
            test_size: Fraction of ratings to hold out for testing
            random_state: Random seed for reproducibility
            relevance_threshold: Minimum rating to consider a product "relevant"
        """
        self.test_size = test_size
        self.random_state = random_state
        self.relevance_threshold = relevance_threshold

    def split_data(self, ratings_df):
        """Split ratings into train and test sets."""
        train_df, test_df = train_test_split(
            ratings_df,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=None
        )
        return train_df, test_df

    def evaluate_rating_prediction(self, model, test_df, method='svd'):
        """
        Evaluate rating prediction accuracy.
        
        Args:
            model: A fitted CollaborativeFilteringRecommender
            test_df: Test ratings DataFrame
            method: Prediction method ('svd', 'user_cf', 'item_cf')
            
        Returns:
            Dict with RMSE and MAE
        """
        predictions = []
        actuals = []

        for _, row in test_df.iterrows():
            pred = model.predict_rating(int(row['user_id']), int(row['product_id']), method=method)
            predictions.append(pred)
            actuals.append(row['rating'])

        predictions = np.array(predictions)
        actuals = np.array(actuals)

        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mae = np.mean(np.abs(predictions - actuals))

        return {
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "n_predictions": len(predictions),
        }

    def precision_at_k(self, recommended_ids, relevant_ids, k):
        """Precision@K: Of the top-K recommended, how many are relevant?"""
        if k == 0:
            return 0.0
        top_k = recommended_ids[:k]
        relevant_in_top_k = len(set(top_k) & set(relevant_ids))
        return relevant_in_top_k / k

    def recall_at_k(self, recommended_ids, relevant_ids, k):
        """Recall@K: Of all relevant items, how many are in top-K?"""
        if not relevant_ids:
            return 0.0
        top_k = recommended_ids[:k]
        relevant_in_top_k = len(set(top_k) & set(relevant_ids))
        return relevant_in_top_k / len(relevant_ids)

    def average_precision_at_k(self, recommended_ids, relevant_ids, k):
        """Average Precision@K for a single user."""
        if not relevant_ids:
            return 0.0

        relevant_set = set(relevant_ids)
        hits = 0
        sum_precision = 0.0

        for i, item_id in enumerate(recommended_ids[:k]):
            if item_id in relevant_set:
                hits += 1
                sum_precision += hits / (i + 1)

        return sum_precision / min(len(relevant_ids), k)

    def evaluate_ranking(self, model, test_df, train_df, k=10, n_users=100):
        """
        Evaluate ranking quality across multiple users.
        
        Args:
            model: A fitted recommender with get_user_recommendations() or get_recommendations()
            test_df: Test ratings DataFrame
            train_df: Train ratings DataFrame
            k: Cutoff for top-K metrics
            n_users: Number of users to evaluate (for performance)
            
        Returns:
            Dict with precision@k, recall@k, map@k
        """
        # Find users who appear in both train and test
        train_users = set(train_df['user_id'].unique())
        test_users = set(test_df['user_id'].unique())
        common_users = list(train_users & test_users)

        if len(common_users) > n_users:
            rng = np.random.RandomState(self.random_state)
            common_users = rng.choice(common_users, size=n_users, replace=False).tolist()

        precisions = []
        recalls = []
        aps = []

        for user_id in common_users:
            # Get relevant items from test set (items the user rated highly)
            user_test = test_df[test_df['user_id'] == user_id]
            relevant = user_test[user_test['rating'] >= self.relevance_threshold]['product_id'].tolist()

            if not relevant:
                continue

            # Get recommendations
            if hasattr(model, 'get_recommendations'):
                recs_df = model.get_recommendations(user_id, n=k)
                if isinstance(recs_df, pd.DataFrame) and not recs_df.empty:
                    recommended = recs_df['product_id'].tolist()
                else:
                    continue
            elif hasattr(model, 'get_user_recommendations'):
                recs = model.get_user_recommendations(user_id, n=k)
                recommended = [pid for pid, _ in recs]
            else:
                continue

            if not recommended:
                continue

            precisions.append(self.precision_at_k(recommended, relevant, k))
            recalls.append(self.recall_at_k(recommended, relevant, k))
            aps.append(self.average_precision_at_k(recommended, relevant, k))

        return {
            f"precision@{k}": round(np.mean(precisions), 4) if precisions else 0.0,
            f"recall@{k}": round(np.mean(recalls), 4) if recalls else 0.0,
            f"map@{k}": round(np.mean(aps), 4) if aps else 0.0,
            "n_users_evaluated": len(precisions),
        }

    def compute_coverage(self, model, all_product_ids, user_ids, k=10, n_users=50):
        """
        Coverage: What fraction of the catalog gets recommended?
        
        Higher coverage = more diverse recommendations = less popularity bias.
        """
        recommended_set = set()
        rng = np.random.RandomState(self.random_state)
        sample_users = rng.choice(user_ids, size=min(n_users, len(user_ids)), replace=False)

        for user_id in sample_users:
            if hasattr(model, 'get_recommendations'):
                recs_df = model.get_recommendations(int(user_id), n=k)
                if isinstance(recs_df, pd.DataFrame) and not recs_df.empty:
                    recommended_set.update(recs_df['product_id'].tolist())
            elif hasattr(model, 'get_user_recommendations'):
                recs = model.get_user_recommendations(int(user_id), n=k)
                recommended_set.update([pid for pid, _ in recs])

        coverage = len(recommended_set) / len(all_product_ids) if all_product_ids else 0
        return {
            "coverage": round(coverage, 4),
            "unique_items_recommended": len(recommended_set),
            "total_catalog_size": len(all_product_ids),
        }

    def compute_novelty(self, recommendations, item_popularity):
        """
        Novelty: Average negative log popularity of recommended items.
        Higher novelty = recommendations are less obvious / more surprising.
        
        Args:
            recommendations: List of recommended product IDs
            item_popularity: Dict {product_id: num_ratings}
        """
        if not recommendations:
            return 0.0

        total_ratings = sum(item_popularity.values())
        if total_ratings == 0:
            return 0.0

        novelty_scores = []
        for pid in recommendations:
            pop = item_popularity.get(pid, 1)
            p = pop / total_ratings
            novelty_scores.append(-np.log2(max(p, 1e-10)))

        return round(np.mean(novelty_scores), 4)

    def full_evaluation(self, hybrid_model, cf_model, ratings_df, products_df, k=10, progress_callback=None):
        """
        Run comprehensive evaluation on all models.
        
        Args:
            hybrid_model: Fitted HybridRecommender
            cf_model: Fitted CollaborativeFilteringRecommender
            ratings_df: Full ratings DataFrame
            products_df: Products DataFrame
            k: Cutoff K
            progress_callback: Optional callable(progress_float, status_text)
            
        Returns:
            Dict with results for each model
        """
        results = {}

        if progress_callback:
            progress_callback(0.05, "Splitting data...")

        train_df, test_df = self.split_data(ratings_df)

        # ── Re-fit CF model on training data ────────────────────────
        if progress_callback:
            progress_callback(0.15, "Re-fitting Collaborative Filtering on train split...")

        from models.collaborative import CollaborativeFilteringRecommender
        cf_eval = CollaborativeFilteringRecommender(n_factors=50, n_neighbors=20)
        cf_eval.fit(train_df)

        # ── Rating prediction metrics ───────────────────────────────
        if progress_callback:
            progress_callback(0.30, "Evaluating SVD rating predictions...")

        # Sample test data for speed
        test_sample = test_df.sample(n=min(2000, len(test_df)), random_state=42)

        results["SVD (Collaborative)"] = {
            "type": "Collaborative Filtering (SVD)",
            **self.evaluate_rating_prediction(cf_eval, test_sample, method='svd'),
        }

        if progress_callback:
            progress_callback(0.45, "Evaluating User-CF predictions...")

        # User-CF (sample smaller for speed)
        small_sample = test_sample.head(500)
        user_cf_metrics = self.evaluate_rating_prediction(cf_eval, small_sample, method='user_cf')
        results["User-User CF"] = {
            "type": "Collaborative Filtering (User-User)",
            **user_cf_metrics,
        }

        # ── Ranking metrics ─────────────────────────────────────────
        if progress_callback:
            progress_callback(0.60, f"Computing Precision/Recall@{k}...")

        ranking_cf = self.evaluate_ranking(cf_eval, test_df, train_df, k=k, n_users=80)
        results["SVD (Collaborative)"].update(ranking_cf)

        if progress_callback:
            progress_callback(0.75, "Computing coverage and novelty...")

        # ── Coverage ─────────────────────────────────────────────────
        all_pids = products_df['product_id'].tolist()
        user_ids = ratings_df['user_id'].unique()
        coverage = self.compute_coverage(cf_eval, all_pids, user_ids, k=k, n_users=40)
        results["SVD (Collaborative)"].update(coverage)

        # ── Novelty ─────────────────────────────────────────────────
        popularity = dict(products_df[['product_id', 'num_ratings']].values)
        # Get sample recommendations for novelty
        sample_recs = []
        for uid in user_ids[:20]:
            recs = cf_eval.get_user_recommendations(int(uid), n=k)
            sample_recs.extend([pid for pid, _ in recs])
        novelty = self.compute_novelty(sample_recs, popularity)
        results["SVD (Collaborative)"]["novelty"] = novelty

        if progress_callback:
            progress_callback(0.90, "Finalizing results...")

        # ── Content-Based approximation ─────────────────────────────
        results["Content-Based"] = {
            "type": "Content-Based Filtering (TF-IDF)",
            "rmse": "N/A (no rating prediction)",
            "mae": "N/A",
            "note": "Content-based models rank items by similarity, not rating prediction.",
        }

        if progress_callback:
            progress_callback(1.0, "Evaluation complete!")

        return results
