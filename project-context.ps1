[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateScript({ Test-Path $_ -PathType Container })]
    [string]$Root = ".",

    # Bez ValidateScript – složku vytvoříme sami
    [Parameter(Mandatory = $false)]
    [string]$OutDir = $null,   # auto: $Root\context

    [Parameter(Mandatory = $false)]
    [string]$OutPrefix,        # auto: název kořene

    [Parameter(Mandatory = $false)]
    [switch]$NoTimestamp,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

# Nepřidávat tento skript do výstupu
$ScriptFullPath = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)

# -------------------------------------
# Konfigurace
# -------------------------------------
$IncludePatterns = @(
    "*.py", "*.js", "*.ts", "*.ps1", "*.sh",
    "pyproject.toml", "requirements*.txt", "setup.cfg", "setup.py",
    "Pipfile*", "tox.ini", "ruff.toml", "mypy.ini",
    "package.json", "tsconfig.json",
    "Dockerfile", "docker-compose*.yml",
    ".github/workflows/*.yml", ".gitlab-ci.yml",
    "README*", "LICENSE", "CHANGELOG*", "CONTRIBUTING*",
    "*.md", "*.rst", "Makefile"
)

# Ignoruj tečkové adresáře + běžné build/cache + výstupní složku
$ExcludeDirPatterns = @(
    ".*",
    "venv", ".venv", "env", "site-packages", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", "htmlcov", "dist", "build",
    ".parcel-cache", ".next", ".turbo", ".cache",
    ".git", ".hg", ".svn", ".idea", ".vscode",
    "data", "datasets", ".aws",
    "context"
)

# Exclude soubory vč. generovaných výstupů
$ExcludeFilePatterns = @(
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe",
    "*.pkl", "*.zip", "*.tar*", "*.pdf",
    "*.png", "*.jpg", "*.jpeg", "*.gif",
    "*.mp4", "*.mov", "*.wav", "*.mp3", "*.ico",
    ".env", "*.env", ".env.*",
    "*.pem", "*.key", "id_rsa*", "id_ed25519*",
    ".npmrc", ".pypirc", ".netrc", "secrets.*",
    ".DS_Store", "Thumbs.db", ".coverage*", "*.ipynb",
    "*.csv", "*.parquet", "*.sqlite*",
    "context-*-index.csv", "context-*.md"
)

# -------------------------------------
# Helpery
# -------------------------------------
function Get-RelativePath {
    param(
        [Parameter(Mandatory=$true)][string]$RootPath,
        [Parameter(Mandatory=$true)][string]$FullPath
    )
    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\','/')
    $fullFull = [System.IO.Path]::GetFullPath($FullPath)
    $getRel = [System.IO.Path].GetMethod('GetRelativePath', [Type[]]@([string],[string]))
    if ($getRel) { return [System.IO.Path]::GetRelativePath($rootFull, $fullFull) }
    if ($fullFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullFull.Substring($rootFull.Length).TrimStart('\','/')
    }
    return $fullFull
}

function Test-ShouldExcludeDirectory {
    param([string]$DirName)
    if ($DirName -like '.*') { return $true } # tečkové adresáře
    foreach ($pattern in $ExcludeDirPatterns) {
        if ($DirName -like $pattern) { return $true }
    }
    return $false
}

function Test-ShouldIncludeFile {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string]$RootPath
    )

    # vyřadit sám skript
    if ([System.IO.Path]::GetFullPath($FilePath) -eq $ScriptFullPath) { return $false }

    $leaf = Split-Path $FilePath -Leaf
    $rel  = Get-RelativePath -RootPath $RootPath -FullPath $FilePath
    $relNorm = $rel -replace '\\','/'

    foreach ($pattern in $ExcludeFilePatterns) {
        if ($leaf -like $pattern) { return $false }
    }
    foreach ($pattern in $IncludePatterns) {
        $patNorm  = $pattern -replace '\\','/'
        if ($patNorm -match '/') {
            if ($relNorm -like $patNorm) { return $true }
        } else {
            if ($leaf -like $patNorm) { return $true }
        }
    }
    return $false
}

function Get-FileExtensionTag {
    param([string]$FilePath)
    switch ([System.IO.Path]::GetExtension($FilePath).ToLower()) {
        ".py" {"py"} ".js" {"js"} ".ts" {"ts"} ".json" {"json"}
        ".yaml" {"yaml"} ".yml" {"yaml"} ".toml" {"toml"}
        ".ps1" {"ps1"} ".sh" {"sh"}
        default { "" }
    }
}

