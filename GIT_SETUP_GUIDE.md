# 🚀 Git Repository Setup Guide

## Step-by-Step Guide to Upload Your Project to Git

### 📋 Prerequisites
- Git installed on your system
- GitHub/GitLab account created
- Project files ready (fraud monitoring system)

---

## 🔧 Step 1: Initialize Local Repository

```bash
# Navigate to your project directory
cd telegram-fraud-monitor

# Initialize git repository
git init

# Check current status
git status
```

---

## 🔒 Step 2: Security Check - Protect Sensitive Files

```bash
# Verify .gitignore exists and covers sensitive files
cat .gitignore

# Check if .env file is properly ignored
git check-ignore .env

# If .env is not ignored, add it to .gitignore
echo ".env" >> .gitignore
```

**⚠️ CRITICAL**: Never commit these files:
- `.env` (contains secrets)
- `*.key`, `*.pem` (certificates)
- `logs/` (may contain sensitive data)

---

## 📁 Step 3: Add Files to Repository

```bash
# Add all files (except those in .gitignore)
git add .

# Check what will be committed
git status

# Verify no sensitive files are staged
git diff --cached --name-only
```

---

## 💾 Step 4: Create Initial Commit

```bash
# Create initial commit with descriptive message
git commit -m "feat: initial commit - fraud monitoring telegram bot

- Add secure telegram bot with fraud detection
- Implement OCR processing for images
- Add PostgreSQL database integration
- Include Docker containerization
- Add comprehensive security hardening
- Include rate limiting and input validation"
```

---

## 🌐 Step 5: Create Remote Repository

### Option A: GitHub (Web Interface)
1. Go to [GitHub](https://github.com)
2. Click "New Repository" (+ icon)
3. Repository name: `telegram-fraud-monitor`
4. Description: `🔐 Secure Telegram bot for fraud detection with OCR and real-time alerts`
5. Set as **Private** (recommended for security)
6. **DO NOT** initialize with README (we already have one)
7. Click "Create Repository"

### Option B: GitHub CLI
```bash
# Install GitHub CLI if not installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Create repository
gh repo create telegram-fraud-monitor --private --description "🔐 Secure Telegram bot for fraud detection with OCR and real-time alerts"
```

---

## 🔗 Step 6: Connect Local to Remote

```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/telegram-fraud-monitor.git

# Verify remote was added
git remote -v

# Set upstream branch and push
git branch -M main
git push -u origin main
```

---

## 🛡️ Step 7: Security Verification

```bash
# Verify no secrets were pushed
git log --oneline
git show --name-only

# Check repository on GitHub/GitLab
# Ensure .env file is NOT visible
```

---

## 📝 Step 8: Repository Configuration

### Set Repository Settings (GitHub Web Interface):
1. Go to repository → Settings
2. **Security**:
   - Enable "Vulnerability alerts"
   - Enable "Dependency graph"
   - Enable "Dependabot alerts"
3. **Branches**:
   - Protect `main` branch
   - Require pull request reviews
4. **Secrets** (for CI/CD later):
   - Add `TELEGRAM_BOT_TOKEN`
   - Add `DB_PASS`

---

## 🏷️ Step 9: Create Release Tag

```bash
# Create and push first release tag
git tag -a v1.0.0 -m "🎉 Initial release - Fraud Monitoring System

Features:
- Telegram bot with fraud detection
- OCR image processing
- Secure PostgreSQL storage
- Docker containerization
- Comprehensive security hardening"

git push origin v1.0.0
```

---

## 🔄 Step 10: Future Workflow

### For future changes:
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push feature branch
git push origin feature/new-feature

# Create Pull Request on GitHub
# After review and merge, update main:
git checkout main
git pull origin main
```

---

## 🚨 Security Checklist

Before pushing, verify:
- [ ] `.env` file is in `.gitignore`
- [ ] No hardcoded passwords in code
- [ ] No API keys in commit history
- [ ] Sensitive logs are excluded
- [ ] Database credentials are not exposed

### Emergency: If secrets were accidentally committed:
```bash
# Remove file from git history (DANGEROUS - use carefully)
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all

# Force push (only if repository is private and you're sure)
git push origin --force --all
```

---

## 📊 Repository Structure

Your final repository should look like:
```
telegram-fraud-monitor/
├── .env.example          ✅ Template (safe to commit)
├── .env                  ❌ Ignored (contains secrets)
├── .gitignore           ✅ Protects sensitive files
├── README.md            ✅ Documentation
├── docker-compose.yml   ✅ Container orchestration
├── Dockerfile           ✅ Container definition
├── deploy.sh            ✅ Deployment script
├── requirements.txt     ✅ Python dependencies
├── src/                 ✅ Source code
│   ├── telegram_bot.py
│   ├── database.py
│   ├── alert_system.py
│   └── ocr_processor.py
└── logs/                ❌ Ignored (runtime logs)
```

---

## 🎉 Completion Verification

1. **Repository is online**: Visit your GitHub repository URL
2. **README displays properly**: Check formatting and badges
3. **No secrets visible**: Verify .env is not in repository
4. **All code files present**: Ensure all source files uploaded
5. **Security settings configured**: Branch protection, alerts enabled

---

## 🔗 Next Steps

1. **Set up CI/CD pipeline** (GitHub Actions)
2. **Configure automated security scanning**
3. **Add issue templates**
4. **Create contribution guidelines**
5. **Set up automated testing**

---

**🛡️ Remember**: Security first! Always verify no sensitive data is committed before pushing to remote repositories.