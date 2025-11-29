import os
import yaml
import requests
import json
import time
import re
from urllib.parse import urlparse, quote_plus

# Configuration
INPUT_YAML = 'nz_trip_image_queries.yaml'
HTML_OUTPUT = 'images.html'
URLS_YAML = 'nz_trip_image_urls.yaml'
MAX_URLS_PER_QUERY = 3  # Just top 3

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def get_google_image_urls(query, max_images=3):
    """Scrape image URLs from Google Images search results."""
    print(f"  Searching Google Images...")
    
    url = f'https://www.google.com/search?q={quote_plus(query)}&tbm=isch&hl=en'
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        print(f"  Response received ({len(res.text)} bytes)")
        
        # Google embeds image URLs in JSON-like structures
        # Pattern to find direct image URLs
        pattern = r'\["(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"'
        matches = re.findall(pattern, res.text)
        
        # Filter and clean URLs
        image_urls = []
        seen = set()
        for url in matches:
            # Skip Google's own URLs and duplicates
            if 'google.com' in url or 'gstatic.com' in url:
                continue
            if url in seen:
                continue
            seen.add(url)
            image_urls.append(url)
            if len(image_urls) >= max_images:
                break
        
        print(f"  Found {len(image_urls)} images")
        return image_urls
        
    except Exception as e:
        print(f"  Error: {e}")
        return []

def generate_html(all_urls_data):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NZ Trip Inspiration Board</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        h1 { text-align: center; color: #333; }
        .day-section { background: white; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .day-title { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; color: #2c3e50; }
        .query-group { margin-bottom: 20px; }
        .query-title { font-size: 1.1em; font-weight: bold; margin: 10px 0; color: #555; }
        .image-grid { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px; }
        .image-card { flex: 0 0 300px; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; background: #fff; }
        .image-card img { width: 100%; height: 200px; object-fit: cover; display: block; }
        .image-url { font-size: 0.8em; padding: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #888; }
    </style>
</head>
<body>
    <h1>New Zealand Cycling & Sailing Trip Inspiration</h1>
"""
    
    for day, queries_map in all_urls_data.items():
        html_content += f'    <div class="day-section">\n        <h2 class="day-title">{day}</h2>\n'
        
        for query, urls in queries_map.items():
            html_content += f'        <div class="query-group">\n            <div class="query-title">{query}</div>\n            <div class="image-grid">\n'
            for url in urls:
                html_content += f'                <div class="image-card">\n                    <img src="{url}" loading="lazy" alt="{query}" onerror="this.style.display=\'none\'">\n                    <div class="image-url"><a href="{url}" target="_blank">Source</a></div>\n                </div>\n'
            html_content += '            </div>\n        </div>\n'
        
        html_content += '    </div>\n'

    html_content += """
</body>
</html>
"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, HTML_OUTPUT)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML gallery written to {output_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_YAML)
    
    if not os.path.exists(input_path):
        print(f"Input file {INPUT_YAML} not found.")
        return

    print(f"Reading queries from {INPUT_YAML}...")
    with open(input_path, 'r') as f:
        query_data = yaml.safe_load(f)
        
    # Load existing URLs if available
    existing_urls = {}
    output_yaml_path = os.path.join(base_dir, URLS_YAML)
    if os.path.exists(output_yaml_path):
        print(f"Loading existing URLs from {URLS_YAML}...")
        with open(output_yaml_path, 'r') as f:
            existing_urls = yaml.safe_load(f) or {}
    
    all_urls = existing_urls.copy()
    
    total_queries = sum(len(q) for q in query_data.values() if q)
    processed_queries = 0
    
    for day, queries in query_data.items():
        print(f"\n{'='*40}\nProcessing {day}\n{'='*40}")
        if day not in all_urls:
            all_urls[day] = {}
        
        if not queries:
            print("No queries for this day.")
            continue
            
        for query in queries:
            processed_queries += 1
            
            # Check if we already have URLs for this query
            if query in all_urls[day] and all_urls[day][query]:
                print(f"[{processed_queries}/{total_queries}] Skipping (already scraped): {query}")
                continue
                
            print(f"\n[{processed_queries}/{total_queries}] {query}")
            urls = get_google_image_urls(query, MAX_URLS_PER_QUERY)
            all_urls[day][query] = urls
            
            # Save incrementally
            with open(output_yaml_path, 'w') as f:
                yaml.dump(all_urls, f)
                
            time.sleep(2.0)  # Throttle: 2 seconds between requests

    # Final Save URLs to yaml
    print(f"\nSaving URLs to {URLS_YAML}...")
    with open(output_yaml_path, 'w') as f:
        yaml.dump(all_urls, f)
        
    # Generate HTML
    print(f"Generating HTML gallery...")
    generate_html(all_urls)
    
    print(f"\nDone! URLs saved to {URLS_YAML} and gallery to {HTML_OUTPUT}")

if __name__ == "__main__":
    main()

