/**
 * Convert HTML slides to PowerPoint
 *
 * Usage:
 * 1. Start your Next.js dev server: npm run dev
 * 2. Run: node scripts/slides-to-ppt.js
 *
 * Requirements:
 * npm install puppeteer pptxgenjs
 */

const puppeteer = require('puppeteer');
const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const SLIDE_URL = 'http://localhost:3000/slide';
const TOTAL_SLIDES = 15;
const OUTPUT_FILE = 'presentation.pptx';
const TEMP_DIR = path.join(__dirname, 'temp_screenshots');

// Helper function for delays
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function captureSlides() {
  console.log('Starting browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // Set viewport to standard presentation size (16:9)
  await page.setViewport({
    width: 1920,
    height: 1080,
    deviceScaleFactor: 2  // High DPI for better quality
  });

  console.log(`Navigating to ${SLIDE_URL}...`);
  await page.goto(SLIDE_URL, { waitUntil: 'networkidle0' });

  // Create temp directory for screenshots
  if (!fs.existsSync(TEMP_DIR)) {
    fs.mkdirSync(TEMP_DIR, { recursive: true });
  }

  const screenshotPaths = [];

  // Capture each slide
  for (let i = 0; i < TOTAL_SLIDES; i++) {
    console.log(`Capturing slide ${i + 1}/${TOTAL_SLIDES}...`);

    // Wait for slide content to load
    await page.waitForSelector('.slide-content', { timeout: 5000 });
    await delay(1000); // Additional wait for animations

    // Take screenshot of the slide area
    const screenshotPath = path.join(TEMP_DIR, `slide-${i + 1}.png`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: false
    });
    screenshotPaths.push(screenshotPath);

    // Navigate to next slide if not the last one
    if (i < TOTAL_SLIDES - 1) {
      await page.keyboard.press('ArrowRight');
      await delay(500); // Wait for transition
    }
  }

  await browser.close();
  console.log('Screenshots captured!');

  return screenshotPaths;
}

async function createPowerPoint(screenshotPaths) {
  console.log('Creating PowerPoint presentation...');

  const pptx = new PptxGenJS();

  // Set presentation properties
  pptx.author = 'RWTH Aachen University - Chair of Databases and Information Systems (i5)';
  pptx.title = 'Building Reliable AI Research Assistants: A Durable Execution Approach';
  pptx.subject = 'Orchestrating Multi-Agent Systems for Academic Literature Review';

  // Add each screenshot as a slide
  screenshotPaths.forEach((imagePath, index) => {
    console.log(`Adding slide ${index + 1}/${screenshotPaths.length} to PPT...`);

    const slide = pptx.addSlide();

    // Add image to fill the entire slide
    slide.addImage({
      path: imagePath,
      x: 0,
      y: 0,
      w: '100%',
      h: '100%'
    });
  });

  // Save the presentation
  const outputPath = path.join(__dirname, '..', OUTPUT_FILE);
  await pptx.writeFile({ fileName: outputPath });

  console.log(`✓ PowerPoint created: ${outputPath}`);
}

async function cleanup() {
  console.log('Cleaning up temporary files...');
  if (fs.existsSync(TEMP_DIR)) {
    fs.rmSync(TEMP_DIR, { recursive: true, force: true });
  }
  console.log('✓ Cleanup complete');
}

async function main() {
  try {
    console.log('=== HTML Slides to PowerPoint Converter ===\n');

    const screenshotPaths = await captureSlides();
    await createPowerPoint(screenshotPaths);
    await cleanup();

    console.log('\n✓ Conversion complete!');
    console.log(`\nYour PowerPoint presentation is ready: ${OUTPUT_FILE}`);
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
