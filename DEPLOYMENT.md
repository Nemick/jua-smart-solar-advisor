# 🚀 Deployment Guide - Jua Smart

This guide provides step-by-step instructions for deploying Jua Smart Solar Advisor for free.

---

## 🎯 Recommended: Streamlit Cloud (100% Free)

**Why Streamlit Cloud?**
- ✅ Completely free for public apps
- ✅ Automatic deployments from GitHub
- ✅ Built-in secrets management
- ✅ Easy updates (just push to GitHub)
- ✅ Custom subdomain

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Make sure your changes are committed
git add .
git commit -m "Prepare for deployment"

# Push to GitHub
git push origin main
```

#### 2. Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. You'll get free hosting instantly!

#### 3. Deploy Your App

1. Click **"New app"** button
2. Configure your deployment:
   - **Repository**: Select `jua-smart-solar-advisor`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. Click **"Advanced settings"**
4. Add your API key in **Secrets**:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
5. Click **"Deploy"**

#### 4. Wait for Deployment (2-3 minutes)

Streamlit will:
- Install dependencies from `requirements.txt`
- Run your app
- Give you a public URL

#### 5. Your App is Live! 🎉

- URL: `https://your-app-name.streamlit.app`
- Share it with anyone!
- Updates automatically when you push to GitHub

### Managing Your Deployment

**View Logs:**
- Click the hamburger menu (☰) on your app
- Select "Manage app"
- View logs, analytics, and settings

**Update Secrets:**
- Go to app settings → Secrets
- Edit and save
- App will restart automatically

**Reboot App:**
- In the hamburger menu: "Reboot app"
- Useful after updating secrets

---

## 🤗 Alternative: Hugging Face Spaces

**Free tier includes:**
- 2 vCPU cores
- 16 GB RAM
- 50 GB storage
- Custom domain option

### Deployment Steps

1. **Create a Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select "Streamlit" as the SDK

2. **Add Your Files**
   ```bash
   # Clone the Space
   git clone https://huggingface.co/spaces/YOUR_USERNAME/jua-smart
   
   # Add your files
   cp -r * ../jua-smart/
   cd ../jua-smart
   
   # Commit and push
   git add .
   git commit -m "Initial deployment"
   git push
   ```

3. **Add Secrets**
   - Go to Space settings → Repository secrets
   - Add `GEMINI_API_KEY`

4. **Your Space is Live!**
   - URL: `https://huggingface.co/spaces/YOUR_USERNAME/jua-smart`

---

## 🚂 Alternative: Railway.app

**Free tier:**
- $5 monthly credit
- Great for hobby projects

### Deployment Steps

1. **Connect GitHub**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

2. **Configure**
   - Select your repository
   - Railway auto-detects Streamlit
   - Add environment variable: `GEMINI_API_KEY`

3. **Generate Domain**
   - Settings → Generate Domain
   - Get a public URL

**Note:** Free tier has usage limits. Monitor your credits.

---

## 🎨 Alternative: Render.com

**Free tier:**
- 750 hours/month
- Auto-deploy from Git

### Deployment Steps

1. **Create Web Service**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repository

2. **Configure Build**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT`

3. **Add Environment Variables**
   - Add `GEMINI_API_KEY`
   - Add `PORT` (Render provides this)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets

✅ **DO:**
- Use `.env` for local development
- Add `.env` to `.gitignore`
- Use platform secrets for deployment

❌ **DON'T:**
- Hardcode API keys in code
- Commit `.env` to Git
- Share keys in public repos

### 2. Use Environment Variables

**Streamlit Cloud:**
```toml
# In Streamlit Cloud Secrets
GEMINI_API_KEY = "your_key_here"
```

**Other Platforms:**
```bash
# Set via platform UI or CLI
GEMINI_API_KEY=your_key_here
```

### 3. Rotate Keys Regularly

If you suspect your key is exposed:
1. Go to [AI Studio](https://aistudio.google.com/app/apikey)
2. Delete the old key
3. Generate a new one
4. Update in deployment platform

---

## 📊 Monitoring & Maintenance

### Streamlit Cloud

- **Analytics**: Built-in viewer analytics
- **Logs**: Real-time logging in the dashboard
- **Alerts**: Email notifications for errors

### Error Handling

Common issues:

1. **Module not found**
   - Check `requirements.txt` is complete
   - Verify Python version compatibility

2. **API key not found**
   - Verify secrets are set correctly
   - Check variable name matches code

3. **Out of memory**
   - Optimize data loading
   - Use caching (`@st.cache_data`)

---

## 🎯 Performance Tips

### 1. Use Caching

Already implemented in the app:
```python
@st.cache_data(ttl=3600)
def load_all_data():
    # Cached for 1 hour
```

### 2. Optimize Images

- Use compressed images
- Serve via CDN if needed

### 3. Monitor Usage

- Track API calls to Gemini
- Stay within free tier limits

---

## 🆘 Troubleshooting

### Issue: App won't start

**Check:**
- `requirements.txt` includes all dependencies
- Python version is compatible (3.9+)
- No syntax errors in code

### Issue: API errors

**Check:**
- `GEMINI_API_KEY` is set correctly
- Key has not been revoked
- API quotas not exceeded

### Issue: Slow performance

**Solutions:**
- Enable caching
- Optimize data loading
- Reduce API calls

---

## 📞 Getting Help

- **Streamlit Forums**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Create an issue in your repo
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)

---

## 🎉 Success!

Your Jua Smart Solar Advisor is now deployed and accessible worldwide!

**Share your deployment:**
- Post on social media
- Share with the solar community
- Help Kenyans go solar! ☀️

---

<div align="center">
  <p><strong>Happy Deploying! 🚀</strong></p>
  <p>Made with ❤️ for Kenya 🇰🇪</p>
</div>
