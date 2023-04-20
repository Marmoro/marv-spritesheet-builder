const { app, BrowserWindow } = require('electron');
const { initialize } = require('@electron/remote/main');
const { enable } = require('@electron/remote/main');



function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 700,
    height: 800,
    minWidth: 700,
    minHeight: 800,
    maxWidth: 700,
    maxHeight: 800,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
    },
  });

  enable(mainWindow.webContents);

  initialize();
  mainWindow.loadFile('index.html');
  
  // Hide the menu bar
  mainWindow.setMenuBarVisibility(false);
}

app.whenReady().then(createWindow);

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

