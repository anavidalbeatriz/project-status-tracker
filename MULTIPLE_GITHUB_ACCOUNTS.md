# Using Multiple GitHub Accounts on the Same Machine

This guide shows you how to use multiple GitHub accounts simultaneously for different repositories.

## Method 1: SSH Keys (Recommended)

This method uses different SSH keys for different GitHub accounts.

### Step 1: Generate SSH Keys for Each Account

**Windows (PowerShell):**

```powershell
# Create .ssh directory if it doesn't exist
if (-not (Test-Path "$env:USERPROFILE\.ssh")) {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force
}

# For your personal account
ssh-keygen -t ed25519 -C "your-personal-email@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_personal" -N '""'

# For your work/other account
ssh-keygen -t ed25519 -C "your-work-email@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_work" -N '""'
```

**Linux/Mac/Git Bash:**

```bash
# For your personal account
ssh-keygen -t ed25519 -C "your-personal-email@example.com" -f ~/.ssh/id_ed25519_personal

# For your work/other account
ssh-keygen -t ed25519 -C "your-work-email@example.com" -f ~/.ssh/id_ed25519_work
```

When prompted, press Enter to accept default locations, or specify custom names. On Windows, use `-N '""'` to skip passphrase prompt.

### Step 2: Add SSH Keys to GitHub

1. **Copy your public keys:**

   **Windows (PowerShell):**
   ```powershell
   # Personal account key
   Get-Content "$env:USERPROFILE\.ssh\id_ed25519_personal.pub"
   
   # Work account key
   Get-Content "$env:USERPROFILE\.ssh\id_ed25519_work.pub"
   ```

   **Linux/Mac/Git Bash:**
   ```bash
   # Personal account key
   cat ~/.ssh/id_ed25519_personal.pub
   
   # Work account key
   cat ~/.ssh/id_ed25519_work.pub
   ```

2. **Add to GitHub:**
   - Go to GitHub → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste the public key for each account
   - Give each key a descriptive title

### Step 3: Create SSH Config File

**Windows (PowerShell):**

```powershell
# Create or edit SSH config
$configContent = @"
# Personal GitHub account
Host github.com-personal
    HostName github.com
    User git
    IdentityFile $env:USERPROFILE\.ssh\id_ed25519_personal
    IdentitiesOnly yes

# Work GitHub account
Host github.com-work
    HostName github.com
    User git
    IdentityFile $env:USERPROFILE\.ssh\id_ed25519_work
    IdentitiesOnly yes
"@

$configPath = "$env:USERPROFILE\.ssh\config"
Set-Content -Path $configPath -Value $configContent
```

**Linux/Mac/Git Bash:**

Create or edit `~/.ssh/config`:

```bash
# Personal GitHub account
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes

# Work GitHub account
Host github.com-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes
```

### Step 4: Test SSH Connections

```bash
# Test personal account
ssh -T git@github.com-personal
# Should see: "Hi username! You've successfully authenticated..."

# Test work account
ssh -T git@github.com-work
# Should see: "Hi username! You've successfully authenticated..."
```

### Step 5: Configure Git for Each Repository

#### For Personal Account Repositories:

```bash
cd /path/to/personal-repo
git remote set-url origin git@github.com-personal:username/repo-name.git
```

#### For Work Account Repositories:

```bash
cd /path/to/work-repo
git remote set-url origin git@github.com-work:username/repo-name.git
```

### Step 6: Set Local Git Config Per Repository

For each repository, set the user name and email:

```bash
# In personal repository
cd /path/to/personal-repo
git config user.name "Your Personal Name"
git config user.email "your-personal-email@example.com"

# In work repository
cd /path/to/work-repo
git config user.name "Your Work Name"
git config user.email "your-work-email@example.com"
```

---

## Method 2: Git Credential Manager (Windows/Mac)

If you're using Git Credential Manager, you can store multiple accounts.

### Windows (Git Credential Manager)

1. **First time cloning:**
   ```bash
   git clone https://github.com/username/repo.git
   ```
   - A browser window will open
   - Sign in with the correct GitHub account
   - Credential Manager will remember it

2. **For different accounts:**
   - When prompted, choose "Sign in with a different account"
   - Or use: `git credential-manager-core erase https://github.com`

3. **View stored credentials:**
   - Windows: Control Panel → Credential Manager → Windows Credentials
   - Look for `git:https://github.com`

### Mac (Keychain)

```bash
# View stored credentials
git credential-osxkeychain erase
host=github.com
protocol=https

# Or use GitHub CLI
gh auth login
```

---

## Method 3: GitHub CLI (gh) with Multiple Accounts

GitHub CLI can handle multiple accounts easily.

### Install GitHub CLI

```bash
# Windows (with Chocolatey)
choco install gh

# Mac
brew install gh

# Or download from: https://cli.github.com/
```

### Authenticate Multiple Accounts

```bash
# Login with personal account
gh auth login --hostname github.com --git-protocol ssh

# Login with work account (use different hostname or token)
gh auth login --hostname github.com --git-protocol ssh
```

### Switch Between Accounts

```bash
# List authenticated accounts
gh auth status

# Switch accounts
gh auth switch
```

---

## Method 4: HTTPS with Different Credentials

### Clone with Different Accounts

```bash
# Personal account
git clone https://username-personal@github.com/username/repo.git

# Work account
git clone https://username-work@github.com/username/repo.git
```

### Store Credentials Per Repository

```bash
# Disable global credential helper for specific repo
cd /path/to/repo
git config credential.helper ""
git config credential.helper store

# Or use cache (temporary)
git config credential.helper cache
```

