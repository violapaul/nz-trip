"""
HTML rendering functions for different section types.
CSS is loaded from styles.css for better maintainability.
"""

import re
import html as html_module
from pathlib import Path
from utils import markdown_to_html, process_inline_markdown, extract_first_sentence


def get_css():
    """Load CSS from external file for better maintainability."""
    css_path = Path(__file__).parent / 'styles.css'
    if css_path.exists():
        return css_path.read_text()
    # Fallback - return empty string if file not found
    return "/* styles.css not found */"


def clean_url(url):
    """Clean URL by decoding JSON unicode escapes and normalizing."""
    if not url:
        return url
    # Decode JSON unicode escapes like \u003d -> =
    try:
        # Handle common JSON escapes in URLs
        url = url.replace('\\u003d', '=')
        url = url.replace('\\u0026', '&')
        url = url.replace('\\u003c', '<')
        url = url.replace('\\u003e', '>')
        # Also handle if they appear without backslash (from YAML loading)
        url = url.encode().decode('unicode_escape') if '\\u' in url else url
    except:
        pass
    return url


def escape_url_for_style(url):
    """Properly escape a URL for use in inline CSS style attribute."""
    url = clean_url(url)
    # Escape quotes in URL
    return url.replace('"', '%22').replace("'", '%27')


def safe_img_url(url):
    """Clean and escape URL for use in img src attribute."""
    return html_module.escape(clean_url(url))


def render_hero(title, content, images):
    """Render hero section with dramatic full-screen impact."""
    lines = content.strip().split('\n') if content.strip() else []
    
    # Extract meaningful intro text from content
    intro_text = ""
    for line in lines:
        line = line.strip()
        # Skip empty lines and headers
        if not line or line.startswith('#'):
            continue
        # Skip lines that look like metadata
        if line.startswith('Duration:') or line.startswith('Theme:'):
            continue
        # Get first substantial paragraph
        if len(line) > 50:
            intro_text = line[:300] + ('...' if len(line) > 300 else '')
            break
    
    # Use first image as background if available
    bg_html = ""
    if images:
        safe_url = escape_url_for_style(images[0])
        bg_html = f'<div class="hero-bg" style="background-image: url(\'{safe_url}\');"></div>'
    
    # Extract subtitle from title (e.g., "(March 2026)" becomes the subtitle)
    main_title = title
    subtitle = ""
    date_match = re.search(r'\(([^)]+)\)', title)
    if date_match:
        subtitle = date_match.group(1)
        main_title = title.replace(f'({subtitle})', '').strip()
    
    # Clean title markers
    main_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', main_title)
    
    return f"""
<section class="hero">
    {bg_html}
    <div class="hero-content">
        <h1>{process_inline_markdown(main_title)}</h1>
        <p class="hero-subtitle">{process_inline_markdown(subtitle)}</p>
        <p class="hero-intro">{process_inline_markdown(intro_text)}</p>
    </div>
    <div class="hero-scroll-hint">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12l7 7 7-7"/>
        </svg>
    </div>
</section>
"""


def render_cards(title, content, images):
    """Render cards grid with smart content extraction."""
    lines = content.strip().split('\n') if content.strip() else []
    cards = []
    current_card = None
    
    # Try to find ### subheaders first
    for line in lines:
        if line.startswith('### '):
            if current_card:
                cards.append(current_card)
            current_card = {'title': line[4:].strip(), 'text': ''}
        elif line.strip() and current_card:
            current_card['text'] += line.strip() + ' '
    
    if current_card:
        cards.append(current_card)
    
    # If no ### found, try bullet points
    if not cards:
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                item_text = line[2:].strip()
                # Extract title from bold text or first sentence
                title_match = re.match(r'\*\*([^*]+)\*\*[:\.]?\s*(.*)', item_text)
                if title_match:
                    cards.append({'title': title_match.group(1), 'text': title_match.group(2)})
                else:
                    first_sentence = extract_first_sentence(item_text)
                    cards.append({'title': first_sentence, 'text': item_text})
    
    # If still no cards, create from paragraphs
    if not cards:
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        for p in paragraphs[:3]:
            first_sentence = extract_first_sentence(p)
            cards.append({'title': first_sentence, 'text': p})
    
    # Build cards HTML
    clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
    cards_html = f'<section class="container cards-section"><h2>{process_inline_markdown(clean_title)}</h2><div class="cards-grid">\n'
    
    for i, card in enumerate(cards):
        img_html = ''
        if i < len(images):
            img_html = f'<img src="{safe_img_url(images[i])}" alt="{html_module.escape(card["title"])}" onerror="this.style.display=\'none\'">'
        
        card_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', card['title'])
        cards_html += f"""<div class="card">
    {img_html}
    <div class="card-content">
        <h4>{process_inline_markdown(card_title)}</h4>
        <p>{process_inline_markdown(card['text'].strip()[:200])}</p>
    </div>
</div>
"""
    
    cards_html += '</div></section>\n'
    return cards_html


