const sharp = require('sharp');
const os = require('os');
const path = require('path');
const fs = require('fs');
const Spritesmith = require('spritesmith');
const { ipcRenderer } = require('electron');
const { dialog } = require('@electron/remote');

const imagemin = require('imagemin');
const imageminPngquant = require('imagemin-pngquant');
const imageminMozjpeg = require('imagemin-mozjpeg');
