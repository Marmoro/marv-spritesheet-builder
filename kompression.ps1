# Define parameters
param (
    [string]$sourceDir = "",  # Source directory where PNG files are located
    [int]$quality = 80 # PNG compression quality (0-100, lower = smaller file size)
)

# Ensure source directory is provided
if (-not $sourceDir) {
    Write-Host "Please provide a source directory."
    exit 1
}

# Set pngquant path (assumes it's in the same directory as the script)
$pngquantPath = "$PSScriptRoot\pngquant.exe"
if (-not (Test-Path $pngquantPath)) {
    Write-Host "pngquant.exe not found in the script directory. Please place it in the same folder as this script."
    exit 1
}

# Get PNG files matching _normal.png or _specular.png
# $files = Get-ChildItem -Path $sourceDir -Filter "*_n.png" -File
# $files += Get-ChildItem -Path $sourceDir -Filter "*_s.png" -File
$files += Get-ChildItem -Path $sourceDir -File

# Process each file
foreach ($file in $files) {
    $inputPath = $file.FullName
    
    Write-Host "Compressing: $inputPath"
    
    # Run pngquant to compress PNG and overwrite the original file
    & "$pngquantPath" --quality=$quality --speed 1 --force --output "$inputPath" -- "$inputPath"
    
    # Check file size
    $fileSize = (Get-Item "$inputPath").Length / 1KB  # Convert to KB
    
    if ($fileSize -gt 170) {
        Write-Host "Warning: $inputPath exceeds 170 KB ($([math]::Round($fileSize, 2)) KB)"
    }
}

Write-Host "Compression complete."