def extract_day_or_module_number(title):
    """Extract day number, module number, or section number from title."""
    # Try "Day X" pattern
    match = re.search(r'Day\s+(\d+)', title, re.IGNORECASE)
    if match:
        return match.group(1), 'Day'
    
    # Try "Module X" pattern
    match = re.search(r'Module\s+(\d+)', title, re.IGNORECASE)
    if match:
        return match.group(1), 'Module'
    
    # Try section number at start "X.Y Title"
    match = re.search(r'^(\d+)\.\d+\s', title)
    if match:
        return match.group(1), 'Part'
    
    # Try just leading number
    match = re.search(r'^(\d+)[\.\s]', title)
    if match:
        return match.group(1), 'Part'
    
    return '•', ''


def render_day_section(title, content, images, day_num=None):
    """Render day/activity section with number badge."""
    # Extract day/module number from title
    num, label = extract_day_or_module_number(title)
    if day_num:
        num = day_num
        label = 'Day'
    
    # Convert content to HTML
    content_html = markdown_to_html(content) if content else '<p><em>Details to be confirmed.</em></p>'
    
    # Clean title
    clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
    clean_title = re.sub(r'^\d+\.\d+\s+', '', clean_title)  # Remove section numbers
    
    # Build images HTML
    images_html = ''
    if images:
        images_html = '<div class="day-images">\n'
        for url in images[:3]:
            images_html += f'    <img src="{safe_img_url(url)}" alt="" onerror="this.style.display=\'none\'">\n'
        images_html += '</div>\n'
    
    return f"""
<div class="day-section container-wide">
    <div class="day-badge">
        <div class="day-number">
            <span>{label}</span>
            <strong>{num}</strong>
        </div>
    </div>
    <div class="day-content">
        <h3 class="day-title">{process_inline_markdown(clean_title)}</h3>
        <div class="day-description">
            {content_html}
        </div>
        {images_html}
    </div>
</div>
"""


def render_gallery(title, content, images):
    """Render image gallery with large featured image."""
    clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
    
    gallery_html = f'<section class="container-wide gallery-section"><h2>{process_inline_markdown(clean_title)}</h2>'
    
    if images:
        gallery_html += '<div class="gallery-grid">\n'
        for url in images[:4]:  # Max 4 images for nice grid
            gallery_html += f'    <img src="{safe_img_url(url)}" alt="" onerror="this.style.display=\'none\'">\n'
        gallery_html += '</div>\n'
    
    # Add content if any
    if content and content.strip():
        content_html = markdown_to_html(content)
        gallery_html += f'<div class="container">{content_html}</div>'
    
    gallery_html += '</section>\n'
    return gallery_html


def render_highlight(title, content, images):
    """Render highlight/callout box."""
    content_html = markdown_to_html(content) if content else ''
    clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
    
    return f"""
<div class="highlight-section container">
    <div class="highlight-box">
        <h3>{process_inline_markdown(clean_title)}</h3>
        {content_html}
    </div>
</div>
"""


def render_content(title, content, images):
    """Render standard content section."""
    content_html = markdown_to_html(content) if content else ''
    clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
    
    # Add images in a grid if available
    images_html = ''
    if images:
        images_html = '<div class="content-images">\n'
        for url in images[:2]:
            images_html += f'<img src="{safe_img_url(url)}" alt="" onerror="this.style.display=\'none\'">\n'
        images_html += '</div>\n'
    
    return f"""
<section class="container content-section">
    <h2>{process_inline_markdown(clean_title)}</h2>
    {images_html}
    {content_html}
</section>
"""


def render_footer(title, content, images):
    """Render footer section."""
    content_html = markdown_to_html(content) if content else ''
    
    return f"""
<footer>
    <div class="container">
        <h2>Journey Complete</h2>
        {content_html}
    </div>
</footer>
"""


def render_table(table_data):
    """Render a table from structured data."""
    if not table_data:
        return ''
    
    headers = table_data.get('headers', [])
    rows = table_data.get('rows', [])
    
    if not headers and not rows:
        return ''
    
    html = '<div class="table-wrapper"><table>\n'
    
    if headers:
        html += '<thead><tr>\n'
        for h in headers:
            html += f'<th>{h}</th>\n'
        html += '</tr></thead>\n'
    
    if rows:
        html += '<tbody>\n'
        for row in rows:
            html += '<tr>\n'
            for cell in row:
                html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
        html += '</tbody>\n'
    
    html += '</table></div>\n'
    return html


