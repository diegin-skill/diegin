---
name: gh-publish
description: "Publish or update Codex skills to GitHub. Use when the user asks to: push code to GitHub, create a repository, make a release, set repository topics, update a GitHub repo, or login to GitHub for publishing. Covers the full workflow: browser-based GitHub login via Edge CDP, git push, release creation, and topic management."
---

# GitHub Publish Skill

Automate publishing/updating Codex skill repositories on GitHub.

## Prerequisites

- **Edge browser** installed at known path (configurable)
- **Git** available (`git --version`)
- **Python** with `websocket`, `requests` packages
- **Network proxy** (default: `http://127.0.0.1:3067`; configurable)

## Workflow

### 1. Login & Get Token

```powershell
python S:\gh-publish-skill\scripts\gh_publish.py login
```

What happens:
- Opens Edge with CDP debug port → navigates to GitHub login
- If not logged in → **user must log in interactively** in the browser, then press Enter
- Creates a Personal Access Token (classic) with `repo` scope
- Token saved to `.gh_token` for reuse

### 2. Push Code Changes

```powershell
python S:\gh-publish-skill\scripts\gh_publish.py push `
  --owner diegin-skill --repo diegin `
  --message "Update: added new feature" `
  --dir S:\diegin-skill
```

- `--dir`: repo root folder (default: parent of `scripts/`)
- Auto-detects changes via `git status`
- Handles proxy, auth, remote URL

### 3. Create Release

```powershell
python S:\gh-publish-skill\scripts\gh_publish.py release `
  --owner diegin-skill --repo diegin `
  --tag v1.1.0 --name "v1.1.0 - New Features" `
  --body "## Changelog\n\n- Feature A\n- Bug fix B" `
  --prerelease
```

- Creates annotated git tag + pushes to GitHub
- Creates GitHub Release with notes
- Omit `--prerelease` for production releases

### 4. Set Repository Topics

```powershell
python S:\gh-publish-skill\scripts\gh_publish.py topics `
  --owner diegin-skill --repo diegin `
  --topics codex codex-skill ai-agent self-evolving dgen
```

Default topics: `codex codex-skill ai-agent self-evolving dgen`

### 5. Raw API Call

```powershell
python S:\gh-publish-skill\scripts\gh_publish.py api `
  --method GET --path /repos/diegin-skill/diegin
python S:\gh-publish-skill\scripts\gh_publish.py api `
  --method PATCH --path /repos/diegin-skill/diegin `
  --data '{"description":"New description"}'
```

## Full Update Example (All Steps)

```powershell
# 1. Login (first time only)
python S:\gh-publish-skill\scripts\gh_publish.py login

# 2. Push changes
python S:\gh-publish-skill\scripts\gh_publish.py push `
  --owner diegin-skill --repo diegin `
  --message "v1.1.0 update" --dir S:\diegin-skill

# 3. Create release
$notes = @"
## v1.1.0

### Changes
- Feature 1
- Feature 2
"@
python S:\gh-publish-skill\scripts\gh_publish.py release `
  --owner diegin-skill --repo diegin `
  --tag v1.1.0 --name "v1.1.0" --body $notes

# 4. Update topics
python S:\gh-publish-skill\scripts\gh_publish.py topics `
  --owner diegin-skill --repo diegin
```

## Troubleshooting

| Issue | Fix |
|:---|:---|
| "No token" | Run `login` first |
| Token expired | Delete `.gh_token` file, re-run `login` |
| Edge won't start | Check `EDGE_PATH` in script |
| Git push timeout | Check proxy config in `PROXY` var |
| CDP port conflict | Kill other Edge instances first |

## Configuration

Edit `S:\gh-publish-skill\scripts\gh_publish.py` top section:

```python
PROXY = "http://127.0.0.1:3067"       # Network proxy
EDGE_DEBUG_PORT = 9222                 # CDP debug port
EDGE_PATH = r"D:\path\to\msedge.exe"   # Edge executable
TOKEN_FILE = ".../.gh_token"           # Saved token path
```
