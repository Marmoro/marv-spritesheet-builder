const { ipcRenderer } = require('electron');
const { dialog } = require('@electron/remote');
const fs = require('fs');
const sharp = require('sharp');
const Spritesmith = require('spritesmith');
const os = require('os');
const path = require('path');
const { promisify } = require('util');
const rimraf = promisify(require('rimraf'));

let images = [];
let firstImageDirectory = null;

document.getElementById('fileInput').addEventListener('change', async (event) => {
  const files = Array.from(event.target.files)
    .map((file) => file.path)
    .sort(); // Sort file paths by file names

  firstImageDirectory = path.dirname(files[0]);
  const maxSize = await findMaxSize(files);

  // Display the uploaded images
  const uploadedImages = document.getElementById('uploadedImages');
  uploadedImages.innerHTML = '';
  for (const file of files) {
    const img = document.createElement('img');
    img.src = file;
    img.width = 50;
    img.height = 50;
    img.style.margin = '2px';
    uploadedImages.appendChild(img);
  }

  images = await Promise.all(
    files.map(async (file) => {
      const outputPath = path.join(os.tmpdir(), path.basename(file));
      await sharp(file)
        .resize(maxSize.width, maxSize.height, {
          background: { r: 0, g: 0, b: 0, alpha: 0 },
          kernel: sharp.kernel.nearest, // Use the nearest kernel for lossless resizing
        })
        .toFile(outputPath);
      return outputPath;
    })
  );
});

document.getElementById('generateButton').addEventListener('click', async () => {
  const exportFileName = document.getElementById('exportFileName').value;
  if (!exportFileName) {
    alert('Please enter an export file name.');
    return;
  }

  // const outputPath = path.join(path.dirname(images[0]), exportFileName + '.png');
  const outputPath = path.join(firstImageDirectory, exportFileName + '.png');

  // Show the progress of the sprite sheet creation
  const progressStatus = document.getElementById('progressStatus');
  progressStatus.textContent = 'Generating sprite sheet...';

  try {
    const result = await new Promise((resolve, reject) => {
      Spritesmith.run(
        {
          src: images,
          algorithm: 'top-down', // Set the algorithm to 'top-down' to align images in a single row
        },
        async (err, result) => {
          if (err) reject(err);
          else resolve(result);
        }
      );
    });

    fs.writeFileSync(outputPath, result.image);

    // Update the progress status
    progressStatus.textContent = 'Sprite sheet successfully generated!';
  } catch (err) {
    console.error(err);
    progressStatus.textContent = 'An error occurred while generating the sprite sheet.';
  }
});


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
