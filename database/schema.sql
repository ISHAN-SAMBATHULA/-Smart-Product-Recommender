-- Indian E-Commerce Product Recommendation System — Database Schema

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    brand TEXT,
    description TEXT,
    price REAL NOT NULL,
    original_price REAL DEFAULT 0.0,
    discount_percent REAL DEFAULT 0.0,
    avg_rating REAL DEFAULT 0.0,
    num_ratings INTEGER DEFAULT 0,
    image_url TEXT,
    platform_prices TEXT,        -- JSON: {"flipkart": 1299, "amazon": 1399, ...}
    best_platform TEXT,          -- e.g. "Flipkart"
    platform_urls TEXT,          -- JSON: {"flipkart": "https://...", "amazon": "https://..."}
    availability TEXT DEFAULT 'In Stock',
    emi_available INTEGER DEFAULT 0,
    delivery_days INTEGER DEFAULT 3,
    model_variant TEXT           -- e.g. "128GB, Midnight Black"
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    join_date TEXT,
    preferred_categories TEXT  -- JSON array of preferred categories
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 5.0),
    review_text TEXT,
    review_date TEXT,
    helpful_votes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE(user_id, product_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_product ON ratings(product_id);
CREATE INDEX IF NOT EXISTS idx_ratings_rating ON ratings(rating);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_best_platform ON products(best_platform);
CREATE INDEX IF NOT EXISTS idx_products_discount ON products(discount_percent);
