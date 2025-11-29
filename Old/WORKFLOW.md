# NZ Trip Markdown Workflow

This workflow helps you maintain and update the trip markdown with images managed through YAML references.

## Overview

1. **Create updated markdown** (`nz_trip_new.md`)
2. **Review differences** with the diff tool
3. **Work with AI agent** to add queries and image tags
4. **Scrape images** for new queries
5. **Build HTML** with resolved image references

## Step-by-Step Usage

### Step 1: Create Your Updated Markdown

Make changes to your trip plan in a new file:
```bash
cp nz_trip.md nz_trip_new.md
# Edit nz_trip_new.md with your changes
```

### Step 2: Review Differences

Run the diff script to see what changed:
```bash
python diff_md.py
```

This shows:
- Summary of changes (lines, sections, images)
- Detailed diff with color coding:
  - `+` Green = Added lines
  - `-` Red = Removed lines
  - `~` Yellow = Modified sections

### Step 3: Work with AI Agent

Ask your AI agent to:

1. **Suggest new image queries** for new sections
   - Review the diff output
   - Add queries to `nz_trip_image_queries.yaml`

2. **Add image reference tags** in the markdown
   - Use format: `{{image:Query Name:index}}`
   - Example: `{{image:Auckland harbour bridge night lights:0}}`
   - Index 0 = first image, 1 = second image, etc.

### Step 4: Scrape New Images

Run the scraper to fetch URLs for new queries:
```bash
python scrape_images.py
```

This will:
- Read queries from `nz_trip_image_queries.yaml`
- Fetch top 3 images per query from Google
- Save URLs to `nz_trip_image_urls.yaml`
- Generate preview HTML to `images.html`

### Step 5: Build Final HTML

Replace the old markdown and build HTML:
```bash
mv nz_trip_new.md nz_trip.md
python md_to_html.py nz_trip.md index.html
```

The converter will:
- Resolve `{{image:query:index}}` tags to actual URLs
- Look up URLs in `nz_trip_image_urls.yaml`
- Generate beautiful HTML with embedded images

## Image Reference Format

### In Markdown
```markdown
Check out this amazing view: {{image:Auckland harbour bridge night lights:0}}

The second image shows another angle: {{image:Auckland harbour bridge night lights:1}}
```

### In YAML Structure
```yaml
Day 1:
  Auckland harbour bridge night lights:
  - https://example.com/image1.jpg  # index 0
  - https://example.com/image2.jpg  # index 1
  - https://example.com/image3.jpg  # index 2
```

### Resolution
The tag `{{image:Auckland harbour bridge night lights:0}}` becomes:
```html
<img src="https://example.com/image1.jpg" alt="Auckland harbour bridge night lights" style="max-width: 100%; height: auto;">
```

## Files

- `nz_trip.md` - Current trip plan markdown
- `nz_trip_new.md` - Updated version (you create this)
- `nz_trip_image_queries.yaml` - Image search queries by day
- `nz_trip_image_urls.yaml` - Scraped image URLs by query
- `diff_md.py` - Diff tool to compare versions
- `scrape_images.py` - Image URL scraper
- `md_to_html.py` - Markdown to HTML converter (supports image tags)
- `index.html` - Final generated HTML
- `images.html` - Preview gallery of all scraped images

## Tips

- Use descriptive query names that you can remember
- Keep queries consistent across YAML and markdown tags
- Preview images in `images.html` before adding tags
- Test with `nz_trip_new.md` before replacing `nz_trip.md`

