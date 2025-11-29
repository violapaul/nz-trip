"""
AI Prompt for Travel Markdown Analysis

This prompt guides the AI to:
1. Analyze markdown structure
2. Assign appropriate styles to sections
3. Generate relevant image queries (or skip images where not needed)
4. Extract day-by-day itineraries into structured format
5. Identify content that should be restructured (e.g., inline days → cards)

The system handles multiple document types:
- Simple weekend trip guides
- Complex multi-week expedition plans
- Day-by-day itineraries
- Mixed academic/adventure travel
"""

ANALYSIS_PROMPT = """# TRAVEL ITINERARY ANALYZER

You are converting a travel itinerary markdown file into a structured YAML document.

## THE GOLDEN RULE: NEVER DROP CONTENT

**Every single piece of text from the markdown MUST appear in the YAML output.**
- Every paragraph
- Every bullet point  
- Every metadata line (Duration, Location, Theme, etc.)
- Every table
- Every note, tip, or warning

The markdown file will be DELETED after conversion. If you drop content, it's gone forever.

## Your Job

1. **Capture ALL content** - this is non-negotiable
2. Identify natural document structure (let the document guide you)
3. Assign visual styles appropriate to each section
4. Generate image queries WHERE APPROPRIATE (not everywhere)
5. Clean up formatting artifacts (escaped chars, markdown syntax)

## CRITICAL RULES

### Rule 0: NEVER DROP CONTENT (Most Important!)

If you see it in the markdown, it MUST be in the YAML. Examples of content to capture:

```markdown
Duration: Days 1–3  
Base Location: Southbank/Arts Precinct  
Theme: Academic engagement paired with active maritime recovery.
```
→ Capture in `meta:` field

```markdown
* **Recommendation:** Qantas Business Class is preferred...
```
→ Capture the full recommendation text

```markdown
| Day | Location | Activity |
| 1 | Melbourne | Arrival |
```
→ Capture in `table:` field

**Every paragraph, bullet, table, metadata line, note, and tip must be preserved.**

### Rule 1: Not Every Section Needs Images
Skip image queries for:
- **Dietary/allergy sections** (no one wants pics of allergens)
- **Insurance/legal sections** (boring paperwork)
- **Risk management sections**
- **Technical logistics** (flight numbers, booking codes)
- **Reference lists** (citations, works cited)
- **Abstract summaries** without visual content

Set `queries: []` for these sections.

### Rule 2: Image Queries Must Be Specific and Scenic
BAD queries (too generic, stock-photo-ish):
- "travel insurance policy paperwork"
- "business traveler at airport"
- "healthy meal"
- "airplane interior"
- "hotel room"

GOOD queries (specific, evocative, destination-focused):
- "Port Phillip Bay sailing yacht rough water Melbourne"
- "Bright Victoria autumn trees golden avenue cyclists"
- "Arrowtown New Zealand historic cottages autumn leaves"
- "Lake Wakatipu Remarkables mountain range sunset"
- "Milford Sound Mitre Peak aerial waterfall"

Always include:
- **Location name** (city, region, landmark)
- **Activity or subject** (cycling, sailing, hiking)
- **Atmospheric details** (autumn, sunset, morning mist)

### Rule 3: Extract Day-by-Day Itineraries
When you see patterns like:
- "Day 1: ...", "Day 2: ..."
- "Day 4: The Grand Valley Rail Trail Loop"
- Multiple activities grouped by day

Extract these into the `itinerary` field with structured data.

### Rule 4: Identify Content Needing Restructuring
If a section contains multiple distinct items that should be cards (e.g., multiple days described in paragraphs), set `needs_restructure: true` and provide `restructure_hint`.

## AVAILABLE STYLES

| Style | Use For | Images? |
|-------|---------|---------|
| `hero` | Main title/intro (1 per doc) | Yes - dramatic landscape |
| `gallery` | Location introductions with visual impact | Yes - 3-4 scenic shots |
| `day-section` | Single day activities | Yes - 2-3 activity shots |
| `cards` | Multiple items (days, recommendations, options) | Yes - 1 per card |
| `content` | Standard paragraphs with optional visuals | Maybe - 0-2 images |
| `highlight` | Important callouts, warnings, tips | No |
| `table` | Structured data (flights, distances) | No |
| `footer` | Conclusion, references | No |

## OUTPUT FORMAT

The YAML contains ALL content - the original markdown is not needed after conversion.

```yaml
metadata:
  title: "Document Title"
  subtitle: "Optional subtitle or tagline"
  destination: "Primary destination(s)"
  duration: "Trip duration if mentioned"
  generated: "ISO timestamp"

sections:
  - id: unique-slug
    title: "Section Title (cleaned of markdown formatting)"
    level: 2  # 1=h1, 2=h2, 3=h3
    style: content
    
    # CONTENT - the actual text (cleaned of markdown artifacts)
    # MUST include ALL text - never drop anything!
    content: |
      The full paragraph text goes here. Multiple paragraphs
      are preserved. Clean up any escaped characters like \.
      
      This is another paragraph of content.
    
    # METADATA - capture any structured info (Duration, Location, Theme, etc.)
    # These vary by document - include whatever the source has
    meta:
      duration: "Days 1-3"              # if present
      location: "Southbank/Arts Precinct"  # if present
      theme: "Some theme description"      # if present
      # ... any other key-value pairs found
    
    # For bullet point content
    bullets:
      - "First bullet point"
      - "Second bullet point"
    
    # IMAGE QUERIES
    needs_images: true  # or false
    queries:  # empty list if needs_images: false
      - "specific scenic query with location"
      - "another specific query"
    
    # SUBSECTIONS (nested structure)
    subsections:
      - id: nested-section
        title: "Subsection Title"
        style: cards
        content: "Subsection content..."
    
    # For day-by-day itineraries
    itinerary:
      - day: 1
        title: "Arrival in Auckland"
        location: "Auckland"
        content: "Detailed description of the day..."
        activities:
          - "Check into hotel"
          - "Evening harbor walk"
        queries:
          - "Auckland Viaduct Harbour evening lights"
    
    # For tabular data (flights, distances, etc.)
    table:
      headers: ["Column 1", "Column 2", "Column 3"]
      rows:
        - ["Cell 1", "Cell 2", "Cell 3"]
        - ["Cell 4", "Cell 5", "Cell 6"]

  # ... more sections
```

## EXAMPLES

The system handles different types of travel documents. Here are examples:

---

### EXAMPLE A: Simple Weekend Trip (e.g., "Weekend in Paris")

**Input markdown structure:**
```markdown
# Weekend in Paris
A quick guide to exploring the City of Light in just three days.

## Why Paris is Perfect for a Weekend
Paris offers an unmatched combination of art, cuisine, and romance...

### Art & Culture
The Louvre and Musée d'Orsay house masterpieces...

### Culinary Excellence  
From Michelin-starred restaurants to charming bistros...

## Day 1: Arrival & Classic Paris
Arrive at Charles de Gaulle and head straight to your hotel...
- Walk along the Seine to Notre-Dame
- Explore Île de la Cité
- Dinner at a traditional bistro

## Day 2: Museums & Montmartre
Start early at the Louvre before the crowds arrive...

## Day 3: Markets & Departure
Your last morning in Paris...
```

**Expected YAML output (contains ALL content):**
```yaml
metadata:
  title: "Weekend in Paris"
  subtitle: "A quick guide to exploring the City of Light in just three days"
  destination: "Paris, France"
  duration: "3 days"

sections:
  - id: weekend-in-paris
    title: "Weekend in Paris"
    level: 1
    style: hero
    content: "A quick guide to exploring the City of Light in just three days."
    needs_images: true
    queries:
      - "Paris Eiffel Tower sunset Seine river"
      - "Paris rooftops aerial view golden hour"

  - id: why-paris-perfect
    title: "Why Paris is Perfect for a Weekend"
    level: 2
    style: content
    content: |
      Paris offers an unmatched combination of art, cuisine, and romance.
      In just a weekend, you can experience world-class museums, stunning
      architecture, and some of the finest food on earth.
    needs_images: true
    queries:
      - "Paris street cafe morning croissant"
    
    # Subsections become cards
    subsections:
      - id: art-culture
        title: "Art & Culture"
        style: card
        content: |
          The Louvre and Musée d'Orsay house masterpieces from centuries
          of artistic achievement. From the Mona Lisa to Monet's water
          lilies, Paris is an art lover's paradise.
        queries:
          - "Louvre Museum pyramid Paris"

      - id: culinary-excellence
        title: "Culinary Excellence"
        style: card
        content: |
          From Michelin-starred restaurants to charming bistros and corner
          bakeries, every meal in Paris is an experience. Don't miss the croissants.
        queries:
          - "Paris bistro terrace evening"

      - id: romantic-atmosphere
        title: "Romantic Atmosphere"
        style: card
        content: |
          The Seine at sunset, cobblestone streets in Le Marais, and hidden
          gardens create an atmosphere unlike anywhere else.
        queries:
          - "Seine river Paris sunset bridges"

  - id: day-1-arrival
    title: "Day 1: Arrival & Classic Paris"
    level: 2
    style: day-section
    content: "Arrive at Charles de Gaulle and head straight to your hotel in the Marais district."
    needs_images: true
    queries:
      - "Notre Dame Cathedral Paris Seine"
      - "Ile de la Cite Paris evening"
    itinerary:
      - day: 1
        title: "Arrival & Classic Paris"
        location: "Le Marais, Paris"
        activities:
          - "Walk along the Seine to Notre-Dame"
          - "Explore Île de la Cité"
          - "Dinner at a traditional bistro"
          - "Evening stroll past the Eiffel Tower"

  - id: day-2-museums
    title: "Day 2: Museums & Montmartre"
    level: 2
    style: day-section
    content: "Start early at the Louvre before the crowds arrive. Spend the morning with the masters."
    needs_images: true
    queries:
      - "Sacre Coeur Montmartre sunset Paris"
      - "Louvre interior grand gallery"
    itinerary:
      - day: 2
        title: "Museums & Montmartre"
        location: "Central Paris"
        activities:
          - "Lunch in the Tuileries Garden"
          - "Afternoon at Musée d'Orsay"
          - "Climb to Sacré-Cœur for sunset"
          - "Dinner in Montmartre"

  - id: day-3-departure
    title: "Day 3: Markets & Departure"
    level: 2
    style: day-section
    content: "Your last morning in Paris."
    needs_images: true
    queries:
      - "Marche d'Aligre Paris market morning"
      - "Paris cafe terrace coffee pastries"
    itinerary:
      - day: 3
        title: "Markets & Departure"
        location: "Paris"
        activities:
          - "Browse the Marché d'Aligre"
          - "Coffee and pastries at a local café"
          - "Last-minute shopping on Rue de Rivoli"
          - "Farewell to Paris"

  - id: conclusion
    title: "Conclusion"
    level: 2
    style: footer
    content: "A weekend in Paris is never enough, but it's a perfect start to falling in love with this incredible city."
    needs_images: false
    queries: []
```

---

### EXAMPLE B: Complex Multi-Region Trip (FICTIONAL - for demonstration only)

# NOTE: This is a made-up example showing common patterns in complex itineraries.
# It demonstrates: modules, day-by-day cycling, dietary restrictions, flight tables.
# Real documents will vary - adapt structure to match the source content.

**Input markdown structure:**
```markdown
# Tuscan Cycling & Culinary Expedition (October 2025)

## 1. Overview and Trip Philosophy
A 12-day cycling-focused journey through Tuscany and Umbria...

### 1.1 Dietary Considerations: Gluten-Free Protocol
Managing celiac requirements in Italy requires advance planning...

## 2. Travel Logistics

### 2.1 Transatlantic Flights
| Leg | Route | Aircraft | Class | Duration |
| 1 | JFK → FCO | A330-900neo | Business | 8h 30m |
| 2 | FCO → JFK | 787-9 | Business | 10h 15m |

## 3. Region 1: Chianti Wine Country

Duration: Days 1-4
Base: Greve in Chianti
Focus: Rolling hills, vineyard cycling, wine education

### 3.1 Daily Cycling Routes

**Day 2: The Classic Chianti Loop**
Route: Greve → Panzano → Radda → Castellina → Greve
Terrain: Paved roads with moderate climbing
Distance: 45 miles (72 km)
Elevation: 3,500 ft gain

**Day 3: Castello Circuit**
Route: Greve → Castello di Brolio → Gaiole → Greve
Distance: 38 miles (61 km)
```

**Expected YAML output (contains ALL content):**
```yaml
# FICTIONAL EXAMPLE - demonstrates structure for complex itineraries
metadata:
  title: "Tuscan Cycling & Culinary Expedition"
  subtitle: "October 2025"
  destination: "Tuscany, Umbria, Italy"
  duration: "12 days"

sections:
  - id: tuscan-expedition
    title: "Tuscan Cycling & Culinary Expedition"
    level: 1
    style: hero
    content: |
      A 12-day cycling-focused journey through Tuscany and Umbria,
      combining world-class road cycling with Italian culinary immersion.
    needs_images: true
    queries:
      - "Tuscany rolling hills cypress trees sunrise"
      - "Chianti vineyard cycling scenic road"

  - id: overview
    title: "Overview and Trip Philosophy"
    level: 2
    style: content
    content: |
      This expedition prioritizes quality over quantity, establishing
      base camps in two distinct regions rather than hotel-hopping.
      Each base allows for multiple day rides while returning to
      comfortable accommodations each evening.
    needs_images: true
    queries:
      - "Tuscan countryside villa cycling"

  - id: dietary-considerations
    title: "Dietary Considerations: Gluten-Free Protocol"
    level: 3
    style: highlight
    content: |
      Managing celiac requirements in Italy requires advance planning.
      While Italian cuisine is naturally gluten-heavy (pasta, bread),
      many restaurants now offer gluten-free options. Key phrases:
      "Sono celiaco" (I am celiac) and "Senza glutine" (without gluten).
      
      Risk areas: Cross-contamination in pasta water, shared fryers,
      flour-dusted surfaces. Safest options: Grilled meats, risotto
      (verify stock), polenta dishes.
    needs_images: false  # No images for dietary/medical content
    queries: []

  - id: travel-logistics
    title: "Travel Logistics"
    level: 2
    style: content
    content: |
      Flights route through Rome Fiumicino (FCO) with car rental
      for the drive to Chianti region (approximately 2.5 hours).
    needs_images: false  # No images for logistics
    queries: []

  - id: flights
    title: "Transatlantic Flights"
    level: 3
    style: table
    content: "Business class ensures arrival rested for first ride."
    needs_images: false
    queries: []
    table:
      headers: ["Leg", "Route", "Aircraft", "Class", "Duration"]
      rows:
        - ["1", "JFK → FCO", "A330-900neo", "Business", "8h 30m"]
        - ["2", "FCO → JFK", "787-9", "Business", "10h 15m"]

  - id: region-1-chianti
    title: "Region 1: Chianti Wine Country"
    level: 2
    style: gallery
    # Capture ALL metadata from source - whatever format it uses
    meta:
      duration: "Days 1-4"
      base: "Greve in Chianti"
      focus: "Rolling hills, vineyard cycling, wine education"
    content: |
      The Chianti Classico region offers iconic Tuscan cycling with
      manageable gradients and stunning vineyard panoramas. October
      brings harvest season, mild temperatures, and golden light.
    needs_images: true
    queries:
      - "Greve in Chianti town square autumn"
      - "Chianti vineyards harvest season cycling"
      - "Tuscan cypress lined road"

  - id: chianti-cycling
    title: "Daily Cycling Routes"
    level: 3
    style: cards
    content: |
      Each route departs from and returns to Greve, allowing for
      flexible start times and easy bail-out options if needed.
    needs_images: true
    itinerary:
      - day: 2
        title: "The Classic Chianti Loop"
        location: "Greve → Panzano → Radda → Castellina → Greve"
        distance: "45 miles (72 km)"
        terrain: "Paved roads with moderate climbing"
        elevation: "3,500 ft gain"
        content: |
          The quintessential Chianti ride hitting all the famous hill
          towns. Morning start recommended to reach Panzano before
          the Antica Macelleria Cecchini opens for lunch.
        highlights:
          - "Panzano butcher shop lunch"
          - "Radda medieval walls"
          - "Castellina fortress views"
        dining_note: |
          Lunch at Antica Macelleria Cecchini - famous butcher with
          communal tables. All meat dishes; naturally gluten-free.
          Reserve ahead.
        queries:
          - "Panzano in Chianti hilltop village"
          - "Radda in Chianti medieval streets"

      - day: 3
        title: "Castello Circuit"
        location: "Greve → Castello di Brolio → Gaiole → Greve"
        distance: "38 miles (61 km)"
        terrain: "Mix of paved and white gravel (strade bianche)"
        content: |
          Features the iconic Castello di Brolio, birthplace of modern
          Chianti wine. The white gravel roads require 28mm+ tires
          but reward with car-free serenity.
        highlights:
          - "Castello di Brolio wine tasting"
          - "Strade bianche gravel sections"
        queries:
          - "Castello di Brolio vineyard aerial"
          - "Strade bianche Tuscany gravel cycling"
```

---

### Quick Reference: Section Types and Image Needs

| Section Type | Style | Needs Images? | Query Style |
|--------------|-------|---------------|-------------|
| Main title | `hero` | YES | Dramatic landscape, destination overview |
| Location intro | `gallery` | YES | 3-4 scenic destination shots |
| Day activities | `day-section` | YES | 2-3 activity/location shots |
| Multiple items | `cards` | YES | 1 per card, specific to item |
| General content | `content` | MAYBE | 0-2 contextual images |
| Warnings/tips | `highlight` | NO | - |
| Dietary/medical | `highlight` | NO | - |
| Flight details | `table` | NO | - |
| Insurance/legal | `highlight` | NO | - |
| References | `footer` | NO | - |

---

## MARKDOWN TO ANALYZE:

"""


def get_analysis_prompt(md_content: str) -> str:
    """
    Generate the full analysis prompt with the markdown content appended.
    """
    return ANALYSIS_PROMPT + "\n" + md_content

