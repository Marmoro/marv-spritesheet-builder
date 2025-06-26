param (
    [Parameter(Mandatory=$true)]
    [string]$InputDirectory,
    
    [Parameter(Mandatory=$false)]
    [string]$CharacterName = "robo",
    
    [Parameter(Mandatory=$false)]
    [int]$BatchSize = 5
)

# Get all PNG files in the specified directory
# Include both files ending with _digits.png and _n.png
$pngFiles = Get-ChildItem -Path $InputDirectory -Filter *.png | 
    Where-Object { $_.Name -match '_\d+\.png$' -or $_.Name -match '_n\.png$' } | 
    Sort-Object Name

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

# Create a list to store batch processing information
$processingBatches = @()

foreach ($group in $groupedFiles) {
    $moveName = $group.Name
    $outputFile = Join-Path $InputDirectory "${CharacterName}_$moveName.png"

    # Determine if this is a normal map group
    $isNormalMap = $moveName -match '_normal$'
    if ($isNormalMap) {
        $moveName = $moveName -replace '_normal$', ''
        $outputFile = Join-Path $InputDirectory "${CharacterName}_${moveName}_n.png"
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
    
    # Add to the processing list
    $processingBatches += [PSCustomObject]@{
        MoveName = $moveName
        InputString = $inputString
        OutputFile = $outputFile
        IsNormalMap = $isNormalMap
    }
}

# Process files in batches
$totalBatches = [Math]::Ceiling($processingBatches.Count / $BatchSize)
Write-Host "Processing $($processingBatches.Count) sprite sets in $totalBatches batches of $BatchSize..."

for ($i = 0; $i -lt $processingBatches.Count; $i += $BatchSize) {
    $batchNumber = [Math]::Floor($i / $BatchSize) + 1
    Write-Host "`nStarting Batch $batchNumber of $totalBatches" -ForegroundColor Cyan
    
    # Get the current batch
    $currentBatch = $processingBatches[$i..([Math]::Min($i + $BatchSize - 1, $processingBatches.Count - 1))]
    
    # Create an array to store background jobs
    $jobs = @()
    
    foreach ($item in $currentBatch) {
        Write-Host "Queuing $($item.MoveName) $(if ($item.IsNormalMap) {'(normal maps)'})"
        
        # Run the Electron app as a background job
        $electronCommand = "npx electron . --input=$($item.InputString) --output=$($item.OutputFile)"
        $jobs += Start-Job -ScriptBlock {
            param($cmd, $name, $isNormal)
            Write-Output "Starting processing of $name $(if ($isNormal) {'(normal maps)'})"
            Invoke-Expression $cmd
            Write-Output "Finished processing $name"
        } -ArgumentList $electronCommand, $item.MoveName, $item.IsNormalMap
    }
    
    # Wait for all jobs in this batch to complete
    Write-Host "Waiting for batch $batchNumber to complete..." -ForegroundColor Yellow
    $jobs | Wait-Job | ForEach-Object {
        $result = Receive-Job $_
        Write-Host $result
        Remove-Job $_ -Force
    }
    
    Write-Host "Batch $batchNumber completed." -ForegroundColor Green
}

Write-Host "`nAll spritesheets have been generated." -ForegroundColor Cyan