def render_itinerary_cards(itinerary, cache=None):
    """Render itinerary items as cards."""
    if not itinerary:
        return ''
    
    html = '<div class="cards-grid">\n'
    
    for item in itinerary:
        day = item.get('day', '')
        item_title = item.get('title', '')
        location = item.get('location', '')
        distance = item.get('distance', '')
        terrain = item.get('terrain', '')
        item_content = item.get('content', '')
        highlights = item.get('highlights', [])
        activities = item.get('activities', [])
        queries = item.get('queries', [])
        
        # Get image for this item
        img_html = ''
        if queries and cache:
            for q in queries:
                if q in cache:
                    urls = cache[q].get('urls', [])
                    if urls:
                        img_html = f'<img src="{safe_img_url(urls[0])}" alt="{html_module.escape(item_title)}" onerror="this.style.display=\'none\'">'
                        break
        
        # Build card content
        card_content = ''
        if location:
            card_content += f'<p class="card-meta">📍 {location}</p>'
        if distance:
            card_content += f'<p class="card-meta">🚴 {distance}</p>'
        if terrain:
            card_content += f'<p class="card-meta">🛤️ {terrain}</p>'
        if item_content:
            card_content += f'<p>{item_content[:200]}</p>'
        
        # Highlights or activities
        items_list = highlights or activities
        if items_list:
            card_content += '<ul class="card-highlights">'
            for h in items_list[:4]:
                card_content += f'<li>{h}</li>'
            card_content += '</ul>'
        
        html += f'''<div class="card">
    {img_html}
    <div class="card-content">
        <div class="card-day-badge">Day {day}</div>
        <h4>{item_title}</h4>
        {card_content}
    </div>
</div>
'''
    
    html += '</div>\n'
    return html


def render_meta_bar(meta):
    """Render section metadata (duration, location, theme) as a styled bar."""
    if not meta:
        return ''
    
    items = []
    if meta.get('Duration'):
        items.append(f'<span class="meta-item">📅 {meta["Duration"]}</span>')
    if meta.get('duration'):
        items.append(f'<span class="meta-item">📅 {meta["duration"]}</span>')
    if meta.get('Base Location') or meta.get('location') or meta.get('base'):
        loc = meta.get('Base Location') or meta.get('location') or meta.get('base')
        items.append(f'<span class="meta-item">📍 {loc}</span>')
    if meta.get('Theme') or meta.get('theme') or meta.get('focus'):
        theme = meta.get('Theme') or meta.get('theme') or meta.get('focus')
        items.append(f'<span class="meta-item">🎯 {theme}</span>')
    
    if not items:
        return ''
    
    return f'<div class="section-meta-bar">{" ".join(items)}</div>\n'


def render_cards_from_data(cards, cache=None):
    """Render cards from a cards array in YAML."""
    if not cards:
        return ''
    
    html = '<div class="cards-grid">\n'
    
    for card in cards:
        card_title = card.get('title', '')
        card_content = card.get('content', '')
        card_queries = card.get('queries', [])
        card_bullets = card.get('bullets', [])
        
        # Get image for this card
        img_html = ''
        if card_queries and cache:
            for q in card_queries:
                if q in cache:
                    urls = cache[q].get('urls', [])
                    if urls:
                        img_html = f'<img src="{safe_img_url(urls[0])}" alt="{html_module.escape(card_title)}" onerror="this.style.display=\'none\'">'
                        break
        
        # Build card content
        content_html = ''
        if card_content:
            content_html = f'<p>{process_inline_markdown(card_content[:300])}</p>'
        
        if card_bullets:
            content_html += '<ul class="card-highlights">'
            for b in card_bullets[:5]:
                content_html += f'<li>{process_inline_markdown(b)}</li>'
            content_html += '</ul>'
        
        html += f'''<div class="card">
    {img_html}
    <div class="card-content">
        <h4>{process_inline_markdown(card_title)}</h4>
        {content_html}
    </div>
</div>
'''
    
    html += '</div>\n'
    return html


