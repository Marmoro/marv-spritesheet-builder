param (
    [Parameter(Mandatory=$true)]
    [string]$InputDirectory,

    [Parameter(Mandatory=$false)]
    [double]$Strength = 2.5,

    [Parameter(Mandatory=$false)]
    [double]$Distance = 2,

    [Parameter(Mandatory=$false)]
    [switch]$Invert,

    [Parameter(Mandatory=$false)]
    [switch]$WrapEdges,

    [Parameter(Mandatory=$false)]
    [int]$ChunkSize = 100
)

# Get all PNG files in the specified directory
$pngFiles = Get-ChildItem -Path $InputDirectory -Filter *.png | Where-Object { $_.Name -match '_\d+\.png$' } | Sort-Object Name
$characterName = "robo"

if ($pngFiles.Count -eq 0) {
    Write-Host "No PNG files found in the specified directory."
    exit
}

# Group files by move name
$groupedFiles = $pngFiles | Group-Object { $_.Name -replace '_\d+\.png$', '' }

foreach ($group in $groupedFiles) {
    $moveName = $group.Name
    $outputFile = Join-Path $InputDirectory "robo_$moveName.png"

    # Sort files numerically
    $sortedFiles = $group.Group | Sort-Object { 
        [int]($_.Name -replace '.*_(\d+)\.png$', '$1')
    }

    # Create the input string for the Electron app
    $inputString = $sortedFiles.FullName -join ','

    # Build the Electron command with additional parameters
    $electronCommand = "npx electron . --input=$inputString --output=$outputFile --strength=$Strength --distance=$Distance --chunk-size=$ChunkSize"

    if ($Invert) {
        $electronCommand += " --invert"
    }
    if ($WrapEdges) {
        $electronCommand += " --wrap-edges"
    }

    Write-Host "Processing $moveName..."
    Write-Host "Running command: $electronCommand"
    Invoke-Expression $electronCommand

    Write-Host "Finished processing $moveName. Output: $outputFile"
    Write-Host ""
}

Write-Host "All spritesheets have been generated."