#!/usr/bin/env python3
"""
Step B2: Use Gemini Vision to select best images for each section.

Usage:
    python travel_md_converter/selector.py travel.analysis.yaml

Reads analysis file and image cache, sends thumbnails to Gemini Vision,
asks AI to pick the best images for each section context.
Updates analysis.yaml with selected_images field.
"""

import yaml
import sys
import os
import base64
from pathlib import Path

CACHE_FILE = 'query_cache.yaml'


def load_cache():
    """Load image cache."""
    cache_path = Path(CACHE_FILE)
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def load_image_as_base64(image_path):
    """Load image file and return base64 encoded data."""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return None


def get_images_for_queries(queries, cache):
    """Get all images (with thumbnails) for a list of queries, deduped by URL."""
    images = []
    seen_urls = set()
    
    for query in queries:
        if query in cache and 'images' in cache[query]:
            for img in cache[query]['images']:
                url = img.get('url', '')
                # Skip duplicates
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                if img.get('thumbnail') and Path(img['thumbnail']).exists():
                    images.append({
                        'url': url,
                        'thumbnail': img['thumbnail'],
                        'query': query
                    })
    return images


def select_images_with_gemini(section_title, section_style, images, num_select=3):
    """
    Use Gemini Vision to select the best images for a section.
    
    Args:
        section_title: Title of the section
        section_style: Style type (hero, gallery, cards, etc.)
        images: List of {url, thumbnail, query} dicts
        num_select: Number of images to select
        
    Returns:
        List of selected image URLs (original, not thumbnails)
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("  ⚠ google-genai not installed, using first images as fallback")
        return [img['url'] for img in images[:num_select]]
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("  ⚠ No GEMINI_API_KEY, using first images as fallback")
        return [img['url'] for img in images[:num_select]]
    
    if not images:
        return []
    
    # Prepare image data for Gemini
    image_parts = []
    valid_images = []
    
    for i, img in enumerate(images):
        img_data = load_image_as_base64(img['thumbnail'])
        if img_data:
            image_parts.append(
                types.Part.from_bytes(
                    data=base64.b64decode(img_data),
                    mime_type='image/jpeg'
                )
            )
            valid_images.append(img)
    
    if not valid_images:
        return []
    
    # Build prompt for Gemini
    style_guidance = {
        'hero': 'dramatic, wide landscape or cityscape, high quality, would work as full-screen background',
        'gallery': 'variety of angles, showcase the location, visually interesting',
        'cards': 'clear subject, good composition, would work as a card thumbnail',
        'day': 'represents the activity or location for that day, action shots good',
        'content': 'relevant to the text content, informative',
        'highlight': 'attention-grabbing, relevant to the highlighted topic',
    }
    
    style_hint = style_guidance.get(section_style, 'high quality, relevant to the content')
    
    prompt = f"""You are selecting images for a travel document section.

Section: "{section_title}"
Style: {section_style} ({style_hint})

I'm showing you {len(valid_images)} candidate images (numbered 1 to {len(valid_images)}).

Select the {min(num_select, len(valid_images))} BEST images for this section. Consider:
- Relevance to "{section_title}"
- Visual quality (no watermarks, good resolution, good composition)
- Appropriateness for {section_style} style
- No duplicate/similar images

Return ONLY a comma-separated list of image numbers, best first.
Example: 2, 5, 1

