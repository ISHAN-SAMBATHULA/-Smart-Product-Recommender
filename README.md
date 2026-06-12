# 🛒 Amazon Product Recommendation System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **production-grade product recommendation system** built with Content-Based Filtering, Collaborative Filtering (SVD), and a Weighted Hybrid Engine — designed to demonstrate real-world ML engineering, scalability thinking, and measurable results.

---

## 🏗️ Architecture

```
amazon-recommender/
├── .streamlit/config.toml         # Dark theme config
├── data/
│   └── generate_data.py           # Synthetic dataset generator (5K products, 500 users, 15K ratings)
├── database/
│   ├── schema.sql                 # SQLite schema with indexes
│   └── db_manager.py              # Database connection & query layer
├── models/
│   ├── content_based.py           # TF-IDF + Cosine Similarity engine
│   ├── collaborative.py           # User-User CF, Item-Item CF, SVD Matrix Factorization
│   ├── hybrid.py                  # Weighted hybrid recommender with cold-start handling
│   └── evaluator.py               # Precision@K, Recall@K, RMSE, MAE, MAP, Coverage, Novelty
├── utils/
│   ├── data_loader.py             # Data abstraction layer (SQLite / CSV)
│   ├── preprocessor.py            # Text normalization, feature engineering
│   └── visualizations.py          # 10+ Plotly interactive charts
├── pages/                         # Streamlit multipage app
│   ├── 1_🏠_Home.py               # Trending & top-rated products
│   ├── 2_🔍_Search.py             # Full-text search with filters
│   ├── 3_📦_Product_Detail.py     # Product info + ML recommendations
│   ├── 4_👤_User_Profile.py       # Personalized recs with explainability
│   ├── 5_📊_Analytics.py          # Data visualization dashboard
│   └── 6_🧪_Model_Evaluation.py   # ML metrics & model comparison
├── app.py                         # Main entry point
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

---

## 🧠 Recommendation Algorithms

### 1. Content-Based Filtering
Recommends products with similar features using **TF-IDF vectorization** and **cosine similarity**.

```
Feature Vector = TF-IDF(title + description + category × 3 + brand × 2)
Similarity(A, B) = cos(θ) = (A · B) / (||A|| × ||B||)
```

### 2. Collaborative Filtering
Uses user-item interaction patterns to discover preferences:

- **User-User CF**: Finds users with similar rating behavior via K-Nearest Neighbors
- **Item-Item CF**: Identifies co-rated item patterns
- **SVD Matrix Factorization**: Decomposes the rating matrix `R ≈ U·Σ·Vᵀ` into latent factors

### 3. Hybrid Engine ⭐
Combines both approaches with configurable blending:

```
score_hybrid = α × score_content + (1 - α) × score_collaborative
```

- `α = 1.0` → Pure content-based (best for cold-start users)
- `α = 0.0` → Pure collaborative (best for users with history)
- `α = 0.4` → Default balanced hybrid

**Cold-start handling**: Automatically falls back to popularity-based recommendations for new users with no rating history.

---

## 📊 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **RMSE** | Root Mean Squared Error of rating predictions |
| **MAE** | Mean Absolute Error |
| **Precision@K** | Fraction of top-K recommendations that are relevant |
| **Recall@K** | Fraction of relevant items captured in top-K |
| **MAP@K** | Mean Average Precision (ranking quality) |
| **Coverage** | Catalog diversity — what % of products gets recommended |
| **Novelty** | How surprising/non-obvious the recommendations are |

All metrics are computed with proper **train/test splits** (80/20) for unbiased evaluation.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/amazon-recommender.git
cd amazon-recommender

# Install dependencies
pip install -r requirements.txt

# Generate dataset (auto-runs on first launch)
python data/generate_data.py

# Launch the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📸 Features

### 🏠 Home Page
- Trending products carousel
- Top-rated products by category
- Real-time recommendations for selected user

### 🔍 Product Search
- Full-text search across 5,000+ products
- Filters: category, price range, minimum rating
- Sort by relevance, price, rating

### 📦 Product Detail
- Complete product information
- **"Customers who viewed this also viewed"** (Content-Based)
- **"Recommended for you"** (Hybrid)
- Rating breakdown charts
- Recent reviews with sentiment

### 👤 User Profile
- User preference radar chart
- **Personalized recommendations with explanations**
- Adjustable hybrid weight (α slider)
- "Because you liked X..." reasoning
- Full rating history

### 📊 Analytics Dashboard
- Rating distribution histograms
- Category treemaps
- Price vs. rating scatter plots
- User activity distributions
- Ratings over time trends

### 🧪 Model Evaluation
- **Live evaluation with progress bar**
- Side-by-side model comparison
- Radar chart visualization
- Configurable K, test size, and relevance threshold
- Metric explanations

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| ML Engine | scikit-learn (TF-IDF, SVD, KNN, Cosine Similarity) |
| Database | SQLite |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy, SciPy |

---

## 📈 Dataset

The system generates a **realistic synthetic dataset** mimicking Amazon product data:

- **5,000 products** across 15 categories (Electronics, Books, Clothing, etc.)
- **500 users** with category preferences
- **15,000 ratings** with realistic distribution (skewed toward 4-5 stars)
- **Text reviews** with sentiment aligned to ratings

The dataset can be swapped for real Amazon review data from Kaggle.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Built as a comprehensive ML engineering project demonstrating:
- Recommendation system algorithms (Content-Based, Collaborative, Hybrid)
- Scalable architecture with proper separation of concerns
- Rigorous model evaluation with industry-standard metrics
- Production-quality UI/UX with interactive visualizations
- Clean, documented, and deployable codebase
