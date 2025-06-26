param (
    [Parameter(Mandatory=$true)]
    [string]$InputDirectory
)

# Get all PNG files in the specified directory
# Include both files ending with _digits.png and _n.png
$pngFiles = Get-ChildItem -Path $InputDirectory -Filter *.png | 
    Where-Object { $_.Name -match '_\d+\.png$' -or $_.Name -match '_n\.png$' } | 
    Sort-Object Name
    
$characterName = "robo"

if ($pngFiles.Count -eq 0) {
    Write-Host "No PNG files found in the specified directory."
    exit
}

# Group files by move name, but handle normal maps specially
$groupedFiles = $pngFiles | Group-Object { 
    if ($_.Name -match '_n\.png$') {
        # For normal maps, group by the name before "_n"
        $_.Name -replace '_n\.png$', '_normal'
    } else {
        # For regular textures, keep original grouping
        $_.Name -replace '_\d+\.png$', ''
    }
}

foreach ($group in $groupedFiles) {
    $moveName = $group.Name
    $outputFile = Join-Path $InputDirectory "robo_$moveName.png"

    # Determine if this is a normal map group
    $isNormalMap = $moveName -match '_normal$'
    if ($isNormalMap) {
        $moveName = $moveName -replace '_normal$', ''
        $outputFile = Join-Path $InputDirectory "robo_${moveName}_n.png"
    }

    # Sort files numerically (normal maps will be sorted properly too)
    $sortedFiles = $group.Group | Sort-Object { 
        if ($_.Name -match '_n\.png$') {
            # Give normal maps a specific sort value if needed
            0  # This will place them at the beginning if mixed with numbered files
        } else {
            # For regular files, sort by the number
            [int]($_.Name -replace '.*_(\d+)\.png$', '$1')
        }
    }

    # Create the input string for the Electron app
    $inputString = $sortedFiles.FullName -join ','

    # Run the Electron app
    $electronCommand = "npx electron . --input=$inputString --output=$outputFile"

    Write-Host "Processing $moveName $(if ($isNormalMap) {'(normal maps)'})..."
    Write-Host "Running command: $electronCommand"
    Invoke-Expression $electronCommand

    Write-Host "Finished processing $moveName. Output: $outputFile"
    Write-Host ""
}

Write-Host "All spritesheets have been generated."