
.\run-advanced-sprite-sheet.bat C:\tmp\mc1
.\run-advanced-sprite-sheet.bat C:\tmp\mc2
.\run-advanced-sprite-sheet.bat C:\tmp\mc3
.\run-advanced-sprite-sheet.bat C:\tmp\mc4
.\run-advanced-sprite-sheet.bat C:\tmp\mc5
.\run-advanced-sprite-sheet.bat C:\tmp\mc6
.\run-advanced-sprite-sheet.bat C:\tmp\weapon_animations

.\resize_by_percentage.ps1 -directory "C:\tmp\mc1\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\mc2\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\mc3\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\mc4\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\mc5\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\mc6\pack" -percentage 50 -quality -1
.\resize_by_percentage.ps1 -directory "C:\tmp\weapon_animations\pack" -percentage 50 -quality -1