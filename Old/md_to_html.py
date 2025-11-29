#!/usr/bin/env python3
"""
Convert a custom Markdown file to a beautiful HTML page.

Custom syntax supported:
  :::hero
  # Title
  ## Subtitle
  Tagline text
  :::

  :::cards
  ### Card Title 1
  Card description text
  
  ### Card Title 2  
  Card description text
  :::

  :::highlight
  Important callout text here
  :::

  :::images day=3 count=3
  (Pulls images from YAML for the specified day)
  :::

  :::day number=1 title="Arrive in Auckland"
  Day content here...
  :::
"""

import re
import yaml
import sys
from pathlib import Path

# CSS styles embedded in the output
CSS_STYLES = """
:root {
    --deep-ocean: #0a1628;
    --twilight: #1a2f4a;
    --pacific-blue: #2563eb;
    --sky-light: #60a5fa;
    --sand: #fef3c7;
    --warm-white: #fefefe;
    --forest: #166534;
    --volcanic: #dc2626;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--warm-white);
    color: #1f2937;
    line-height: 1.7;
}

/* Hero Section */
.hero {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--deep-ocean) 0%, var(--twilight) 50%, var(--pacific-blue) 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('https://imgc.allpostersimages.com/img/posters/ian-viaduct-harbour-and-sky-tower-at-sunset-auckland-north-island-new-zealand-pacific_u-l-pxxetc0.jpg') center/cover;
    opacity: 0.2;
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 900px;
}

.hero h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 700;
    color: white;
    margin-bottom: 1rem;
    text-shadow: 2px 4px 20px rgba(0,0,0,0.3);
}

.hero h2 {
    font-size: clamp(1.1rem, 2.5vw, 1.5rem);
    color: var(--sand);
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-bottom: 2rem;
    border: none;
    padding: 0;
}

.hero p {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.8);
    max-width: 600px;
    margin: 0 auto;
}

.scroll-indicator {
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    font-size: 2rem;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateX(-50%) translateY(0); }
    50% { transform: translateX(-50%) translateY(10px); }
}

/* Main Content */
.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

section {
    padding: 4rem 0;
}

h2 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.25rem;
    color: var(--deep-ocean);
    margin: 2.5rem 0 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e7eb;
}

h3 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--twilight);
    margin: 2rem 0 1rem;
}

h4 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.25rem;
    color: var(--deep-ocean);
    margin: 1.5rem 0 0.75rem;
}

p {
    margin-bottom: 1.25rem;
    font-size: 1.1rem;
    color: #374151;
}

strong { color: var(--deep-ocean); }
em { font-style: italic; }

ul, ol {
    margin: 1rem 0 1.5rem 1.5rem;
}

li {
    margin-bottom: 0.5rem;
    font-size: 1.05rem;
}

hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 3rem 0;
}

/* Feature Cards */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.card .card-content {
    padding: 1.5rem;
}

.card h4 {
    margin-top: 0;
    margin-bottom: 0.5rem;
}

.card p {
    font-size: 1rem;
    margin-bottom: 0;
    color: #6b7280;
}

/* Highlight Box */
.highlight {
    background: linear-gradient(135deg, var(--sand) 0%, #fef9e7 100%);
    border-left: 4px solid var(--pacific-blue);
    padding: 1.5rem 2rem;
    margin: 2rem 0;
    border-radius: 0 12px 12px 0;
}

.highlight p {
    margin-bottom: 0;
    font-style: italic;
}

/* Image Gallery */
.image-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.image-gallery img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 12px;
    transition: transform 0.3s ease;
}

.image-gallery img:hover {
    transform: scale(1.02);
}

.image-gallery.large img:first-child {
    grid-column: span 2;
    height: 280px;
}

/* Day Sections */
.day-section {
    padding: 3rem 0;
    border-bottom: 1px solid #e5e7eb;
}

.day-section:last-child {
    border-bottom: none;
}

.day-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.day-number {
    background: linear-gradient(135deg, var(--pacific-blue), var(--sky-light));
    color: white;
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
}

.day-number span {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.day-number strong {
    font-size: 1.75rem;
    color: white;
    line-height: 1;
}

.day-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--deep-ocean);
    margin: 0;
}

.day-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: start;
}

@media (max-width: 768px) {
    .day-content {
        grid-template-columns: 1fr;
    }
}

.day-images {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.day-images img {
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 8px;
}

.day-images img:first-child {
    grid-column: span 2;
    height: 180px;
}

/* Footer */
footer {
    background: var(--deep-ocean);
    color: white;
    text-align: center;
    padding: 3rem 2rem;
    margin-top: 3rem;
}

footer p {
    color: rgba(255,255,255,0.7);
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
{css}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


class MarkdownConverter:
    def __init__(self, image_yaml_path=None):
        self.images = {}
        if image_yaml_path and Path(image_yaml_path).exists():
            with open(image_yaml_path, 'r') as f:
                self.images = yaml.safe_load(f) or {}
    
    def resolve_image_reference(self, tag_content):
        """
        Resolve an image reference tag like 'Auckland harbour bridge night lights:0'
        to the actual URL from the YAML file.
        
        Returns the URL or None if not found.
        """
        # Parse the tag: query:index
        parts = tag_content.rsplit(':', 1)
        if len(parts) != 2:
            return None
        
        query = parts[0].strip()
        try:
            index = int(parts[1].strip())
        except ValueError:
            return None
        
        # Search through all days for this query
        for day_data in self.images.values():
            if not isinstance(day_data, dict):
                continue
            
            for query_key, urls in day_data.items():
                if query_key.strip() == query:
                    # Found the query
                    if isinstance(urls, list) and 0 <= index < len(urls):
                        return urls[index]
        
        return None
    
    def get_images_for_day(self, day_num, count=3):
        """Get image URLs for a specific day."""
        day_key = f"Day {day_num}"
        if day_key not in self.images:
            return []
        
        urls = []
        for query, query_urls in self.images[day_key].items():
            if isinstance(query_urls, list):
                urls.extend(query_urls[:2])  # Take up to 2 from each query
            if len(urls) >= count:
                break
        return urls[:count]
    
    def get_images_by_query(self, query_substring, count=3):
        """Get images matching a query substring."""
        urls = []
        for day_data in self.images.values():
            for query, query_urls in day_data.items():
                if query_substring.lower() in query.lower():
                    if isinstance(query_urls, list):
                        urls.extend(query_urls)
        return urls[:count]
    
    def parse_block_params(self, param_str):
        """Parse parameters like 'day=3 count=3' into a dict."""
        params = {}
        if not param_str:
            return params
        for match in re.finditer(r'(\w+)=(["\']?)([^"\'\s]+)\2', param_str):
            params[match.group(1)] = match.group(3)
        return params
    
    def process_inline_markdown(self, text):
        """Convert inline markdown (bold, italic, links) to HTML."""
        # First resolve image reference tags {{image:query:index}}
        def replace_image_ref(match):
            tag_content = match.group(1)
            url = self.resolve_image_reference(tag_content)
            if url:
                # Extract a simple alt text from the query
                query = tag_content.rsplit(':', 1)[0]
                return f'<img src="{url}" alt="{query}" style="max-width: 100%; height: auto;" onerror="this.style.display=\'none\'">'
            else:
                # Tag not found, leave a comment
                return f'<!-- Image reference not found: {tag_content} -->'
        
        text = re.sub(r'\{\{image:([^}]+)\}\}', replace_image_ref, text)
        
        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text
    
    def markdown_to_html(self, md_content):
        """Convert markdown content to HTML."""
        lines = md_content.split('\n')
        html_parts = []
        i = 0
        in_list = False
        list_type = None
        title = "New Zealand Trip"
        
        while i < len(lines):
            line = lines[i]
            
            # Check for custom blocks
            if line.strip().startswith(':::'):
                block_match = re.match(r':::\s*(\w+)\s*(.*)?', line.strip())
                if block_match:
                    block_type = block_match.group(1)
                    params_str = block_match.group(2) or ''
                    params = self.parse_block_params(params_str)
                    
                    # Find block end
                    block_content = []
                    i += 1
                    while i < len(lines) and not lines[i].strip() == ':::':
                        block_content.append(lines[i])
                        i += 1
                    
                    html_parts.append(self.render_block(block_type, params, '\n'.join(block_content)))
                    i += 1
                    continue
            
            # Close list if needed
            if in_list and not (line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\d+\.', line.strip())):
                html_parts.append(f'</{list_type}>')
                in_list = False
                list_type = None
            
            # Headers
            if line.startswith('# '):
                title = line[2:].strip()
                html_parts.append(f'<h1>{self.process_inline_markdown(line[2:])}</h1>')
            elif line.startswith('## '):
                html_parts.append(f'<h2>{self.process_inline_markdown(line[3:])}</h2>')
            elif line.startswith('### '):
                html_parts.append(f'<h3>{self.process_inline_markdown(line[4:])}</h3>')
            elif line.startswith('#### '):
                html_parts.append(f'<h4>{self.process_inline_markdown(line[5:])}</h4>')
            
            # Horizontal rule
            elif line.strip() == '---':
                html_parts.append('<hr>')
            
            # Unordered list
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                content = line.strip()[2:]
                html_parts.append(f'<li>{self.process_inline_markdown(content)}</li>')
            
            # Ordered list
            elif re.match(r'^\d+\.', line.strip()):
                if not in_list:
                    html_parts.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                content = re.sub(r'^\d+\.\s*', '', line.strip())
                html_parts.append(f'<li>{self.process_inline_markdown(content)}</li>')
            
            # Paragraph
            elif line.strip():
                html_parts.append(f'<p>{self.process_inline_markdown(line)}</p>')
            
            i += 1
        
        # Close any open list
        if in_list:
            html_parts.append(f'</{list_type}>')
        
        content = '\n'.join(html_parts)
        return title, content
    
    def render_block(self, block_type, params, content):
        """Render a custom block to HTML."""
        
        if block_type == 'hero':
            return self.render_hero(content)
        
        elif block_type == 'cards':
            return self.render_cards(content)
        
        elif block_type == 'highlight':
            return self.render_highlight(content)
        
        elif block_type == 'images':
            return self.render_images(params)
        
        elif block_type == 'day':
            return self.render_day(params, content)
        
        elif block_type == 'footer':
            return self.render_footer(content)
        
        else:
            # Unknown block, just render content
            _, html = self.markdown_to_html(content)
            return f'<div class="{block_type}">{html}</div>'
    
    def render_hero(self, content):
        """Render hero section."""
        lines = content.strip().split('\n')
        title = subtitle = tagline = ""
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## '):
                subtitle = line[3:].strip()
            elif line.strip():
                tagline = line.strip()
        
        return f'''
<section class="hero">
    <div class="hero-content">
        <h1>{title}</h1>
        <h2>{subtitle}</h2>
        <p>{tagline}</p>
    </div>
    <div class="scroll-indicator">↓</div>
</section>
<section><div class="container">
'''
    
    def render_cards(self, content):
        """Render cards from ### headers and following paragraphs."""
        cards = []
        current_card = None
        
        for line in content.split('\n'):
            if line.startswith('### '):
                if current_card:
                    cards.append(current_card)
                current_card = {'title': line[4:].strip(), 'text': '', 'image': ''}
            elif line.startswith('!['):
                # Image: ![alt](url)
                match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
                if match and current_card:
                    current_card['image'] = match.group(2)
            elif line.strip() and current_card:
                current_card['text'] += self.process_inline_markdown(line.strip()) + ' '
        
        if current_card:
            cards.append(current_card)
        
        html = '<div class="cards-grid">\n'
        for card in cards:
            img_html = f'<img src="{card["image"]}" alt="{card["title"]}" onerror="this.style.display=\'none\'">' if card['image'] else ''
            html += f'''<div class="card">
    {img_html}
    <div class="card-content">
        <h4>{card["title"]}</h4>
        <p>{card["text"].strip()}</p>
    </div>
</div>
'''
        html += '</div>\n'
        return html
    
    def render_highlight(self, content):
        """Render highlight/callout box."""
        _, inner = self.markdown_to_html(content)
        return f'<div class="highlight">{inner}</div>'
    
    def render_images(self, params):
        """Render image gallery from YAML data."""
        day = params.get('day')
        query = params.get('query')
        count = int(params.get('count', 3))
        large = params.get('large', 'true') == 'true'
        
        if day:
            urls = self.get_images_for_day(int(day), count)
        elif query:
            urls = self.get_images_by_query(query, count)
        else:
            urls = []
        
        if not urls:
            return '<!-- No images found -->'
        
        large_class = ' large' if large else ''
        html = f'<div class="image-gallery{large_class}">\n'
        for url in urls:
            html += f'    <img src="{url}" alt="" onerror="this.style.display=\'none\'">\n'
        html += '</div>\n'
        return html
    
    def render_day(self, params, content):
        """Render a day section with number badge and images."""
        day_num = params.get('number', '?')
        title = params.get('title', f'Day {day_num}')
        
        # Get images for this day
        images = self.get_images_for_day(int(day_num), 3) if day_num.isdigit() else []
        
        # Convert content
        _, inner_html = self.markdown_to_html(content)
        
        # Build images HTML
        images_html = ''
        if images:
            images_html = '<div class="day-images">\n'
            for url in images:
                images_html += f'    <img src="{url}" alt="" onerror="this.style.display=\'none\'">\n'
            images_html += '</div>\n'
        
        return f'''
<div class="day-section">
    <div class="day-header">
        <div class="day-number">
            <span>Day</span>
            <strong>{day_num}</strong>
        </div>
        <h3 class="day-title">{title}</h3>
    </div>
    <div class="day-content">
        <div class="day-description">
            {inner_html}
        </div>
        {images_html}
    </div>
</div>
'''
    
    def render_footer(self, content):
        """Render footer section."""
        lines = [f'<p>{self.process_inline_markdown(line.strip())}</p>' for line in content.strip().split('\n') if line.strip()]
        return f'''
</div></section>
<footer>
    <div class="container">
        {''.join(lines)}
    </div>
</footer>
'''
    
    def convert(self, md_content):
        """Convert full markdown document to HTML."""
        title, content = self.markdown_to_html(md_content)
        
        # Wrap non-hero content in container if not already
        if '<section class="hero">' not in content:
            content = f'<section><div class="container">\n{content}\n</div></section>'
        
        # Close container if footer didn't do it
        if '</div></section>' not in content and '<footer>' not in content:
            content += '\n</div></section>'
        
        return HTML_TEMPLATE.format(
            title=title,
            css=CSS_STYLES,
            content=content
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py input.md [output.html] [images.yaml]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '.html')
    image_yaml = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Auto-detect image yaml in same directory
    if not image_yaml:
        input_path = Path(input_file)
        possible_yaml = input_path.parent / 'nz_trip_image_urls.yaml'
        if possible_yaml.exists():
            image_yaml = str(possible_yaml)
    
    print(f"Converting {input_file} -> {output_file}")
    if image_yaml:
        print(f"Using images from {image_yaml}")
    
    with open(input_file, 'r') as f:
        md_content = f.read()
    
    converter = MarkdownConverter(image_yaml)
    html_content = converter.convert(md_content)
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Done! Generated {output_file}")


if __name__ == '__main__':
    main()

