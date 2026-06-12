"""
SQLite Database Manager
Handles all database connections and queries for the recommendation system.
"""

import sqlite3
import os
import pandas as pd
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "amazon_recommendations.db")


@contextmanager
def get_connection(db_path=None):
    """Context manager for database connections."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_all_products(limit=None):
    """Fetch all products as a DataFrame."""
    query = "SELECT * FROM products ORDER BY num_ratings DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_product(product_id):
    """Fetch a single product by ID."""
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM products WHERE product_id = ?",
            conn, params=(product_id,)
        )


def search_products(query, category=None, min_price=None, max_price=None,
                     min_rating=None, platform=None, sort_by="relevance", limit=50):
    """Full-text search with filters."""
    conditions = []
    params = []

    if query:
        conditions.append("(title LIKE ? OR description LIKE ? OR brand LIKE ?)")
        q = f"%{query}%"
        params.extend([q, q, q])

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    if min_price is not None:
        conditions.append("price >= ?")
        params.append(min_price)

    if max_price is not None:
        conditions.append("price <= ?")
        params.append(max_price)

    if min_rating is not None:
        conditions.append("avg_rating >= ?")
        params.append(min_rating)
        
    if platform and platform != "All":
        conditions.append("best_platform = ?")
        params.append(platform)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    order_map = {
        "relevance": "num_ratings DESC",
        "price_low": "price ASC",
        "price_high": "price DESC",
        "rating": "avg_rating DESC",
        "newest": "product_id DESC",
        "discount": "discount_percent DESC",
    }
    order = order_map.get(sort_by, "num_ratings DESC")

    sql = f"SELECT * FROM products WHERE {where_clause} ORDER BY {order} LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def get_categories():
    """Get all unique categories."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [row[0] for row in cursor.fetchall()]


def get_all_users():
    """Fetch all users."""
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM users ORDER BY user_id", conn)


def get_user(user_id):
    """Fetch a single user."""
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM users WHERE user_id = ?",
            conn, params=(user_id,)
        )


def get_user_ratings(user_id):
    """Fetch all ratings by a user, joined with product info."""
    sql = """
        SELECT r.*, p.title, p.category, p.brand, p.price, p.image_url
        FROM ratings r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.user_id = ?
        ORDER BY r.rating DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=(user_id,))


def get_product_ratings(product_id):
    """Fetch all ratings for a product."""
    sql = """
        SELECT r.*, u.username
        FROM ratings r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.product_id = ?
        ORDER BY r.helpful_votes DESC, r.review_date DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=(product_id,))


def get_ratings_matrix():
    """Build the user-item ratings matrix as a DataFrame (pivot table)."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT user_id, product_id, rating FROM ratings", conn)
    if df.empty:
        return df
    return df.pivot_table(index='user_id', columns='product_id', values='rating')


def get_all_ratings():
    """Fetch all ratings as a flat DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM ratings", conn)


def get_top_products(category=None, n=20):
    """Get top-rated products, optionally filtered by category."""
    conditions = ["num_ratings >= 3"]
    params = []
    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    where = " AND ".join(conditions)
    sql = f"""
        SELECT * FROM products
        WHERE {where}
        ORDER BY avg_rating DESC, num_ratings DESC
        LIMIT ?
    """
    params.append(n)
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def get_trending_products(n=20):
    """Get products with highest recent ratings count."""
    sql = """
        SELECT p.*, COUNT(r.rating_id) as recent_ratings
        FROM products p
        JOIN ratings r ON p.product_id = r.product_id
        WHERE r.review_date >= '2024-06-01'
        GROUP BY p.product_id
        ORDER BY recent_ratings DESC, p.avg_rating DESC
        LIMIT ?
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=(n,))


def get_best_deals(category=None, platform=None, min_discount=10, limit=20):
    """Get products with the highest discount."""
    conditions = ["discount_percent >= ?"]
    params = [min_discount]

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)
        
    if platform and platform != "All":
        conditions.append("best_platform = ?")
        params.append(platform)

    where = " AND ".join(conditions)
    sql = f"""
        SELECT * FROM products
        WHERE {where}
        ORDER BY discount_percent DESC, num_ratings DESC
        LIMIT ?
    """
    params.append(limit)
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def get_products_by_platform(platform, category=None, limit=20):
    """Get top products where the specified platform has the best price."""
    conditions = ["best_platform = ?"]
    params = [platform]

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    where = " AND ".join(conditions)
    sql = f"""
        SELECT * FROM products
        WHERE {where}
        ORDER BY num_ratings DESC, avg_rating DESC
        LIMIT ?
    """
    params.append(limit)
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def get_stats():
    """Get database statistics."""
    stats = {}
    with get_connection() as conn:
        stats["total_products"] = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        stats["total_users"] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        stats["total_ratings"] = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
        stats["avg_rating"] = conn.execute("SELECT ROUND(AVG(rating), 2) FROM ratings").fetchone()[0]
        stats["categories"] = conn.execute("SELECT COUNT(DISTINCT category) FROM products").fetchone()[0]
        stats["brands"] = conn.execute("SELECT COUNT(DISTINCT brand) FROM products").fetchone()[0]
    return stats


def db_exists():
    """Check if the database file exists."""
    return os.path.exists(DB_PATH)