function Get-UniqueOutputPath {
    param([string]$BasePath)
    $path = $BasePath; $i = 1
    while (Test-Path $path) {
        $dir = Split-Path $BasePath -Parent
        $name = [System.IO.Path]::GetFileNameWithoutExtension($BasePath)
        $ext = [System.IO.Path]::GetExtension($BasePath)
        $path = Join-Path $dir ("{0}-{1:000}{2}" -f $name, $i, $ext)
        $i++
    }
    $path
}

# -------------------------------------
# Sken projektu
# -------------------------------------
function Get-ProjectFiles {
    param([string]$RootPath)
    $files = @()
    $queue = @($RootPath)
    while ($queue.Count -gt 0) {
        $current = $queue[0]
        # Guard na slice fronty
        if ($queue.Count -gt 1) { $queue = $queue[1..($queue.Count - 1)] } else { $queue = @() }

        $items = Get-ChildItem -LiteralPath $current -Force -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            # skip reparse points (symlinks/junctions)
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { continue }

            if ($item.PSIsContainer) {
                if (-not (Test-ShouldExcludeDirectory $item.Name)) { $queue += $item.FullName }
            } else {
                if (Test-ShouldIncludeFile -FilePath $item.FullName -RootPath $RootPath) {
                    $files += [PSCustomObject]@{
                        FullPath     = $item.FullName
                        RelativePath = Get-RelativePath -RootPath $RootPath -FullPath $item.FullName
                    }
                }
            }
        }
    }
    $files | Sort-Object RelativePath
}

# -------------------------------------
# Čtení obsahu a hash
# -------------------------------------
function Read-FileContent {
    param([string]$FilePath)
    try {
        $bytes = [System.IO.File]::ReadAllBytes($FilePath)
        for ($i=0; $i -lt [Math]::Min(512,$bytes.Length); $i++) { if ($bytes[$i] -eq 0) { throw [System.IO.InvalidDataException]::new("Binary") } }

        # strict UTF-8
        $utf8 = New-Object System.Text.UTF8Encoding($false,$true)
        try { $content = $utf8.GetString($bytes) } catch {
            return [PSCustomObject]@{ Content=""; Lines=0; Bytes=$bytes.Length; ReadError=$true; Hash=""; IsBinary=$false }
        }

        $contentBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $sha1 = [System.Security.Cryptography.SHA1]::Create()
        $hash = ([System.BitConverter]::ToString($sha1.ComputeHash($contentBytes))).Replace("-","").ToUpperInvariant()

        [PSCustomObject]@{
            Content=$content; Lines=($content -split "`n").Count; Bytes=$bytes.Length
            ReadError=$false; Hash=$hash; IsBinary=$false
        }
    } catch {
        [PSCustomObject]@{ Content=""; Lines=0; Bytes=0; ReadError=$true; Hash=""; IsBinary=$true }
    }
}

# -------------------------------------
# Výstupy
# -------------------------------------
function Write-MarkdownOutput {
    param([string]$OutputPath, [string]$RootPath, [string]$Timestamp, [array]$FileData)

    $totalFiles = $FileData.Count
    $totalSize = ($FileData | Measure-Object -Property Bytes -Sum).Sum

    $header = @"
## Project Context

- Root Path: $RootPath
- Timestamp: $Timestamp
- Total Files: $totalFiles
- Total Size: $totalSize bytes

## Summary Table

| Relative Path | Bytes | Lines |
|---------------|-------|-------|
"@
    foreach ($f in $FileData) { $header += "`n| $($f.RelativePath) | $($f.Bytes) | $($f.Lines) |" }
    $header += "`n`n## File Contents`n`n"

    $content = $header
    foreach ($f in $FileData) {
        $tag = Get-FileExtensionTag $f.FullPath
        $content += "### $($f.RelativePath)`n`n"
        if ([string]::IsNullOrEmpty($tag)) {
            $content += "````n$($f.Content)`n````n`n" -replace '```','```'   # výsledkem jsou 3 backticky
        } else {
            $content += "```$tag`n$($f.Content)`n````n`n" -replace '```','```'
        }
    }
    $content | Out-File $OutputPath -Encoding UTF8
}

function Write-CsvIndex {
    param([string]$OutputPath, [array]$FileData)
    $csvData = foreach ($file in $FileData) {
        $fi = Get-Item -LiteralPath $file.FullPath -ErrorAction SilentlyContinue
        $createdUtc  = if ($fi) { $fi.CreationTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "" }
        $modifiedUtc = if ($fi) { $fi.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "" }

        [PSCustomObject]@{
            relative_path = $file.RelativePath
            bytes         = $file.Bytes
            lines         = $file.Lines
            hash_sha1     = $file.Hash
            is_binary     = $file.IsBinary
            read_error    = $file.ReadError
            created_utc   = $createdUtc
            modified_utc  = $modifiedUtc
        }
    }
    $csvData | Export-Csv $OutputPath -NoTypeInformation -Encoding UTF8
}

