# Quick Start Checklist — Win the Kaggle Capstone

## Deadline: July 6, 2026 at 11:59 PM PT

## PHASE 1: CODE FIXES (Day 1-2)

- [ ] Replace `dashboard/app.py` with the enhanced version
- [ ] Replace `README.md` with the complete version
- [ ] Add `.env.example` to repo
- [ ] Add `.gitignore` to repo
- [ ] Add `Dockerfile` to repo
- [ ] Add `packages.txt` to repo
- [ ] Add `agent.py` to repo root
- [ ] Add `agents/__init__.py` to repo
- [ ] Verify `requirements.txt` has all dependencies
- [ ] Test the full pipeline: `python agents/orchestrator.py`
- [ ] Test the dashboard: `streamlit run dashboard/app.py`
- [ ] Test ADK CLI: `adk run .`

## PHASE 2: DEPLOYMENT (Day 3-4)

- [ ] Deploy to Streamlit Community Cloud
- [ ] Test the live URL on mobile
- [ ] Add the live URL to README.md and Kaggle Writeup

## PHASE 3: VIDEO (Day 5-7)

- [ ] Follow VIDEO_SCRIPT.md
- [ ] Record screen at 1920x1080
- [ ] Keep it under 5 minutes
- [ ] Upload to YouTube as Public or Unlisted
- [ ] Add video to Kaggle Writeup Media Gallery

## PHASE 4: KAGGLE WRITEUP (Day 8-10)

- [ ] Copy KAGGLE_WRITEUP.md into Kaggle Writeup
- [ ] Fill in your YouTube link, live demo URL, GitHub repo URL
- [ ] Add cover image to Media Gallery
- [ ] Keep under 2,500 words
- [ ] Select "Agents for Business" track
- [ ] Submit before deadline

## PHASE 5: FINAL POLISH (Day 11-14)

- [ ] Test the entire flow on a fresh machine
- [ ] Verify no API keys in repo: `git grep -i "api_key"` returns nothing
- [ ] Verify `.env` is gitignored
- [ ] Create architecture diagram PNG in `docs/`
- [ ] Add LICENSE file
- [ ] Star your own repo
