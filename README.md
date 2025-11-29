# Travel Markdown Converter

Transform travel itinerary markdown into beautiful, styled HTML pages with AI-powered analysis and automatic images.

## Quick Start

```bash
# Set your Gemini API key (get one at https://aistudio.google.com/apikey)
export GEMINI_API_KEY="your-key-here"

# Convert your trip markdown to HTML
python convert.py your_trip.md
```

Creates `your_trip.html` with beautiful styling and relevant images.

## How It Works

```
Markdown → YAML → HTML
```

1. **Analyze**: AI reads markdown, creates structured YAML with styles and image queries
2. **Scrape**: Fetches relevant images from Google (cached for reuse)
3. **Generate**: Creates beautiful HTML from YAML

## Step by Step

```bash
# Step 1: Analyze markdown → YAML
python travel_md_converter/analyze.py trip.md

# Step 2: Scrape images
python travel_md_converter/scraper.py trip.analysis.yaml

# Step 3: Generate HTML
python travel_md_converter/generator.py trip.analysis.yaml
```

## Section Styles

The AI automatically assigns styles:

- **hero** - Full-screen opening with background image
- **gallery** - Location intro with image grid
- **cards** - Grid of items (activities, dining, etc.)
- **day** - Daily itinerary with day badge
- **highlight** - Important callout box
- **table** - Data summary
- **content** - Standard text sections
- **footer** - Closing section

## Project Structure

```
travel_md_converter/
├── analyze.py      # Markdown → YAML (AI)
├── scraper.py      # Image fetching
├── generator.py    # YAML → HTML
├── styles.css      # All styling
├── styles.py       # Render functions
├── prompt.py       # AI prompt
└── utils.py        # Utilities
```

## Requirements

```bash
pip install pyyaml requests google-genai
```

## Without API Key

Works in manual mode - copies prompt for you to paste into any AI (Claude, ChatGPT).

## License

MIT
