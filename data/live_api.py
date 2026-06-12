import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
import random
import time

# List of user agents to rotate and avoid basic blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def scrape_amazon_in(query):
    """
    Scrapes Amazon India search results for a given query.
    Returns a list of dictionaries containing product details.
    """
    url = f"https://www.amazon.in/s?k={urllib.parse.quote(query)}"
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Amazon Scraping Error: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []
    
    # Amazon search results usually have the data-component-type="s-search-result"
    results = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    for idx, item in enumerate(results[:10]):  # Limit to top 10 results
        try:
            # Title
            title_elem = item.find('h2', class_='a-size-mini') or item.find('span', class_='a-text-normal')
            if not title_elem:
                continue
            title = title_elem.text.strip()
            
            # Price
            price_elem = item.find('span', class_='a-price-whole')
            if not price_elem:
                price = 0
            else:
                price_str = price_elem.text.replace(',', '').strip()
                price = float(price_str) if price_str.isdigit() else 0
                
            # Original Price (Optional)
            orig_price_elem = item.find('span', class_='a-text-price')
            if orig_price_elem:
                orig_price_str = orig_price_elem.find('span', class_='a-offscreen')
                if orig_price_str:
                    orig_str = orig_price_str.text.replace('₹', '').replace(',', '').strip()
                    original_price = float(orig_str) if orig_str.isdigit() else price
                else:
                    original_price = price
            else:
                original_price = price
                
            # Rating
            rating_elem = item.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_str = rating_elem.text.split(' ')[0]
                try:
                    rating = float(rating_str)
                except ValueError:
                    rating = 4.0
            else:
                rating = 4.0
                
            # Num Ratings
            num_ratings_elem = item.find('span', class_='a-size-base s-underline-text')
            if num_ratings_elem:
                num_str = num_ratings_elem.text.replace(',', '').strip()
                try:
                    num_ratings = int(num_str)
                except ValueError:
                    num_ratings = 100
            else:
                num_ratings = 100
                
            # URL
            link_elem = item.find('a', class_='a-link-normal s-no-outline')
            url_path = link_elem['href'] if link_elem else f"/s?k={urllib.parse.quote(query)}"
            full_url = f"https://www.amazon.in{url_path}"

            products.append({
                "product_id": f"live_{int(time.time())}_{idx}",
                "title": title,
                "price": price,
                "original_price": original_price,
                "discount_percent": round(((original_price - price) / original_price) * 100) if original_price > price else 0,
                "avg_rating": rating,
                "num_ratings": num_ratings,
                "category": "Electronics", # Default for live searches
                "brand": title.split(' ')[0], # Guess brand from first word
                "url": full_url,
                "best_platform": "Amazon"
            })
            
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue
            
    return products

def search_live_products(query):
    """
    Main entry point for live searching. Returns a DataFrame.
    """
    # Scrape Amazon
    amazon_products = scrape_amazon_in(query)
    
    if amazon_products:
        return pd.DataFrame(amazon_products)
    else:
        # If scraper is blocked or no results, return empty DataFrame
        return pd.DataFrame()

# Test the scraper if run directly
if __name__ == "__main__":
    print("Testing live Amazon scraper for 'iPhone 15'...")
    df = search_live_products("iPhone 15")
    if not df.empty:
        print(f"Found {len(df)} results!")
        print(df[['title', 'price', 'avg_rating']].head())
    else:
        print("No results found. Amazon might have blocked the scraper with a CAPTCHA.")
