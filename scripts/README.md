# Convert HTML Slides to PowerPoint

## Method 1: Automated Script (Recommended)

This script uses Puppeteer to screenshot each slide and PptxGenJS to create the PowerPoint.

### Steps:

1. **Install dependencies:**
   ```bash
   cd scripts
   npm install
   ```

2. **Start your Next.js development server:**
   ```bash
   cd ../temporal-client
   npm run dev
   ```

3. **Run the conversion script (in a new terminal):**
   ```bash
   cd scripts
   node slides-to-ppt.js
   ```

4. **Output:** `presentation.pptx` will be created in the project root

### What it does:
- Launches headless browser
- Navigates through all 16 slides
- Takes high-resolution screenshots (1920x1080 @ 2x DPI)
- Generates PowerPoint with each slide as an image
- Cleans up temporary files

---

## Method 2: Python Alternative (using python-pptx)

If you prefer Python (as noted in CLAUDE.md that you use `uv`):

### Install:
```bash
uv pip install python-pptx Pillow playwright
playwright install chromium
```

### Script:
Create `scripts/slides_to_ppt.py`:

```python
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches
import os

SLIDE_URL = 'http://localhost:3000/slide'
TOTAL_SLIDES = 16
OUTPUT_FILE = 'presentation.pptx'

def capture_slides():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto(SLIDE_URL)

        screenshots = []
        for i in range(TOTAL_SLIDES):
            print(f'Capturing slide {i+1}/{TOTAL_SLIDES}...')
            page.wait_for_selector('.slide-content')
            page.wait_for_timeout(1000)

            screenshot_path = f'temp_slide_{i+1}.png'
            page.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)

            if i < TOTAL_SLIDES - 1:
                page.keyboard.press('ArrowRight')
                page.wait_for_timeout(500)

        browser.close()
        return screenshots

def create_powerpoint(screenshots):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)  # 16:9 ratio

    for screenshot in screenshots:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        slide.shapes.add_picture(screenshot, 0, 0,
                                width=prs.slide_width,
                                height=prs.slide_height)

    prs.save(OUTPUT_FILE)

    # Cleanup
    for screenshot in screenshots:
        os.remove(screenshot)

    print(f'✓ PowerPoint created: {OUTPUT_FILE}')

if __name__ == '__main__':
    screenshots = capture_slides()
    create_powerpoint(screenshots)
```

### Run:
```bash
uv run python scripts/slides_to_ppt.py
```

---

## Method 3: Manual Browser Export

If you want manual control:

1. **Open the presentation:**
   ```bash
   npm run dev
   # Navigate to http://localhost:3000/slide
   ```

2. **Use browser Print to PDF:**
   - Press `Ctrl+P` (or `Cmd+P` on Mac)
   - Select "Save as PDF"
   - Set margins to "None"
   - Save as `slides.pdf`

3. **Convert PDF to PowerPoint:**
   - Use Adobe Acrobat (File → Export To → Microsoft PowerPoint)
   - Or online converter: https://www.adobe.com/acrobat/online/pdf-to-ppt.html
   - Or LibreOffice: Open PDF → Export as PPTX

---

## Method 4: Use Reveal.js Export (Recommended for Best Quality)

If you're willing to convert your slides to Reveal.js format:

1. Install reveal.js export plugin
2. Export slides with speaker notes and transitions
3. Convert to PDF with `decktape`
4. Convert PDF to PPT

---

## Troubleshooting

### Port is already in use
Make sure Next.js is running on port 3000, or update the URL in the script.

### Screenshots look blurry
Increase `deviceScaleFactor` in the script (currently set to 2).

### Some slides are cut off
Adjust viewport dimensions or use `fullPage: true` in screenshot options.

### Script hangs
Increase timeout values in `waitForSelector` and `waitForTimeout`.

---

## Output Customization

### Adjust Slide Size
Edit the script to change resolution:
```javascript
await page.setViewport({
  width: 1920,  // Change width
  height: 1080, // Change height
  deviceScaleFactor: 2  // Higher = better quality, larger file
});
```

### Add Transitions
Modify the PptxGenJS code to add slide transitions:
```javascript
const slide = pptx.addSlide();
slide.transition = { type: 'fade', duration: 0.5 };
```

### Preserve Text (Advanced)
For editable text, you'd need to parse the HTML and recreate the layout using PptxGenJS primitives (text boxes, shapes, etc.) instead of screenshots. This is complex but possible.
