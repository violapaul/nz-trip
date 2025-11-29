#!/usr/bin/env python3
"""
Compare nz_trip.md with nz_trip_new.md and show the differences.

Usage:
    python diff_md.py
    python diff_md.py nz_trip.md nz_trip_new.md

Output shows:
    + Added lines (green)
    - Removed lines (red)
    ~ Modified sections (yellow)
"""

import difflib
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def colorize(text, color):
    """Add color to text for terminal output."""
    return f"{color}{text}{RESET}"


def show_diff(old_file, new_file):
    """Show a readable diff between two markdown files."""
    
    # Check if files exist
    old_path = Path(old_file)
    new_path = Path(new_file)
    
    if not old_path.exists():
        print(f"Error: {old_file} not found")
        return
    
    if not new_path.exists():
        print(f"Error: {new_file} not found")
        return
    
    # Read files
    with open(old_path, 'r') as f:
        old_lines = f.readlines()
    
    with open(new_path, 'r') as f:
        new_lines = f.readlines()
    
    # Generate unified diff
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=old_file,
        tofile=new_file,
        lineterm=''
    )
    
    # Print header
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}Comparing: {old_file} → {new_file}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    # Track if we found any differences
    found_changes = False
    
    # Process and display diff
    for line in diff:
        line = line.rstrip()
        
        if line.startswith('---') or line.startswith('+++'):
            print(colorize(line, BLUE))
        elif line.startswith('@@'):
            print(colorize(f"\n{line}", YELLOW))
            found_changes = True
        elif line.startswith('+'):
            print(colorize(line, GREEN))
        elif line.startswith('-'):
            print(colorize(line, RED))
        else:
            # Context lines
            print(line)
    
    if not found_changes:
        print(colorize("\n✓ No differences found - files are identical", GREEN))
    else:
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(colorize("Legend:", BOLD))
        print(colorize("  + Added lines", GREEN))
        print(colorize("  - Removed lines", RED))
        print(colorize("  ~ Section headers", YELLOW))
        print(f"{BOLD}{'='*70}{RESET}\n")


def show_summary(old_file, new_file):
    """Show a high-level summary of changes."""
    
    old_path = Path(old_file)
    new_path = Path(new_file)
    
    if not old_path.exists() or not new_path.exists():
        return
    
    with open(old_path, 'r') as f:
        old_lines = f.readlines()
    
    with open(new_path, 'r') as f:
        new_lines = f.readlines()
    
    # Count sections (lines starting with ## or ###)
    old_sections = [l.strip() for l in old_lines if l.startswith('##')]
    new_sections = [l.strip() for l in new_lines if l.startswith('##')]
    
    # Count image references
    old_images = sum(1 for l in old_lines if '![' in l or '{{image:' in l)
    new_images = sum(1 for l in new_lines if '![' in l or '{{image:' in l)
    
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Lines: {len(old_lines)} → {len(new_lines)} ({len(new_lines) - len(old_lines):+d})")
    print(f"  Sections: {len(old_sections)} → {len(new_sections)} ({len(new_sections) - len(old_sections):+d})")
    print(f"  Images: {old_images} → {new_images} ({new_images - old_images:+d})")
    
    # Show new sections
    new_section_titles = set(new_sections) - set(old_sections)
    if new_section_titles:
        print(f"\n{colorize('New sections:', GREEN)}")
        for section in sorted(new_section_titles):
            print(f"  + {section}")
    
    # Show removed sections
    removed_section_titles = set(old_sections) - set(new_sections)
    if removed_section_titles:
        print(f"\n{colorize('Removed sections:', RED)}")
        for section in sorted(removed_section_titles):
            print(f"  - {section}")


def main():
    # Get file paths from arguments or use defaults
    if len(sys.argv) >= 3:
        old_file = sys.argv[1]
        new_file = sys.argv[2]
    else:
        # Use defaults relative to script location
        script_dir = Path(__file__).parent
        old_file = str(script_dir / 'nz_trip.md')
        new_file = str(script_dir / 'nz_trip_new.md')
    
    # Show summary first
    show_summary(old_file, new_file)
    
    # Show detailed diff
    show_diff(old_file, new_file)


if __name__ == '__main__':
    main()

