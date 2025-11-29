# Gemini API Setup Guide

Enable fully automatic travel markdown analysis with Google's Gemini API.

## Step 1: Get Your API Key

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your key (starts with `AIza...`)

## Step 2: Set Environment Variable

### Option A: Temporary (current session)
```bash
export GEMINI_API_KEY="AIza..."
```

### Option B: Permanent (add to ~/.bashrc or ~/.zshrc)
```bash
echo 'export GEMINI_API_KEY="AIza..."' >> ~/.bashrc
source ~/.bashrc
```

### Option C: Per-project (.env file)
```bash
# Create .env file
echo 'export GEMINI_API_KEY="AIza..."' > .env

# Load it before running
source .env
```

## Step 3: Test It

```bash
python test_gemini.py
```

Expected output:
```
✓ API key found: AIza...
✓ Calling Gemini API...
✓ Response received!

AI uses algorithms and data to learn patterns and make predictions or decisions.
```

## Step 4: Use with Analyze

Now `analyze.py` will automatically call Gemini:

```bash
python travel_md_converter/analyze.py example_trip.md
```

Output:
```
✓ Detected 8 sections
✓ GEMINI_API_KEY found - using automatic mode
✓ Calling Gemini API...
✓ Received response from Gemini
✓ Saved analysis to: example_trip.analysis.yaml
```

## Troubleshooting

### "google-genai not installed"
```bash
pip install google-genai
```

### "API key not found"
Check your environment:
```bash
echo $GEMINI_API_KEY
```

Should show your key. If empty, set it again.

### "Invalid API key"
- Make sure you copied the full key
- Check for extra spaces or quotes
- Generate a new key if needed

### "Falling back to manual mode"
The script will automatically fall back to manual copy/paste if:
- API key not set
- API call fails
- Package not installed

This ensures you can always use the tool!

## Benefits of Automatic Mode

✅ **No copy/paste** - Script handles everything  
✅ **Faster** - Instant analysis  
✅ **Consistent** - Same quality every time  
✅ **Easy** - Just run one command  

## Manual Mode Still Works

Don't want to use an API key? No problem! Just don't set `GEMINI_API_KEY` and the tool works exactly like before with manual copy/paste.

