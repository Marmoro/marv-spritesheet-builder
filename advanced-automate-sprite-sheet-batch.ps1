param (
    [Parameter(Mandatory=$true)]
    [string]$InputDirectory,
    
    [Parameter(Mandatory=$false)]
    [string]$CharacterName = "robo"
)

# Get all PNG files in the specified directory
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
        $_.Name -replace '_n\.png$', '_normal'
    } else {
        $_.Name -replace '_\d+\.png$', ''
    }
}

# Create tasks array
$tasks = @()

foreach ($group in $groupedFiles) {
    $moveName = $group.Name
    $outputFile = Join-Path $InputDirectory "${CharacterName}_$moveName.png"

    # Determine if this is a normal map group
    $isNormalMap = $moveName -match '_normal$'
    if ($isNormalMap) {
        $moveName = $moveName -replace '_normal$', ''
        $outputFile = Join-Path $InputDirectory "${CharacterName}_${moveName}_n.png"
    }

    # Sort files numerically
    $sortedFiles = $group.Group | Sort-Object { 
        if ($_.Name -match '_n\.png$') {
            0
        } else {
            [int]($_.Name -replace '.*_(\d+)\.png$', '$1')
        }
    }

    # Add to tasks array
    $tasks += @{
        inputs = $sortedFiles.FullName
        output = $outputFile
        name = $moveName
    }
}

# Create a temporary file for the tasks
$tempTaskFile = [System.IO.Path]::GetTempFileName() + ".json"

# Convert tasks to JSON and write to file WITHOUT BOM
$jsonContent = $tasks | ConvertTo-Json -Depth 3
# Use .NET method to write without BOM instead of Out-File
[System.IO.File]::WriteAllText($tempTaskFile, $jsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "Processing batch of $($tasks.Count) sprite sheets..."
Write-Host "Task file created at: $tempTaskFile"

# Set environment variable and run Electron
$env:SPRITE_TASK_FILE = $tempTaskFile
$electronCommand = "npx electron main-batched.js"

Write-Host "Running Electron process..."
Invoke-Expression $electronCommand

# Clean up environment variable
Remove-Item Env:\SPRITE_TASK_FILE

Write-Host "All spritesheets have been generated."