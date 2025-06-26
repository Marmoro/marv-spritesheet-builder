
# use blender and run the script. set resolution of the render to 1024x1024
use player_main_character_BK1.blend

# resize sprites to 512x512
python.exe .\resize.py C:\tmp\mc1_preprocess

# generate normal maps
.\normal-map-gen.bat "C:\tmp\mc1_preprocess" 2.0 2 100 0

.\normal-map-gen.bat "C:\tmp\mc1_preprocess" 0.4 0 0 1 1.2 scharr 1 1.0 100 1.5 1 3.1 0.1 0.1
.\normal-map-gen.bat "C:\tmp\mc1_preprocess\affinitied" 0.4 0 0 1 1.2 scharr 1 1.0 100 1.5 1 3.1 0.1 0.1
.\normal-map-gen.bat "C:\tmp\mc1_preprocess\affinitied" 0.4 0 0 1 1.2 scharr 1 1.0 10 1.5 1 3.1 0.1 0.1

# finally pack everything into distinct spritesheet
.\run-advanced-sprite-sheet.bat C:\tmp\mc1_preprocess
.\run-advanced-sprite-sheet.bat C:\tmp\mc1_preprocess\affinitied

## fix
.\rename_files.bat C:\tmp\mc1_preprocess\2k_resized_to_1k\maps



############################


## New Workflow: No Python scripts

## using resize

# Just resize to 512px max dimension
.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess\2k_bk" -maxSize 512
.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess\2k_resized_to_1k" -maxSize 1024


.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess" -maxSize 1024


# Just compress with quality 80
.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess" -quality 50

# Both resize and compress
.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess" -maxSize 512 -quality 80

# Resize to 256px without keeping aspect ratio
.\kompression-to-512.ps1 -directory "C:\tmp\mc1_preprocess" -maxSize 256 -maintainAspectRatio:$false


## pack things