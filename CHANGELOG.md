# Changelog

## Version 2.0 - Gemini API Integration (2025-11-28)

### 🚀 Major Features

**Automatic AI Analysis with Gemini API**
- Integrated Google Gemini API for fully automatic markdown analysis
- No more copy/paste - just set `GEMINI_API_KEY` and run
- Automatic fallback to manual mode if API unavailable
- Uses `gemini-2.0-flash-exp` model for fast, accurate results

### 📦 New Files

- `test_gemini.py` - Test script to verify API integration
- `GEMINI_SETUP.md` - Complete setup guide for Gemini API
- `requirements.txt` - Package dependencies (including google-genai)
- `env.example` - Example environment configuration

### 🔧 Updated Files

**analyze.py**
- Added `call_gemini_api()` function for automatic analysis
- Added `manual_input_mode()` for fallback copy/paste workflow
- Auto-detects `GEMINI_API_KEY` environment variable
- Graceful error handling with fallback to manual mode

**README.md**
- Added Gemini API setup section
- Updated installation instructions
- Added link to GEMINI_SETUP.md

**QUICKSTART.md**
- Updated with automatic/manual mode instructions
- Added API key setup steps

### 💡 How It Works

**With API Key (Automatic):**
```bash
export GEMINI_API_KEY="your-key"
python travel_md_converter/analyze.py example_trip.md
# ✓ Automatic analysis in seconds!
```

**Without API Key (Manual):**
```bash
python travel_md_converter/analyze.py example_trip.md
# → Shows prompt to copy/paste into any AI
```

### ⚙️ Technical Details

- Uses `google.genai.Client` for API calls
- Model: `gemini-2.0-flash-exp`
- Parses both raw YAML and ```yaml``` code blocks
- Zero changes needed to scraper or generator
- Backward compatible with manual workflow

### 📝 Dependencies

Added:
- `google-genai>=1.0.0`

Existing:
- `pyyaml>=6.0`
- `requests>=2.31.0`

---

## Version 1.0 - Initial Release (2025-11-28)

### Core System

**Three-Step Workflow**
1. **Analyze** - Parse markdown, generate AI prompts
2. **Scrape** - Fetch images with persistent caching
3. **Generate** - Create beautiful HTML

**7 Style Types**
- hero, cards, day-section, gallery, highlight, content, footer

**Smart Image Caching**
- Persistent `query_cache.yaml`
- Reuse across projects
- No re-scraping

**Modular Architecture**
- `travel_md_converter/` package
- Separate concerns (analysis, scraping, rendering)
- Easy to extend

### Migration from v0

- Moved old files to `Old/` directory
- Backward compatible with existing trip files
- Improved styling and responsiveness

