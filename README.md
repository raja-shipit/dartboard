# Dartboard Fletch — BESS Intelligence Dashboard

A permanent internal dashboard for the Dartboard team, hosted on GitHub Pages.

**Live URL:** `https://dartboard.github.io/fletch-bess/`
*(Update this after you create the repo)*

## Pages
| Page | File | Description |
|------|------|-------------|
| BESS Map | `index.html` | Interactive US map of all BESS plants |
| Pipeline | `pipeline.html` | *(coming soon)* EIA-860M monthly leads |
| Insurance Brief | `insurance.html` | *(coming soon)* Regional risk dashboard |
| ML Labels | `ml.html` | *(coming soon)* Failure/retirement analysis |

## How to update the dashboard

1. Edit any `.html` file in this folder
2. Run:
   ```bash
   git add .
   git commit -m "update: describe your change"
   git push
   ```
3. GitHub Pages auto-deploys in ~30 seconds. Everyone sees the update immediately at the same URL.

## First-time setup (do once)

```bash
cd ~/Documents/dartboard_fletch/github_pages

# Initialize git
git init
git branch -M main

# Connect to your GitHub repo (create it first at github.com/dartboard)
git remote add origin https://github.com/dartboard/fletch-bess.git

# Push
git add .
git commit -m "initial: Dartboard Fletch BESS dashboard"
git push -u origin main

# Enable GitHub Pages:
# → Go to repo Settings → Pages → Source: Deploy from branch → Branch: main → / (root) → Save
# Your URL will be: https://dartboard.github.io/fletch-bess/
```

## Access control (Google SSO via Cloudflare Access — recommended)

Protects the URL so only @dartboard.com Google accounts can access it:

1. Add your site to Cloudflare (free): https://dash.cloudflare.com
2. Go to **Zero Trust → Access → Applications → Add an application**
3. Select **Self-hosted** → enter your GitHub Pages URL
4. Under **Policies**, set rule: `Emails ending in` → `Dartboard`
5. Identity provider: **Google Workspace**
6. Save

Now anyone hitting the URL gets a Google login prompt first. No shared passwords.
