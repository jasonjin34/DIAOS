/**
 * Convert HTML slides to PDF
 *
 * Usage:
 * 1. Start your Next.js dev server: npm run dev
 * 2. Run: node scripts/slides-to-pdf.js
 *
 * Requirements:
 * npm install puppeteer (already installed)
 */

const puppeteer = require('puppeteer');
const path = require('path');

const SLIDE_URL = 'http://localhost:3000/slide';
const TOTAL_SLIDES = 16;
const OUTPUT_FILE = 'presentation.pdf';

// Helper function for delays
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function captureSlidesToPDF() {
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
    deviceScaleFactor: 1
  });

  console.log(`Navigating to ${SLIDE_URL}...`);
  await page.goto(SLIDE_URL, { waitUntil: 'networkidle0' });

  // Wait for first slide to load
  await page.waitForSelector('.slide-content', { timeout: 5000 });
  await delay(1000);

  const outputPath = path.join(__dirname, '..', OUTPUT_FILE);

  console.log('Generating PDF...');

  // Generate PDF of the entire page with print media emulation
  await page.emulateMediaType('screen');

  // Method 1: Capture current view and iterate
  const pages = [];

  for (let i = 0; i < TOTAL_SLIDES; i++) {
    console.log(`Capturing slide ${i + 1}/${TOTAL_SLIDES}...`);

    await page.waitForSelector('.slide-content', { timeout: 5000 });
    await delay(1000);

    // Navigate to next slide if not the last one
    if (i < TOTAL_SLIDES - 1) {
      await page.keyboard.press('ArrowRight');
      await delay(500);
    }
  }

  // Reset to first slide
  await page.goto(SLIDE_URL, { waitUntil: 'networkidle0' });
  await delay(1000);

  // Use Puppeteer's built-in PDF generation
  // This will print the current page view
  console.log('Creating PDF file...');

  // Option: Use print to PDF with custom settings
  await page.pdf({
    path: outputPath,
    width: '1920px',
    height: '1080px',
    printBackground: true,
    preferCSSPageSize: false,
    pageRanges: '1',
    displayHeaderFooter: false,
    margin: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    }
  });

  await browser.close();

  console.log(`✓ PDF created: ${outputPath}`);
}

async function captureAllSlidesAsPDF() {
  console.log('Starting browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const outputPath = path.join(__dirname, '..', OUTPUT_FILE);

  // Create a temporary HTML file with all slides
  const pages = [];

  for (let i = 0; i < TOTAL_SLIDES; i++) {
    const page = await browser.newPage();

    await page.setViewport({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2
    });

    console.log(`Loading slide ${i + 1}/${TOTAL_SLIDES}...`);
    await page.goto(SLIDE_URL, { waitUntil: 'networkidle0' });

    // Navigate to the correct slide
    for (let j = 0; j < i; j++) {
      await page.keyboard.press('ArrowRight');
      await delay(100);
    }

    await delay(1000);

    // Get the PDF buffer for this slide
    const pdfBuffer = await page.pdf({
      width: '1920px',
      height: '1080px',
      printBackground: true,
      displayHeaderFooter: false,
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });

    pages.push(pdfBuffer);
    await page.close();
  }

  await browser.close();

  // For now, just save the first page
  // To merge PDFs, we'd need pdf-lib
  console.log('Note: Individual PDF generation complete.');
  console.log('To merge into single PDF, we need to install pdf-lib');

  return outputPath;
}

async function captureWithScreenshots() {
  console.log('=== HTML Slides to PDF Converter ===\n');
  console.log('Starting browser...');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // Set to standard presentation size
  await page.setViewport({
    width: 1920,
    height: 1080,
    deviceScaleFactor: 2  // High quality
  });

  console.log(`Navigating to ${SLIDE_URL}...`);
  await page.goto(SLIDE_URL, { waitUntil: 'networkidle0' });

  const fs = require('fs');
  const tempDir = path.join(__dirname, 'temp_pdf_images');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  const screenshots = [];

  // Capture each slide as image
  for (let i = 0; i < TOTAL_SLIDES; i++) {
    console.log(`Capturing slide ${i + 1}/${TOTAL_SLIDES}...`);

    await page.waitForSelector('.slide-content', { timeout: 5000 });
    await delay(1000);

    const screenshotPath = path.join(tempDir, `slide-${i + 1}.png`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: false
    });
    screenshots.push(screenshotPath);

    if (i < TOTAL_SLIDES - 1) {
      await page.keyboard.press('ArrowRight');
      await delay(500);
    }
  }

  await browser.close();
  console.log('Screenshots captured!');

  // Now convert images to PDF using pdf-lib
  const PDFDocument = require('pdf-lib').PDFDocument;
  const pdfDoc = await PDFDocument.create();

  for (let i = 0; i < screenshots.length; i++) {
    console.log(`Adding slide ${i + 1}/${screenshots.length} to PDF...`);

    const imageBytes = fs.readFileSync(screenshots[i]);
    const image = await pdfDoc.embedPng(imageBytes);

    const page = pdfDoc.addPage([1920, 1080]);
    page.drawImage(image, {
      x: 0,
      y: 0,
      width: 1920,
      height: 1080
    });
  }

  const outputPath = path.join(__dirname, '..', OUTPUT_FILE);
  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(outputPath, pdfBytes);

  console.log(`✓ PDF created: ${outputPath}`);

  // Cleanup
  console.log('Cleaning up temporary files...');
  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log('✓ Cleanup complete');

  return outputPath;
}

async function main() {
  try {
    await captureWithScreenshots();
    console.log('\n✓ Conversion complete!');
    console.log(`\nYour PDF presentation is ready: ${OUTPUT_FILE}`);
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
