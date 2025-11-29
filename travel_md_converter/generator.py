#!/usr/bin/env python3
"""
Step C: Generate HTML from YAML analysis file.

Usage:
    python travel_md_converter/generator.py travel.analysis.yaml
    
The YAML file contains ALL content - no markdown file needed.
Creates travel.html with styled sections and images from cache.
"""

import yaml
import sys
from pathlib import Path
from utils import get_images_for_section
from styles import get_css, render_section, safe_img_url


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Nunito+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
{css}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


def load_cache():
    """Load image URL cache."""
    cache_path = Path('query_cache.yaml')
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def get_images_for_queries(queries, cache):
    """Get image URLs for a list of queries from cache."""
    urls = []
    for query in queries:
        if query in cache:
            query_urls = cache[query].get('urls', [])
            urls.extend(query_urls)
    return urls[:3]  # Max 3 images


def render_section_from_yaml(section, cache, depth=0):
    """
    Render a section from YAML data with proper hierarchy.
    
    The section dict can contain:
    - id, title, level, style
    - content: main text content
    - bullets: list of bullet points
    - queries: image search queries
    - needs_images: whether to include images
    - itinerary: list of day items
    - subsections: nested sections
    - cards: list of card items
    - table: tabular data
    - meta: section metadata (duration, location, theme)
    """
    section_id = section.get('id', '')
    title = section.get('title', '')
    style = section.get('style', 'content')
    content = section.get('content', '')
    bullets = section.get('bullets', [])
    itinerary = section.get('itinerary', [])
    subsections = section.get('subsections', [])
    cards = section.get('cards', [])
    table_data = section.get('table')
    meta = section.get('meta', {})
    
    # Get images if needed
    images = []
    if section.get('needs_images', True):
        queries = section.get('queries', [])
        images = get_images_for_queries(queries, cache)
    
    # Build content string from various fields
    full_content = content or ''
    
    # Add bullet points
    if bullets:
        bullet_html = '\n'.join(f'- {b}' for b in bullets)
        full_content += '\n\n' + bullet_html
    
    # If this section has subsections, wrap everything in a section-group for hierarchy
    has_subsections = len(subsections) > 0
    
    html_parts = []
    
    if has_subsections and depth == 0:
        # Start a section group for proper hierarchy
        html_parts.append(f'<div class="section-group" id="{section_id}">')
        html_parts.append(f'<div class="section-header"><h2>{title}</h2></div>')
        
        # Add main section content if any
        if full_content.strip() or images:
            html_parts.append('<div class="section-content">')
            if images:
                html_parts.append('<div class="content-images">')
                for url in images[:3]:
                    html_parts.append(f'<img src="{safe_img_url(url)}" alt="" onerror="this.style.display=\'none\'">')
                html_parts.append('</div>')
            from utils import markdown_to_html
            html_parts.append(markdown_to_html(full_content))
            html_parts.append('</div>')
        
        # Render subsections inside the group
        html_parts.append('<div class="subsections">')
        for subsection in subsections:
            sub_html = render_section_from_yaml(subsection, cache, depth + 1)
            html_parts.append(sub_html)
        html_parts.append('</div>')
        
        html_parts.append('</div>')  # Close section-group
    else:
        # Regular rendering (no subsections or nested subsection)
        html = render_section(
            style=style,
            title=title,
            content=full_content,
            images=images,
            section_data=section,
            cache=cache
        )
        html_parts.append(html)
        
        # Render any subsections (for deeply nested cases)
        for subsection in subsections:
            sub_html = render_section_from_yaml(subsection, cache, depth + 1)
            html_parts.append(sub_html)
    
    return '\n'.join(html_parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generator.py travel.analysis.yaml")
        print("\nThe YAML file contains all content - no markdown file needed.")
        sys.exit(1)
    
    analysis_file = Path(sys.argv[1])
    
    # Check file exists
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found")
        sys.exit(1)
    
    # Load analysis YAML
    print(f"\n✓ Loading {analysis_file.name}...")
    with open(analysis_file, 'r') as f:
        analysis = yaml.safe_load(f)
    
    print(f"✓ Loading image cache...")
    cache = load_cache()
    
    # Get metadata
    metadata = analysis.get('metadata', {})
    title = metadata.get('title', analysis_file.stem)
    
    # Generate HTML
    print(f"✓ Generating HTML from YAML...")
    print("="*70)
    
    hero_html = ""
    body_parts = []
    
    # Render each section
    sections = analysis.get('sections', [])
    for i, section in enumerate(sections, 1):
        section_title = section.get('title', 'Untitled')
        section_style = section.get('style', 'content')
        
        print(f"  [{i}/{len(sections)}] {section_title} ({section_style})")
        
        # Count images
        image_count = 0
        if section.get('needs_images', True):
            queries = section.get('queries', [])
            image_count = len(get_images_for_queries(queries, cache))
        print(f"      → {image_count} images")
        
        # Render section
        html = render_section_from_yaml(section, cache)
        
        # Hero stays outside the page-wrapper
        if section_style == 'hero':
            hero_html = html
        else:
            body_parts.append(html)
    
    # Combine: hero + page-wrapper containing rest of content
    content = hero_html + '\n<div class="page-wrapper">\n' + '\n'.join(body_parts) + '\n</div>'
    full_html = HTML_TEMPLATE.format(
        title=title,
        css=get_css(),
        content=content
    )
    
    # Write output - use stem from analysis file name
    output_name = analysis_file.stem.replace('.analysis', '')
    output_file = analysis_file.parent / f"{output_name}.html"
    with open(output_file, 'w') as f:
        f.write(full_html)
    
    print("="*70)
    print(f"\n✓ Generated: {output_file}")
    print(f"  Sections: {len(sections)}")


if __name__ == '__main__':
    main()
