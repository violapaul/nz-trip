#!/usr/bin/env python3
"""
Step B: Scrape images and download Google thumbnails for AI selection.

Usage:
    python travel_md_converter/scraper.py travel.analysis.yaml
    
Reads analysis file, extracts ALL queries (including nested ones in
itinerary and subsections), checks cache, scrapes new queries.
Downloads Google's cached thumbnails (small, fast) for AI evaluation.
Updates query_cache.yaml with original URL → thumbnail mapping.
"""

import yaml
import requests
import re
import time
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

CACHE_FILE = 'query_cache.yaml'
IMAGES_DIR = Path('images')
MAX_IMAGES = 6  # Get more candidates for AI to choose from

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


def ensure_images_dir():
    """Create images directory if it doesn't exist."""
    IMAGES_DIR.mkdir(exist_ok=True)


def url_to_filename(url, query):
    """Generate a unique filename for a thumbnail based on URL hash."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    safe_query = re.sub(r'[^\w\s-]', '', query)[:30].strip().replace(' ', '_').lower()
    return f"{safe_query}_{url_hash}.jpg"


def download_thumbnail(url, local_path):
    """Download thumbnail from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type and 'octet-stream' not in content_type:
            return False
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if local_path.exists() and local_path.stat().st_size > 500:
            return True
        else:
            local_path.unlink(missing_ok=True)
            return False
            
    except Exception:
        return False


def collect_queries_from_section(section, queries_set):
    """Recursively collect all queries from a section."""
    for query in section.get('queries', []):
        if query:
            queries_set.add(query)
    
    for item in section.get('itinerary', []):
        for query in item.get('queries', []):
            if query:
                queries_set.add(query)
    
    for subsection in section.get('subsections', []):
        collect_queries_from_section(subsection, queries_set)


def decode_url(url):
    """Decode Unicode escapes in URL (e.g., \\u003d → =)."""
    return url.encode().decode('unicode_escape')


def scrape_google_images(query, max_images=6):
    """
    Scrape Google Images for original URLs and Google's cached thumbnails.
    
    Returns list of dicts: {original_url, thumbnail_url}
    """
    url = f'https://www.google.com/search?q={quote_plus(query)}&tbm=isch&hl=en'
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        html = res.text
        
        # Get Google's cached thumbnails 
        # URLs contain Unicode escapes: \u003d = '='
        # Pattern matches: https://encrypted-tbn0.gstatic.com/images?q\u003dtbn:...
        thumb_pattern = r'(https://encrypted-tbn\d*\.gstatic\.com/images\?q[^"\'>\s]+)'
        raw_thumbs = re.findall(thumb_pattern, html)
        # Decode unicode escapes and dedupe
        thumbnails = []
        seen = set()
        for t in raw_thumbs:
            decoded = decode_url(t)
            if decoded not in seen:
                seen.add(decoded)
                thumbnails.append(decoded)
        
        # Get original image URLs (also have Unicode escapes)
        # Look for patterns with dimensions: ["url", width, height] or similar
        orig_pattern = r'\["(https://[^"]+)",\s*(\d+),\s*(\d+)\]'
        raw_originals = re.findall(orig_pattern, html)
        
        # Decode and filter
        originals = []
        for raw_url, w, h in raw_originals:
            url = decode_url(raw_url)
            # Skip Google's own, small images, and non-image URLs
            if 'google.com' in url or 'gstatic.com' in url:
                continue
            if int(w) < 200 or int(h) < 200:
                continue
            if not any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                continue
            originals.append((url, int(w), int(h)))
        
        # Pair originals with thumbnails
        results = []
        for i, (orig_url, w, h) in enumerate(originals[:max_images]):
            result = {'original_url': orig_url, 'width': w, 'height': h}
            if i < len(thumbnails):
                result['thumbnail_url'] = thumbnails[i]
            results.append(result)
        
        # Fallback: if no originals found, use thumbnails as both source and display
        if not results and thumbnails:
            for thumb in thumbnails[:max_images]:
                results.append({
                    'original_url': thumb,
                    'thumbnail_url': thumb
                })
        
        return results
        
    except Exception as e:
        print(f"    ✗ Search error: {e}")
        return []


def scrape_and_download(query):
    """
    Scrape images for a query and save thumbnails locally.
    Returns list of {url, thumbnail} dicts.
    """
    print(f"  Searching Google Images...")
    results = scrape_google_images(query, MAX_IMAGES)
    
    if not results:
        return []
    
    print(f"  Found {len(results)} images, downloading thumbnails...")
    
    images = []
    for i, r in enumerate(results):
        original_url = r.get('original_url', '')
        if not original_url:
            continue
            
        filename = url_to_filename(original_url, query)
        local_path = IMAGES_DIR / filename
        
        # Skip if already exists
        if local_path.exists() and local_path.stat().st_size > 500:
            images.append({
                'url': original_url,
                'thumbnail': str(local_path)
            })
            print(f"    [{i+1}] ✓ cached")
            continue
        
        saved = False
        
        # Try Google's thumbnail first (small ~5KB, fast, reliable)
        if 'thumbnail_url' in r:
            saved = download_thumbnail(r['thumbnail_url'], local_path)
            if saved:
                print(f"    [{i+1}] ✓ google thumb")
        
        # Fallback to original (larger, slower)
        if not saved:
            saved = download_thumbnail(original_url, local_path)
            if saved:
                print(f"    [{i+1}] ✓ original")
            else:
                print(f"    [{i+1}] ✗ failed")
        
        if saved:
            images.append({
                'url': original_url,
                'thumbnail': str(local_path)
            })
        
        time.sleep(0.1)
    
    print(f"  → {len(images)} thumbnails saved")
    return images


def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py travel.analysis.yaml")
        sys.exit(1)
    
    analysis_file = Path(sys.argv[1])
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found")
        sys.exit(1)
    
    ensure_images_dir()
    
    with open(analysis_file, 'r') as f:
        analysis = yaml.safe_load(f)
    
    cache = load_cache()
    print(f"\n✓ Loaded cache: {len(cache)} queries")
    
    all_queries = set()
    for section in analysis.get('sections', []):
        collect_queries_from_section(section, all_queries)
    
    print(f"✓ Found {len(all_queries)} unique queries")
    
    # Check which need processing
    queries_to_process = []
    for q in all_queries:
        if q not in cache:
            queries_to_process.append(q)
        elif 'images' not in cache[q]:
            queries_to_process.append(q)
    
    cached = len(all_queries) - len(queries_to_process)
    print(f"  • {cached} cached")
    print(f"  • {len(queries_to_process)} need scraping")
    
    if not queries_to_process:
        print("\n✓ All queries have thumbnails!")
        return
    
    print(f"\nProcessing {len(queries_to_process)} queries...")
    print("="*60)
    
    for i, query in enumerate(queries_to_process, 1):
        print(f"\n[{i}/{len(queries_to_process)}] {query}")
        
        images = scrape_and_download(query)
        
        cache[query] = {
            'images': images,
            'scraped_at': datetime.now().isoformat()
        }
        
        save_cache(cache)
        
        if i < len(queries_to_process):
            time.sleep(1.5)  # Rate limit
    
    total_images = sum(len(c.get('images', [])) for c in cache.values())
    
    print("\n" + "="*60)
    print(f"✓ Done! {len(cache)} queries, {total_images} thumbnails")
    print(f"  Thumbnails: {IMAGES_DIR}/")


if __name__ == '__main__':
    main()