# -------------------------------------
# Hlavní tok – ZERO-ARGS friendly
# -------------------------------------
$Root = (Resolve-Path $Root).Path

# OutDir = $Root\context (vytvoř, pokud není)
if (-not $PSBoundParameters.ContainsKey('OutDir') -or [string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $Root 'context'
}
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null } else { $OutDir = (Resolve-Path $OutDir).Path }

if (-not $OutPrefix) { $OutPrefix = Split-Path $Root -Leaf }
$timestamp = if ($NoTimestamp) { "" } else { Get-Date -Format "yyyyMMdd-HHmmss" }

# Sken jednou, pak rozděl na openspec vs zbytek
Write-Host "Scanning directory: $Root"
$allFiles = Get-ProjectFiles $Root
Write-Host "Found $($allFiles.Count) files (before partition)"

# Partition: openspec = vše pod 'openspec/' + všechny .md kdekoliv; other = zbytek bez .md
$allFilesNorm = $allFiles | ForEach-Object {
    $_ | Add-Member -NotePropertyName RelNorm -NotePropertyValue ( ($_.RelativePath -replace '\\','/')) -Force; $_
}
$filesOpenSpec = $allFilesNorm | Where-Object { $_.RelNorm -like 'openspec/*' -or $_.RelNorm.ToLower().EndsWith('.md') }
$filesOther    = $allFilesNorm | Where-Object { $_.RelNorm -notlike 'openspec/*' -and -not ($_.RelNorm.ToLower().EndsWith('.md')) }

function Build-FileData { param([array]$Files)
    $out = @()
    foreach ($file in $Files) {
        $d = Read-FileContent $file.FullPath
        $d | Add-Member -NotePropertyName RelativePath -NotePropertyValue $file.RelativePath -Force
        $d | Add-Member -NotePropertyName FullPath -NotePropertyValue $file.FullPath -Force
        if ($d.Bytes -gt 5MB) { Write-Warning "Large file: $($file.RelativePath) ($($d.Bytes) bytes)" }
        if ($d.ReadError) { Write-Warning "Read error for: $($file.RelativePath)" }
        $out += $d
    }
    $out | Sort-Object RelativePath
}

$fileDataOpenSpec = Build-FileData $filesOpenSpec
$fileDataOther    = Build-FileData $filesOther

if ($DryRun) {
    Write-Host ("Dry run: openspec={0} files, other={1} files" -f $fileDataOpenSpec.Count, $fileDataOther.Count)
    $sumOpen = ($fileDataOpenSpec | Measure-Object Bytes -Sum).Sum
    $sumOther= ($fileDataOther    | Measure-Object Bytes -Sum).Sum
    Write-Host ("Sizes: openspec={0} bytes, other={1} bytes" -f $sumOpen, $sumOther)
    exit 0
}

# Cesty a zápis – dva páry souborů
$baseMdOpen  = "context-$OutPrefix-$timestamp-openspec.md"
$baseCsvOpen = "context-$OutPrefix-$timestamp-openspec-index.csv"
$baseMdOther = "context-$OutPrefix-$timestamp-other.md"
$baseCsvOther= "context-$OutPrefix-$timestamp-other-index.csv"

$mdPathOpen  = Get-UniqueOutputPath (Join-Path $OutDir $baseMdOpen)
$csvPathOpen = Get-UniqueOutputPath (Join-Path $OutDir $baseCsvOpen)
$mdPathOther = Get-UniqueOutputPath (Join-Path $OutDir $baseMdOther)
$csvPathOther= Get-UniqueOutputPath (Join-Path $OutDir $baseCsvOther)

Write-MarkdownOutput $mdPathOpen  $Root $timestamp $fileDataOpenSpec
Write-CsvIndex       $csvPathOpen $fileDataOpenSpec
Write-MarkdownOutput $mdPathOther $Root $timestamp $fileDataOther
Write-CsvIndex       $csvPathOther $fileDataOther

Write-Host "Generated: $mdPathOpen"
Write-Host "Generated: $csvPathOpen"
Write-Host "Generated: $mdPathOther"
Write-Host "Generated: $csvPathOther"
Write-Host ("Totals -> openspec: {0} files; other: {1} files" -f $fileDataOpenSpec.Count, $fileDataOther.Count)
exit 0
