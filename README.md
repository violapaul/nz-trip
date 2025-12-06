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
Markdown → YAML → Thumbnails → AI Selection → HTML
```

1. **Analyze**: AI reads markdown, creates structured YAML with styles and image queries
2. **Scrape**: Fetches images from Google, downloads thumbnails locally
3. **Select**: Gemini Vision evaluates thumbnails, picks best images for each section
4. **Generate**: Creates beautiful HTML using AI-selected images

## Step by Step

```bash
# Step 1: Analyze markdown → YAML
python travel_md_converter/analyze.py trip.md

# Step 2: Scrape images + download thumbnails
python travel_md_converter/scraper.py trip.analysis.yaml

# Step 3: AI selects best images
python travel_md_converter/selector.py trip.analysis.yaml

# Step 4: Generate HTML
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
├── scraper.py      # Image fetching + thumbnails
├── selector.py     # AI image selection (Gemini Vision)
├── generator.py    # YAML → HTML
├── styles.css      # All styling
├── styles.py       # Render functions
├── prompt.py       # AI prompt
└── utils.py        # Utilities

images/             # Downloaded thumbnails (for AI evaluation)
query_cache.yaml    # Image URLs + thumbnail paths
```

## Requirements

```bash
pip install pyyaml requests google-genai
```

## Without API Key

Works in manual mode - copies prompt for you to paste into any AI (Claude, ChatGPT).

## License

MIT
