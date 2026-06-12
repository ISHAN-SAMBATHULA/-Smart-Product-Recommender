"""
Data Loader — Abstraction layer for loading data from SQLite or CSV.
"""

import pandas as pd
import os
from database import db_manager


def load_products(source="db", csv_path=None):
    """Load products from database or CSV."""
    if source == "csv" and csv_path and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return db_manager.get_all_products()


def load_ratings(source="db", csv_path=None):
    """Load ratings from database or CSV."""
    if source == "csv" and csv_path and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return db_manager.get_all_ratings()


def load_users(source="db", csv_path=None):
    """Load users from database or CSV."""
    if source == "csv" and csv_path and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return db_manager.get_all_users()


def load_ratings_matrix(source="db"):
    """Load user-item ratings matrix."""
    return db_manager.get_ratings_matrix()


def ensure_data_ready():
    """Ensure the database exists; generate if missing."""
    if not db_manager.db_exists():
        from data.generate_data import build_database
        build_database()
    return True
