#!/usr/bin/env python3
"""
All-in-one script: Analyze → Scrape → Generate

Usage:
    python convert.py travel.md
    
This runs all three steps automatically:
    1. Analyze (with Gemini API) - converts markdown to YAML with all content
    2. Scrape images (with caching)
    3. Generate HTML from YAML (markdown no longer needed)

Output: travel.html
"""

import sys
import subprocess
from pathlib import Path


def run_step(step_name, command, description):
    """Run a step and handle errors."""
    print("\n" + "="*70)
    print(f"STEP {step_name}: {description}")
    print("="*70 + "\n")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error in {description}")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠ Cancelled by user")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert.py travel.md")
        print("\nThis will:")
        print("  1. Analyze markdown with AI → generates .analysis.yaml (contains ALL content)")
        print("  2. Scrape images → updates query_cache.yaml")
        print("  3. Generate HTML from YAML (markdown no longer needed)")
        print("\nRequired: Set GEMINI_API_KEY for automatic analysis")
        print("\nAlternatively, run steps manually:")
        print("  python travel_md_converter/analyze.py travel.md")
        print("  python travel_md_converter/scraper.py travel.analysis.yaml")
        print("  python travel_md_converter/generator.py travel.analysis.yaml")
        sys.exit(1)
    
    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"✗ Error: {md_file} not found")
        sys.exit(1)
    
    # Derived file names
    analysis_file = md_file.with_suffix('.analysis.yaml')
    html_file = md_file.with_suffix('.html')
    
    print("\n" + "🚀 "*35)
    print(f"Converting: {md_file.name} → {html_file.name}")
    print("🚀 "*35)
    
    # Step 1: Analyze (converts MD → YAML with all content)
    if not run_step(
        "1/3",
        [sys.executable, "travel_md_converter/analyze.py", str(md_file)],
        "AI Analysis (MD → YAML)"
    ):
        print("\n✗ Analysis failed. Exiting.")
        sys.exit(1)
    
    if not analysis_file.exists():
        print(f"\n✗ Expected {analysis_file} but not found")
        sys.exit(1)
    
    # Step 2: Scrape images
    if not run_step(
        "2/3",
        [sys.executable, "travel_md_converter/scraper.py", str(analysis_file)],
        "Image Scraping"
    ):
        print("\n⚠ Scraping had issues, but continuing...")
    
    # Step 3: Generate HTML from YAML (no longer needs MD file!)
    if not run_step(
        "3/3",
        [sys.executable, "travel_md_converter/generator.py", str(analysis_file)],
        "HTML Generation (YAML → HTML)"
    ):
        print("\n✗ HTML generation failed. Exiting.")
        sys.exit(1)
    
    # Success!
    print("\n" + "✅ "*35)
    print("🎉 SUCCESS! Your beautiful travel page is ready!")
    print("✅ "*35)
    print(f"\n📄 Output: {html_file}")
    print(f"🖼️  Images: Cached in query_cache.yaml")
    print(f"📋 Analysis: {analysis_file} (contains all content)")
    print(f"\n💡 Open it: open {html_file}")
    print(f"\n📝 Note: The markdown file is no longer needed after analysis.")
    print(f"   Edit {analysis_file} directly to modify content.")
    print()


if __name__ == '__main__':
    main()
