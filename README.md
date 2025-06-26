# Marv Spritesheet Builder
I built this middleware, co-founded with GPT4, to build spritesheets for Unity. I used many different free spritesheet builders but I couldn't find one that suits my needs.


## generate normal maps using NMO (Web Browser)


## compress maps

.\kompression.ps1 -sourceDir C:\tmp\mc1_preprocess\ -quality 80

.\kompression.ps1 -sourceDir C:\tmp\mc1_preprocess\ -quality 80

.\kompression.ps1 -sourceDir C:\tmp\mc1_preprocess\ -quality 90

.\kompression.ps1 -sourceDir C:\tmp\mc1_preprocess\ -quality 30



.\kompression.ps1 -sourceDir C:\tmp\mc1_preprocess\2k_resized_to_1k\packed -quality 80

## RENAME IN CASE _n or _s is found at the end

# the steps I used last:
- run blender
- make copy
- batch uplaod to NMO
- copy from DOwnloads to mc1
- run rename_files
- run sprite packer
- compress if needed
- upload to godot


# if using maps on indivuidaul imaes
.\rename_files.ps1 C:\tmp\mc1

.\run-advanced-sprite-sheet.bat C:\tmp\mc2
<!-- .\advanced-automate-sprite-sheet-batch.ps1 -InputDirectory "C:\tmp\mc1" -->
.\kompression.ps1 -sourceDir C:\tmp\mc1\pack -quality 75
### Texture Specification

Blender


# TOTAL IMAGE SIZE = 576