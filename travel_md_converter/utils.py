"""
Utility functions for markdown parsing and HTML generation.
"""

import re
from typing import List, Dict, Tuple


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def normalize_title(text):
    """
    Normalize a title for comparison by removing markdown formatting.
    Handles: **bold**, escaped characters like \., extra whitespace.
    """
    # Remove bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove backslash escapes (e.g., \. -> .)
    text = re.sub(r'\\(.)', r'\1', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()


def process_inline_markdown(text):
    """Convert inline markdown (bold, italic, links) to HTML."""
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def parse_table(lines: List[str], start_idx: int) -> Tuple[str, int]:
    """
    Parse a markdown table starting at the given index.
    Returns (html_string, next_line_index).
    """
    table_lines = []
    i = start_idx
    
    # Collect all table lines
    while i < len(lines) and '|' in lines[i]:
        table_lines.append(lines[i].strip())
        i += 1
    
    if len(table_lines) < 2:
        return '', start_idx
    
    html = '<div class="table-wrapper"><table>\n'
    
    # Parse header row
    header_cells = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]
    html += '<thead><tr>\n'
    for cell in header_cells:
        html += f'<th>{process_inline_markdown(cell)}</th>\n'
    html += '</tr></thead>\n'
    
    # Skip separator row (line with :---: patterns)
    data_start = 1
    if len(table_lines) > 1 and re.match(r'^[\s|:\-]+$', table_lines[1]):
        data_start = 2
    
    # Parse data rows
    if data_start < len(table_lines):
        html += '<tbody>\n'
        for row in table_lines[data_start:]:
            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            html += '<tr>\n'
            for cell in cells:
                html += f'<td>{process_inline_markdown(cell)}</td>\n'
            html += '</tr>\n'
        html += '</tbody>\n'
    
    html += '</table></div>\n'
    return html, i


def markdown_to_html(md_text):
    """
    Convert basic markdown to HTML.
    Handles: paragraphs, lists, bold, italic, links, tables.
    """
    lines = md_text.split('\n')
    html_parts = []
    i = 0
    in_list = False
    list_type = None
    
    while i < len(lines):
        line = lines[i]
        
        # Close list if needed
        if in_list and not (line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\d+\.', line.strip())):
            html_parts.append(f'</{list_type}>')
            in_list = False
            list_type = None
        
        # Skip headers (handled separately)
        if line.startswith('#'):
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            html_parts.append('<hr>')
            i += 1
            continue
        
        # Table detection (line starts with | or has | separators)
        if '|' in line and line.strip().startswith('|'):
            table_html, next_i = parse_table(lines, i)
            if table_html:
                html_parts.append(table_html)
                i = next_i
                continue
        
        # Unordered list
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
                list_type = 'ul'
            content = line.strip()[2:]
            html_parts.append(f'<li>{process_inline_markdown(content)}</li>')
        
        # Ordered list
        elif re.match(r'^\d+\.', line.strip()):
            if not in_list:
                html_parts.append('<ol>')
                in_list = True
                list_type = 'ol'
            content = re.sub(r'^\d+\.\s*', '', line.strip())
            html_parts.append(f'<li>{process_inline_markdown(content)}</li>')
        
        # Paragraph
        elif line.strip():
            html_parts.append(f'<p>{process_inline_markdown(line)}</p>')
        
        i += 1
    
    # Close any open list
    if in_list:
        html_parts.append(f'</{list_type}>')
    
    return '\n'.join(html_parts)


def parse_markdown_sections(md_content: str, sections_info: List[Dict]) -> Dict[str, str]:
    """
    Parse markdown content into sections based on section info from analysis.
    Returns dict mapping section_id -> markdown content.
    Uses fuzzy title matching to handle markdown formatting differences.
    """
    lines = md_content.split('\n')
    sections = {}
    
    # Build index of header lines with normalized titles
    header_lines = {}
    for i, line in enumerate(lines):
        if line.startswith('# ') and not line.startswith('## '):
            header_lines[i] = {'level': 1, 'title': line[2:].strip(), 'normalized': normalize_title(line[2:].strip())}
        elif line.startswith('## '):
            header_lines[i] = {'level': 2, 'title': line[3:].strip(), 'normalized': normalize_title(line[3:].strip())}
        elif line.startswith('### '):
            header_lines[i] = {'level': 3, 'title': line[4:].strip(), 'normalized': normalize_title(line[4:].strip())}
    
    # Extract content for each section
    for section_info in sections_info:
        section_title = section_info['title']
        section_level = section_info['level']
        section_id = section_info['id']
        
        # Normalize the expected title for comparison
        normalized_expected = normalize_title(section_title)
        
        # Find the line with this header (fuzzy match on normalized titles)
        start_line = None
        for line_num, header in header_lines.items():
            # Match if normalized titles are equal OR if one contains the other
            if header['level'] == section_level or (section_level == 1 and header['level'] == 2):
                if (header['normalized'] == normalized_expected or 
                    normalized_expected in header['normalized'] or
                    header['normalized'] in normalized_expected):
                    start_line = line_num
                    break
        
        if start_line is None:
            sections[section_id] = ""
            continue
        
        # Find the end (next header of same or higher level)
        end_line = len(lines)
        sorted_headers = sorted(header_lines.keys())
        for line_num in sorted_headers:
            header = header_lines[line_num]
            if line_num > start_line and header['level'] <= header_lines[start_line]['level']:
                end_line = line_num
                break
        
        # Extract content (skip the header itself)
        content_lines = lines[start_line + 1:end_line]
        sections[section_id] = '\n'.join(content_lines).strip()
    
    return sections


def extract_first_sentence(text):
    """Extract the first sentence from text."""
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Find first sentence
    match = re.match(r'^([^.!?]+[.!?])', text.strip())
    if match:
        return match.group(1)
    
    # If no sentence end found, return first 100 chars
    if len(text) > 100:
        return text[:100] + '...'
    return text


def get_images_for_section(section_info: Dict, cache: Dict) -> List[str]:
    """
    Get image URLs for a section from cache.
    Returns list of URLs (up to 3).
    
    Respects the 'needs_images' field - returns empty list if False.
    """
    # Check if section explicitly doesn't need images
    if section_info.get('needs_images') is False:
        return []
    
    # If queries is empty, return empty list
    queries = section_info.get('queries', [])
    if not queries:
        return []
    
    urls = []
    for query in queries:
        if query in cache:
            query_urls = cache[query].get('urls', [])
            urls.extend(query_urls)
    
    # Return up to 3 images
    return urls[:3]

