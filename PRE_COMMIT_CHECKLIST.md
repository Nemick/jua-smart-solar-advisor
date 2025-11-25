# 📋 Pre-Commit Checklist - Jua Smart

**Before you push to GitHub, verify all these items:**

---

## ✅ Security Checklist

### API Keys & Secrets

- [ ] **.env file is NOT committed**
  ```bash
  # Check:
  git status | grep ".env"
  # Should return nothing
  ```

- [ ] **.env is in .gitignore**
  ```bash
  # Check:
  grep "^\.env$" .gitignore
  # Should show: .env
  ```

- [ ] **.env.example has NO real keys**
  ```bash
  # Check:
  cat .env.example | grep -i "AIza"
  # Should return nothing
  ```

- [ ] **No hardcoded API keys in code**
  ```bash
  # Check:
  grep -r "AIza" --exclude-dir=venv --exclude=".env" .
  # Should return nothing
  ```

---

## 📁 Files to Commit

### Required Files

- [x] `README.md` - Project documentation
- [x] `DEPLOYMENT.md` - Deployment guide
- [x] `.gitignore` - Protects secrets
- [x] `.env.example` - Template (with placeholders only!)
- [x] `requirements.txt` - Python dependencies
- [x] `app.py` - Main application
- [x] `config.py` - Configuration
- [x] All files in `utils/`, `data/`, `prompts/`, `assets/`

### Files to EXCLUDE

- [ ] `.env` - **NEVER commit this!**
- [ ] `venv/` - Virtual environment
- [ ] `__pycache__/` - Python cache
- [ ] `.streamlit/secrets.toml` - Local secrets

---

## 🔍 Final Verification

### 1. Check Git Status

```bash
git status
```

**Verify:**
- `.env` is NOT in the list
- Only intended files are staged

### 2. Review Changed Files

```bash
git diff --cached
```

**Look for:**
- No API keys visible
- No sensitive data
- No personal information

### 3. Test .gitignore

```bash
# This should show no .env file
git ls-files | grep ".env"
```

### 4. Check for Secrets

```bash
# Search for common API key patterns
grep -r "AIza" --exclude-dir=venv --exclude=".env" .
grep -r "sk-" --exclude-dir=venv --exclude=".env" .
grep -r "api_key.*=" --exclude-dir=venv --exclude=".env" . | grep -v "your_.*_key"
```

**All should return nothing or only safe placeholders!**

---

## 🚀 Safe to Commit Commands

```bash
# 1. Add files (excluding .env automatically due to .gitignore)
git add .

# 2. Double-check what you're committing
git status

# 3. Commit with meaningful message
git commit -m "Initial commit: Jua Smart Solar Advisor v2.1"

# 4. Push to GitHub
git push origin main
```

---

## ⚠️ If You Accidentally Commit a Secret

### Immediate Actions:

1. **DO NOT just delete the file!** (It's still in Git history)

2. **Revoke the exposed API key immediately:**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Delete the exposed key
   - Generate a new one

3. **Remove from Git history:**
   ```bash
   # Using git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --invert-paths --path .env

   # Or using BFG Repo-Cleaner
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

4. **Force push (dangerous!):**
   ```bash
   git push origin main --force
   ```

5. **Update your new API key:**
   - Add new key to `.env` locally
   - Add to deployment platform secrets

---

## ✅ Post-Commit Verification

After pushing to GitHub:

1. **Check GitHub repository:**
   - Browse files on GitHub.com
   - Verify `.env` is NOT visible
   - Check `.gitignore` is present

2. **Check a random file:**
   - Open a code file (like `app.py`)
   - Search for API key patterns
   - Should only see `os.getenv()` calls

3. **Verify secrets protection:**
   - Try viewing `.env` on GitHub
   - Should show "404: This file is not in the repository"

---

## 🎯 Ready for Deployment

Once verified safe:

1. ✅ All secrets protected
2. ✅ Code pushed to GitHub
3. ✅ `.gitignore` working correctly
4. ✅ No sensitive data exposed

**You can now deploy following DEPLOYMENT.md!**

---

<div align="center">
  <p><strong>Security First! 🔒</strong></p>
  <p>Always double-check before committing</p>
</div>
