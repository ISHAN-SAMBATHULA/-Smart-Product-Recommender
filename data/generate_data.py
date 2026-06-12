"""
Real Indian E-Commerce Product Dataset Generator
Generates REAL product names, models, variants with ₹ prices and multi-platform comparison.
Covers every major model/variant available on Indian e-commerce platforms.
"""

import sqlite3
import os
import random
import json
from datetime import datetime, timedelta

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORMS with search URL templates
# ═══════════════════════════════════════════════════════════════════════════════
PLATFORMS = {
    "Amazon": {
        "url_template": "https://www.amazon.in/s?k={query}",
        "delivery_range": (1, 4),
        "price_factor": (0.97, 1.05),  # relative to base price
        "emi": True,
    },
    "Flipkart": {
        "url_template": "https://www.flipkart.com/search?q={query}",
        "delivery_range": (1, 5),
        "price_factor": (0.95, 1.03),
        "emi": True,
    },
    "Meesho": {
        "url_template": "https://www.meesho.com/search?q={query}",
        "delivery_range": (3, 8),
        "price_factor": (0.85, 0.98),
        "emi": False,
    },
    "Croma": {
        "url_template": "https://www.croma.com/searchB?q={query}",
        "delivery_range": (2, 6),
        "price_factor": (1.00, 1.10),
        "emi": True,
    },
    "Myntra": {
        "url_template": "https://www.myntra.com/{query}",
        "delivery_range": (2, 5),
        "price_factor": (0.90, 1.02),
        "emi": False,
    },
    "JioMart": {
        "url_template": "https://www.jiomart.com/search/{query}",
        "delivery_range": (2, 7),
        "price_factor": (0.93, 1.04),
        "emi": False,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# REAL PRODUCT CATALOG — Every major model/variant
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORIES = {
    # ─────────────────────── SMARTPHONES ───────────────────────
    "Smartphones": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            # Apple iPhone
            {"brand": "Apple", "name": "iPhone 16 Pro Max", "variants": ["256GB", "512GB", "1TB"], "colors": ["Desert Titanium", "Natural Titanium", "White Titanium", "Black Titanium"], "base_price": 144900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 16 Pro", "variants": ["128GB", "256GB", "512GB", "1TB"], "colors": ["Desert Titanium", "Natural Titanium", "White Titanium", "Black Titanium"], "base_price": 119900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 16", "variants": ["128GB", "256GB", "512GB"], "colors": ["Ultramarine", "Teal", "Pink", "White", "Black"], "base_price": 79900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 16 Plus", "variants": ["128GB", "256GB", "512GB"], "colors": ["Ultramarine", "Teal", "Pink", "White", "Black"], "base_price": 89900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 15", "variants": ["128GB", "256GB", "512GB"], "colors": ["Blue", "Pink", "Yellow", "Green", "Black"], "base_price": 69900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 15 Plus", "variants": ["128GB", "256GB", "512GB"], "colors": ["Blue", "Pink", "Yellow", "Green", "Black"], "base_price": 79900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone 14", "variants": ["128GB", "256GB", "512GB"], "colors": ["Blue", "Purple", "Midnight", "Starlight", "Red"], "base_price": 59900, "sub": "iPhone"},
            {"brand": "Apple", "name": "iPhone SE (3rd Gen)", "variants": ["64GB", "128GB", "256GB"], "colors": ["Midnight", "Starlight", "Red"], "base_price": 49900, "sub": "iPhone"},
            # Samsung Galaxy S series
            {"brand": "Samsung", "name": "Galaxy S25 Ultra", "variants": ["256GB", "512GB", "1TB"], "colors": ["Titanium Silverblue", "Titanium Gray", "Titanium Black", "Titanium Whitesilver"], "base_price": 129999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S25+", "variants": ["256GB", "512GB"], "colors": ["Icyblue", "Navy", "Mint", "Silver Shadow"], "base_price": 99999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S25", "variants": ["128GB", "256GB"], "colors": ["Icyblue", "Navy", "Mint", "Silver Shadow"], "base_price": 80999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S24 Ultra", "variants": ["256GB", "512GB", "1TB"], "colors": ["Titanium Gray", "Titanium Black", "Titanium Violet", "Titanium Yellow"], "base_price": 109999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S24+", "variants": ["256GB", "512GB"], "colors": ["Cobalt Violet", "Amber Yellow", "Onyx Black", "Marble Gray"], "base_price": 79999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S24", "variants": ["128GB", "256GB"], "colors": ["Cobalt Violet", "Amber Yellow", "Onyx Black", "Marble Gray"], "base_price": 64999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S24 FE", "variants": ["128GB", "256GB"], "colors": ["Blue", "Gray", "Green", "Yellow", "Graphite"], "base_price": 49999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy S23 FE", "variants": ["128GB", "256GB"], "colors": ["Cream", "Graphite", "Mint", "Purple"], "base_price": 39999, "sub": "Samsung Galaxy"},
            # Samsung Galaxy A series
            {"brand": "Samsung", "name": "Galaxy A55 5G", "variants": ["128GB", "256GB"], "colors": ["Awesome Iceblue", "Awesome Lilac", "Awesome Lemon", "Awesome Navy"], "base_price": 29999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy A35 5G", "variants": ["128GB", "256GB"], "colors": ["Awesome Iceblue", "Awesome Lilac", "Awesome Lemon", "Awesome Navy"], "base_price": 22999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy A16 5G", "variants": ["128GB"], "colors": ["Blue Black", "Gold", "Light Green"], "base_price": 14999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy A06 4G", "variants": ["64GB", "128GB"], "colors": ["Black", "Gold", "Light Blue"], "base_price": 8999, "sub": "Samsung Galaxy"},
            # Samsung Galaxy M series
            {"brand": "Samsung", "name": "Galaxy M55 5G", "variants": ["128GB", "256GB"], "colors": ["Thunder Grey", "Light Green"], "base_price": 24999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy M35 5G", "variants": ["128GB", "256GB"], "colors": ["Daybreak Blue", "Thunder Grey", "Moonlight Night"], "base_price": 17999, "sub": "Samsung Galaxy"},
            {"brand": "Samsung", "name": "Galaxy M15 5G", "variants": ["128GB"], "colors": ["Blue Topaz", "Celestial Blue", "Stone Grey"], "base_price": 12999, "sub": "Samsung Galaxy"},
            # OnePlus
            {"brand": "OnePlus", "name": "OnePlus 13", "variants": ["256GB", "512GB"], "colors": ["Midnight Ocean", "Arctic Dawn", "Black Eclipse"], "base_price": 69999, "sub": "OnePlus"},
            {"brand": "OnePlus", "name": "OnePlus 13R", "variants": ["128GB", "256GB"], "colors": ["Nebula Noir", "Astral Trail"], "base_price": 42999, "sub": "OnePlus"},
            {"brand": "OnePlus", "name": "OnePlus 12", "variants": ["256GB", "512GB"], "colors": ["Flowy Emerald", "Silky Black"], "base_price": 59999, "sub": "OnePlus"},
            {"brand": "OnePlus", "name": "OnePlus 12R", "variants": ["128GB", "256GB"], "colors": ["Cool Blue", "Iron Gray"], "base_price": 39999, "sub": "OnePlus"},
            {"brand": "OnePlus", "name": "OnePlus Nord 4", "variants": ["128GB", "256GB"], "colors": ["Mercurial Silver", "Obsidian Midnight", "Oasis Green"], "base_price": 29999, "sub": "OnePlus Nord"},
            {"brand": "OnePlus", "name": "OnePlus Nord CE 4", "variants": ["128GB", "256GB"], "colors": ["Dark Chrome", "Celadon Marble"], "base_price": 24999, "sub": "OnePlus Nord"},
            {"brand": "OnePlus", "name": "OnePlus Nord CE 4 Lite", "variants": ["128GB", "256GB"], "colors": ["Super Silver", "Mega Blue"], "base_price": 19999, "sub": "OnePlus Nord"},
            # Xiaomi / Redmi / POCO
            {"brand": "Xiaomi", "name": "Xiaomi 14 Ultra", "variants": ["512GB"], "colors": ["Black", "White"], "base_price": 99999, "sub": "Xiaomi"},
            {"brand": "Xiaomi", "name": "Xiaomi 14", "variants": ["256GB", "512GB"], "colors": ["Jade Green", "Black", "White"], "base_price": 69999, "sub": "Xiaomi"},
            {"brand": "Redmi", "name": "Redmi Note 13 Pro+ 5G", "variants": ["128GB", "256GB", "512GB"], "colors": ["Fusion Purple", "Fusion Black", "Fusion White"], "base_price": 29999, "sub": "Redmi Note"},
            {"brand": "Redmi", "name": "Redmi Note 13 Pro 5G", "variants": ["128GB", "256GB"], "colors": ["Coral Purple", "Midnight Black", "Arctic White"], "base_price": 23999, "sub": "Redmi Note"},
            {"brand": "Redmi", "name": "Redmi Note 13 5G", "variants": ["128GB", "256GB"], "colors": ["Arctic White", "Chromatic Purple", "Stealth Black"], "base_price": 16999, "sub": "Redmi Note"},
            {"brand": "Redmi", "name": "Redmi 14C 5G", "variants": ["64GB", "128GB"], "colors": ["Starblue", "Stardust Purple", "Starlight Black"], "base_price": 9999, "sub": "Redmi"},
            {"brand": "POCO", "name": "POCO X6 Pro 5G", "variants": ["128GB", "256GB", "512GB"], "colors": ["Nebula Green", "Stellar Silver", "Comet Grey"], "base_price": 24999, "sub": "POCO"},
            {"brand": "POCO", "name": "POCO X6 5G", "variants": ["128GB", "256GB"], "colors": ["Snowstorm White", "Comet Grey", "Mirror Black"], "base_price": 17999, "sub": "POCO"},
            {"brand": "POCO", "name": "POCO M6 Pro", "variants": ["64GB", "128GB", "256GB"], "colors": ["Forest Green", "Burnished Bronze", "Arctic White"], "base_price": 12999, "sub": "POCO"},
            {"brand": "POCO", "name": "POCO C65", "variants": ["64GB", "128GB", "256GB"], "colors": ["Pastel Blue", "Matte Black", "Purple"], "base_price": 7499, "sub": "POCO"},
            # Realme
            {"brand": "Realme", "name": "Realme GT 6T", "variants": ["128GB", "256GB", "512GB"], "colors": ["Fluid Silver", "Razor Green"], "base_price": 29999, "sub": "Realme GT"},
            {"brand": "Realme", "name": "Realme GT 6", "variants": ["256GB", "512GB"], "colors": ["Miracle Purple", "Fluid Silver"], "base_price": 40999, "sub": "Realme GT"},
            {"brand": "Realme", "name": "Realme 13 Pro+ 5G", "variants": ["128GB", "256GB", "512GB"], "colors": ["Monet Gold", "Monet Purple", "Emerald Forest"], "base_price": 32999, "sub": "Realme"},
            {"brand": "Realme", "name": "Realme 13 Pro 5G", "variants": ["128GB", "256GB"], "colors": ["Monet Gold", "Monet Purple", "Emerald Forest"], "base_price": 26999, "sub": "Realme"},
            {"brand": "Realme", "name": "Realme Narzo 70 Pro 5G", "variants": ["128GB", "256GB"], "colors": ["Glass Gold", "Glass Green"], "base_price": 19999, "sub": "Realme Narzo"},
            {"brand": "Realme", "name": "Realme Narzo 70x 5G", "variants": ["128GB"], "colors": ["Ice Blue", "Forest Green"], "base_price": 11999, "sub": "Realme Narzo"},
            {"brand": "Realme", "name": "Realme C67 5G", "variants": ["64GB", "128GB"], "colors": ["Dark Purple", "Sunny Oasis"], "base_price": 10499, "sub": "Realme"},
            # Vivo
            {"brand": "Vivo", "name": "Vivo X200 Pro", "variants": ["256GB", "512GB"], "colors": ["Cosmos Black", "Titanium Grey"], "base_price": 94999, "sub": "Vivo X"},
            {"brand": "Vivo", "name": "Vivo X200", "variants": ["256GB", "512GB"], "colors": ["Cosmos Black", "Natural Green"], "base_price": 65999, "sub": "Vivo X"},
            {"brand": "Vivo", "name": "Vivo V40 Pro", "variants": ["256GB", "512GB"], "colors": ["Ganges Blue", "Titanium Grey"], "base_price": 49999, "sub": "Vivo V"},
            {"brand": "Vivo", "name": "Vivo V40", "variants": ["128GB", "256GB"], "colors": ["Ganges Blue", "Lotus Purple", "Titanium Grey"], "base_price": 34999, "sub": "Vivo V"},
            {"brand": "Vivo", "name": "Vivo T3 5G", "variants": ["128GB"], "colors": ["Crystal Flake", "Energy Green"], "base_price": 19999, "sub": "Vivo T"},
            {"brand": "Vivo", "name": "Vivo T3x 5G", "variants": ["128GB"], "colors": ["Crimson Bliss", "Marine Blue"], "base_price": 13499, "sub": "Vivo T"},
            {"brand": "Vivo", "name": "Vivo Y28 5G", "variants": ["128GB"], "colors": ["Crystal Purple", "Twinkling Gold", "Vintage Red"], "base_price": 15499, "sub": "Vivo Y"},
            {"brand": "Vivo", "name": "Vivo Y18", "variants": ["64GB", "128GB"], "colors": ["Space Black", "Gem Green"], "base_price": 8999, "sub": "Vivo Y"},
            # iQOO
            {"brand": "iQOO", "name": "iQOO 13", "variants": ["256GB", "512GB"], "colors": ["Legend", "Nardo Grey", "Midnight Race"], "base_price": 54999, "sub": "iQOO"},
            {"brand": "iQOO", "name": "iQOO Neo 9 Pro", "variants": ["128GB", "256GB"], "colors": ["Fiery Red", "Conqueror Black"], "base_price": 36999, "sub": "iQOO Neo"},
            {"brand": "iQOO", "name": "iQOO Z9 5G", "variants": ["128GB", "256GB"], "colors": ["Brushed Green", "Graphene Blue", "Titanium Matte"], "base_price": 18999, "sub": "iQOO Z"},
            # Nothing
            {"brand": "Nothing", "name": "Nothing Phone (2a) Plus", "variants": ["256GB"], "colors": ["Grey", "Black"], "base_price": 27999, "sub": "Nothing Phone"},
            {"brand": "Nothing", "name": "Nothing Phone (2a)", "variants": ["128GB", "256GB"], "colors": ["Milk", "Black"], "base_price": 23999, "sub": "Nothing Phone"},
            {"brand": "Nothing", "name": "Nothing Phone (2)", "variants": ["128GB", "256GB", "512GB"], "colors": ["White", "Dark Grey"], "base_price": 34999, "sub": "Nothing Phone"},
            # Google Pixel
            {"brand": "Google", "name": "Pixel 9 Pro XL", "variants": ["128GB", "256GB", "512GB", "1TB"], "colors": ["Obsidian", "Porcelain", "Hazel", "Rose Quartz"], "base_price": 109999, "sub": "Google Pixel"},
            {"brand": "Google", "name": "Pixel 9 Pro", "variants": ["128GB", "256GB", "512GB"], "colors": ["Obsidian", "Porcelain", "Hazel", "Rose Quartz"], "base_price": 99999, "sub": "Google Pixel"},
            {"brand": "Google", "name": "Pixel 9", "variants": ["128GB", "256GB"], "colors": ["Obsidian", "Porcelain", "Wintergreen", "Peony"], "base_price": 79999, "sub": "Google Pixel"},
            {"brand": "Google", "name": "Pixel 8a", "variants": ["128GB", "256GB"], "colors": ["Obsidian", "Porcelain", "Bay", "Aloe"], "base_price": 52999, "sub": "Google Pixel"},
            # Motorola
            {"brand": "Motorola", "name": "Motorola Edge 50 Ultra", "variants": ["256GB", "512GB"], "colors": ["Forest Grey", "Nordic Wood", "Peach Fuzz"], "base_price": 59999, "sub": "Motorola Edge"},
            {"brand": "Motorola", "name": "Motorola Edge 50 Pro", "variants": ["256GB"], "colors": ["Moonlight Pearl", "Black Beauty", "Luxe Lavender"], "base_price": 35999, "sub": "Motorola Edge"},
            {"brand": "Motorola", "name": "Motorola Edge 50 Fusion", "variants": ["128GB", "256GB"], "colors": ["Hot Pink", "Marshmallow Blue", "Forest Green"], "base_price": 24999, "sub": "Motorola Edge"},
            {"brand": "Motorola", "name": "Moto G85 5G", "variants": ["128GB", "256GB"], "colors": ["Olive Green", "Urban Grey", "Cobalt Blue"], "base_price": 17999, "sub": "Moto G"},
            {"brand": "Motorola", "name": "Moto G64 5G", "variants": ["128GB", "256GB"], "colors": ["Ice Lilac", "Mint Green", "Pearl Blue"], "base_price": 13999, "sub": "Moto G"},
            # OPPO
            {"brand": "OPPO", "name": "OPPO Find X8 Pro", "variants": ["256GB", "512GB"], "colors": ["Space Black", "Pearl White"], "base_price": 69999, "sub": "OPPO Find"},
            {"brand": "OPPO", "name": "OPPO Reno 12 Pro 5G", "variants": ["256GB", "512GB"], "colors": ["Space Brown", "Sunset Gold", "Astro Silver"], "base_price": 36999, "sub": "OPPO Reno"},
            {"brand": "OPPO", "name": "OPPO Reno 12 5G", "variants": ["128GB", "256GB"], "colors": ["Sunset Gold", "Astro Silver", "Matte Brown"], "base_price": 29999, "sub": "OPPO Reno"},
            {"brand": "OPPO", "name": "OPPO A80 5G", "variants": ["128GB"], "colors": ["Starry Black", "Moonlight Purple"], "base_price": 17999, "sub": "OPPO A"},
            {"brand": "OPPO", "name": "OPPO A60", "variants": ["128GB"], "colors": ["Ripple Blue", "Midnight Purple"], "base_price": 13999, "sub": "OPPO A"},
            # Tecno
            {"brand": "Tecno", "name": "Tecno Phantom V Fold 2", "variants": ["256GB", "512GB"], "colors": ["Karst Green", "Moondust Grey"], "base_price": 89999, "sub": "Tecno Phantom"},
            {"brand": "Tecno", "name": "Tecno Camon 30 Premier", "variants": ["256GB", "512GB"], "colors": ["Lava Grey", "Dark Welkin"], "base_price": 36999, "sub": "Tecno Camon"},
            {"brand": "Tecno", "name": "Tecno Spark 20 Pro+", "variants": ["128GB", "256GB"], "colors": ["Magic Skin Green", "Magic Skin Black"], "base_price": 14999, "sub": "Tecno Spark"},
            # Infinix
            {"brand": "Infinix", "name": "Infinix Note 40 Pro 5G", "variants": ["256GB"], "colors": ["Vintage Green", "Titan Gold"], "base_price": 21999, "sub": "Infinix Note"},
            {"brand": "Infinix", "name": "Infinix GT 20 Pro", "variants": ["256GB"], "colors": ["Mecha Blue", "Mecha Orange", "Mecha Silver"], "base_price": 24999, "sub": "Infinix GT"},
            {"brand": "Infinix", "name": "Infinix Smart 8 HD", "variants": ["64GB"], "colors": ["Timber Black", "Shiny Gold", "Galaxy White"], "base_price": 6299, "sub": "Infinix Smart"},
            # Lava (Indian Brand)
            {"brand": "Lava", "name": "Lava Agni 3 5G", "variants": ["128GB", "256GB"], "colors": ["Heather Glass", "Pristine Glass"], "base_price": 20999, "sub": "Lava Agni"},
            {"brand": "Lava", "name": "Lava Blaze 3 5G", "variants": ["128GB"], "colors": ["Glass Blue", "Glass Gold"], "base_price": 9999, "sub": "Lava Blaze"},
            {"brand": "Lava", "name": "Lava Yuva 3 Pro", "variants": ["128GB"], "colors": ["Cosmos Blue", "Meadow Green", "Forest Viridian"], "base_price": 7999, "sub": "Lava Yuva"},
            # Honor
            {"brand": "Honor", "name": "Honor 200 Pro 5G", "variants": ["512GB"], "colors": ["Ocean Cyan", "Black"], "base_price": 57999, "sub": "Honor"},
            {"brand": "Honor", "name": "Honor 200 5G", "variants": ["256GB", "512GB"], "colors": ["Moonlight White", "Black"], "base_price": 34999, "sub": "Honor"},
            {"brand": "Honor", "name": "Honor X9b 5G", "variants": ["256GB"], "colors": ["Sunrise Orange", "Midnight Black"], "base_price": 25999, "sub": "Honor"},
            # CMF (by Nothing)
            {"brand": "CMF", "name": "CMF Phone 1", "variants": ["128GB"], "colors": ["Black", "Orange", "Light Green", "Blue"], "base_price": 15999, "sub": "CMF by Nothing"},
            # Asus ROG Gaming Phones
            {"brand": "ASUS", "name": "ASUS ROG Phone 8 Pro", "variants": ["512GB"], "colors": ["Phantom Black"], "base_price": 94999, "sub": "ASUS ROG Phone"},
        ],
    },

    # ─────────────────────── LAPTOPS ───────────────────────
    "Laptops": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            # Apple MacBook
            {"brand": "Apple", "name": "MacBook Air M3", "variants": ["8GB/256GB", "8GB/512GB", "16GB/512GB", "24GB/1TB"], "colors": ["Midnight", "Starlight", "Space Gray", "Silver"], "base_price": 114900, "sub": "MacBook"},
            {"brand": "Apple", "name": "MacBook Air M2", "variants": ["8GB/256GB", "8GB/512GB", "16GB/512GB"], "colors": ["Midnight", "Starlight", "Space Gray", "Silver"], "base_price": 99900, "sub": "MacBook"},
            {"brand": "Apple", "name": "MacBook Pro 14-inch M3", "variants": ["8GB/512GB", "18GB/512GB", "18GB/1TB"], "colors": ["Space Gray", "Silver"], "base_price": 159900, "sub": "MacBook"},
            {"brand": "Apple", "name": "MacBook Pro 14-inch M3 Pro", "variants": ["18GB/512GB", "18GB/1TB", "36GB/1TB"], "colors": ["Space Black", "Silver"], "base_price": 199900, "sub": "MacBook"},
            {"brand": "Apple", "name": "MacBook Pro 16-inch M3 Pro", "variants": ["18GB/512GB", "36GB/512GB", "36GB/1TB"], "colors": ["Space Black", "Silver"], "base_price": 249900, "sub": "MacBook"},
            {"brand": "Apple", "name": "MacBook Pro 16-inch M3 Max", "variants": ["36GB/1TB", "48GB/1TB", "128GB/8TB"], "colors": ["Space Black", "Silver"], "base_price": 329900, "sub": "MacBook"},
            # HP Laptops
            {"brand": "HP", "name": "HP Pavilion 14", "variants": ["i5/8GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Natural Silver", "Warm Gold"], "base_price": 62999, "sub": "HP Pavilion"},
            {"brand": "HP", "name": "HP Pavilion 15", "variants": ["i5/8GB/512GB", "i7/16GB/512GB", "Ryzen 5/8GB/512GB", "Ryzen 7/16GB/512GB"], "colors": ["Natural Silver", "Fog Blue", "Ceramic White"], "base_price": 58999, "sub": "HP Pavilion"},
            {"brand": "HP", "name": "HP Envy x360 14", "variants": ["i5/8GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Nightfall Black", "Glacier Silver"], "base_price": 79999, "sub": "HP Envy"},
            {"brand": "HP", "name": "HP Spectre x360 14", "variants": ["i7/16GB/512GB", "i7/16GB/1TB", "i7/32GB/2TB"], "colors": ["Nightfall Black", "Pale Brass"], "base_price": 129999, "sub": "HP Spectre"},
            {"brand": "HP", "name": "HP 15s", "variants": ["i3/8GB/512GB", "i5/8GB/512GB", "Ryzen 3/8GB/512GB", "Ryzen 5/8GB/512GB"], "colors": ["Natural Silver", "Jet Black"], "base_price": 39999, "sub": "HP 15"},
            {"brand": "HP", "name": "HP 14s", "variants": ["i3/8GB/256GB", "i3/8GB/512GB", "i5/8GB/512GB"], "colors": ["Natural Silver", "Snow White"], "base_price": 34999, "sub": "HP 14"},
            {"brand": "HP", "name": "HP Victus 15", "variants": ["i5/8GB/512GB/RTX 3050", "i5/16GB/512GB/RTX 4050", "i7/16GB/1TB/RTX 4060", "Ryzen 5/8GB/512GB/RTX 3050"], "colors": ["Mica Silver", "Performance Blue"], "base_price": 62999, "sub": "HP Victus"},
            {"brand": "HP", "name": "HP Omen 16", "variants": ["i7/16GB/512GB/RTX 4060", "i7/16GB/1TB/RTX 4070", "i9/32GB/1TB/RTX 4080"], "colors": ["Shadow Black"], "base_price": 109999, "sub": "HP Omen"},
            # Dell Laptops
            {"brand": "Dell", "name": "Dell Inspiron 15 3520", "variants": ["i3/8GB/512GB", "i5/8GB/512GB", "i5/16GB/512GB"], "colors": ["Carbon Black", "Platinum Silver"], "base_price": 38999, "sub": "Dell Inspiron"},
            {"brand": "Dell", "name": "Dell Inspiron 14 5430", "variants": ["i5/8GB/512GB", "i5/16GB/512GB", "i7/16GB/512GB"], "colors": ["Platinum Silver", "Dark Blue"], "base_price": 58999, "sub": "Dell Inspiron"},
            {"brand": "Dell", "name": "Dell Inspiron 16 5630", "variants": ["i5/8GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Platinum Silver"], "base_price": 62999, "sub": "Dell Inspiron"},
            {"brand": "Dell", "name": "Dell XPS 14", "variants": ["Ultra 5/16GB/512GB", "Ultra 7/16GB/1TB", "Ultra 7/32GB/1TB"], "colors": ["Platinum", "Graphite"], "base_price": 139999, "sub": "Dell XPS"},
            {"brand": "Dell", "name": "Dell XPS 16", "variants": ["Ultra 7/16GB/512GB", "Ultra 7/32GB/1TB", "Ultra 9/64GB/2TB"], "colors": ["Platinum", "Graphite"], "base_price": 169999, "sub": "Dell XPS"},
            {"brand": "Dell", "name": "Dell G15 5530", "variants": ["i5/8GB/512GB/RTX 3050", "i5/16GB/512GB/RTX 4050", "i7/16GB/1TB/RTX 4060"], "colors": ["Dark Shadow Grey", "Phantom Grey with Neon Green"], "base_price": 64999, "sub": "Dell G15 Gaming"},
            {"brand": "Dell", "name": "Dell Latitude 5440", "variants": ["i5/8GB/256GB", "i5/16GB/512GB", "i7/16GB/512GB"], "colors": ["Grey"], "base_price": 74999, "sub": "Dell Latitude"},
            # Lenovo Laptops
            {"brand": "Lenovo", "name": "Lenovo IdeaPad Slim 3", "variants": ["i3/8GB/256GB", "i3/8GB/512GB", "i5/8GB/512GB", "Ryzen 5/8GB/512GB"], "colors": ["Arctic Grey", "Abyss Blue", "Cloud Grey"], "base_price": 33999, "sub": "Lenovo IdeaPad"},
            {"brand": "Lenovo", "name": "Lenovo IdeaPad Slim 5", "variants": ["i5/8GB/512GB", "i5/16GB/512GB", "i7/16GB/512GB", "Ryzen 5/16GB/512GB"], "colors": ["Cloud Grey", "Storm Grey", "Abyss Blue"], "base_price": 56999, "sub": "Lenovo IdeaPad"},
            {"brand": "Lenovo", "name": "Lenovo IdeaPad Slim 5 Pro", "variants": ["i7/16GB/512GB", "Ryzen 7/16GB/512GB"], "colors": ["Storm Grey", "Cloud Grey"], "base_price": 69999, "sub": "Lenovo IdeaPad"},
            {"brand": "Lenovo", "name": "Lenovo Yoga Slim 7i", "variants": ["i5/16GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Storm Grey", "Luna Grey"], "base_price": 79999, "sub": "Lenovo Yoga"},
            {"brand": "Lenovo", "name": "Lenovo Yoga 9i", "variants": ["i7/16GB/512GB", "i7/16GB/1TB", "i7/32GB/1TB"], "colors": ["Oatmeal", "Storm Grey"], "base_price": 139999, "sub": "Lenovo Yoga"},
            {"brand": "Lenovo", "name": "Lenovo ThinkPad E14 Gen 5", "variants": ["i5/8GB/256GB", "i5/8GB/512GB", "i5/16GB/512GB", "i7/16GB/512GB"], "colors": ["Graphite Black"], "base_price": 52999, "sub": "Lenovo ThinkPad"},
            {"brand": "Lenovo", "name": "Lenovo LOQ 15", "variants": ["i5/8GB/512GB/RTX 3050", "i5/16GB/512GB/RTX 4050", "i7/16GB/512GB/RTX 4060"], "colors": ["Luna Grey", "Storm Grey"], "base_price": 57999, "sub": "Lenovo LOQ Gaming"},
            {"brand": "Lenovo", "name": "Lenovo Legion Pro 5i", "variants": ["i7/16GB/1TB/RTX 4060", "i9/32GB/1TB/RTX 4070", "i9/32GB/1TB/RTX 4080"], "colors": ["Onyx Grey", "Eclipse Black"], "base_price": 139999, "sub": "Lenovo Legion Gaming"},
            # ASUS Laptops
            {"brand": "ASUS", "name": "ASUS VivoBook 15", "variants": ["i3/8GB/512GB", "i5/8GB/512GB", "i5/16GB/512GB", "Ryzen 5/8GB/512GB"], "colors": ["Indie Black", "Transparent Silver", "Quiet Blue"], "base_price": 37999, "sub": "ASUS VivoBook"},
            {"brand": "ASUS", "name": "ASUS VivoBook S15", "variants": ["i5/16GB/512GB", "i7/16GB/512GB"], "colors": ["Cool Silver", "Midnight Black"], "base_price": 64999, "sub": "ASUS VivoBook"},
            {"brand": "ASUS", "name": "ASUS Zenbook 14 OLED", "variants": ["i5/16GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Ponder Blue", "Jasper Gray"], "base_price": 79999, "sub": "ASUS Zenbook"},
            {"brand": "ASUS", "name": "ASUS ROG Strix G16", "variants": ["i7/16GB/512GB/RTX 4060", "i7/16GB/1TB/RTX 4070", "i9/32GB/1TB/RTX 4080"], "colors": ["Eclipse Gray", "Volt Green"], "base_price": 109999, "sub": "ASUS ROG Gaming"},
            {"brand": "ASUS", "name": "ASUS ROG Zephyrus G14", "variants": ["Ryzen 9/16GB/1TB/RTX 4060", "Ryzen 9/32GB/1TB/RTX 4070"], "colors": ["Moonlight White", "Eclipse Gray"], "base_price": 129999, "sub": "ASUS ROG Gaming"},
            {"brand": "ASUS", "name": "ASUS TUF Gaming F15", "variants": ["i5/8GB/512GB/RTX 3050", "i5/16GB/512GB/RTX 4050", "i7/16GB/1TB/RTX 4060"], "colors": ["Mecha Gray", "Graphite Black"], "base_price": 59999, "sub": "ASUS TUF Gaming"},
            # Acer Laptops
            {"brand": "Acer", "name": "Acer Aspire Lite 15", "variants": ["i3/8GB/512GB", "i5/8GB/512GB", "Ryzen 5/8GB/512GB"], "colors": ["Steel Gray"], "base_price": 29999, "sub": "Acer Aspire"},
            {"brand": "Acer", "name": "Acer Aspire 5", "variants": ["i5/8GB/512GB", "i5/16GB/512GB", "i7/16GB/512GB"], "colors": ["Iron", "Steel Gray", "Safari Gold"], "base_price": 49999, "sub": "Acer Aspire"},
            {"brand": "Acer", "name": "Acer Swift Go 14", "variants": ["i5/16GB/512GB", "i7/16GB/512GB", "i7/16GB/1TB"], "colors": ["Pure Silver", "Midnight Blue"], "base_price": 69999, "sub": "Acer Swift"},
            {"brand": "Acer", "name": "Acer Nitro V 15", "variants": ["i5/8GB/512GB/RTX 3050", "i5/16GB/512GB/RTX 4050", "i7/16GB/1TB/RTX 4060"], "colors": ["Obsidian Black"], "base_price": 55999, "sub": "Acer Nitro Gaming"},
            {"brand": "Acer", "name": "Acer Predator Helios 16", "variants": ["i7/16GB/1TB/RTX 4060", "i9/32GB/1TB/RTX 4070", "i9/32GB/2TB/RTX 4080"], "colors": ["Abyssal Black"], "base_price": 139999, "sub": "Acer Predator Gaming"},
            # MSI Laptops
            {"brand": "MSI", "name": "MSI Modern 14", "variants": ["i3/8GB/512GB", "i5/8GB/512GB", "i5/16GB/512GB"], "colors": ["Classic Black", "Blue Stone"], "base_price": 39999, "sub": "MSI Modern"},
            {"brand": "MSI", "name": "MSI Katana 15", "variants": ["i5/16GB/512GB/RTX 4050", "i7/16GB/512GB/RTX 4060", "i7/16GB/1TB/RTX 4070"], "colors": ["Black"], "base_price": 74999, "sub": "MSI Katana Gaming"},
            {"brand": "MSI", "name": "MSI Raider GE78 HX", "variants": ["i9/32GB/1TB/RTX 4070", "i9/64GB/2TB/RTX 4080", "i9/64GB/2TB/RTX 4090"], "colors": ["Dark Grey"], "base_price": 199999, "sub": "MSI Raider Gaming"},
        ],
    },

    # ─────────────────────── HEADPHONES & EARBUDS ───────────────────────
    "Headphones & Earbuds": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart", "Meesho"],
        "products": [
            # boAt
            {"brand": "boAt", "name": "boAt Airdopes 141", "variants": ["Standard"], "colors": ["Active Black", "Cyan", "Purple", "Orange"], "base_price": 1299, "sub": "TWS Earbuds"},
            {"brand": "boAt", "name": "boAt Airdopes 161", "variants": ["Standard"], "colors": ["Midnight Black", "Cool Blue", "Petal White"], "base_price": 1499, "sub": "TWS Earbuds"},
            {"brand": "boAt", "name": "boAt Airdopes Atom 81", "variants": ["Standard"], "colors": ["Active Black", "Ivory White", "Cherry Red"], "base_price": 1799, "sub": "TWS Earbuds"},
            {"brand": "boAt", "name": "boAt Airdopes Max", "variants": ["Standard"], "colors": ["Carbon Black", "Pearl White"], "base_price": 3999, "sub": "TWS Earbuds"},
            {"brand": "boAt", "name": "boAt Rockerz 450", "variants": ["Standard"], "colors": ["Luscious Black", "Hazel Beige", "Aqua Blue", "Red"], "base_price": 1599, "sub": "Over-Ear Headphones"},
            {"brand": "boAt", "name": "boAt Rockerz 550", "variants": ["Standard"], "colors": ["Black", "Green", "Blue", "Silver"], "base_price": 1899, "sub": "Over-Ear Headphones"},
            {"brand": "boAt", "name": "boAt Nirvana Ion ANC", "variants": ["Standard"], "colors": ["Midnight Black", "Silver Frost"], "base_price": 4999, "sub": "TWS Earbuds"},
            {"brand": "boAt", "name": "boAt Immortal 201", "variants": ["Standard"], "colors": ["Black Sabre", "Blue Blaze"], "base_price": 999, "sub": "Gaming Earbuds"},
            # Noise
            {"brand": "Noise", "name": "Noise Buds VS104", "variants": ["Standard"], "colors": ["Charcoal Black", "Mint Green", "Cherry Red", "Lavender"], "base_price": 1199, "sub": "TWS Earbuds"},
            {"brand": "Noise", "name": "Noise Buds Connect", "variants": ["Standard"], "colors": ["Midnight Black", "Chrome Silver", "Rose Gold"], "base_price": 1499, "sub": "TWS Earbuds"},
            {"brand": "Noise", "name": "Noise Air Buds Pro 3", "variants": ["Standard"], "colors": ["Charcoal Black", "Pearl White"], "base_price": 2499, "sub": "TWS Earbuds"},
            # JBL
            {"brand": "JBL", "name": "JBL Tune 230NC TWS", "variants": ["Standard"], "colors": ["Black", "Blue", "Sand", "Ghost White"], "base_price": 4999, "sub": "TWS Earbuds"},
            {"brand": "JBL", "name": "JBL Tune 520BT", "variants": ["Standard"], "colors": ["Black", "Blue", "White", "Purple"], "base_price": 3999, "sub": "On-Ear Headphones"},
            {"brand": "JBL", "name": "JBL Tune 770NC", "variants": ["Standard"], "colors": ["Black", "Blue", "Purple", "White"], "base_price": 5999, "sub": "Over-Ear Headphones"},
            {"brand": "JBL", "name": "JBL Live Pro 2 TWS", "variants": ["Standard"], "colors": ["Black", "Blue", "Silver", "Rose"], "base_price": 9999, "sub": "TWS Earbuds"},
            {"brand": "JBL", "name": "JBL Live 670NC", "variants": ["Standard"], "colors": ["Black", "Blue", "White", "Pink"], "base_price": 7999, "sub": "Over-Ear Headphones"},
            # Sony
            {"brand": "Sony", "name": "Sony WH-1000XM5", "variants": ["Standard"], "colors": ["Black", "Silver", "Midnight Blue", "Smoky Pink"], "base_price": 26990, "sub": "Over-Ear Headphones"},
            {"brand": "Sony", "name": "Sony WH-1000XM4", "variants": ["Standard"], "colors": ["Black", "Silver", "Midnight Blue"], "base_price": 19990, "sub": "Over-Ear Headphones"},
            {"brand": "Sony", "name": "Sony WF-1000XM5", "variants": ["Standard"], "colors": ["Black", "Silver"], "base_price": 24990, "sub": "TWS Earbuds"},
            {"brand": "Sony", "name": "Sony WF-C700N", "variants": ["Standard"], "colors": ["Black", "Lavender", "Sage Green", "White"], "base_price": 8990, "sub": "TWS Earbuds"},
            {"brand": "Sony", "name": "Sony WH-CH720N", "variants": ["Standard"], "colors": ["Black", "Blue", "White"], "base_price": 7990, "sub": "Over-Ear Headphones"},
            # Apple
            {"brand": "Apple", "name": "AirPods Pro 2 (USB-C)", "variants": ["Standard"], "colors": ["White"], "base_price": 24900, "sub": "TWS Earbuds"},
            {"brand": "Apple", "name": "AirPods 3rd Gen (Lightning)", "variants": ["Standard"], "colors": ["White"], "base_price": 19900, "sub": "TWS Earbuds"},
            {"brand": "Apple", "name": "AirPods Max", "variants": ["Standard"], "colors": ["Midnight", "Starlight", "Blue", "Purple", "Orange"], "base_price": 59900, "sub": "Over-Ear Headphones"},
            # Samsung
            {"brand": "Samsung", "name": "Samsung Galaxy Buds3 Pro", "variants": ["Standard"], "colors": ["Silver", "White"], "base_price": 17999, "sub": "TWS Earbuds"},
            {"brand": "Samsung", "name": "Samsung Galaxy Buds FE", "variants": ["Standard"], "colors": ["Graphite", "White", "Lavender"], "base_price": 6999, "sub": "TWS Earbuds"},
            # Sennheiser
            {"brand": "Sennheiser", "name": "Sennheiser Momentum 4", "variants": ["Standard"], "colors": ["Black", "White", "Copper"], "base_price": 29990, "sub": "Over-Ear Headphones"},
            {"brand": "Sennheiser", "name": "Sennheiser Momentum True Wireless 4", "variants": ["Standard"], "colors": ["Black Chrome", "White Silver", "Copper"], "base_price": 24990, "sub": "TWS Earbuds"},
            # OnePlus
            {"brand": "OnePlus", "name": "OnePlus Buds 3", "variants": ["Standard"], "colors": ["Metallic Grey", "Splendid Blue"], "base_price": 5499, "sub": "TWS Earbuds"},
            {"brand": "OnePlus", "name": "OnePlus Nord Buds 3 Pro", "variants": ["Standard"], "colors": ["Soft Jade", "Starry Black"], "base_price": 3299, "sub": "TWS Earbuds"},
            # Bose
            {"brand": "Bose", "name": "Bose QuietComfort Ultra Headphones", "variants": ["Standard"], "colors": ["Black", "White Smoke", "Sandstone"], "base_price": 32900, "sub": "Over-Ear Headphones"},
            {"brand": "Bose", "name": "Bose QuietComfort Ultra Earbuds", "variants": ["Standard"], "colors": ["Black", "White Smoke", "Moonstone Blue"], "base_price": 27900, "sub": "TWS Earbuds"},
            {"brand": "Bose", "name": "Bose QuietComfort Headphones", "variants": ["Standard"], "colors": ["Black", "White Smoke", "Green Cypress"], "base_price": 26900, "sub": "Over-Ear Headphones"},
        ],
    },

    # ─────────────────────── SMARTWATCHES ───────────────────────
    "Smartwatches": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart", "Myntra"],
        "products": [
            {"brand": "Apple", "name": "Apple Watch Ultra 2", "variants": ["49mm GPS+Cellular"], "colors": ["Natural Titanium"], "base_price": 89900, "sub": "Apple Watch"},
            {"brand": "Apple", "name": "Apple Watch Series 9", "variants": ["41mm GPS", "45mm GPS", "41mm GPS+Cellular", "45mm GPS+Cellular"], "colors": ["Midnight", "Starlight", "Silver", "Pink", "Red"], "base_price": 41900, "sub": "Apple Watch"},
            {"brand": "Apple", "name": "Apple Watch SE 2nd Gen", "variants": ["40mm GPS", "44mm GPS", "40mm GPS+Cellular", "44mm GPS+Cellular"], "colors": ["Midnight", "Starlight", "Silver"], "base_price": 29900, "sub": "Apple Watch"},
            {"brand": "Samsung", "name": "Samsung Galaxy Watch6 Classic", "variants": ["43mm", "47mm"], "colors": ["Black", "Silver"], "base_price": 34999, "sub": "Samsung Galaxy Watch"},
            {"brand": "Samsung", "name": "Samsung Galaxy Watch6", "variants": ["40mm", "44mm"], "colors": ["Graphite", "Gold", "Silver"], "base_price": 24999, "sub": "Samsung Galaxy Watch"},
            {"brand": "Samsung", "name": "Samsung Galaxy Watch FE", "variants": ["40mm"], "colors": ["Black", "Pink Gold", "Silver"], "base_price": 14999, "sub": "Samsung Galaxy Watch"},
            {"brand": "Noise", "name": "Noise ColorFit Pro 5", "variants": ["Standard"], "colors": ["Jet Black", "Rose Gold", "Chrome Silver", "Deep Wine"], "base_price": 4999, "sub": "Noise Smartwatch"},
            {"brand": "Noise", "name": "Noise ColorFit Pro 5 Max", "variants": ["Standard"], "colors": ["Classic Black", "Vintage Brown", "Silver Grey"], "base_price": 5999, "sub": "Noise Smartwatch"},
            {"brand": "Noise", "name": "Noise Evolve 2 AMOLED", "variants": ["Standard"], "colors": ["Charcoal Black", "Rose Pink", "Metallic Silver"], "base_price": 3999, "sub": "Noise Smartwatch"},
            {"brand": "boAt", "name": "boAt Wave Sigma 2", "variants": ["Standard"], "colors": ["Active Black", "Cool Grey", "Midnight Blue"], "base_price": 1999, "sub": "boAt Smartwatch"},
            {"brand": "boAt", "name": "boAt Ultima Chronos", "variants": ["Standard"], "colors": ["Active Black", "Cherry Blossom", "Steel Blue"], "base_price": 2499, "sub": "boAt Smartwatch"},
            {"brand": "boAt", "name": "boAt Lunar Oasis", "variants": ["Standard"], "colors": ["Active Black", "Cool Blue", "Rose Gold"], "base_price": 3999, "sub": "boAt Smartwatch"},
            {"brand": "Amazfit", "name": "Amazfit GTR 4", "variants": ["Standard"], "colors": ["Superspeed Black", "Racetrack Grey", "Vintage Brown"], "base_price": 14999, "sub": "Amazfit Smartwatch"},
            {"brand": "Amazfit", "name": "Amazfit GTS 4 Mini", "variants": ["Standard"], "colors": ["Midnight Black", "Moonlight White", "Flamingo Pink", "Mint Blue"], "base_price": 5999, "sub": "Amazfit Smartwatch"},
            {"brand": "Amazfit", "name": "Amazfit T-Rex Ultra", "variants": ["Standard"], "colors": ["Abyss Black", "Sahara"], "base_price": 29999, "sub": "Amazfit Smartwatch"},
            {"brand": "Fire-Boltt", "name": "Fire-Boltt Phoenix Ultra", "variants": ["Standard"], "colors": ["Black", "Grey", "Brown"], "base_price": 2999, "sub": "Fire-Boltt Smartwatch"},
            {"brand": "Fire-Boltt", "name": "Fire-Boltt Ninja Call Pro Max", "variants": ["Standard"], "colors": ["Black", "Gold", "Silver"], "base_price": 1999, "sub": "Fire-Boltt Smartwatch"},
            {"brand": "Garmin", "name": "Garmin Venu 3", "variants": ["Standard"], "colors": ["Black/Slate", "Sage Grey/Silver", "Ivory/Cream Gold"], "base_price": 49990, "sub": "Garmin Smartwatch"},
            {"brand": "Garmin", "name": "Garmin Forerunner 265", "variants": ["Standard"], "colors": ["Black/Powder Gray", "Whitestone/Tidal Blue", "Aqua/Black"], "base_price": 44990, "sub": "Garmin Smartwatch"},
            {"brand": "Garmin", "name": "Garmin Fenix 7 Pro", "variants": ["Standard"], "colors": ["Carbon Gray/Black", "Silver/Whitestone"], "base_price": 74990, "sub": "Garmin Smartwatch"},
            {"brand": "OnePlus", "name": "OnePlus Watch 2", "variants": ["Standard"], "colors": ["Black Steel", "Radiant Steel"], "base_price": 24999, "sub": "OnePlus Watch"},
        ],
    },

    # ─────────────────────── TELEVISIONS ───────────────────────
    "Televisions": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            {"brand": "Samsung", "name": "Samsung Crystal 4K UHD TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch"], "colors": ["Black"], "base_price": 32999, "sub": "4K Smart TV"},
            {"brand": "Samsung", "name": "Samsung Neo QLED 4K TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch", "85 inch"], "colors": ["Black", "Silver"], "base_price": 64999, "sub": "QLED Smart TV"},
            {"brand": "Samsung", "name": "Samsung OLED 4K TV", "variants": ["55 inch", "65 inch", "77 inch"], "colors": ["Black"], "base_price": 129999, "sub": "OLED Smart TV"},
            {"brand": "Samsung", "name": "Samsung The Frame 4K TV", "variants": ["32 inch", "43 inch", "50 inch", "55 inch", "65 inch", "75 inch", "85 inch"], "colors": ["Charcoal Black"], "base_price": 39999, "sub": "Lifestyle TV"},
            {"brand": "LG", "name": "LG UR7500 4K UHD TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch"], "colors": ["Black"], "base_price": 29999, "sub": "4K Smart TV"},
            {"brand": "LG", "name": "LG QNED80 4K TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch"], "colors": ["Black"], "base_price": 49999, "sub": "QNED Smart TV"},
            {"brand": "LG", "name": "LG C3 OLED 4K TV", "variants": ["42 inch", "48 inch", "55 inch", "65 inch", "77 inch", "83 inch"], "colors": ["Black"], "base_price": 89999, "sub": "OLED Smart TV"},
            {"brand": "LG", "name": "LG G3 OLED evo 4K TV", "variants": ["55 inch", "65 inch", "77 inch", "83 inch"], "colors": ["Black"], "base_price": 159999, "sub": "OLED Smart TV"},
            {"brand": "Sony", "name": "Sony Bravia X80L 4K TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch", "85 inch"], "colors": ["Black"], "base_price": 44999, "sub": "4K Smart TV"},
            {"brand": "Sony", "name": "Sony Bravia X90L 4K TV", "variants": ["55 inch", "65 inch", "75 inch", "85 inch"], "colors": ["Black"], "base_price": 84999, "sub": "Full Array LED TV"},
            {"brand": "Sony", "name": "Sony Bravia A80L OLED 4K TV", "variants": ["55 inch", "65 inch", "77 inch"], "colors": ["Black"], "base_price": 149999, "sub": "OLED Smart TV"},
            {"brand": "Mi", "name": "Mi TV 5X", "variants": ["43 inch", "50 inch", "55 inch"], "colors": ["Black"], "base_price": 22999, "sub": "4K Smart TV"},
            {"brand": "Redmi", "name": "Redmi Smart Fire TV", "variants": ["32 inch HD", "40 inch Full HD", "43 inch 4K"], "colors": ["Black"], "base_price": 12999, "sub": "Smart TV"},
            {"brand": "OnePlus", "name": "OnePlus TV 55 Q2 Pro", "variants": ["55 inch 4K"], "colors": ["Black"], "base_price": 49999, "sub": "QLED Smart TV"},
            {"brand": "TCL", "name": "TCL C745 4K QLED TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch", "75 inch", "85 inch"], "colors": ["Black"], "base_price": 34999, "sub": "QLED Smart TV"},
            {"brand": "Hisense", "name": "Hisense U6K 4K Mini-LED ULED TV", "variants": ["55 inch", "65 inch", "75 inch"], "colors": ["Black"], "base_price": 39999, "sub": "Mini-LED TV"},
            {"brand": "Vu", "name": "Vu GloLED TV", "variants": ["43 inch", "50 inch", "55 inch", "65 inch"], "colors": ["Black"], "base_price": 23999, "sub": "4K Smart TV"},
        ],
    },

    # ─────────────────────── CLOTHING ───────────────────────
    "Clothing": {
        "platforms": ["Amazon", "Flipkart", "Myntra", "Meesho", "JioMart"],
        "products": [
            {"brand": "Nike", "name": "Nike Dri-FIT T-Shirt", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Black", "White", "Navy", "Grey"], "base_price": 1995, "sub": "T-Shirts"},
            {"brand": "Nike", "name": "Nike Air Max 270", "variants": ["UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["Black/White", "White/Red", "Grey/Blue"], "base_price": 12995, "sub": "Sneakers"},
            {"brand": "Nike", "name": "Nike Air Force 1 '07", "variants": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["White", "Black", "White/Black"], "base_price": 8195, "sub": "Sneakers"},
            {"brand": "Adidas", "name": "Adidas Ultraboost Light", "variants": ["UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["Core Black", "Cloud White", "Grey"], "base_price": 16999, "sub": "Sneakers"},
            {"brand": "Adidas", "name": "Adidas Originals Superstar", "variants": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10"], "colors": ["White/Black", "White/Green", "Black/White"], "base_price": 8999, "sub": "Sneakers"},
            {"brand": "Adidas", "name": "Adidas 3-Stripes Essential Shorts", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Black", "Navy", "Grey"], "base_price": 1599, "sub": "Shorts"},
            {"brand": "Puma", "name": "Puma Smash V2 Sneakers", "variants": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10"], "colors": ["Black-White", "White-Navy", "Grey"], "base_price": 2799, "sub": "Sneakers"},
            {"brand": "Puma", "name": "Puma ESS Logo T-Shirt", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Black", "White", "Peacoat", "Medium Grey"], "base_price": 999, "sub": "T-Shirts"},
            {"brand": "Levi's", "name": "Levi's 511 Slim Fit Jeans", "variants": ["28", "30", "32", "34", "36", "38"], "colors": ["Dark Indigo", "Mid Wash", "Light Wash", "Black"], "base_price": 3299, "sub": "Jeans"},
            {"brand": "Levi's", "name": "Levi's 501 Original Fit Jeans", "variants": ["28", "30", "32", "34", "36", "38"], "colors": ["Dark Stonewash", "Medium Stonewash", "Black"], "base_price": 4299, "sub": "Jeans"},
            {"brand": "H&M", "name": "H&M Regular Fit Crew-Neck T-Shirt Pack of 3", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Black", "White", "Grey"], "base_price": 899, "sub": "T-Shirts"},
            {"brand": "H&M", "name": "H&M Relaxed Fit Hoodie", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Black", "Grey Melange", "Dark Green", "Cream"], "base_price": 1999, "sub": "Hoodies"},
            {"brand": "U.S. Polo Assn.", "name": "U.S. Polo Assn. Solid Polo T-Shirt", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Navy", "White", "Red", "Black", "Green"], "base_price": 1299, "sub": "Polo T-Shirts"},
            {"brand": "Allen Solly", "name": "Allen Solly Slim Fit Formal Shirt", "variants": ["38", "39", "40", "42", "44"], "colors": ["White", "Light Blue", "Pink", "Grey"], "base_price": 1499, "sub": "Formal Shirts"},
            {"brand": "Van Heusen", "name": "Van Heusen Slim Fit Formal Trousers", "variants": ["30", "32", "34", "36", "38"], "colors": ["Black", "Navy", "Grey", "Beige"], "base_price": 1899, "sub": "Formal Trousers"},
            {"brand": "Raymond", "name": "Raymond Contemporary Fit Blazer", "variants": ["36", "38", "40", "42", "44", "46"], "colors": ["Navy", "Black", "Charcoal Grey"], "base_price": 5999, "sub": "Blazers"},
            {"brand": "Peter England", "name": "Peter England Slim Fit Casual Shirt", "variants": ["38", "39", "40", "42", "44"], "colors": ["Blue Check", "White", "Navy Print", "Green Stripes"], "base_price": 1099, "sub": "Casual Shirts"},
            {"brand": "Biba", "name": "Biba Printed Cotton Kurta", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Blue", "Red", "Green", "Yellow", "Pink"], "base_price": 1299, "sub": "Kurtas"},
            {"brand": "W", "name": "W Ethnic Anarkali Kurta", "variants": ["XS", "S", "M", "L", "XL"], "colors": ["Maroon", "Navy", "Green", "Teal"], "base_price": 1799, "sub": "Kurtas"},
            {"brand": "Fabindia", "name": "Fabindia Cotton Printed Kurta Set", "variants": ["S", "M", "L", "XL", "XXL"], "colors": ["Indigo", "Mustard", "Olive", "Maroon"], "base_price": 2999, "sub": "Kurta Sets"},
        ],
    },

    # ─────────────────────── HOME & KITCHEN ───────────────────────
    "Home & Kitchen": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart", "Meesho"],
        "products": [
            {"brand": "Prestige", "name": "Prestige Svachh Pressure Cooker", "variants": ["2L", "3L", "5L"], "colors": ["Silver"], "base_price": 1899, "sub": "Cookers"},
            {"brand": "Prestige", "name": "Prestige Iris 750W Mixer Grinder", "variants": ["3 Jars", "4 Jars"], "colors": ["White/Purple", "White/Blue"], "base_price": 3299, "sub": "Mixer Grinders"},
            {"brand": "Hawkins", "name": "Hawkins Classic Pressure Cooker", "variants": ["2L", "3L", "5L", "8L", "10L"], "colors": ["Silver"], "base_price": 1599, "sub": "Cookers"},
            {"brand": "Pigeon", "name": "Pigeon by Stovekraft Favourite Non-Stick Pan", "variants": ["240mm", "280mm"], "colors": ["Black"], "base_price": 449, "sub": "Cookware"},
            {"brand": "Instant Pot", "name": "Instant Pot Duo 7-in-1", "variants": ["3 Quart", "6 Quart", "8 Quart"], "colors": ["Silver/Black"], "base_price": 7999, "sub": "Electric Cookers"},
            {"brand": "Bajaj", "name": "Bajaj Majesty 2200W Induction Cooktop", "variants": ["Standard"], "colors": ["Black"], "base_price": 2199, "sub": "Induction Cooktop"},
            {"brand": "Philips", "name": "Philips Digital Air Fryer HD9252", "variants": ["4.1L"], "colors": ["Black"], "base_price": 7999, "sub": "Air Fryers"},
            {"brand": "Philips", "name": "Philips Air Fryer XL HD9270", "variants": ["6.2L"], "colors": ["Black"], "base_price": 12999, "sub": "Air Fryers"},
            {"brand": "Dyson", "name": "Dyson V12 Detect Slim", "variants": ["Standard"], "colors": ["Yellow/Nickel"], "base_price": 52900, "sub": "Vacuum Cleaners"},
            {"brand": "Dyson", "name": "Dyson V15 Detect", "variants": ["Standard"], "colors": ["Yellow/Nickel", "Purple/Nickel"], "base_price": 62900, "sub": "Vacuum Cleaners"},
            {"brand": "Eureka Forbes", "name": "Eureka Forbes Aquaguard Aura RO+UV+MTDS", "variants": ["7L"], "colors": ["White/Black"], "base_price": 14999, "sub": "Water Purifiers"},
            {"brand": "Kent", "name": "Kent Grand RO Water Purifier", "variants": ["8L"], "colors": ["White/Blue"], "base_price": 12499, "sub": "Water Purifiers"},
            {"brand": "Havells", "name": "Havells Instanio Prime 3L Instant Water Heater", "variants": ["1L", "3L", "6L", "10L", "15L", "25L"], "colors": ["White/Blue", "White/Brown"], "base_price": 3499, "sub": "Water Heaters"},
            {"brand": "Crompton", "name": "Crompton Aura 2 Anti-Dust Ceiling Fan", "variants": ["48 inch"], "colors": ["Ivory", "Brown", "White"], "base_price": 2199, "sub": "Ceiling Fans"},
            {"brand": "Orient Electric", "name": "Orient Electric Aeroquiet BLDC Ceiling Fan", "variants": ["48 inch"], "colors": ["Cosmos Black", "Marble White", "Caramel Brown"], "base_price": 3799, "sub": "Ceiling Fans"},
            {"brand": "IFB", "name": "IFB Senator WSS 8kg Front Load Washing Machine", "variants": ["6kg", "6.5kg", "7kg", "8kg"], "colors": ["White", "Silver"], "base_price": 28990, "sub": "Washing Machines"},
            {"brand": "Samsung", "name": "Samsung 253L Frost Free Double Door Refrigerator", "variants": ["192L", "253L", "314L", "394L", "580L"], "colors": ["Elegant Inox", "Luxe Black", "Digi-Touch Cool White"], "base_price": 22990, "sub": "Refrigerators"},
            {"brand": "LG", "name": "LG 260L Frost Free Double Door Refrigerator", "variants": ["185L", "260L", "340L", "471L", "655L"], "colors": ["Shiny Steel", "Dazzle Steel", "Scarlet Quartz"], "base_price": 24990, "sub": "Refrigerators"},
            {"brand": "Voltas", "name": "Voltas 1.5 Ton 5 Star Inverter Split AC", "variants": ["1 Ton", "1.5 Ton", "2 Ton"], "colors": ["White"], "base_price": 35990, "sub": "Air Conditioners"},
            {"brand": "Daikin", "name": "Daikin 1.5 Ton 5 Star Inverter Split AC", "variants": ["1 Ton", "1.5 Ton", "2 Ton"], "colors": ["White"], "base_price": 42990, "sub": "Air Conditioners"},
        ],
    },

    # ─────────────────────── TABLETS & iPADS ───────────────────────
    "Tablets": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            {"brand": "Apple", "name": "iPad Pro M4 11-inch", "variants": ["256GB WiFi", "512GB WiFi", "1TB WiFi", "256GB WiFi+Cell", "512GB WiFi+Cell", "1TB WiFi+Cell"], "colors": ["Space Black", "Silver"], "base_price": 99900, "sub": "iPad"},
            {"brand": "Apple", "name": "iPad Pro M4 13-inch", "variants": ["256GB WiFi", "512GB WiFi", "1TB WiFi", "256GB WiFi+Cell"], "colors": ["Space Black", "Silver"], "base_price": 119900, "sub": "iPad"},
            {"brand": "Apple", "name": "iPad Air M2 11-inch", "variants": ["128GB WiFi", "256GB WiFi", "512GB WiFi", "1TB WiFi"], "colors": ["Space Gray", "Starlight", "Purple", "Blue"], "base_price": 59900, "sub": "iPad"},
            {"brand": "Apple", "name": "iPad Air M2 13-inch", "variants": ["128GB WiFi", "256GB WiFi", "512GB WiFi"], "colors": ["Space Gray", "Starlight", "Purple", "Blue"], "base_price": 79900, "sub": "iPad"},
            {"brand": "Apple", "name": "iPad 10th Gen", "variants": ["64GB WiFi", "256GB WiFi", "64GB WiFi+Cell", "256GB WiFi+Cell"], "colors": ["Blue", "Pink", "Yellow", "Silver"], "base_price": 39900, "sub": "iPad"},
            {"brand": "Apple", "name": "iPad mini 6th Gen", "variants": ["64GB WiFi", "256GB WiFi", "64GB WiFi+Cell", "256GB WiFi+Cell"], "colors": ["Space Grey", "Starlight", "Pink", "Purple"], "base_price": 46900, "sub": "iPad"},
            {"brand": "Samsung", "name": "Samsung Galaxy Tab S9 FE", "variants": ["128GB WiFi", "256GB WiFi"], "colors": ["Gray", "Silver", "Mint", "Lavender"], "base_price": 34999, "sub": "Samsung Tablet"},
            {"brand": "Samsung", "name": "Samsung Galaxy Tab S9", "variants": ["128GB WiFi", "256GB WiFi"], "colors": ["Graphite", "Beige"], "base_price": 64999, "sub": "Samsung Tablet"},
            {"brand": "Samsung", "name": "Samsung Galaxy Tab S9 Ultra", "variants": ["256GB WiFi", "512GB WiFi", "1TB WiFi"], "colors": ["Graphite", "Beige"], "base_price": 108999, "sub": "Samsung Tablet"},
            {"brand": "Samsung", "name": "Samsung Galaxy Tab A9+", "variants": ["64GB WiFi", "128GB WiFi"], "colors": ["Graphite", "Silver", "Navy"], "base_price": 17999, "sub": "Samsung Tablet"},
            {"brand": "Xiaomi", "name": "Xiaomi Pad 6", "variants": ["128GB", "256GB"], "colors": ["Gravity Gray", "Mist Blue", "Champagne Gold"], "base_price": 24999, "sub": "Xiaomi Tablet"},
            {"brand": "OnePlus", "name": "OnePlus Pad Go", "variants": ["128GB"], "colors": ["Twin Mint", "Slate Gray"], "base_price": 19999, "sub": "OnePlus Tablet"},
            {"brand": "Lenovo", "name": "Lenovo Tab P12", "variants": ["128GB", "256GB"], "colors": ["Storm Grey"], "base_price": 29999, "sub": "Lenovo Tablet"},
            {"brand": "Realme", "name": "Realme Pad 2", "variants": ["128GB"], "colors": ["Imagination Grey", "Imagination Blue"], "base_price": 17999, "sub": "Realme Tablet"},
        ],
    },

    # ─────────────────────── CAMERAS ───────────────────────
    "Cameras": {
        "platforms": ["Amazon", "Flipkart", "Croma"],
        "products": [
            {"brand": "Canon", "name": "Canon EOS R50 Mirrorless Camera", "variants": ["Body Only", "with RF-S 18-45mm Kit"], "colors": ["Black", "White"], "base_price": 67995, "sub": "Mirrorless"},
            {"brand": "Canon", "name": "Canon EOS R6 Mark II", "variants": ["Body Only", "with RF 24-105mm Kit"], "colors": ["Black"], "base_price": 231995, "sub": "Mirrorless"},
            {"brand": "Canon", "name": "Canon EOS R8", "variants": ["Body Only", "with RF 24-50mm Kit"], "colors": ["Black"], "base_price": 152995, "sub": "Mirrorless"},
            {"brand": "Canon", "name": "Canon EOS 1500D DSLR", "variants": ["with 18-55mm Kit"], "colors": ["Black"], "base_price": 36990, "sub": "DSLR"},
            {"brand": "Canon", "name": "Canon EOS 200D II DSLR", "variants": ["with 18-55mm Kit"], "colors": ["Black", "White", "Silver"], "base_price": 54990, "sub": "DSLR"},
            {"brand": "Sony", "name": "Sony Alpha A7 IV", "variants": ["Body Only", "with 28-70mm Kit"], "colors": ["Black"], "base_price": 219990, "sub": "Mirrorless"},
            {"brand": "Sony", "name": "Sony Alpha A7C II", "variants": ["Body Only", "with 28-60mm Kit"], "colors": ["Silver", "Black"], "base_price": 174990, "sub": "Mirrorless"},
            {"brand": "Sony", "name": "Sony ZV-E10 II", "variants": ["Body Only", "with 16-50mm Kit"], "colors": ["Black", "White"], "base_price": 74990, "sub": "Mirrorless Vlogging"},
            {"brand": "Sony", "name": "Sony ZV-1 II", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 67990, "sub": "Compact Vlogging"},
            {"brand": "Nikon", "name": "Nikon Z6 III", "variants": ["Body Only", "with 24-70mm Kit"], "colors": ["Black"], "base_price": 204995, "sub": "Mirrorless"},
            {"brand": "Nikon", "name": "Nikon Z50 II", "variants": ["Body Only", "with 16-50mm Kit", "Dual Lens Kit"], "colors": ["Black"], "base_price": 82995, "sub": "Mirrorless"},
            {"brand": "Nikon", "name": "Nikon D5600 DSLR", "variants": ["with 18-55mm Kit"], "colors": ["Black"], "base_price": 49990, "sub": "DSLR"},
            {"brand": "Fujifilm", "name": "Fujifilm X-T5", "variants": ["Body Only", "with 18-55mm Kit"], "colors": ["Silver", "Black"], "base_price": 169999, "sub": "Mirrorless"},
            {"brand": "Fujifilm", "name": "Fujifilm X-S20", "variants": ["Body Only", "with 15-45mm Kit"], "colors": ["Black"], "base_price": 119999, "sub": "Mirrorless"},
            {"brand": "Fujifilm", "name": "Fujifilm Instax Mini 12", "variants": ["Standard"], "colors": ["Blossom Pink", "Mint Green", "Lilac Purple", "Clay White", "Pastel Blue"], "base_price": 5999, "sub": "Instant Camera"},
            {"brand": "GoPro", "name": "GoPro HERO12 Black", "variants": ["Standard", "Creator Edition"], "colors": ["Black"], "base_price": 39990, "sub": "Action Camera"},
            {"brand": "DJI", "name": "DJI Osmo Pocket 3", "variants": ["Standard", "Creator Combo"], "colors": ["Black"], "base_price": 36990, "sub": "Gimbal Camera"},
            {"brand": "DJI", "name": "DJI Mini 4 Pro Drone", "variants": ["Standard", "Fly More Combo", "Fly More Combo Plus"], "colors": ["Grey"], "base_price": 79990, "sub": "Drone"},
            {"brand": "Insta360", "name": "Insta360 X4", "variants": ["Standard"], "colors": ["Black"], "base_price": 49990, "sub": "360 Camera"},
        ],
    },

    # ─────────────────────── SPEAKERS ───────────────────────
    "Speakers": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            {"brand": "JBL", "name": "JBL Flip 6", "variants": ["Standard"], "colors": ["Black", "Blue", "Red", "Teal", "Pink", "Grey", "Squad"], "base_price": 9999, "sub": "Portable Speaker"},
            {"brand": "JBL", "name": "JBL Charge 5", "variants": ["Standard"], "colors": ["Black", "Blue", "Red", "Teal", "Grey", "Squad"], "base_price": 14999, "sub": "Portable Speaker"},
            {"brand": "JBL", "name": "JBL Go 3", "variants": ["Standard"], "colors": ["Black", "Blue", "Red", "Teal", "Pink", "Orange"], "base_price": 3499, "sub": "Portable Speaker"},
            {"brand": "JBL", "name": "JBL PartyBox 310", "variants": ["Standard"], "colors": ["Black"], "base_price": 34999, "sub": "Party Speaker"},
            {"brand": "Sony", "name": "Sony SRS-XB100", "variants": ["Standard"], "colors": ["Black", "Blue", "Orange", "Grey", "Coral Pink"], "base_price": 3990, "sub": "Portable Speaker"},
            {"brand": "Sony", "name": "Sony SRS-XE300", "variants": ["Standard"], "colors": ["Black", "Blue", "Light Grey"], "base_price": 12990, "sub": "Portable Speaker"},
            {"brand": "Marshall", "name": "Marshall Emberton II", "variants": ["Standard"], "colors": ["Black & Brass", "Cream"], "base_price": 14999, "sub": "Portable Speaker"},
            {"brand": "Marshall", "name": "Marshall Stanmore III", "variants": ["Standard"], "colors": ["Black", "Cream", "Brown"], "base_price": 39999, "sub": "Home Speaker"},
            {"brand": "boAt", "name": "boAt Stone 352", "variants": ["Standard"], "colors": ["Raging Black", "Blue", "Red"], "base_price": 1299, "sub": "Portable Speaker"},
            {"brand": "boAt", "name": "boAt Stone 1200F", "variants": ["Standard"], "colors": ["Black", "Blue", "Red"], "base_price": 3499, "sub": "Portable Speaker"},
            {"brand": "Bose", "name": "Bose SoundLink Flex", "variants": ["Standard"], "colors": ["Black", "White Smoke", "Stone Blue", "Carmine Red"], "base_price": 14900, "sub": "Portable Speaker"},
            {"brand": "Bose", "name": "Bose SoundLink Max", "variants": ["Standard"], "colors": ["Blue Dusk", "Black"], "base_price": 34900, "sub": "Portable Speaker"},
            {"brand": "Ultimate Ears", "name": "UE Wonderboom 3", "variants": ["Standard"], "colors": ["Active Black", "Hyper Pink", "Performance Blue", "Joyous Bright"], "base_price": 6999, "sub": "Portable Speaker"},
            {"brand": "Sonos", "name": "Sonos One (Gen 2)", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 19999, "sub": "Smart Speaker"},
            {"brand": "Amazon", "name": "Echo Dot 5th Gen", "variants": ["Standard", "with Clock"], "colors": ["Charcoal", "Glacier White", "Deep Sea Blue"], "base_price": 4999, "sub": "Smart Speaker"},
            {"brand": "Amazon", "name": "Echo 4th Gen", "variants": ["Standard"], "colors": ["Charcoal", "Glacier White", "Twilight Blue"], "base_price": 9999, "sub": "Smart Speaker"},
            {"brand": "Google", "name": "Google Nest Mini 2nd Gen", "variants": ["Standard"], "colors": ["Charcoal", "Chalk", "Coral", "Sky"], "base_price": 4499, "sub": "Smart Speaker"},
        ],
    },

    # ─────────────────────── BEAUTY & PERSONAL CARE ───────────────────────
    "Beauty & Personal Care": {
        "platforms": ["Amazon", "Flipkart", "Myntra", "Meesho", "JioMart"],
        "products": [
            {"brand": "Mamaearth", "name": "Mamaearth Vitamin C Face Wash", "variants": ["100ml", "150ml", "250ml"], "colors": ["Standard"], "base_price": 349, "sub": "Face Wash"},
            {"brand": "Mamaearth", "name": "Mamaearth Onion Hair Oil", "variants": ["150ml", "250ml"], "colors": ["Standard"], "base_price": 399, "sub": "Hair Oil"},
            {"brand": "Mamaearth", "name": "Mamaearth Rice Water Shampoo", "variants": ["250ml"], "colors": ["Standard"], "base_price": 349, "sub": "Shampoo"},
            {"brand": "Cetaphil", "name": "Cetaphil Gentle Skin Cleanser", "variants": ["125ml", "250ml", "500ml"], "colors": ["Standard"], "base_price": 499, "sub": "Face Wash"},
            {"brand": "CeraVe", "name": "CeraVe Moisturizing Cream", "variants": ["177ml", "340g", "539g"], "colors": ["Standard"], "base_price": 899, "sub": "Moisturizer"},
            {"brand": "The Ordinary", "name": "The Ordinary Niacinamide 10% + Zinc 1%", "variants": ["30ml", "60ml"], "colors": ["Standard"], "base_price": 590, "sub": "Serum"},
            {"brand": "Minimalist", "name": "Minimalist 10% Niacinamide Face Serum", "variants": ["30ml"], "colors": ["Standard"], "base_price": 499, "sub": "Serum"},
            {"brand": "Minimalist", "name": "Minimalist Salicylic Acid 2% Face Wash", "variants": ["100ml"], "colors": ["Standard"], "base_price": 299, "sub": "Face Wash"},
            {"brand": "Lakme", "name": "Lakme Absolute Skin Dew Serum Foundation", "variants": ["Standard"], "colors": ["Ivory Cream", "Warm Natural", "Cool Tan", "Almond Honey"], "base_price": 799, "sub": "Foundation"},
            {"brand": "Lakme", "name": "Lakme 9 to 5 Primer + Matte Lipstick", "variants": ["Standard"], "colors": ["Red Coat", "Rose Day", "Blush Book", "Burgundy Passion"], "base_price": 550, "sub": "Lipstick"},
            {"brand": "Maybelline", "name": "Maybelline Fit Me Matte Foundation", "variants": ["Standard"], "colors": ["110 Porcelain", "128 Warm Nude", "220 Natural Beige", "310 Sun Beige", "330 Toffee"], "base_price": 475, "sub": "Foundation"},
            {"brand": "Maybelline", "name": "Maybelline Lash Sensational Sky High Mascara", "variants": ["Standard"], "colors": ["Very Black", "Brownish Black"], "base_price": 799, "sub": "Mascara"},
            {"brand": "Nivea", "name": "Nivea Soft Light Moisturizing Cream", "variants": ["50ml", "100ml", "200ml", "300ml"], "colors": ["Standard"], "base_price": 225, "sub": "Moisturizer"},
            {"brand": "Dove", "name": "Dove Intense Repair Shampoo", "variants": ["180ml", "340ml", "650ml", "1L"], "colors": ["Standard"], "base_price": 299, "sub": "Shampoo"},
            {"brand": "Philips", "name": "Philips BT3211/15 Beard Trimmer", "variants": ["Standard"], "colors": ["Black"], "base_price": 1445, "sub": "Trimmer"},
            {"brand": "Braun", "name": "Braun Series 5 Electric Shaver", "variants": ["Standard"], "colors": ["Black/Blue"], "base_price": 8999, "sub": "Electric Shaver"},
            {"brand": "Dyson", "name": "Dyson Supersonic Hair Dryer", "variants": ["Standard"], "colors": ["Iron/Fuchsia", "Prussian Blue/Rich Copper", "Nickel/Copper"], "base_price": 34900, "sub": "Hair Dryer"},
            {"brand": "Dyson", "name": "Dyson Airwrap Multi-Styler", "variants": ["Complete", "Complete Long"], "colors": ["Nickel/Copper", "Blue Blush", "Strawberry Bronze"], "base_price": 45900, "sub": "Hair Styler"},
        ],
    },

    # ─────────────────────── GAMING ───────────────────────
    "Gaming": {
        "platforms": ["Amazon", "Flipkart", "Croma", "JioMart"],
        "products": [
            {"brand": "Sony", "name": "PlayStation 5 Slim Console", "variants": ["Digital Edition", "Disc Edition"], "colors": ["White"], "base_price": 44990, "sub": "Console"},
            {"brand": "Sony", "name": "PS5 DualSense Wireless Controller", "variants": ["Standard"], "colors": ["White", "Midnight Black", "Cosmic Red", "Galactic Purple", "Starlight Blue", "Nova Pink", "Ice Blue"], "base_price": 5990, "sub": "Controller"},
            {"brand": "Sony", "name": "PS5 DualSense Edge Wireless Controller", "variants": ["Standard"], "colors": ["White"], "base_price": 18990, "sub": "Controller"},
            {"brand": "Sony", "name": "PlayStation VR2", "variants": ["Standard", "Horizon Bundle"], "colors": ["White"], "base_price": 54999, "sub": "VR Headset"},
            {"brand": "Microsoft", "name": "Xbox Series X Console", "variants": ["1TB"], "colors": ["Black", "White"], "base_price": 49990, "sub": "Console"},
            {"brand": "Microsoft", "name": "Xbox Series S Console", "variants": ["512GB", "1TB"], "colors": ["White", "Carbon Black"], "base_price": 34990, "sub": "Console"},
            {"brand": "Microsoft", "name": "Xbox Wireless Controller", "variants": ["Standard"], "colors": ["Carbon Black", "Robot White", "Shock Blue", "Pulse Red", "Electric Volt", "Deep Pink"], "base_price": 5390, "sub": "Controller"},
            {"brand": "Nintendo", "name": "Nintendo Switch OLED Model", "variants": ["Standard"], "colors": ["White", "Neon Red/Neon Blue", "Pokemon Scarlet & Violet Edition"], "base_price": 34999, "sub": "Console"},
            {"brand": "Nintendo", "name": "Nintendo Switch Lite", "variants": ["Standard"], "colors": ["Blue", "Coral", "Yellow", "Turquoise", "Grey"], "base_price": 19999, "sub": "Console"},
            {"brand": "Logitech", "name": "Logitech G502 Hero Gaming Mouse", "variants": ["Standard"], "colors": ["Black"], "base_price": 3995, "sub": "Gaming Mouse"},
            {"brand": "Logitech", "name": "Logitech G Pro X Superlight 2", "variants": ["Standard"], "colors": ["Black", "White", "Pink"], "base_price": 12995, "sub": "Gaming Mouse"},
            {"brand": "Razer", "name": "Razer DeathAdder V3", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 7999, "sub": "Gaming Mouse"},
            {"brand": "Razer", "name": "Razer BlackWidow V4", "variants": ["Standard"], "colors": ["Black"], "base_price": 14999, "sub": "Gaming Keyboard"},
            {"brand": "Razer", "name": "Razer Kraken V3 X", "variants": ["Standard"], "colors": ["Black"], "base_price": 3999, "sub": "Gaming Headset"},
            {"brand": "HyperX", "name": "HyperX Cloud III", "variants": ["Standard"], "colors": ["Black", "Red/Black"], "base_price": 8999, "sub": "Gaming Headset"},
            {"brand": "SteelSeries", "name": "SteelSeries Arctis Nova 7", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 14999, "sub": "Gaming Headset"},
            {"brand": "Corsair", "name": "Corsair K70 RGB Pro", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 13499, "sub": "Gaming Keyboard"},
            {"brand": "Ant Esports", "name": "Ant Esports MK1200 Mini Keyboard", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 1999, "sub": "Gaming Keyboard"},
            {"brand": "Cosmic Byte", "name": "Cosmic Byte Equinox Nimbus Gaming Chair", "variants": ["Standard"], "colors": ["Black/Blue", "Black/Red", "Black/Green", "Black/Orange"], "base_price": 12999, "sub": "Gaming Chair"},
        ],
    },

    # ─────────────────────── BOOKS ───────────────────────
    "Books": {
        "platforms": ["Amazon", "Flipkart", "JioMart"],
        "products": [
            {"brand": "Penguin", "name": "Atomic Habits by James Clear", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 499, "sub": "Self-Help"},
            {"brand": "Penguin", "name": "The Psychology of Money by Morgan Housel", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 349, "sub": "Finance"},
            {"brand": "Harper", "name": "Ikigai: The Japanese Secret to a Long and Happy Life", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 299, "sub": "Self-Help"},
            {"brand": "Penguin", "name": "Rich Dad Poor Dad by Robert Kiyosaki", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 399, "sub": "Finance"},
            {"brand": "Rupa", "name": "The Alchemist by Paulo Coelho", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 299, "sub": "Fiction"},
            {"brand": "Penguin", "name": "Sapiens by Yuval Noah Harari", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 499, "sub": "Non-Fiction"},
            {"brand": "Simon & Schuster", "name": "Think and Grow Rich by Napoleon Hill", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 199, "sub": "Self-Help"},
            {"brand": "Scholastic", "name": "Harry Potter Complete Box Set (7 Books)", "variants": ["Standard"], "colors": ["Standard"], "base_price": 2999, "sub": "Fiction"},
            {"brand": "HarperCollins", "name": "The Subtle Art of Not Giving a F*ck", "variants": ["Paperback", "Hardcover"], "colors": ["Standard"], "base_price": 350, "sub": "Self-Help"},
            {"brand": "Macmillan", "name": "Thinking, Fast and Slow by Daniel Kahneman", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 499, "sub": "Psychology"},
            {"brand": "Penguin", "name": "Deep Work by Cal Newport", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 399, "sub": "Productivity"},
            {"brand": "Fingerprint", "name": "You Can Win by Shiv Khera", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 199, "sub": "Self-Help"},
            {"brand": "Penguin", "name": "The Monk Who Sold His Ferrari by Robin Sharma", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 225, "sub": "Self-Help"},
            {"brand": "Westland", "name": "The Immortals of Meluha by Amish Tripathi", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 299, "sub": "Fiction"},
            {"brand": "Rupa", "name": "Five Point Someone by Chetan Bhagat", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 175, "sub": "Fiction"},
            {"brand": "Rupa", "name": "Wings of Fire by APJ Abdul Kalam", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 199, "sub": "Biography"},
            {"brand": "O'Reilly", "name": "Python Crash Course by Eric Matthes", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 699, "sub": "Technology"},
            {"brand": "Pearson", "name": "Let Us C by Yashavant Kanetkar", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 399, "sub": "Technology"},
            {"brand": "BPB", "name": "Data Structures and Algorithms Made Easy", "variants": ["Paperback"], "colors": ["Standard"], "base_price": 499, "sub": "Technology"},
        ],
    },

    # ─────────────────────── SPORTS & FITNESS ───────────────────────
    "Sports & Fitness": {
        "platforms": ["Amazon", "Flipkart", "Myntra", "JioMart"],
        "products": [
            {"brand": "Nike", "name": "Nike Revolution 6 Running Shoes", "variants": ["UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["Black/White", "Grey/Volt", "Navy/Red"], "base_price": 3695, "sub": "Running Shoes"},
            {"brand": "Adidas", "name": "Adidas RunFalcon 3.0 Running Shoes", "variants": ["UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["Core Black", "Cloud White", "Grey"], "base_price": 3999, "sub": "Running Shoes"},
            {"brand": "Boldfit", "name": "Boldfit Protein Shaker Bottle", "variants": ["500ml", "700ml"], "colors": ["Black", "Blue", "Green", "Red"], "base_price": 249, "sub": "Gym Accessories"},
            {"brand": "Boldfit", "name": "Boldfit Resistance Bands Set", "variants": ["Light", "Medium", "Heavy", "Full Set"], "colors": ["Multicolor"], "base_price": 399, "sub": "Gym Accessories"},
            {"brand": "Nivia", "name": "Nivia Storm Football", "variants": ["Size 5"], "colors": ["White/Blue", "White/Black"], "base_price": 749, "sub": "Football"},
            {"brand": "Yonex", "name": "Yonex Astrox 88D Pro Badminton Racket", "variants": ["Standard"], "colors": ["Camel Gold"], "base_price": 12999, "sub": "Badminton"},
            {"brand": "Yonex", "name": "Yonex Nanoray Light 18i Badminton Racket", "variants": ["Standard"], "colors": ["Black/Red", "Black/Blue"], "base_price": 2399, "sub": "Badminton"},
            {"brand": "Li-Ning", "name": "Li-Ning Super Series SS-98 G7 Badminton Racket", "variants": ["Standard"], "colors": ["Black/Gold"], "base_price": 3499, "sub": "Badminton"},
            {"brand": "MR. DARK", "name": "Adjustable Dumbbells Set", "variants": ["10kg Pair", "20kg Pair", "30kg Pair"], "colors": ["Black"], "base_price": 1999, "sub": "Dumbbells"},
            {"brand": "Strauss", "name": "Strauss Anti-Skid Yoga Mat 6mm", "variants": ["4mm", "6mm", "8mm"], "colors": ["Purple", "Blue", "Grey", "Pink", "Green"], "base_price": 399, "sub": "Yoga"},
            {"brand": "PowerMax", "name": "PowerMax TDA-230M Motorized Treadmill", "variants": ["Standard"], "colors": ["Black/Grey"], "base_price": 24999, "sub": "Treadmill"},
            {"brand": "Decathlon", "name": "Decathlon Kiprun Run 100 Running Shoes", "variants": ["UK 7", "UK 8", "UK 9", "UK 10", "UK 11"], "colors": ["Black", "Blue", "Grey"], "base_price": 2499, "sub": "Running Shoes"},
            {"brand": "Cosco", "name": "Cosco All Court Tennis Ball (Pack of 3)", "variants": ["Standard"], "colors": ["Yellow"], "base_price": 199, "sub": "Tennis"},
            {"brand": "Kookaburra", "name": "Kookaburra Kahuna Pro Cricket Bat", "variants": ["SH", "LH"], "colors": ["Natural"], "base_price": 12999, "sub": "Cricket"},
            {"brand": "SG", "name": "SG RSD Xtreme Cricket Bat", "variants": ["SH", "Full Size"], "colors": ["Natural"], "base_price": 4999, "sub": "Cricket"},
            {"brand": "SS", "name": "SS Ton Gladiator Cricket Bat", "variants": ["SH"], "colors": ["Natural/Blue"], "base_price": 7999, "sub": "Cricket"},
        ],
    },

    # ─────────────────────── GROCERY & ESSENTIALS ───────────────────────
    "Grocery & Essentials": {
        "platforms": ["Amazon", "Flipkart", "JioMart", "Meesho"],
        "products": [
            {"brand": "Tata", "name": "Tata Gold Tea", "variants": ["250g", "500g", "1kg"], "colors": ["Standard"], "base_price": 199, "sub": "Tea"},
            {"brand": "Nescafe", "name": "Nescafe Classic Coffee", "variants": ["50g", "100g", "200g"], "colors": ["Standard"], "base_price": 299, "sub": "Coffee"},
            {"brand": "Bru", "name": "Bru Instant Coffee", "variants": ["50g", "100g", "200g"], "colors": ["Standard"], "base_price": 249, "sub": "Coffee"},
            {"brand": "Aashirvaad", "name": "Aashirvaad Superior MP Atta", "variants": ["1kg", "2kg", "5kg", "10kg"], "colors": ["Standard"], "base_price": 299, "sub": "Flour"},
            {"brand": "Fortune", "name": "Fortune Sunlite Refined Sunflower Oil", "variants": ["1L", "2L", "5L"], "colors": ["Standard"], "base_price": 169, "sub": "Cooking Oil"},
            {"brand": "Saffola", "name": "Saffola Gold Cooking Oil", "variants": ["1L", "2L", "5L"], "colors": ["Standard"], "base_price": 199, "sub": "Cooking Oil"},
            {"brand": "Maggi", "name": "Maggi 2-Minute Noodles Masala", "variants": ["Pack of 4", "Pack of 8", "Pack of 12", "Family Pack"], "colors": ["Standard"], "base_price": 56, "sub": "Noodles"},
            {"brand": "Cadbury", "name": "Cadbury Dairy Milk Silk", "variants": ["60g", "150g", "Oreo", "Bubbly", "Roast Almond"], "colors": ["Standard"], "base_price": 99, "sub": "Chocolates"},
            {"brand": "Amul", "name": "Amul Butter", "variants": ["100g", "200g", "500g"], "colors": ["Standard"], "base_price": 56, "sub": "Dairy"},
            {"brand": "Haldiram's", "name": "Haldiram's Aloo Bhujia", "variants": ["200g", "400g", "1kg"], "colors": ["Standard"], "base_price": 99, "sub": "Snacks"},
            {"brand": "Britannia", "name": "Britannia Good Day Cashew Cookies", "variants": ["120g", "250g", "600g"], "colors": ["Standard"], "base_price": 40, "sub": "Biscuits"},
            {"brand": "Parle", "name": "Parle-G Gold Biscuits", "variants": ["100g", "200g", "500g"], "colors": ["Standard"], "base_price": 25, "sub": "Biscuits"},
            {"brand": "Mother Dairy", "name": "Mother Dairy Classic Curd", "variants": ["200g", "400g", "1kg"], "colors": ["Standard"], "base_price": 35, "sub": "Dairy"},
            {"brand": "Real", "name": "Real Fruit Power Mixed Fruit Juice", "variants": ["200ml", "1L"], "colors": ["Standard"], "base_price": 99, "sub": "Beverages"},
            {"brand": "Paper Boat", "name": "Paper Boat Aam Panna", "variants": ["200ml Pack of 6"], "colors": ["Standard"], "base_price": 180, "sub": "Beverages"},
        ],
    },

    # ─────────────────────── MOBILE ACCESSORIES ───────────────────────
    "Mobile Accessories": {
        "platforms": ["Amazon", "Flipkart", "Meesho", "JioMart"],
        "products": [
            {"brand": "Spigen", "name": "Spigen Ultra Hybrid Case for iPhone 16 Pro", "variants": ["Standard"], "colors": ["Crystal Clear", "Matte Black", "Frost Black"], "base_price": 1499, "sub": "Phone Cases"},
            {"brand": "Ringke", "name": "Ringke Fusion Case for Samsung Galaxy S25 Ultra", "variants": ["Standard"], "colors": ["Clear", "Matte Clear", "Smoke Black"], "base_price": 1299, "sub": "Phone Cases"},
            {"brand": "Anker", "name": "Anker 735 Charger (Nano II 65W)", "variants": ["Standard"], "colors": ["Black", "White"], "base_price": 3999, "sub": "Chargers"},
            {"brand": "Anker", "name": "Anker 622 MagGo Magnetic Battery", "variants": ["5000mAh"], "colors": ["Black", "Blue", "Green", "White"], "base_price": 4999, "sub": "Power Banks"},
            {"brand": "Belkin", "name": "Belkin 20W USB-C PD Wall Charger", "variants": ["Standard"], "colors": ["White", "Black"], "base_price": 1999, "sub": "Chargers"},
            {"brand": "Samsung", "name": "Samsung 25W Travel Adapter", "variants": ["Standard"], "colors": ["White", "Black"], "base_price": 1249, "sub": "Chargers"},
            {"brand": "Apple", "name": "Apple 20W USB-C Power Adapter", "variants": ["Standard"], "colors": ["White"], "base_price": 1900, "sub": "Chargers"},
            {"brand": "Apple", "name": "Apple MagSafe Charger", "variants": ["Standard"], "colors": ["White"], "base_price": 4500, "sub": "Wireless Chargers"},
            {"brand": "Mi", "name": "Mi 20000mAh Power Bank 3i", "variants": ["10000mAh", "20000mAh"], "colors": ["Black"], "base_price": 1499, "sub": "Power Banks"},
            {"brand": "Ambrane", "name": "Ambrane 10000mAh Lithium Polymer Power Bank", "variants": ["10000mAh", "20000mAh", "27000mAh"], "colors": ["Black", "White", "Blue"], "base_price": 799, "sub": "Power Banks"},
            {"brand": "boAt", "name": "boAt Deuce USB 300 Micro USB Cable", "variants": ["1m", "1.5m"], "colors": ["Mercurial Black", "Jade Green"], "base_price": 199, "sub": "Cables"},
            {"brand": "OnePlus", "name": "OnePlus SUPERVOOC 100W Dual Port Charger", "variants": ["Standard"], "colors": ["White"], "base_price": 3999, "sub": "Chargers"},
            {"brand": "Spigen", "name": "Spigen Tempered Glass Screen Protector", "variants": ["iPhone 16 Pro", "Samsung Galaxy S25 Ultra", "OnePlus 13", "Pixel 9 Pro"], "colors": ["Clear"], "base_price": 999, "sub": "Screen Protectors"},
            {"brand": "Portronics", "name": "Portronics Car Charger Dual USB", "variants": ["Standard"], "colors": ["Black"], "base_price": 699, "sub": "Car Chargers"},
        ],
    },

    # ─────────────────────── TOYS & GAMES ───────────────────────
    "Toys & Games": {
        "platforms": ["Amazon", "Flipkart", "Meesho", "JioMart"],
        "products": [
            {"brand": "LEGO", "name": "LEGO Technic Bugatti Chiron", "variants": ["Standard"], "colors": ["Blue/Black"], "base_price": 32999, "sub": "Building Sets"},
            {"brand": "LEGO", "name": "LEGO Star Wars Millennium Falcon", "variants": ["Standard"], "colors": ["Grey"], "base_price": 14999, "sub": "Building Sets"},
            {"brand": "LEGO", "name": "LEGO City Police Station", "variants": ["Standard"], "colors": ["Multicolor"], "base_price": 5999, "sub": "Building Sets"},
            {"brand": "LEGO", "name": "LEGO Creator 3-in-1 Exotic Parrot", "variants": ["Standard"], "colors": ["Multicolor"], "base_price": 1699, "sub": "Building Sets"},
            {"brand": "Hasbro", "name": "Monopoly Classic Board Game", "variants": ["Standard"], "colors": ["Standard"], "base_price": 999, "sub": "Board Games"},
            {"brand": "Hasbro", "name": "Jenga Classic Game", "variants": ["Standard"], "colors": ["Natural Wood"], "base_price": 699, "sub": "Board Games"},
            {"brand": "Mattel", "name": "UNO Card Game", "variants": ["Standard", "UNO Flip", "UNO Attack"], "colors": ["Standard"], "base_price": 199, "sub": "Card Games"},
            {"brand": "Mattel", "name": "Hot Wheels 20-Car Gift Pack", "variants": ["Standard"], "colors": ["Assorted"], "base_price": 1299, "sub": "Die-Cast Cars"},
            {"brand": "Mattel", "name": "Barbie Fashionistas Doll", "variants": ["Standard"], "colors": ["Blonde", "Brunette", "Red Hair", "Black Hair"], "base_price": 899, "sub": "Dolls"},
            {"brand": "Funko", "name": "Funko Pop! Marvel Iron Man", "variants": ["Standard"], "colors": ["Standard"], "base_price": 1499, "sub": "Collectibles"},
            {"brand": "Funko", "name": "Funko Pop! Harry Potter", "variants": ["Standard"], "colors": ["Standard"], "base_price": 1299, "sub": "Collectibles"},
            {"brand": "Funskool", "name": "Funskool Scrabble Original Board Game", "variants": ["Standard"], "colors": ["Standard"], "base_price": 549, "sub": "Board Games"},
            {"brand": "Toyshine", "name": "Toyshine Remote Control Car", "variants": ["Standard"], "colors": ["Red", "Blue", "Black"], "base_price": 799, "sub": "RC Vehicles"},
            {"brand": "Smartivity", "name": "Smartivity Mechanical Hand STEM Toy", "variants": ["Standard"], "colors": ["Wood"], "base_price": 999, "sub": "STEM Toys"},
            {"brand": "Ravensburger", "name": "Ravensburger 1000 Piece Puzzle", "variants": ["Standard"], "colors": ["Various Themes"], "base_price": 1499, "sub": "Puzzles"},
            {"brand": "Nerf", "name": "Nerf Elite 2.0 Commander RD-6", "variants": ["Standard"], "colors": ["Blue/Orange"], "base_price": 1299, "sub": "Blasters"},
        ],
    },
}

# Indian names for users
INDIAN_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Atharva", "Advik", "Pranav", "Advaith",
    "Ananya", "Diya", "Myra", "Sara", "Aanya", "Aadhya", "Aaradhya", "Anvi",
    "Priya", "Sneha", "Kavya", "Isha", "Navya", "Pari", "Saanvi",
    "Rahul", "Amit", "Rohit", "Vikram", "Suresh", "Rajesh", "Ravi",
    "Neha", "Pooja", "Deepika", "Shruti", "Meera", "Nisha", "Sakshi",
    "Karan", "Nikhil", "Siddharth", "Harsh", "Dev", "Yash", "Rohan",
    "Zara", "Rhea", "Tara", "Dia", "Mira", "Naina", "Kiara",
    "Arnav", "Dhruv", "Kabir", "Rudra", "Shiv", "Aryan", "Manav",
    "Riya", "Simran", "Tanvi", "Aisha", "Kritika", "Lavanya", "Divya",
    "Varun", "Gaurav", "Akash", "Mohit", "Tushar", "Ankit", "Sumit",
    "Swati", "Rashmi", "Pallavi", "Sonal", "Komal", "Preeti", "Jyoti",
    "Om", "Shaan", "Rehan", "Kartik", "Ishan", "Lakshay", "Parth",
    "Aahana", "Mahika", "Anika", "Samaira", "Siya", "Kyra", "Trisha",
    "Vikash", "Deepak", "Sanjay", "Ramesh", "Naresh", "Dinesh", "Manoj",
]

# Review templates
REVIEW_TEMPLATES = {
    5: [
        "Absolutely love this {sub}! {reason}. Best purchase on {platform}.",
        "Paisa vasool! {reason}. Highly recommend buying from {platform}.",
        "Five stars isn't enough! {reason}. Delivery was superfast.",
        "Amazing product! {reason}. Much better than expected.",
        "Top quality {sub}! {reason}. Will definitely buy again.",
        "Bahut accha product hai! {reason}. Very satisfied with purchase.",
    ],
    4: [
        "Really good {sub} overall. {reason}. Minor issues but worth buying.",
        "Great value for money! {reason}. Happy with this purchase.",
        "Solid product, does what it promises. {reason}. Good quality.",
        "Accha product hai. {reason}. Would recommend to friends.",
        "Very pleased with quality. {reason}. Fast delivery from {platform}.",
    ],
    3: [
        "Decent {sub}, theek hai. {reason}. Gets the job done.",
        "Average product for the price. {reason}. Expected better quality.",
        "OK OK quality. {reason}. Not great, not terrible.",
        "Chalega for this price. {reason}. Mixed feelings overall.",
        "Fair product. {reason}. Could have been better.",
    ],
    2: [
        "Below expectations. {reason}. Overpriced for what you get.",
        "Not impressed at all. {reason}. Quality is poor.",
        "Disappointing. {reason}. Looking for a return/refund.",
        "Bekaar quality for ₹{price}. {reason}. Don't waste money.",
    ],
    1: [
        "Terrible quality! {reason}. Complete waste of money.",
        "Don't buy this! {reason}. Broke after first use.",
        "Worst {sub} I've ever bought. {reason}. Scam product.",
        "Very disappointed with {brand}. {reason}. Returning immediately.",
    ],
}

POSITIVE_REASONS = [
    "Build quality is premium", "Perfect fit and finish",
    "Easy to use from day one", "Looks even better in person",
    "Battery life is outstanding", "Value for money is great",
    "Packaging was superb", "Camera quality is amazing",
    "Performance is buttery smooth", "Best in this price range",
    "Color is exactly as shown", "Very comfortable to use daily",
]
NEUTRAL_REASONS = [
    "Works as expected", "Standard quality for the price",
    "Does the basic job well", "Nothing to complain about",
    "About what you'd expect at this price",
]
NEGATIVE_REASONS = [
    "Material feels cheap", "Stopped working within a week",
    "Not as shown in photos", "Arrived with a dent",
    "Poor build quality", "Heating issue observed",
    "Way smaller than expected", "Colors don't match listing",
]


def _make_platform_prices(base_price, available_platforms):
    """Generate realistic platform-specific prices."""
    prices = {}
    urls = {}
    for platform in available_platforms:
        pinfo = PLATFORMS[platform]
        factor = random.uniform(*pinfo["price_factor"])
        p = round(base_price * factor)
        # Round to nearest 9 (Indian pricing style)
        p = (p // 10) * 10 + 9 if p > 100 else p
        prices[platform] = p
        query = "test"  # Will be filled per product
        urls[platform] = pinfo["url_template"]

    best = min(prices, key=prices.get)
    return prices, urls, best


def _variant_price_delta(base_price, variant, product_name):
    """Calculate price adjustment for a variant."""
    variant_lower = variant.lower()

    # Storage-based pricing
    if "1tb" in variant_lower:
        return int(base_price * 0.25)
    elif "512gb" in variant_lower:
        return int(base_price * 0.12)
    elif "256gb" in variant_lower:
        return int(base_price * 0.05)
    elif "128gb" in variant_lower:
        return 0
    elif "64gb" in variant_lower:
        return -int(base_price * 0.05)

    # RAM/Storage combos for laptops
    if "32gb" in variant_lower or "2tb" in variant_lower:
        return int(base_price * 0.30)
    elif "16gb/1tb" in variant_lower or "36gb" in variant_lower:
        return int(base_price * 0.20)
    elif "16gb/512gb" in variant_lower or "18gb" in variant_lower:
        return int(base_price * 0.10)
    elif "8gb/512gb" in variant_lower:
        return int(base_price * 0.03)
    elif "8gb/256gb" in variant_lower:
        return -int(base_price * 0.05)

    # GPU-based (laptops)
    if "rtx 4090" in variant_lower:
        return int(base_price * 0.6)
    elif "rtx 4080" in variant_lower:
        return int(base_price * 0.4)
    elif "rtx 4070" in variant_lower:
        return int(base_price * 0.25)
    elif "rtx 4060" in variant_lower:
        return int(base_price * 0.15)
    elif "rtx 4050" in variant_lower:
        return int(base_price * 0.08)
    elif "rtx 3050" in variant_lower:
        return 0

    # Size-based (TVs, watches)
    if "85 inch" in variant_lower:
        return int(base_price * 1.5)
    elif "83 inch" in variant_lower:
        return int(base_price * 1.3)
    elif "77 inch" in variant_lower:
        return int(base_price * 1.0)
    elif "75 inch" in variant_lower:
        return int(base_price * 0.8)
    elif "65 inch" in variant_lower:
        return int(base_price * 0.5)
    elif "55 inch" in variant_lower:
        return int(base_price * 0.2)
    elif "50 inch" in variant_lower:
        return int(base_price * 0.1)
    elif "43 inch" in variant_lower or "42 inch" in variant_lower:
        return 0
    elif "32 inch" in variant_lower:
        return -int(base_price * 0.15)

    # Weight-based (grocery, cookers)
    if "10kg" in variant_lower or "10l" in variant_lower:
        return int(base_price * 0.6)
    elif "8kg" in variant_lower or "8l" in variant_lower:
        return int(base_price * 0.4)
    elif "5kg" in variant_lower or "5l" in variant_lower:
        return int(base_price * 0.3)
    elif "2l" in variant_lower or "2kg" in variant_lower:
        return int(base_price * 0.1)
    elif "1l" in variant_lower or "1kg" in variant_lower:
        return 0

    # Clothing sizes (no price change)
    if variant_lower in ["xs", "s", "m", "l", "xl", "xxl", "28", "30", "32", "34", "36", "38", "39", "40", "42", "44", "46"]:
        return 0

    # Volume-based (beauty)
    if "500ml" in variant_lower or "539g" in variant_lower:
        return int(base_price * 0.5)
    elif "340g" in variant_lower or "300ml" in variant_lower:
        return int(base_price * 0.3)
    elif "250ml" in variant_lower or "256gb" in variant_lower:
        return int(base_price * 0.15)
    elif "200ml" in variant_lower or "200g" in variant_lower:
        return int(base_price * 0.1)
    elif "150ml" in variant_lower:
        return int(base_price * 0.05)
    elif "100ml" in variant_lower or "100g" in variant_lower:
        return 0
    elif "50ml" in variant_lower or "50g" in variant_lower:
        return -int(base_price * 0.1)

    # Book variants
    if "hardcover" in variant_lower:
        return int(base_price * 0.4)

    # TV sizes already handled, watch sizes
    if "45mm" in variant_lower or "44mm" in variant_lower:
        return int(base_price * 0.1)
    elif "47mm" in variant_lower or "49mm" in variant_lower:
        return int(base_price * 0.15)

    # Phone cellular variants
    if "cellular" in variant_lower or "cell" in variant_lower:
        return int(base_price * 0.15)

    return 0


def generate_products():
    """Generate all product entries with every variant and color."""
    products = []
    pid = 0

    for category, cat_info in CATEGORIES.items():
        available_platforms = cat_info["platforms"]

        for prod in cat_info["products"]:
            brand = prod["brand"]
            name = prod["name"]
            base_price = prod["base_price"]
            sub_category = prod["sub"]

            for variant in prod["variants"]:
                for color in prod["colors"]:
                    pid += 1

                    # Calculate variant-specific price
                    delta = _variant_price_delta(base_price, variant, name)
                    actual_price = max(base_price + delta, int(base_price * 0.5))

                    # Generate title
                    if color != "Standard" and variant != "Standard":
                        title = f"{name} ({variant}, {color})"
                    elif color != "Standard":
                        title = f"{name} ({color})"
                    elif variant != "Standard":
                        title = f"{name} ({variant})"
                    else:
                        title = name

                    model_variant = f"{variant}, {color}" if color != "Standard" and variant != "Standard" else variant if variant != "Standard" else color if color != "Standard" else ""

                    # Generate description
                    description = f"{title} by {brand}. "
                    desc_parts = [
                        f"Premium quality {sub_category.lower()} available in India",
                        f"Official {brand} product with manufacturer warranty",
                        f"Category: {category} > {sub_category}",
                        f"Compare prices across Flipkart, Amazon & more to get the best deal",
                        f"Free delivery available on most platforms",
                    ]
                    description += ". ".join(desc_parts) + "."

                    # MRP and discount
                    discount = random.choice([0, 5, 8, 10, 12, 15, 18, 20, 22, 25, 30, 35, 40])
                    original_price = round(actual_price / (1 - discount / 100)) if discount > 0 else actual_price
                    # Round original price to nearest 10
                    original_price = round(original_price / 10) * 10

                    # Platform prices
                    platform_prices, platform_urls, best_platform = _make_platform_prices(actual_price, available_platforms)

                    # Make proper URLs with product name
                    search_query = title.replace(" ", "+").replace("(", "").replace(")", "")
                    final_urls = {}
                    for plat, url_t in platform_urls.items():
                        final_urls[plat] = PLATFORMS[plat]["url_template"].format(query=search_query)

                    # EMI availability
                    emi_available = 1 if actual_price >= 3000 else 0

                    # Delivery days
                    delivery = random.randint(1, 5)

                    # Availability
                    avail = random.choices(
                        ["In Stock", "In Stock", "In Stock", "In Stock", "Limited Stock", "Out of Stock"],
                        weights=[60, 20, 10, 5, 4, 1]
                    )[0]

                    products.append({
                        "product_id": pid,
                        "title": title,
                        "category": category,
                        "sub_category": sub_category,
                        "brand": brand,
                        "description": description,
                        "price": actual_price,
                        "original_price": original_price,
                        "discount_percent": discount,
                        "avg_rating": 0.0,
                        "num_ratings": 0,
                        "image_url": f"https://picsum.photos/seed/{pid}/300/300",
                        "platform_prices": json.dumps(platform_prices),
                        "best_platform": best_platform,
                        "platform_urls": json.dumps(final_urls),
                        "availability": avail,
                        "emi_available": emi_available,
                        "delivery_days": delivery,
                        "model_variant": model_variant,
                    })

    return products


def generate_users(n=500):
    """Generate users with Indian names and category preferences."""
    users = []
    categories_list = list(CATEGORIES.keys())

    for uid in range(1, n + 1):
        name = random.choice(INDIAN_NAMES)
        username = f"{name.lower()}_{uid}"
        join_date = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900))).strftime("%Y-%m-%d")
        prefs = random.sample(categories_list, k=random.randint(2, 5))
        users.append({
            "user_id": uid,
            "username": username,
            "join_date": join_date,
            "preferred_categories": json.dumps(prefs),
        })
    return users


def generate_ratings(products, users, n_ratings=25000):
    """Generate ratings with realistic patterns."""
    ratings = []
    product_by_cat = {}
    for p in products:
        product_by_cat.setdefault(p["category"], []).append(p["product_id"])

    seen = set()
    rating_id = 0
    platform_names = list(PLATFORMS.keys())

    for user in users:
        prefs = json.loads(user["preferred_categories"])
        n_user_ratings = random.randint(15, 100)

        for _ in range(n_user_ratings):
            if rating_id >= n_ratings:
                break

            # 70% chance preferred category
            if random.random() < 0.7 and prefs:
                cat = random.choice(prefs)
                if cat in product_by_cat and product_by_cat[cat]:
                    pid = random.choice(product_by_cat[cat])
                else:
                    pid = random.choice(products)["product_id"]
            else:
                pid = random.choice(products)["product_id"]

            key = (user["user_id"], pid)
            if key in seen:
                continue
            seen.add(key)

            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.07, 0.12, 0.28, 0.48], k=1)[0]

            # Find product info for review
            prod_info = None
            for p in products:
                if p["product_id"] == pid:
                    prod_info = p
                    break

            rounded = max(1, min(5, rating))
            template = random.choice(REVIEW_TEMPLATES[rounded])
            if rounded >= 4:
                reason = random.choice(POSITIVE_REASONS)
            elif rounded == 3:
                reason = random.choice(NEUTRAL_REASONS)
            else:
                reason = random.choice(NEGATIVE_REASONS)

            platform = random.choice(platform_names)
            sub = prod_info["sub_category"] if prod_info else "product"
            brand = prod_info["brand"] if prod_info else "brand"
            price = prod_info["price"] if prod_info else 999

            review_text = template.format(
                reason=reason,
                platform=platform,
                sub=sub,
                brand=brand,
                price=price,
            )
            review_date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))).strftime("%Y-%m-%d")

            ratings.append({
                "user_id": user["user_id"],
                "product_id": pid,
                "rating": float(rating),
                "review_text": review_text,
                "review_date": review_date,
                "helpful_votes": random.randint(0, 80) if random.random() < 0.3 else 0,
            })
            rating_id += 1

        if rating_id >= n_ratings:
            break

    return ratings


def build_database(db_path=None):
    """Build the complete SQLite database with real Indian products."""
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "amazon_recommendations.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if os.path.exists(db_path):
        os.remove(db_path)

    print("🔧 Generating Real Indian E-Commerce Dataset...")
    products = generate_products()
    users = generate_users(500)
    ratings_data = generate_ratings(products, users, 25000)

    print(f"   📦 Products: {len(products)} (all models & variants)")
    print(f"   👤 Users:    {len(users)}")
    print(f"   ⭐ Ratings:  {len(ratings_data)}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")
    with open(schema_path, "r") as f:
        cursor.executescript(f.read())

    cursor.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(p["product_id"], p["title"], p["category"], p["sub_category"],
          p["brand"], p["description"], p["price"], p["original_price"],
          p["discount_percent"], p["avg_rating"], p["num_ratings"],
          p["image_url"], p["platform_prices"], p["best_platform"],
          p["platform_urls"], p["availability"], p["emi_available"],
          p["delivery_days"], p["model_variant"]) for p in products]
    )

    cursor.executemany(
        "INSERT INTO users VALUES (?,?,?,?)",
        [(u["user_id"], u["username"], u["join_date"],
          u["preferred_categories"]) for u in users]
    )

    cursor.executemany(
        "INSERT INTO ratings (user_id, product_id, rating, review_text, review_date, helpful_votes) VALUES (?,?,?,?,?,?)",
        [(r["user_id"], r["product_id"], r["rating"], r["review_text"],
          r["review_date"], r["helpful_votes"]) for r in ratings_data]
    )

    cursor.execute("""
        UPDATE products SET
            avg_rating = (SELECT ROUND(AVG(r.rating), 2) FROM ratings r WHERE r.product_id = products.product_id),
            num_ratings = (SELECT COUNT(*) FROM ratings r WHERE r.product_id = products.product_id)
        WHERE product_id IN (SELECT DISTINCT product_id FROM ratings)
    """)

    conn.commit()
    conn.close()
    print(f"   ✅ Database saved to: {db_path}")
    return db_path


if __name__ == "__main__":
    build_database()
