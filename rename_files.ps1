param (
    [Parameter(Mandatory=$true)]
    [string]$directoryPath
)

# Navigate to the directory
Set-Location -Path $directoryPath

Write-Host "Processing files in $directoryPath..."

# Process _n files
$nFiles = Get-ChildItem -File -Path "*_n.*"
foreach ($file in $nFiles) {
    $fileName = $file.Name
    $extension = $file.Extension
    $nameWithoutExtension = $file.BaseName  # This gets the name without the extension
    
    # Remove the _n suffix
    $nameWithoutSuffix = $nameWithoutExtension.Substring(0, $nameWithoutExtension.Length - 2)
    
    # Find the last underscore position
    $lastUnderscorePos = $nameWithoutSuffix.LastIndexOf("_")
    
    if ($lastUnderscorePos -ge 0) {
        # Split the filename at the last underscore
        $prefix = $nameWithoutSuffix.Substring(0, $lastUnderscorePos)
        $suffix = $nameWithoutSuffix.Substring($lastUnderscorePos + 1)  # +1 to exclude the underscore itself
        
        # Create the new name
        $newName = "${prefix}_n_${suffix}${extension}"
        
        Write-Host "Renaming $fileName to $newName"
        Rename-Item -Path $file.FullName -NewName $newName
    } else {
        Write-Host "No underscore found in $fileName, skipping."
    }
}

# Process _s files
$sFiles = Get-ChildItem -File -Path "*_s.*"
foreach ($file in $sFiles) {
    $fileName = $file.Name
    $extension = $file.Extension
    $nameWithoutExtension = $file.BaseName  # This gets the name without the extension
    
    # Remove the _s suffix
    $nameWithoutSuffix = $nameWithoutExtension.Substring(0, $nameWithoutExtension.Length - 2)
    
    # Find the last underscore position
    $lastUnderscorePos = $nameWithoutSuffix.LastIndexOf("_")
    
    if ($lastUnderscorePos -ge 0) {
        # Split the filename at the last underscore
        $prefix = $nameWithoutSuffix.Substring(0, $lastUnderscorePos)
        $suffix = $nameWithoutSuffix.Substring($lastUnderscorePos + 1)  # +1 to exclude the underscore itself
        
        # Create the new name
        $newName = "${prefix}_s_${suffix}${extension}"
        
        Write-Host "Renaming $fileName to $newName"
        Rename-Item -Path $file.FullName -NewName $newName
    } else {
        Write-Host "No underscore found in $fileName, skipping."
    }
}

Write-Host "Done."