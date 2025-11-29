# Travel Markdown Converter

Transform travel itinerary markdown files into beautiful, styled HTML pages with AI-powered analysis and automatic image sourcing.

![Example Output](https://via.placeholder.com/800x400?text=Travel+Itinerary+Preview)

## Features

- **AI-Powered Analysis**: Uses Gemini API to intelligently structure your content
- **YAML as Single Source of Truth**: All content stored in structured YAML format
- **Beautiful Design**: "Expedition Journal" aesthetic with Cormorant Garamond headings
- **Hierarchical Layout**: Sections and subsections properly grouped visually
- **Responsive Design**: Looks great on mobile, tablet, and wide screens
- **Smart Image Caching**: Reuse images across documents, avoid re-scraping
- **Multiple Section Styles**: Hero, gallery, cards, day itineraries, highlights, tables

## Quick Start

```bash
# One command converts everything!
python convert.py example_trip.md
```

This creates `example_trip.html` with beautiful styling and images.

## How It Works

### Three-Step Pipeline

```
Markdown → YAML → HTML
   ↓         ↓       ↓
analyze.py  (AI)   generator.py
               ↓
           scraper.py (images)
```

1. **Analyze** (`analyze.py`): AI reads your markdown and creates structured YAML
2. **Scrape** (`scraper.py`): Fetches relevant images based on AI queries
3. **Generate** (`generator.py`): Creates HTML from YAML with embedded images

### The YAML is the Source of Truth

After analysis, the YAML file contains ALL content. The original markdown is no longer needed:

```yaml
sections:
  - id: executive-summary
    title: "1. Executive Summary"
    style: content
    content: |
      This report outlines a comprehensive framework...
    subsections:
      - id: climate-analysis
        title: "1.1 Climate Analysis"
        content: |
          March is the optimal month...
    queries:
      - "Melbourne skyline Yarra river sunset"
    needs_images: true
```

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/travel-md-converter.git
cd travel-md-converter

# Install dependencies
pip install -r requirements.txt

# Set up Gemini API (optional but recommended)
export GEMINI_API_KEY="your-key-here"
```

Get a Gemini API key at: https://aistudio.google.com/apikey

## Usage

### All-in-One

```bash
python convert.py your_trip.md
```

### Step by Step

```bash
# Step 1: Analyze markdown → YAML
python travel_md_converter/analyze.py your_trip.md

# Step 2: Scrape images for queries
python travel_md_converter/scraper.py your_trip.analysis.yaml

# Step 3: Generate HTML from YAML
python travel_md_converter/generator.py your_trip.analysis.yaml
```

## Project Structure

```
travel-md-converter/
├── travel_md_converter/     # Core package
│   ├── analyze.py           # Markdown → YAML (with AI)
│   ├── scraper.py           # Image scraping with caching
│   ├── generator.py         # YAML → HTML
│   ├── styles.py            # HTML rendering functions
│   ├── styles.css           # All CSS styles (separate file)
│   ├── prompt.py            # AI prompt template
│   └── utils.py             # Shared utilities
├── convert.py               # All-in-one CLI
├── example_trip.md          # Example input
├── example_trip.html        # Example output
├── requirements.txt
└── README.md
```

## Section Styles

The AI assigns these styles based on content:

| Style | Use Case | Features |
|-------|----------|----------|
| `hero` | Opening section | Full-screen background image |
| `gallery` | Location intros | Image grid with featured image |
| `cards` | Multiple items | Grid of clickable cards |
| `day` | Daily itinerary | Day badge, route info, activities |
| `highlight` | Important notes | Yellow callout box |
| `table` | Data summary | Styled responsive table |
| `content` | General text | Standard paragraphs |
| `footer` | Closing/refs | Dark background |

## Customization

### Editing Styles

CSS is in `travel_md_converter/styles.css`:

```css
:root {
    --deep-earth: #16213e;
    --sunset-gold: #e8a838;
    --parchment: #faf7f2;
}
```

### Editing the AI Prompt

The AI prompt is in `travel_md_converter/prompt.py`. Modify to:
- Change section detection rules
- Add new style types
- Adjust image query generation

### Adding New Renderers

Add functions in `styles.py`:

```python
def render_your_style(title, content, images, section_data, cache):
    return f'''<section class="your-style">
        <h2>{title}</h2>
        ...
    </section>'''
```

## Cache Management

Image URLs are cached in `query_cache.yaml`:

```bash
# View cache size
wc -l query_cache.yaml

# Clear cache
rm query_cache.yaml
```

## Requirements

- Python 3.7+
- pyyaml
- requests
- google-genai (for Gemini API)

## Troubleshooting

**Images not loading?**
- Check if URLs have special characters (handled automatically now)
- Verify `query_cache.yaml` has entries
- Try regenerating: `rm query_cache.yaml && python convert.py trip.md`

**AI analysis fails?**
- Ensure `GEMINI_API_KEY` is set
- Falls back to manual mode without API key
- Check `GEMINI_SETUP.md` for detailed instructions

**Sections not grouping properly?**
- Verify YAML has correct `subsections` nesting
- Check that section IDs are unique

## License

MIT License - Feel free to use and modify!

## Credits

Built with ❤️ for beautiful travel documentation.

Design: "Expedition Journal" aesthetic
- Fonts: Cormorant Garamond, Nunito Sans
- Color palette: Earth tones with warm accents
