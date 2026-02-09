# PowerShell script to set up GitHub account for a repository
# Usage: .\setup-github-account.ps1 -Account "personal" -RepoPath "C:\Projects\my-repo"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("personal", "work")]
    [string]$Account,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoPath
)

# Configuration for each account
# TODO: Update these with your actual names and emails
$config = @{
    "personal" = @{
        "name" = "Ana Beatriz Vidal"  # Update with your personal name
        "email" = "anavidalbeatriz@gmail.com"  # Update with your personal email
        "host" = "github.com-personal"
        "username" = "anavidalbeatriz"  # Your GitHub username
    }
    "work" = @{
        "name" = "Your Work Name"  # Update with your work name
        "email" = "your-work-email@example.com"  # Update with your work email
        "host" = "github.com-work"
        "username" = "aiurah7_amway"  # Your GitHub username
    }
}

$accountConfig = $config[$Account]

if (-not (Test-Path $RepoPath)) {
    Write-Host "Error: Repository path does not exist: $RepoPath" -ForegroundColor Red
    exit 1
}

Set-Location $RepoPath

# Check if it's a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Error: Not a git repository: $RepoPath" -ForegroundColor Red
    exit 1
}

# Set git user name and email
git config user.name $accountConfig.name
git config user.email $accountConfig.email

Write-Host "✓ Set user.name to: $($accountConfig.name)" -ForegroundColor Green
Write-Host "✓ Set user.email to: $($accountConfig.email)" -ForegroundColor Green

# Update remote URL if it exists
$remoteUrl = git remote get-url origin 2>$null
if ($remoteUrl) {
    if ($remoteUrl -match "github\.com") {
        $newUrl = $remoteUrl -replace "github\.com", $accountConfig.host
        git remote set-url origin $newUrl
        Write-Host "✓ Updated remote URL to use $Account account" -ForegroundColor Green
        Write-Host "  Old: $remoteUrl" -ForegroundColor Gray
        Write-Host "  New: $newUrl" -ForegroundColor Gray
    } else {
        Write-Host "⚠ Remote URL doesn't use github.com, skipping URL update" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ No remote 'origin' found. Add one with:" -ForegroundColor Yellow
    Write-Host "  git remote add origin git@$($accountConfig.host):username/repo.git" -ForegroundColor Cyan
}

Write-Host "`nRepository configured for $Account account!" -ForegroundColor Green
Write-Host "`nCurrent configuration:" -ForegroundColor Cyan
Write-Host "  User: $(git config user.name)"
Write-Host "  Email: $(git config user.email)"
if ($remoteUrl) {
    Write-Host "  Remote: $(git remote get-url origin)"
}