def render_itinerary_full(itinerary, cache=None):
    """Render full itinerary items as cards."""
    if not itinerary:
        return ''
    
    html = '<div class="cards-grid itinerary-cards">\n'
    
    for item in itinerary:
        day = item.get('day', '')
        item_title = item.get('title', '')
        location = item.get('location', '')
        distance = item.get('distance', '')
        terrain = item.get('terrain', '')
        item_content = item.get('content', '')
        activities = item.get('activities', [])
        details = item.get('details', [])
        highlights = item.get('highlights', [])
        dietary_note = item.get('dietary_note', '')
        queries = item.get('queries', [])
        
        # Get image for this card
        card_img = ''
        if queries and cache:
            for q in queries:
                if q in cache:
                    urls = cache[q].get('urls', [])
                    if urls:
                        card_img = f'<img src="{safe_img_url(urls[0])}" alt="{html_module.escape(item_title)}" onerror="this.style.display=\'none\'">'
                        break
        
        # Build card content
        content_html = ''
        
        # Meta info
        meta_items = []
        if location:
            meta_items.append(f'📍 {location}')
        if distance:
            meta_items.append(f'🚴 {distance}')
        if terrain:
            meta_items.append(f'🛤️ {terrain}')
        
        if meta_items:
            content_html += f'<div class="card-meta">{" · ".join(meta_items)}</div>\n'
        
        if item_content:
            # Truncate long content for card display
            truncated = item_content[:250] + '...' if len(item_content) > 250 else item_content
            content_html += f'<p>{process_inline_markdown(truncated)}</p>\n'
        
        # Activities or details list (show first few)
        list_items = activities or details or highlights
        if list_items:
            content_html += '<ul class="card-highlights">\n'
            for li in list_items[:4]:  # Max 4 items
                content_html += f'<li>{process_inline_markdown(li)}</li>\n'
            if len(list_items) > 4:
                content_html += f'<li class="more-items">+{len(list_items) - 4} more...</li>\n'
            content_html += '</ul>\n'
        
        if dietary_note:
            # Truncate dietary note for card
            truncated_note = dietary_note[:150] + '...' if len(dietary_note) > 150 else dietary_note
            content_html += f'<div class="card-dietary-note">🍽️ {process_inline_markdown(truncated_note)}</div>\n'
        
        html += f'''<div class="card day-card">
    <div class="day-badge-inline">Day {day}</div>
    {card_img}
    <div class="card-content">
        <h4>{process_inline_markdown(item_title)}</h4>
        {content_html}
    </div>
</div>
'''
    
    html += '</div>\n'
    return html


def render_section(style, title, content, images, section_data=None, cache=None):
    """
    Render a section based on its style.
    
    Args:
        style: Style type (hero, cards, day-section, etc.)
        title: Section title
        content: Section text content
        images: List of image URLs
        section_data: Full section dict for advanced rendering (itinerary, table, etc.)
        cache: Image cache for nested lookups
    
    Returns:
        HTML string
    """
    section_data = section_data or {}
    meta = section_data.get('meta', {})
    cards = section_data.get('cards', [])
    itinerary = section_data.get('itinerary', [])
    
    if style == 'hero':
        return render_hero(title, content, images)
    
    elif style == 'cards':
        clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        base_html = f'<section class="container cards-section"><h2>{process_inline_markdown(clean_title)}</h2>\n'
        if content:
            base_html += f'<p class="section-intro">{process_inline_markdown(content)}</p>\n'
        
        # Check if we have cards data
        if cards:
            base_html += render_cards_from_data(cards, cache)
        # Or itinerary data to render as cards
        elif itinerary:
            base_html += render_itinerary_cards(itinerary, cache)
        else:
            # Fall back to parsing content
            base_html += '<div class="cards-grid"></div>\n'
        
        base_html += '</section>\n'
        return base_html
    
    elif style == 'day-section':
        # Check if we have itinerary items to render
        if itinerary:
            clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
            html = f'<section class="container"><h2>{process_inline_markdown(clean_title)}</h2>\n'
            if content:
                html += f'<p class="section-intro">{process_inline_markdown(content)}</p>\n'
            html += '</section>\n'
            html += render_itinerary_full(itinerary, cache)
            return html
        return render_day_section(title, content, images)
    
    elif style == 'gallery':
        clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        html = f'<section class="container-wide gallery-section"><h2>{process_inline_markdown(clean_title)}</h2>'
        
        # Add meta bar if present
        html += render_meta_bar(meta)
        
        if images:
            html += '<div class="gallery-grid">\n'
            for url in images[:4]:
                html += f'    <img src="{safe_img_url(url)}" alt="" onerror="this.style.display=\'none\'">\n'
            html += '</div>\n'
        
        if content:
            html += f'<div class="container"><p>{process_inline_markdown(content)}</p></div>'
        
        html += '</section>\n'
        return html
    
    elif style == 'highlight':
        return render_highlight(title, content, images)
    
    elif style == 'table':
        table_data = section_data.get('table')
        clean_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        table_html = f'<section class="container content-section"><h2>{process_inline_markdown(clean_title)}</h2>\n'
        if content:
            table_html += f'<p>{process_inline_markdown(content)}</p>\n'
        table_html += render_table(table_data)
        table_html += '</section>\n'
        return table_html
    
    elif style == 'footer':
        return render_footer(title, content, images)
    
    else:  # default to 'content'
        return render_content(title, content, images)
