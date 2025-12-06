#!/usr/bin/env python3
"""
All-in-one script: Analyze → Scrape → Select → Generate

Usage:
    python convert.py travel.md
    
This runs all steps automatically:
    1. Analyze (with Gemini API) - converts markdown to YAML with all content
    2. Scrape images + download thumbnails
    3. Select best images (with Gemini Vision)
    4. Generate HTML from YAML

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
        print("  1. Analyze markdown with AI (skipped if .analysis.yaml exists)")
        print("  2. Scrape images + thumbnails (cached in query_cache.yaml)")
        print("  3. Select best images with AI (cached in .analysis.yaml)")
        print("  4. Generate HTML")
        print("\nRequired: Set GEMINI_API_KEY for analysis & selection")
        print("\nTips:")
        print("  • Delete .analysis.yaml to force re-analysis")
        print("  • Use selector.py --force to re-select images")
        print("\nAlternatively, run steps manually:")
        print("  python travel_md_converter/analyze.py travel.md")
        print("  python travel_md_converter/scraper.py travel.analysis.yaml")
        print("  python travel_md_converter/selector.py travel.analysis.yaml")
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
    # Skip if analysis file already exists
    if analysis_file.exists():
        print("\n" + "="*70)
        print(f"STEP 1/4: AI Analysis - SKIPPED (using existing {analysis_file.name})")
        print("="*70)
        print(f"\n✓ Found existing analysis: {analysis_file}")
        print("  Delete it to force re-analysis.")
    else:
        if not run_step(
            "1/4",
            [sys.executable, "travel_md_converter/analyze.py", str(md_file)],
            "AI Analysis (MD → YAML)"
        ):
            print("\n✗ Analysis failed. Exiting.")
            sys.exit(1)
        
        if not analysis_file.exists():
            print(f"\n✗ Expected {analysis_file} but not found")
            sys.exit(1)
    
    # Step 2: Scrape images + download thumbnails
    if not run_step(
        "2/4",
        [sys.executable, "travel_md_converter/scraper.py", str(analysis_file)],
        "Image Scraping + Thumbnails"
    ):
        print("\n⚠ Scraping had issues, but continuing...")
    
    # Step 3: Select best images with Gemini Vision
    if not run_step(
        "3/4",
        [sys.executable, "travel_md_converter/selector.py", str(analysis_file)],
        "AI Image Selection"
    ):
        print("\n⚠ Selection had issues, will use fallback images...")
    
    # Step 4: Generate HTML from YAML
    if not run_step(
        "4/4",
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
    print(f"🖼️  Images: AI-selected, thumbnails in images/")
    print(f"📋 Analysis: {analysis_file}")
    print(f"\n💡 Open it: open {html_file}")
    print()


if __name__ == '__main__':
    main()
