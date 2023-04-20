const { generateSpriteSheets } = require('./spritesmith');

let images = [];
let firstImageDirectory = null;

document.getElementById('fileInput').addEventListener('change', async (event) => {
  const files = Array.from(event.target.files)
    .map((file) => file.path)
    .sort();

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

  images = await prepareImages(files, maxSize);
});

document.getElementById('generateButton').addEventListener('click', async () => {
  const exportFileName = document.getElementById('exportFileName').value;
  if (!exportFileName) {
    alert('Please enter an export file name.');
    return;
  }

  const outputPath = path.join(firstImageDirectory, exportFileName + '.png');
  const progressStatus = document.getElementById('progressStatus');

  await generateSpriteSheets(images, outputPath, progressStatus);
});
