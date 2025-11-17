# Spotify + Terraform + AI - Automated Playlist Pipeline

A local, end-to-end pipeline that turns AI playlist ideas into *real* Spotify playlists reproducibly and version-controlled with Terraform.

This README is a complete. It includes everything you need: setup, how the pipeline works, exact commands for PowerShell and bash, safe environment handling, Terraform snippets, troubleshooting checks (echo commands), and tips to avoid the common pitfalls we fixed while building the project.

_NOTE:- Before using this repoistory it is advised you refer to https://github.com/Arhamjain1/spotify_terraform to understand how spotify and terraform are working._
## Table of contents

* [What this does](#what-this-does)
* [Why this approach](#why-this-approach)
* [Repository layout (what each file does)](#repository-layout-what-each-file-does)
* [Prerequisites](#prerequisites)
* [One-time setup](#one-time-setup)
* [Run the pipeline (quickstart)](#run-the-pipeline-quickstart)
* [Key file examples (paste-ready)](#key-file-examples-paste-ready)

  * `ai_curation.py` (super-strict prompt)
  * `spotify_lookup.py` (title+artist fuzzy matching)
  * `generate_tf.py` (converts to Terraform locals)
  * `playlist.tf` / `provider.tf` / `variables.tf` (Terraform)
* [Run helpers (optional)](#run-helpers-optional)
* [Troubleshooting checklist & quick commands](#troubleshooting-checklist--quick-commands)
* [Advanced notes local provider binary](#advanced-notes--local-provider-binary)
* [Security, best practices & next steps](#security-best-practices--next-steps)
* [License](#license)

---

## What this does

* Optionally uses Gemini (LLM) to generate a playlist idea (`playlist_songs.json`) using a **super-strict** prompt to minimize hallucinations.
* Resolves each AI suggestion to a real Spotify track using the Spotify Web API (`spotify_results.json`).
* Converts matched Spotify results into Terraform-friendly data (URIs like `spotify:track:...`) (`generated_tracks.tf`).
* Uses Terraform with the Spotify provider to create/update a playlist and add tracks in your Spotify account.

Everything runs locally no cloud required and is reproducible via Git + Terraform.

---

## Why this approach

* **AI → real-world**: LLMs are creative but hallucinate. This pipeline validates every suggestion against Spotify, so you only push real tracks.
* **Versioned infra**: Storing the playlist as Terraform config makes changes auditable, reversible, and shareable.
* **Local-first**: Works on Windows, macOS, and Linux; uses `.env` for secrets.

---

## Repository layout (what each file does)

```
Spotify_TF/
├─ ai_curation.py        # OPTIONAL: Gemini prompt → playlist_songs.json (super-strict)
├─ playlist_songs.json   # LLM output (title + artist list)
├─ spotify_lookup.py     # Resolve LLM list → spotify_results.json
├─ spotify_results.json  # Search results with spotify_url / match_score
├─ generate_tf.py        # Convert spotify_results.json → generated_tracks.tf
├─ generated_tracks.tf   # Terraform locals with spotify:track:... URIs
├─ playlist.tf           # Terraform playlist + resource that consumes locals
├─ provider.tf           # Terraform provider config
├─ variables.tf          # Terraform variables (no duplicates)
├─ .env                  # secrets (GEMINI_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
└─ README.md
```

---

## Prerequisites

* Python 3.10+
* Terraform 1.3+
* A Spotify Developer App (Client ID & Client Secret) - [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
* (Optional) Google Gemini API key for AI step
* Python packages:

  * `requests`
  * `python-dotenv`
  * `rapidfuzz` (or use `difflib`)
  * `google-genai` (only if using Gemini)

Install Python dependencies:

```bash
python -m venv .venv
# PowerShell:
.\.venv\Scripts\Activate
# bash:
source .venv/bin/activate

pip install requests python-dotenv rapidfuzz google-genai
```

---

## One-time setup

1. **Create `.env`** (DO NOT commit)

```text
GEMINI_API_KEY=your_gemini_api_key_here     # optional
SPOTIFY_CLIENT_ID=CLIENT_ID
SPOTIFY_CLIENT_SECRET=CLIENT_SECRET
```

2. **Verify environment variables**
   PowerShell:

```powershell
# Show (or test) env values in current shell
echo $env:SPOTIFY_CLIENT_ID
echo $env:SPOTIFY_CLIENT_SECRET
```

bash:

```bash
export SPOTIFY_CLIENT_ID=CLIENT_ID
export SPOTIFY_CLIENT_SECRET=CLIENT_SECRET
echo $SPOTIFY_CLIENT_ID
```

3. **(Optional) Put provider binary** (only if using a local provider binary) - see the Advanced section below.

---

## Run the pipeline (quickstart)

> Assumes `.env` is configured and venv activated.

1. **(Optional) Generate AI suggestions (Gemini, strict mode)**

```powershell
python ai_curation.py "lofi studying late night" -n 15 -o playlist_songs.json
```

This writes `playlist_songs.json` with `{"songs":[{"title":"...", "artist":"..."}]}`.

2. **Resolve AI suggestions to Spotify**

```bash
python spotify_lookup.py
# reads playlist_songs.json and writes spotify_results.json
```

3. **Generate Terraform track data**

```bash
python generate_tf.py
# writes generated_tracks.tf which exposes `local.generated_tracks` (list of { id = "spotify:track:..." })
```

4. **Apply with Terraform**

```bash
terraform init
terraform plan
terraform apply
```

Terraform will create the playlist and add tracks (confirm plan before apply).

---

## Key file examples (paste-ready)

Below are the paste-ready examples for the core files. Replace values where needed.

---

### `ai_curation.py` - super-strict prompt (USE AS-IS IF YOU HAVE GEMINI)

This file exists in the repo already; here is the *super-strict* prompt snippet used by the script:

```python
prompt = f"""
You MUST follow these rules STRICTLY:
1. Only suggest songs that definitely exist on Spotify.
2. Use well-known, globally released tracks from verified artists.
3. Absolutely DO NOT create fictional songs or fictional artists.
4. If you are not 100% certain a song exists on Spotify, DO NOT include it.
Task: Suggest EXACTLY {n} songs for the playlist theme: "{theme}"
Output ONLY valid JSON:
{{
  "songs": [
    {{"title": "Song Name", "artist": "Artist Name"}},
    ...
  ]
}}
"""
```

> This reduces hallucinations. You **must still** validate results against Spotify (see step 2 above).

---

### `spotify_lookup.py` - resolve to Spotify (title+artist fuzzy matching)

A script that reads `playlist_songs.json`, obtains a Client Credentials token, queries Spotify, and writes `spotify_results.json`. Ensure your copy converts Spotify URLs → URIs or includes `spotify_url` in output.

(Already there in the repo; keep it; it should output `spotify_url` for each match.)

---

### `generate_tf.py` - convert search results to Terraform locals

This converts `spotify_results.json` into `generated_tracks.tf` (a `locals` block). Use the version that converts URLs into `spotify:track:ID` and writes a `local.generated_tracks` list:

Example output `generated_tracks.tf` structure:

```hcl
locals {
  generated_tracks = [
    { id = "spotify:track:3ukklz..." },
    { id = "spotify:track:2dphvm..." },
    ...
  ]
}
```

(If your `generate_tf.py` writes a different filename, use that name in Terraform.)

---

### `provider.tf` (example)

```hcl
terraform {
  required_providers {
    spotify = {
      source  = "conradludgate/spotify"
      version = "~> 0.2"
    }
  }
}

provider "spotify" {
  api_key = var.api_key
}
```

### `variables.tf`

```hcl
variable "api_key" {
  type = string
  description = "Spotify provider API key (if provider requires it)."
}
```

### `playlist.tf` - create playlist + attach tracks

This example expects `local.generated_tracks` (from `generated_tracks.tf`).

```hcl
resource "spotify_playlist" "ai_playlist" {
  name        = "AI Generated Playlist"
  description = "Generated via AI + Terraform"
  public      = false
}

locals {
  tracks = local.generated_tracks
}

# Create one resource per track using for_each; provider must support this resource
resource "spotify_playlist_track" "generated" {
  for_each    = { for idx, t in local.tracks : idx => t }
  playlist_id = spotify_playlist.ai_playlist.id
  track_id    = each.value.id
}
```

> Note: Some provider versions use a multi-track resource (`spotify_playlist_tracks`) instead. If you get `Invalid resource type`, switch to the multi-track resource pattern shown earlier in this repo history or consult provider docs.

---

## Run helpers (optional)

If you prefer a single command, here are small scripts you can add to automate safety checks.

### `run_all.ps1` (PowerShell)

```powershell
# run_all.ps1
# run entire pipeline (PowerShell)

# Ensure env loaded (if using .env file and python-dotenv isn't used)
# $env:SPOTIFY_CLIENT_ID="..."
# $env:SPOTIFY_CLIENT_SECRET="..."

python ai_curation.py "lofi studying late night" -n 15 -o playlist_songs.json
python spotify_lookup.py
python generate_tf.py

terraform init
terraform plan
Write-Host "If plan looks good: run `terraform apply`"
```

### `run_all.sh` (bash)

```bash
#!/usr/bin/env bash
python ai_curation.py "lofi studying late night" -n 15 -o playlist_songs.json
python spotify_lookup.py
python generate_tf.py

terraform init
terraform plan
echo "If plan looks good: run 'terraform apply'"
```

---

## Troubleshooting checklist & quick commands

Copy-paste these to inspect and diagnose common issues.

### Check `.env` exists and contents

PowerShell:

```powershell
Get-Content .env
```

bash:

```bash
cat .env
```

### Verify Spotify env vars in current shell

PowerShell:

```powershell
echo $env:SPOTIFY_CLIENT_ID
echo $env:SPOTIFY_CLIENT_SECRET
```

bash:

```bash
echo "$SPOTIFY_CLIENT_ID"
echo "$SPOTIFY_CLIENT_SECRET"
```

### Check `spotify_results.json` content

```bash
# macOS / Linux
jq . spotify_results.json | less
# Windows PowerShell
Get-Content spotify_results.json -Raw | ConvertFrom-Json
```

### If `generate_tf.py` produced empty file

* Print debug:

```powershell
python generate_tf.py
# It should print loaded tracks. If empty, fix spotify_lookup output to include spotify_url or uri.
```

### Delete Terraform lock and re-init (if switching provider binary)

PowerShell:

```powershell
del .terraform.lock.hcl
terraform init
```

bash:

```bash
rm .terraform.lock.hcl
terraform init
```

### View generated TF file quickly

PowerShell:

```powershell
Get-Content generated_tracks.tf -TotalCount 200
```

bash:

```bash
sed -n '1,200p' generated_tracks.tf
```

### If Terraform shows `No changes` after apply

* Ensure `playlist.tf` contains resources that use `local.generated_tracks`. If you only have a `locals` block and no resources consuming it, Terraform will do nothing.

### If provider says `Invalid resource type`

* Check the provider version. Use `terraform providers` and consult provider docs. Either:

  * install a provider version that supports `spotify_playlist_track`, or
  * adapt `playlist.tf` to use the provider's supported resource (e.g., `spotify_playlist_tracks`).

---

## Advanced notes - local provider binary

If you downloaded a local provider (custom binary), Terraform expects it under the plugins directory:

**Windows PowerShell:**

```powershell
$dst = "$env:APPDATA\terraform.d\plugins\registry.terraform.io\conradludgate\spotify\1.0.0\windows_amd64"
New-Item -ItemType Directory -Force -Path $dst
Copy-Item ".\terraform-provider-spotify\terraform-provider-spotify.exe" -Destination "$dst\terraform-provider-spotify_v1.0.0.exe"
# Remove lock and init
del .terraform.lock.hcl
terraform init
```

**macOS / Linux:** copy into `~/.terraform.d/plugins/registry.terraform.io/conradludgate/spotify/1.0.0/<os_arch>/`

---
