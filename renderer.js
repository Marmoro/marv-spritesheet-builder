const { generateSpriteSheets } = require('./spritesmith');

const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');

let images = [];
let firstImageDirectory = null;

dropZone.addEventListener('click', () => {
  fileInput.click();
});

dropZone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (event) => {
  event.preventDefault();
  dropZone.classList.remove('dragover');
  const files = Array.from(event.dataTransfer.files);

  // Set the files to the file input
  const dataTransfer = new DataTransfer();
  files.forEach((file) => dataTransfer.items.add(file));
  fileInput.files = dataTransfer.files;

  handleFileInputChange(files);
});

fileInput.addEventListener('change', (event) => {
  const files = Array.from(event.target.files);
  handleFileInputChange(files);
});

// Wrap the existing file input handling logic in a new function
async function handleFileInputChange(files) {
  const filePaths = files
    .map((file) => file.path)
    .sort();

  firstImageDirectory = path.dirname(filePaths[0]);
  const maxSize = await findMaxSize(filePaths);

  // Display the uploaded images
  const uploadedImages = document.getElementById('uploadedImages');
  uploadedImages.innerHTML = '';
  for (const file of filePaths) {
    const img = document.createElement('img');
    img.src = file;
    img.width = 50;
    img.height = 50;
    img.style.margin = '2px';
    uploadedImages.appendChild(img);
  }

  images = await prepareImages(filePaths, maxSize);
}

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
