# Deployment Guide

## Option 1: Streamlit Community Cloud (Recommended — Free & Easiest)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Create a new app:
   - Select your repo: `Tee808-bigD/AI-Expense-Procurement-Auditor`
   - Branch: `main`
   - Main file path: `dashboard/app.py`
4. Add secrets:
   - Click "Advanced settings"
   - Add `GOOGLE_API_KEY` = your actual API key
5. Deploy

## Option 2: Render (Free Tier)

1. Create a `render.yaml` or use the web UI
2. Set build command: `pip install -r requirements.txt && python data/db_setup.py`
3. Set start command: `streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add environment variable: `GOOGLE_API_KEY`
5. Deploy

## Option 3: Docker

```bash
docker build -t expense-auditor .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key_here expense-auditor
```

## Pre-Deployment Checklist

- [ ] `requirements.txt` is complete and tested on a fresh environment
- [ ] `.env.example` has all required variables documented
- [ ] `.gitignore` excludes `.env`, `*.db`, `output/`
- [ ] No API keys or secrets are in the repository
- [ ] The dashboard loads without errors on a fresh machine
- [ ] The live URL is public (no login required)
- [ ] The live URL works on mobile
- [ ] The video is uploaded to YouTube and is public/unlisted
- [ ] The Kaggle Writeup is submitted before the deadline
