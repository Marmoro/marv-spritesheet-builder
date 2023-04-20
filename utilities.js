

async function findMaxSize(files) {
  let maxWidth = 0;
  let maxHeight = 0;

  for (const file of files) {
    const { width, height } = await sharp(file).metadata();
    maxWidth = Math.max(maxWidth, width);
    maxHeight = Math.max(maxHeight, height);
  }

  return { width: maxWidth, height: maxHeight };
}

async function prepareImages(files, maxSize) {
  return await Promise.all(
    files.map(async (file) => {
      const outputPath = path.join(os.tmpdir(), path.basename(file));
      await sharp(file)
        .resize(maxSize.width, maxSize.height, {
          background: { r: 0, g: 0, b: 0, alpha: 0 },
          kernel: sharp.kernel.nearest,
        })
        .toFile(outputPath);
      return outputPath;
    })
  );
}

module.exports = {
  findMaxSize,
  prepareImages,
};
