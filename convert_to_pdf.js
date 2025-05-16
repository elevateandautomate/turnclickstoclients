// This script uses puppeteer to convert HTML to PDF
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function convertHTMLToPDF(htmlFilePath, pdfFilePath) {
  console.log(`Converting ${htmlFilePath} to ${pdfFilePath}...`);

  try {
    // Launch a headless browser
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    // Create a new page
    const page = await browser.newPage();

    // Get the absolute path to the HTML file
    const absolutePath = path.resolve(htmlFilePath);

    // Load the HTML file
    await page.goto(`file://${absolutePath}`, {
      waitUntil: 'networkidle0'
    });

    // Set PDF options
    const pdfOptions = {
      path: pdfFilePath,
      format: 'Letter',
      printBackground: true,
      margin: {
        top: '0.4in',
        right: '0.4in',
        bottom: '0.4in',
        left: '0.4in'
      }
    };

    // Generate PDF
    await page.pdf(pdfOptions);

    // Close the browser
    await browser.close();

    console.log(`Successfully converted ${htmlFilePath} to ${pdfFilePath}`);
    return true;
  } catch (error) {
    console.error('Error converting HTML to PDF:', error);
    return false;
  }
}

// Convert the resume HTML to PDF
const htmlFilePath = 'aaron_price_cover_letter_revised.html';
const pdfFilePath = 'Aaron_Price_Cover_Letter_Final.pdf';

convertHTMLToPDF(htmlFilePath, pdfFilePath)
  .then(success => {
    if (success) {
      console.log('Conversion completed successfully!');
    } else {
      console.error('Conversion failed.');
    }
  })
  .catch(error => {
    console.error('Error in conversion process:', error);
  });
