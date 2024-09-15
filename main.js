
const path = require('path');
const { app, BrowserWindow, dialog } = require('electron');
const { initialize, enable } = require('@electron/remote/main');

// Import your existing utility functions
const { generateSpriteSheets } = require('./spritesmith');
const { findMaxSize, prepareImages } = require('./utilities');

let mainWindow;

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
    app.exit(1);
  }
}

function parseArguments() {
  const args = process.argv.slice(2);
  const inputArg = args.find(arg => arg.startsWith('--input='));
  const outputArg = args.find(arg => arg.startsWith('--output='));

  if (inputArg && outputArg) {
    const inputFiles = inputArg.split('=')[1].split(',');
    const outputFile = outputArg.split('=')[1];
    return { inputFiles, outputFile };
  }
  
  return null;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 700,
    height: 800,
    minWidth: 700,
    minHeight: 800,
    maxWidth: 700,
    maxHeight: 800,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
      enableRemoteModule: true,
    },
  });

  enable(mainWindow.webContents);

  initialize();
  mainWindow.loadFile('index.html');
  
  mainWindow.setMenuBarVisibility(false);
}

function startApp() {
  const cliArgs = parseArguments();
  if (cliArgs) {
    processSpriteSheet(cliArgs.inputFiles, cliArgs.outputFile).then(() => {
      app.quit();
    });
  } else {
    createWindow();
  }
}

app.whenReady().then(startApp);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});