---

## Quick Setup Script

Create a script to quickly set up a repository for a specific account:

### Windows PowerShell Script

```powershell
# setup-git-repo.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Account,  # "personal" or "work"
    
    [Parameter(Mandatory=$true)]
    [string]$RepoPath
)

$config = @{
    "personal" = @{
        "name" = "Your Personal Name"
        "email" = "personal@example.com"
        "host" = "github.com-personal"
    }
    "work" = @{
        "name" = "Your Work Name"
        "email" = "work@example.com"
        "host" = "github.com-work"
    }
}

$accountConfig = $config[$Account]
if (-not $accountConfig) {
    Write-Host "Invalid account. Use 'personal' or 'work'"
    exit 1
}

Set-Location $RepoPath
git config user.name $accountConfig.name
git config user.email $accountConfig.email

# Update remote URL if it exists
$remoteUrl = git remote get-url origin
if ($remoteUrl) {
    $newUrl = $remoteUrl -replace "github.com", $accountConfig.host
    git remote set-url origin $newUrl
    Write-Host "Updated remote URL to use $Account account"
}

Write-Host "Repository configured for $Account account"
```

**Usage:**
```powershell
.\setup-git-repo.ps1 -Account "personal" -RepoPath "C:\Projects\my-repo"
```

### Bash Script (Linux/Mac/Git Bash)

```bash
#!/bin/bash
# setup-git-repo.sh

ACCOUNT=$1
REPO_PATH=$2

if [ "$ACCOUNT" = "personal" ]; then
    NAME="Your Personal Name"
    EMAIL="personal@example.com"
    HOST="github.com-personal"
elif [ "$ACCOUNT" = "work" ]; then
    NAME="Your Work Name"
    EMAIL="work@example.com"
    HOST="github.com-work"
else
    echo "Invalid account. Use 'personal' or 'work'"
    exit 1
fi

cd "$REPO_PATH"
git config user.name "$NAME"
git config user.email "$EMAIL"

# Update remote URL
REMOTE_URL=$(git remote get-url origin)
if [ -n "$REMOTE_URL" ]; then
    NEW_URL=$(echo "$REMOTE_URL" | sed "s/github.com/$HOST/")
    git remote set-url origin "$NEW_URL"
    echo "Updated remote URL to use $ACCOUNT account"
fi

echo "Repository configured for $ACCOUNT account"
```

**Usage:**
```bash
chmod +x setup-git-repo.sh
./setup-git-repo.sh personal /path/to/repo
```

---

## For This Project (Project Status Tracker)

If you want to use a specific GitHub account for this project:

### Option 1: Use SSH Method

```bash
cd "C:\Users\AnaBeatrizVidal\Projects\Personal projects\project-status-tracker-kis"

# If using personal account
git remote set-url origin git@github.com-personal:your-username/project-status-tracker-kis.git
git config user.name "Your Name"
git config user.email "your-email@example.com"

# If using work account
git remote set-url origin git@github.com-work:your-username/project-status-tracker-kis.git
git config user.name "Your Work Name"
git config user.email "your-work-email@example.com"
```

### Option 2: Use HTTPS with Credential Manager

```bash
cd "C:\Users\AnaBeatrizVidal\Projects\Personal projects\project-status-tracker-kis"

# Clone or update remote
git remote set-url origin https://github.com/your-username/project-status-tracker-kis.git

# When you push, Windows Credential Manager will prompt you
# Choose the correct account
```

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution:**
1. Check SSH key is added to GitHub account
2. Test connection: `ssh -T git@github.com-personal`
3. Verify SSH config file exists and is correct
4. Make sure you're using the correct host alias in remote URL

### Issue: Wrong account commits

**Solution:**
1. Check local git config: `git config user.name` and `git config user.email`
2. Set per-repository: `git config user.name "Correct Name"`
3. For already committed changes, use: `git commit --amend --author="Name <email>"`

### Issue: Credential Manager keeps using wrong account

**Solution:**
1. Clear stored credentials:
   ```bash
   # Windows
   git credential-manager-core erase
   host=github.com
   protocol=https
   
   # Or use Windows Credential Manager UI
   ```
2. Re-authenticate when prompted

### Issue: Can't push to repository

**Solution:**
1. Verify remote URL: `git remote -v`
2. Check SSH connection: `ssh -T git@github.com-personal`
3. Ensure you have push access to the repository
4. Try: `git push -u origin main` (first time)

---

## Best Practices

1. **Use SSH keys** for better security and convenience
2. **Set git config per repository** instead of globally
3. **Use descriptive SSH host aliases** (github.com-personal, github.com-work)
4. **Keep SSH keys secure** - don't share private keys
5. **Use different emails** for different accounts to avoid confusion
6. **Test connections** after setup: `ssh -T git@github.com-personal`

---

## Quick Reference

### Check Current Configuration

```bash
# Check git user
git config user.name
git config user.email

# Check remote URL
git remote -v

# Check SSH connection
ssh -T git@github.com-personal
```

### Switch Account for a Repository

```bash
# Change remote URL
git remote set-url origin git@github.com-personal:username/repo.git

# Change user config
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

---

## Summary

**Recommended approach:**
1. Use **SSH keys with host aliases** (Method 1) - most reliable
2. Set **per-repository git config** - prevents confusion
3. Use **descriptive host names** - easy to identify which account

This setup allows you to:
- ✅ Use multiple GitHub accounts simultaneously
- ✅ Keep accounts separate and secure
- ✅ Avoid authentication conflicts
- ✅ Work with both personal and work repositories easily

Need help setting this up? Let me know which method you prefer!