Your selection:"""

    try:
        client = genai.Client(api_key=api_key)
        
        # Build content with images and prompt
        content_parts = []
        for i, part in enumerate(image_parts):
            content_parts.append(types.Part.from_text(f"Image {i+1}:"))
            content_parts.append(part)
        content_parts.append(types.Part.from_text(prompt))
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=content_parts,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for consistent selection
                max_output_tokens=50,
            )
        )
        
        # Parse response to get image indices
        response_text = response.text.strip()
        
        # Extract numbers from response
        import re
        numbers = re.findall(r'\d+', response_text)
        selected_indices = []
        for num in numbers:
            idx = int(num) - 1  # Convert to 0-based
            if 0 <= idx < len(valid_images) and idx not in selected_indices:
                selected_indices.append(idx)
                if len(selected_indices) >= num_select:
                    break
        
        # Return original URLs for selected images
        selected_urls = [valid_images[i]['url'] for i in selected_indices]
        
        # If we didn't get enough, pad with remaining images
        if len(selected_urls) < num_select:
            for img in valid_images:
                if img['url'] not in selected_urls:
                    selected_urls.append(img['url'])
                    if len(selected_urls) >= num_select:
                        break
        
        return selected_urls
        
    except Exception as e:
        print(f"  ⚠ Gemini error: {e}")
        return [img['url'] for img in valid_images[:num_select]]


def collect_queries_for_section(section):
    """Collect all queries for a section (including nested)."""
    queries = list(section.get('queries', []))
    
    # Add queries from itinerary items
    for item in section.get('itinerary', []):
        queries.extend(item.get('queries', []))
    
    return queries


def process_section(section, cache, depth=0, force=False):
    """
    Process a section and its subsections to select images.
    Modifies section in place to add selected_images.
    
    Skips sections that already have selected_images (cached).
    """
    indent = "  " * depth
    title = section.get('title', 'Untitled')
    style = section.get('style', 'content')
    needs_images = section.get('needs_images', True)
    
    # Check if already has selections (cached)
    existing = section.get('selected_images', [])
    if existing and not force:
        print(f"{indent}[{style}] {title} ✓ cached ({len(existing)} images)")
    elif needs_images:
        queries = collect_queries_for_section(section)
        
        if queries:
            print(f"{indent}[{style}] {title}")
            images = get_images_for_queries(queries, cache)
            
            if images:
                print(f"{indent}  Found {len(images)} candidate images")
                selected = select_images_with_gemini(title, style, images, num_select=3)
                section['selected_images'] = selected
                print(f"{indent}  → Selected {len(selected)} images")
            else:
                print(f"{indent}  No thumbnails available")
                section['selected_images'] = []
        else:
            section['selected_images'] = []
    else:
        section['selected_images'] = []
    
    # Process itinerary items
    for item in section.get('itinerary', []):
        item_title = item.get('title', 'Untitled')
        item_queries = item.get('queries', [])
        
        # Check cache for itinerary items too
        item_existing = item.get('selected_images', [])
        if item_existing and not force:
            print(f"{indent}  Day: {item_title} ✓ cached")
            continue
        
        if item_queries:
            images = get_images_for_queries(item_queries, cache)
            if images:
                print(f"{indent}  Day: {item_title}")
                selected = select_images_with_gemini(
                    f"{title} - {item_title}", 
                    'day', 
                    images, 
                    num_select=2
                )
                item['selected_images'] = selected
                print(f"{indent}    → Selected {len(selected)} images")
            else:
                item['selected_images'] = []
        else:
            item['selected_images'] = []
    
    # Process subsections recursively
    for subsection in section.get('subsections', []):
        process_section(subsection, cache, depth + 1, force=force)


def count_selections(sections):
    """Count how many sections already have selected_images."""
    cached = 0
    total = 0
    for section in sections:
        total += 1
        if section.get('selected_images'):
            cached += 1
        # Count itinerary items
        for item in section.get('itinerary', []):
            total += 1
            if item.get('selected_images'):
                cached += 1
        # Recurse into subsections
        sub_cached, sub_total = count_selections(section.get('subsections', []))
        cached += sub_cached
        total += sub_total
    return cached, total


def main():
    # Parse args
    force = '--force' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    
    if len(args) < 1:
        print("Usage: python selector.py travel.analysis.yaml [--force]")
        print("\nOptions:")
        print("  --force    Re-select all images (ignore cache)")
        sys.exit(1)
    
    analysis_file = Path(args[0])
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found")
        sys.exit(1)
    
    # Load analysis
    print(f"\n✓ Loading {analysis_file}...")
    with open(analysis_file, 'r') as f:
        analysis = yaml.safe_load(f)
    
    # Load cache
    cache = load_cache()
    print(f"✓ Loaded cache: {len(cache)} queries")
    
    # Check for thumbnails
    total_thumbnails = sum(
        len([img for img in c.get('images', []) if img.get('thumbnail')])
        for c in cache.values()
    )
    print(f"✓ Found {total_thumbnails} thumbnails available")
    
    if total_thumbnails == 0:
        print("\n⚠ No thumbnails found! Run scraper.py first.")
        sys.exit(1)
    
    # Check existing selections
    cached, total = count_selections(analysis.get('sections', []))
    print(f"✓ Selections: {cached}/{total} already cached")
    
    if cached == total and not force:
        print("\n✓ All sections already have selections! Use --force to re-select.")
        return
    
    if force:
        print("\n⚠ Force mode: re-selecting all images")
    
    # Process each section
    print(f"\nSelecting best images...")
    print("="*70)
    
    for section in analysis.get('sections', []):
        process_section(section, cache, force=force)
    
    # Save updated analysis
    with open(analysis_file, 'w') as f:
        yaml.dump(analysis, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n" + "="*70)
    print(f"✓ Updated: {analysis_file}")


if __name__ == '__main__':
    main()



