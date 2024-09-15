const sharp = require('sharp');
const os = require('os');
const path = require('path');
const fs = require('fs');
const Spritesmith = require('spritesmith');
const imagemin = require('imagemin');
const imageminPngquant = require('imagemin-pngquant');

// Import your existing utility functions
const { generateSpriteSheets } = require('./spritesmith');
const { findMaxSize, prepareImages } = require('./utilities');

async function processSpriteSheet(inputFiles, outputFile) {
  try {
    const maxSize = await findMaxSize(inputFiles);
    const preparedImages = await prepareImages(inputFiles, maxSize);
    
    const outputPath = path.resolve(outputFile);
    await generateSpriteSheets(preparedImages, outputPath, {
      textContent: (text) => console.log(text)
    });
    
    console.log('Sprite sheet generated successfully!');
  } catch (error) {
    console.error('Error generating sprite sheet:', error);
    process.exit(1);
  }
}

function parseArguments() {
  const args = process.argv.slice(2);
  const inputArg = args.find(arg => arg.startsWith('--input='));
  const outputArg = args.find(arg => arg.startsWith('--output='));

  if (!inputArg || !outputArg) {
    console.error('Usage: node cli-main.js --input=file1.png,file2.png,file3.png --output=output.png');
    process.exit(1);
  }

  const inputFiles = inputArg.split('=')[1].split(',');
  const outputFile = outputArg.split('=')[1];

  return { inputFiles, outputFile };
}

async function main() {
  const { inputFiles, outputFile } = parseArguments();
  await processSpriteSheet(inputFiles, outputFile);
  process.exit(0);
}

main();