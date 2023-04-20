

function chunkArray(arr, chunkSize) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    chunks.push(arr.slice(i, i + chunkSize));
  }
  return chunks;
}

async function generateSpriteSheet(images, algorithm) {
  return new Promise((resolve, reject) => {
    Spritesmith.run({ src: images, algorithm }, (err, result) => {
      if (err) {
        reject(err);
      } else {
        resolve(result.image);
      }
    });
  });
}

async function generateSpriteSheets(images, outputPath, progressStatus) {
  progressStatus.textContent = 'Generating sprite sheets...';

  try {
    const imageChunks = chunkArray(images, 8);
    const intermediateSpriteSheets = await Promise.all(
      imageChunks.map((chunk) => generateSpriteSheet(chunk, 'left-right'))
    );

    const intermediateFiles = await Promise.all(
      intermediateSpriteSheets.map(async (spriteSheet, index) => {
        const tempFilePath = path.join(os.tmpdir(), `intermediate_${index}.png`);
        await fs.promises.writeFile(tempFilePath, spriteSheet);
        return tempFilePath;
      })
    );

    progressStatus.textContent = 'Combining sprite sheets...';
    const finalSpriteSheet = await generateSpriteSheet(intermediateFiles, 'top-down');
    const optimizedSpriteSheet = await optimizeImage(finalSpriteSheet); // Add this line

    await fs.promises.writeFile(outputPath, optimizedSpriteSheet);

    await Promise.all(intermediateFiles.map((filePath) => fs.promises.unlink(filePath)));

    progressStatus.textContent = 'Sprite sheet successfully generated!';
  } catch (err) {
    console.error(err);
    progressStatus.textContent = 'An error occurred while generating the sprite sheet.';
  }
}

async function optimizeImage(inputBuffer) {
  return await imagemin.buffer(inputBuffer, {
    plugins: [
      imageminPngquant({ quality: [0.8, 0.9] }),
    ],
  });
}

module.exports = {
  generateSpriteSheets,
};
