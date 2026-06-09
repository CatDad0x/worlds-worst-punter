#!/bin/bash
# Run this any time you want to refresh data and push to the live site
# It fetches latest odds, rebuilds the site, and pushes to GitHub (Netlify auto-deploys)

echo "🔄 Fetching latest odds data..."
python3 fetch_all_data.py

echo "🏗  Rebuilding site..."
python3 build_site.py

echo "📤 Pushing to GitHub..."
git add index.html
git commit -m "Update: $(date '+%d %b %Y %H:%M')"
git push

echo "✅ Done! Netlify will deploy in ~30 seconds."
