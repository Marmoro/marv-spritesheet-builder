# Define parameters
param (
    [Parameter(ParameterSetName='ByDirectory', Mandatory=$true)]
    [string]$directory,                 # Directory containing images to process
    [Parameter(ParameterSetName='ByFile', Mandatory=$true)]
    [string]$filePath,                  # Single image file to process
    [Parameter(Mandatory=$true)]
    [int]$percentage,                  # Percentage to resize images
    [switch]$createBackups = $false,    # Whether to create backup files
    [string]$outputDir = "",            # Output directory (if not specified, originals will be replaced)
    [int]$quality = -1,                 # PNG compression quality (0-100, -1 to skip compression)
    [switch]$maintainAspectRatio = $true # Whether to maintain aspect ratio when resizing
)

# Set pngquant path (assumes it's in the same directory as the script)
$pngquantPath = "$PSScriptRoot\pngquant.exe"
if (($quality -ge 0) -and (-not (Test-Path $pngquantPath))) {
    Write-Host "pngquant.exe not found in the script directory. Please place it in the same folder as this script."
    exit 1
}

# Check if at least one operation is selected
if (($quality -lt 0) -and ($percentage -eq 0)) {
    Write-Host "No operations specified. Please specify either quality, percentage, or both."
    Write-Host "Use -quality [0-100] to enable compression (or -1 to skip)"
    Write-Host "Use -percentage [1-100] to enable resizing (or 0 to skip)"
    exit 1
}

# Create output directory if specified and doesn't exist
if ($outputDir -and (-not (Test-Path $outputDir))) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
    Write-Host "Created output directory: $outputDir"
}

# Load System.Drawing assembly for image processing if resizing is enabled
if ($percentage -gt 0) {
    Add-Type -AssemblyName System.Drawing
}

# Find all PNG files in the directory
# Find all PNG files
$imageFiles = @()
if ($PSCmdlet.ParameterSetName -eq 'ByFile') {
    $imageFiles += Get-Item -Path $filePath -ErrorAction Stop
} else { # ByDirectory
    $imageFiles = Get-ChildItem -Path $directory -Filter "*.png" -File
}

if ($imageFiles.Count -eq 0) {
    Write-Host "No PNG files found in $directory"
    exit 0
}

Write-Host "Found $($imageFiles.Count) PNG files to process"
Write-Host "Operations: $(if ($percentage -gt 0) { "Resize to ${percentage}%" } else { "No resize" })$(if ($quality -ge 0) { " | Compress to quality $quality" } else { " | No compression" })"

# Process each file
foreach ($file in $imageFiles) {
    $inputPath = $file.FullName
    
    # Determine output path
    if ($outputDir) {
        $outputPath = Join-Path $outputDir $file.Name
    } else {
        $outputPath = $inputPath
    }
    
    # Create backup if needed
    if ($createBackups) {
        $backupPath = "$inputPath.backup"
        if (-not (Test-Path $backupPath)) {
            Copy-Item -Path $inputPath -Destination $backupPath
            Write-Host "Created backup: $backupPath"
        }
    }
    
    # Calculate original file size
    $originalSize = (Get-Item $inputPath).Length / 1KB
    
    # Create temporary file paths
    $tempResizePath = "$inputPath.resize.png"
    $tempCompressPath = "$inputPath.temp"
    
    Write-Host "Processing: $($file.Name)"
    $currentPath = $inputPath
    
    # Step 1: Resize the image if enabled
    if ($percentage -gt 0) {
        try {
            # Load the image
            $image = [System.Drawing.Image]::FromFile($inputPath)
            
            $width = $image.Width
            $height = $image.Height
            
            # Calculate new dimensions based on percentage
            $newWidth = [int]($width * ($percentage / 100))
            $newHeight = [int]($height * ($percentage / 100))
            
            # Check if resizing is needed
            if ($newWidth -gt 0 -and $newHeight -gt 0) {
                # Create resized bitmap
                $resizedImage = New-Object System.Drawing.Bitmap($newWidth, $newHeight)
                $graphics = [System.Drawing.Graphics]::FromImage($resizedImage)
                $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $graphics.DrawImage($image, 0, 0, $newWidth, $newHeight)
                
                # Save resized image to temporary file
                $resizedImage.Save($tempResizePath, [System.Drawing.Imaging.ImageFormat]::Png)
                
                # Clean up
                $graphics.Dispose()
                $resizedImage.Dispose()
                $image.Dispose()
                
                $currentPath = $tempResizePath
                Write-Host "  Resized from ${width}x${height} to ${newWidth}x${newHeight}"
            } else {
                $image.Dispose()
                Write-Host "  Image already smaller than ${percentage}%, skipping resize"
            }
        }
        catch {
            Write-Host "  Error resizing image: $_" -ForegroundColor Red
            if ($null -ne $image) { $image.Dispose() }
            # Continue with original path if resize fails
        }
    }
    
    # Step 2: Compress the image if enabled
    if ($quality -ge 0) {
        Write-Host "  Compressing with quality: $quality"
        
        $finalPath = if (($currentPath -eq $inputPath) -and (-not $outputDir) -and (-not $createBackups)) {
            # Need to use temp file for in-place replacement
            $tempCompressPath 
        } else { 
            # Can output directly
            $outputPath 
        }
        
        # Process with pngquant
        & "$pngquantPath" --quality=0-$quality --speed 1 --force --output "$finalPath" -- "$currentPath"
        
        # Handle final file move if needed
        if ($finalPath -eq $tempCompressPath -and (Test-Path $tempCompressPath)) {
            Move-Item -Path $tempCompressPath -Destination $outputPath -Force
        }
        
        # Update current path for final reporting
        $currentPath = $outputPath
    } elseif ($currentPath -ne $outputPath) {
        # If we resized but didn't compress, and output is different, we need to move the file
        Copy-Item -Path $currentPath -Destination $outputPath -Force
        $currentPath = $outputPath
    }
    
    # Clean up temporary resize file if it exists
    if (Test-Path $tempResizePath) {
        Remove-Item $tempResizePath -Force
    }
    
    # Calculate new file size and reduction if the file was successfully processed
    if (Test-Path $currentPath) {
        $newSize = (Get-Item $currentPath).Length / 1KB
        $reduction = (1 - ($newSize / $originalSize)) * 100
        
        Write-Host "  Completed: $($file.Name)"
        Write-Host "  Size reduction: $($originalSize.ToString("F2"))KB → $($newSize.ToString("F2"))KB ($($reduction.ToString("F1"))%)"
    } else {
        Write-Host "  Error processing $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "Processing complete."
