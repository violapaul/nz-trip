#!/usr/bin/env python3
"""
Step B: Scrape images for queries, using cache to avoid re-scraping.

Usage:
    python travel_md_converter/scraper.py travel.analysis.yaml
    
Reads analysis file, extracts ALL queries (including nested ones in
itinerary and subsections), checks cache, scrapes new queries.
Updates query_cache.yaml with results.
"""

import yaml
import requests
import re
import time
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

CACHE_FILE = 'query_cache.yaml'
MAX_IMAGES = 3

# Headers for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def load_cache():
    """Load existing cache or create empty."""
    cache_path = Path(CACHE_FILE)
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def save_cache(cache):
    """Save cache to disk."""
    with open(CACHE_FILE, 'w') as f:
        yaml.dump(cache, f, default_flow_style=False, sort_keys=False)


def collect_queries_from_section(section, queries_set):
    """
    Recursively collect all queries from a section, including:
    - Top-level queries
    - Queries in itinerary items
    - Queries in subsections
    """
    # Top-level queries
    for query in section.get('queries', []):
        if query:  # Skip empty strings
            queries_set.add(query)
    
    # Queries in itinerary items
    for item in section.get('itinerary', []):
        for query in item.get('queries', []):
            if query:
                queries_set.add(query)
    
    # Recursively process subsections
    for subsection in section.get('subsections', []):
        collect_queries_from_section(subsection, queries_set)


def scrape_google_images(query, max_images=3):
    """
    Scrape image URLs from Google Images search results.
    """
    print(f"  Searching Google Images...")
    
    url = f'https://www.google.com/search?q={quote_plus(query)}&tbm=isch&hl=en'
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        
        # Google embeds image URLs in JSON-like structures
        # Pattern to find direct image URLs
        pattern = r'\["(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"'
        matches = re.findall(pattern, res.text)
        
        # Filter and clean URLs
        image_urls = []
        seen = set()
        for match_url in matches:
            # Skip Google's own URLs and duplicates
            if 'google.com' in match_url or 'gstatic.com' in match_url:
                continue
            if match_url in seen:
                continue
            seen.add(match_url)
            image_urls.append(match_url)
            if len(image_urls) >= max_images:
                break
        
        print(f"  → Found {len(image_urls)} images")
        return image_urls
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py travel.analysis.yaml")
        sys.exit(1)
    
    analysis_file = Path(sys.argv[1])
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found")
        sys.exit(1)
    
    # Load analysis
    with open(analysis_file, 'r') as f:
        analysis = yaml.safe_load(f)
    
    # Load cache
    cache = load_cache()
    print(f"\n✓ Loaded cache: {len(cache)} queries already cached")
    
    # Collect all unique queries (including nested ones)
    all_queries = set()
    for section in analysis.get('sections', []):
        collect_queries_from_section(section, all_queries)
    
    print(f"✓ Found {len(all_queries)} unique queries in analysis")
    
    # Determine which queries need scraping
    new_queries = [q for q in all_queries if q not in cache]
    cached_queries = len(all_queries) - len(new_queries)
    
    print(f"  • {cached_queries} already in cache")
    print(f"  • {len(new_queries)} need scraping")
    
    if len(new_queries) == 0:
        print("\n✓ All queries already cached! Nothing to scrape.")
        return
    
    # Scrape new queries
    print(f"\nScraping {len(new_queries)} new queries...")
    print("="*70)
    
    for i, query in enumerate(new_queries, 1):
        print(f"\n[{i}/{len(new_queries)}] {query}")
        urls = scrape_google_images(query, MAX_IMAGES)
        
        cache[query] = {
            'urls': urls,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Save incrementally (in case of interruption)
        save_cache(cache)
        
        # Rate limit to be polite
        if i < len(new_queries):
            time.sleep(2)
    
    print("\n" + "="*70)
    print(f"✓ Cache updated: {CACHE_FILE}")
    print(f"  Total queries cached: {len(cache)}")
    print(f"  New queries added: {len(new_queries)}")


if __name__ == '__main__':
    main()
