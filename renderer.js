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

document.getElementById('fileInput').addEventListener('change', async (event) => {
  const files = Array.from(event.target.files).map((file) => file.path);

  const maxSize = await findMaxSize(files);

  images = await Promise.all(
    files.map(async (file) => {
      const outputPath = path.join(os.tmpdir(), path.basename(file));
      await sharp(file)
        .resize(maxSize.width, maxSize.height, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .toFile(outputPath);
      return outputPath;
    })
  );
});

document.getElementById('generateButton').addEventListener('click', async () => {
  const outputPath = dialog.showSaveDialogSync({ filters: [{ name: 'Images', extensions: ['png'] }] });

  if (!outputPath) return;

  Spritesmith.run(
    {
      src: images,
      padding: 5,
    },
    async (err, result) => {
      if (err) throw err;
      fs.writeFileSync(outputPath, result.image);

      // Remove temporary resized image files
      await Promise.all(images.map((file) => rimraf(file)));
    }
  );
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
