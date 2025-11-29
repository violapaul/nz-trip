# Quick Start Guide

Get started in 2 minutes!

## Installation

```bash
pip install -r requirements.txt
```

**Optional - Enable Automatic Mode:**
```bash
export GEMINI_API_KEY="your-api-key"
```
Get your key at: https://aistudio.google.com/apikey

## Easiest Way: One Command! ⚡

```bash
python convert.py example_trip.md
```

That's it! Opens `example_trip.html` when done. 🎉

---

## Alternative: Manual Steps (3 Commands)

If you want more control:

### 1️⃣ Analyze with AI

```bash
python travel_md_converter/analyze.py example_trip.md
```

**Automatic Mode (with API key):**
- Script calls Gemini API automatically
- Analyzes sections and suggests styles
- Generates image queries
- Saves `example_trip.analysis.yaml`

**Manual Mode (no API key):**
- Script shows you an AI prompt
- Copy it and paste into Claude/ChatGPT/Gemini
- Paste the AI's YAML response back
- Press Ctrl+D when done

### 2️⃣ Scrape Images

```bash
python travel_md_converter/scraper.py example_trip.analysis.yaml
```

**What happens:**
- Checks cache for existing queries
- Scrapes only NEW queries from Google Images
- Saves 3 images per query
- Updates `query_cache.yaml`

**Output:**
```
✓ Found 15 unique queries in analysis
  • 0 already in cache
  • 15 need scraping

[1/15] Paris Eiffel Tower sunset aerial view
  → Found 3 images
...
✓ Cache updated: query_cache.yaml
```

### 3️⃣ Generate HTML

```bash
python travel_md_converter/generator.py example_trip.md example_trip.analysis.yaml
```

**What happens:**
- Reads your markdown
- Applies AI-suggested styles
- Inserts cached images
- Creates `example_trip.html`

**Output:**
```
✓ Generating HTML...
  [1/7] Weekend in Paris (hero)
      → 2 images
  [2/7] Why Paris is Perfect for a Weekend (cards)
      → 3 images
...
✓ Generated: example_trip.html
```

## View Result

Open `example_trip.html` in your browser:

```bash
open example_trip.html
```

That's it! Beautiful travel page ready to share. 🎉

## Next Steps

- Try it with your own travel.md
- Reuse the cache for similar trips
- Customize styles in `travel_md_converter/styles.py`

## Tips

💡 **Use convert.py**: One command does everything! `python convert.py travel.md`

💡 **Cache is your friend**: Once queries are scraped, they're cached forever. Create multiple HTML versions without re-scraping!

💡 **Iterate fast**: Edit your markdown, just run `python convert.py travel.md` again. Cache makes it super fast!

💡 **Start small**: Test with `example_trip.md` before your full itinerary.

💡 **Set API key once**: `export GEMINI_API_KEY="..."` and forget about it!

## Need Help?

Check `README.md` for detailed documentation.

