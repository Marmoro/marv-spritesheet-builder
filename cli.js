const { generateSpriteSheets } = require('./spritesmith');
const { findMaxSize, prepareImages } = require('./utilities');
const path = require('path');
const fs = require('fs');

function handleCliArgs() {
  const args = process.argv.slice(2);
  const inputArg = args.find(arg => arg.startsWith('--input='));
  const outputArg = args.find(arg => arg.startsWith('--output='));

  if (inputArg && outputArg) {
    const inputFiles = inputArg.split('=')[1].split(',');
    const outputFile = outputArg.split('=')[1];
    
    processSpriteSheet(inputFiles, outputFile);
    return true;
  }
  
  return false;
}

async function processSpriteSheet(inputFiles, outputFile) {
  try {
    const maxSize = await findMaxSize(inputFiles);
    const preparedImages = await prepareImages(inputFiles, maxSize);
    
    const outputPath = path.resolve(outputFile);
    await generateSpriteSheets(preparedImages, outputPath, {
      textContent: (text) => console.log(text)
    });
    
    console.log('Sprite sheet generated successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Error generating sprite sheet:', error);
    process.exit(1);
  }
}

module.exports = { handleCliArgs }; 