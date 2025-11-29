#!/usr/bin/env python3
"""
Step A: Analyze markdown and generate AI prompt for section styling.

Usage:
    python travel_md_converter/analyze.py travel.md
    
    With Gemini API (automatic):
        export GEMINI_API_KEY="your-key-here"
        python travel_md_converter/analyze.py travel.md
    
    Manual mode (no API key):
        python travel_md_converter/analyze.py travel.md
    
This will:
1. Parse sections from markdown
2. Generate prompt for AI
3. Call Gemini API (if key available) OR wait for manual paste
4. Save to travel.analysis.yaml
"""

import yaml
import sys
import os
from pathlib import Path
import re

# Import the prompt from the dedicated prompt file
from prompt import get_analysis_prompt


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def extract_sections(md_content):
    """Parse markdown to find all ## and ### headers."""
    sections = []
    lines = md_content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('## '):
            title = line[3:].strip()
            sections.append({
                'level': 2,
                'title': title,
                'id': slugify(title),
                'line': i
            })
        elif line.startswith('### '):
            title = line[4:].strip()
            sections.append({
                'level': 3,
                'title': title,
                'id': slugify(title),
                'line': i
            })
    
    return sections


def generate_prompt(md_content):
    """Generate the AI analysis prompt."""
    return get_analysis_prompt(md_content)


def call_gemini_api(prompt, api_key):
    """
    Call Gemini API to get analysis.
    Returns the response text or None on error.
    """
    try:
        from google import genai
        
        print("✓ Calling Gemini API...")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",            
            contents=prompt,
        )
        
        print("✓ Received response from Gemini")
        return response.text
        
    except ImportError:
        print("✗ Error: google-genai package not installed")
        print("  Install with: pip install google-genai")
        return None
    except Exception as e:
        print(f"✗ Error calling Gemini API: {e}")
        return None


def manual_input_mode(prompt):
    """
    Manual mode: display prompt and wait for user to paste response.
    """
    print("\n" + "="*70)
    print("COPY THE PROMPT BELOW AND PASTE INTO CLAUDE/CHATGPT/GEMINI")
    print("="*70 + "\n")
    
    print(prompt)
    
    print("\n" + "="*70)
    print("After getting the AI response, paste it below.")
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
    print("="*70 + "\n")
    
    # Read AI response from stdin
    try:
        response_lines = []
        while True:
            try:
                line = input()
                response_lines.append(line)
            except EOFError:
                break
        
        return '\n'.join(response_lines)
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py travel.md")
        print("\nOptional: Set GEMINI_API_KEY environment variable for automatic mode")
        sys.exit(1)
    
    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        sys.exit(1)
    
    md_content = md_file.read_text()
    
    # Show detected sections
    sections = extract_sections(md_content)
    print(f"\n✓ Detected {len(sections)} sections:")
    for s in sections:
        indent = "  " * (s['level'] - 2)
        print(f"  {indent}{'#' * s['level']} {s['title']}")
    
    # Generate prompt
    prompt = generate_prompt(md_content)
    
    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if api_key:
        print("\n✓ GEMINI_API_KEY found - using automatic mode")
        response = call_gemini_api(prompt, api_key)
        if response is None:
            print("\n⚠ Falling back to manual mode...")
            response = manual_input_mode(prompt)
    else:
        print("\n⚠ GEMINI_API_KEY not found - using manual mode")
        print("  (Set GEMINI_API_KEY to enable automatic analysis)")
        response = manual_input_mode(prompt)
    
    if response is None:
        print("\n✗ No response received")
        sys.exit(1)
    
    # Parse YAML from response
    try:
        # Extract YAML block if wrapped in ```yaml
        if '```yaml' in response:
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                response = yaml_match.group(1)
        
        analysis = yaml.safe_load(response)
        
        # Validate structure
        if 'sections' not in analysis:
            print("\n✗ Error: Response missing 'sections' key")
            sys.exit(1)
        
        # Save to file
        output_file = md_file.parent / f"{md_file.stem}.analysis.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(analysis, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n✓ Saved analysis to: {output_file}")
        print(f"  Found {len(analysis.get('sections', []))} sections with styles")
        
        # Show summary
        styles_count = {}
        queries_count = 0
        for section in analysis['sections']:
            style = section.get('style', 'unknown')
            styles_count[style] = styles_count.get(style, 0) + 1
            queries_count += len(section.get('queries', []))
        
        print(f"  Styles used: {dict(styles_count)}")
        print(f"  Total queries: {queries_count}")
        
    except Exception as e:
        print(f"\n✗ Error parsing response: {e}")
        print("Please check the YAML format")
        sys.exit(1)


if __name__ == '__main__':
    main()

