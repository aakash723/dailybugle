# World Comics — Interactive 3D Comic Library

> A single-page web application that renders a **3D comic library scene** (Babylon.js), provides an **auth gate**, a **comic grid** with search/filter, a **turn.js flipbook reader** + **PDF.js viewer**, and a **video player** — all client-side, hosted on **GitHub Pages** with assets served via **Git LFS CDN**.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture & Backend Infrastructure](#architecture--backend-infrastructure)
4. [Key Features](#key-features)
5. [Comic Library (21 Series, 116 Issues)](#comic-library-21-series-116-issues)
6. [Tools & Bots](#tools--bots)
    - [Comic Downloader Bot](#1-comic-downloader-bot)
    - [Thumbnail Generator](#2-thumbnail-generator-generate_thumbspy)
    - [Image Color Converter](#3-image-color-converter-convert_fin_comics_whitepy)
    - [Video Compressor](#4-video-compressor-compress_special_videops1)
    - [Layout Editors](#5-layout-editors-editorhtml--editor2html)
7. [CDN & Storage Strategy](#cdn--storage-strategy)
8. [Git Commit History](#git-commit-history)
9. [Project Structure](#project-structure)
10. [Mobile vs Desktop](#mobile-vs-desktop)
11. [Setup & Installation](#setup--installation)
12. [Deployment](#deployment)
13. [Bonus: Pokemon Flipbook](#bonus-pokemon-flipbook)
14. [Credits & Data Sources](#credits--data-sources)

---

## Project Overview

**World Comics** is a fully client-side web application built to showcase, browse, read, and organize digital comic books. It features:

- A **3D scene** (Babylon.js) with rotating comic planes, a laptop playing video, and hover interactions
- An **auth gate** (signup/signin) that controls access on desktop
- A **comic grid** organized into Marvel and DC sections with thumbnail covers
- Two **reader modes**: turn.js flipbook (page-flip animation) and PDF.js (full-page viewer)
- A **video player** that opens a full-screen video.js overlay on laptop click
- **Search & filter** across the entire library
- A **persistent library** (localStorage) for saving favorites
- An **admin panel** for file upload/delete
- Full **mobile optimization** — the 3D scene and auth gate are skipped on mobile (<768px)

All 116 comic PDFs, 142+ PNG thumbnails, and video assets are stored in **Git LFS** and served via **media.githubusercontent.com** (GitHub's LFS CDN), which provides proper CORS headers.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **3D Rendering** | Babylon.js 4.x (WebGL) |
| **Flipbook Reader** | turn.js v4.1.0 (jQuery plugin) |
| **PDF Viewer** | PDF.js |
| **Video Player** | video.js (full-screen overlay) |
| **Layout Library** | jQuery 3.7.1 |
| **Styling** | Vanilla CSS (no framework) |
| **Storage (client)** | localStorage (auth, library, editor layouts) |
| **Asset Storage** | Git LFS (PDFs, PNGs, MP4s) |
| **CDN** | media.githubusercontent.com (CORS-enabled) |
| **Hosting** | GitHub Pages |
| **Downloader Scripts** | Python 3 (PyMuPDF, img2pdf, tkinter, ThreadPoolExecutor) |
| **Video Compression** | PowerShell + FFmpeg |

---

## Architecture & Backend Infrastructure

Despite being a **client-side** application, World Comics relies on a robust backend infrastructure — it just isn't code we wrote:

| Component | What It Does |
|-----------|-------------|
| **GitHub + Git LFS** | Stores 264 LFS objects (116 PDFs ~6.1 GB, 142+ PNGs, MP4s, ZIPs). All assets version-controlled and served from GitHub's infrastructure. |
| **GitHub Pages** | Static hosting for `index.html`, CSS, JavaScript, and library files. No server-side processing needed — just serves the app. |
| **media.githubusercontent.com** | Git LFS CDN — serves all binary assets (PDFs, PNGs, MP4s) with `Access-Control-Allow-Origin: *` headers, enabling cross-origin canvas operations. |
| **ysk-comics.com API** | Third-party backend that provides comic page data — consumed by the downloader bots. |
| **localStorage (browser)** | Client-side persistence for user accounts (`deco_accounts`), saved library (`deco_library`), editor layouts (`editor_layout`), and user name (`deco_name`). |

**What we DON'T have**: no custom application server (no Express, FastAPI, Flask, etc.), no SQL/NoSQL database, no server-side sessions, no custom API endpoints. Everything runs in the user's browser.

---

## Key Features

### 3D Scene (Desktop Only)
- 8 rotating comic planes positioned around a central `comics.glb` 3D model
- Each plane displays a comic cover using `BABYLON.Texture` (loaded directly from CDN URL)
- Camera position: `[-4.22, 1.24, 1.59]` with rotation `[0, π, 0]` and FOV `1.27 × 0.9`
- Laptop plane plays `videoplayback.mp4`; click opens full-screen video.js overlay
- Hover highlight: planes scale up by 1.22× on mouseenter
- Texture correction: PNGs are flipped vertically (`vScale = -1`, `vOffset = 1`) to match cube map orientation

### Auth Gate (Desktop Only)
- Full-page overlay shown on first visit (no `deco_name` in localStorage)
- Two tabs: **Create Account** (name, email, password, favorite comic) and **Sign In** (email + password)
- Credentials stored in `localStorage.deco_accounts` as `{email: {password, name, favorite}}`
- On successful auth: plays `loding.mp4` (loading video) as transition animation
- Returning visitors skip auth gate automatically
- Mobile (<768px) bypasses auth entirely — goes straight to overlay

### Comic Grid
- Organized in **Marvel** and **DC** sections (also shows Library section)
- Each card shows a **PNG thumbnail cover** drawn on a `<canvas>` element
- Thumbnails generated from PDF first pages via `generate_thumbs.py`
- Cards show: cover, title, issue number, Read / Download / Add to Library buttons
- **Event delegation**: single `document.addEventListener` handles all card interactions via `e.target.closest()`
- **Search bar**: filters comics by title in real-time

### Readers
1. **Flipbook** (turn.js) — page-flip animation, requires jQuery
2. **PDF.js** — scrollable full-page view using Mozilla's PDF renderer
3. **Swipe support** (mobile) — touchstart/touchend events detect >40px swipe gestures for page navigation
4. Mobile reader: scrollable top bar with `white-space: nowrap` and touch scrolling

### Library
- **Add to Library** button on each comic card
- Persisted in `localStorage` as `deco_library` (array of comic IDs)
- Separate Library section in the comic grid showing saved comics
- **Remove from Library** button for each saved comic

### Video Player
- Laptop in 3D scene plays `videoplayback.mp4` via CDN
- Click on the laptop opens a full-screen video.js overlay
- Video controls: play, pause, seek, volume, full-screen toggle

### Deco Overlay
- `overlay.png`: full-viewport edge-to-edge element (`100vw × 100vh`, `object-fit: cover`)
- Non-interactable (`pointer-events: none`)
- Two additional decorative images positioned with absolute px values in `#decoContainer`
- `#decoContainer` uses `top/left` instead of `inset`, no `overflow: hidden` to avoid clipping negative-x images
- All deco elements hidden in reader mode

### Admin Panel
- File upload via browser API
- File delete capability
- Inline in the overlay UI

---

## Comic Library (21 Series, 116 Issues)

All comics downloaded from **ysk-comics.com** via the downloader bot. Each issue stored as PDF (~30–50 MB each) with a PNG cover thumbnail (300px wide).

### Marvel Series
| Series | Issues | Folder |
|--------|--------|--------|
| Alien 3 (2018) | #1–5 | `all_comics/Alien 3(2018)/` |
| Carnage Eddie Brock (2025) | #1–6 | `all_comics/Carnage Eddie Brock(2025)/` |
| Daredevil (2023) | #1–11 | `all_comics/Daredevil(2023)/` |
| Doctor Strange of Asgard (2025) | #1–5 | `all_comics/Doctor Strange of Asgard(2025)/` |
| Hellverine (2024) | #1–4 | `all_comics/Hellverine(2024)/` |
| Spider-Girl (2025) | #1–5 | `all_comics/Spider-Girl(2025)/` |
| Star Wars: Target Vader (2019) | #1–6 | `all_comics/Star Wars Target Vader(2019)/` |
| Thor God of Thunder (2022) | #1–7 | `all_comics/Thor God of Thunder(2022)/` |

### DC Series
| Series | Issues | Folder |
|--------|--------|--------|
| Batman Secret Files (2018) | #1–2 | `all_comics/Batman Secret Files(2018)/` |
| Batman The Devastator (2017) | #1 | `all_comics/Batman The Devastator(2017)/` |
| batman (2025) | #1–9 | `all_comics/batman(2025)/` |
| Danger Street (2022) | #1–11 | `all_comics/Danger Street(2022)/` |
| Legends of the Dark Knight (2021) | #1–6 | `all_comics/Legends of the Dark Knight(2021)/` |
| Nightmare Country: The Glass House (2023) | #1–6 | `all_comics/Nightmare Country The Glass House(2023)/` |

### Independent / Other Series
| Series | Issues | Folder |
|--------|--------|--------|
| Black Widow and Hawkeye (2024) | #1–3 | `all_comics/Black Widow and Hawkeye(2024)/` |
| Chandra (2018) | #1–4 | `all_comics/Chandra(2018)/` |
| Deep Target (2021) | #1–7 | `all_comics/Deep Target(2021)/` |
| Edenfrost (2023) | #1–4 | `all_comics/Edenfrost(2023)/` |
| Gunland (2020) | #1–12 | `all_comics/Gunland(2020)/` |
| Nils (2020) | #1–2 | `all_comics/Nils(2020)/` |
| Pretty Deadly: The Rat (2019) | #1–5 | `all_comics/Pretty Deadly The Rat(2019)/` |

---

## Tools & Bots

### 1. Comic Downloader Bot

Located in `comicdownloader_bot/`, this Python tool downloads comics from **ysk-comics.com**.

#### `comic_downloader.py`

- Connects to `http://ysk-comics.com/api` with `API_SECRET = "123456"`
- Fetches comic metadata (title, issue number, page count, page URLs)
- Downloads all pages in parallel using `ThreadPoolExecutor`
- Converts downloaded images to PDF using `img2pdf`
- Supports single-series download

#### `mass_downloader.py`

- Scrapes all available comic slugs from the site's HTML pages
- Iterates through every series and downloads each issue
- Per-series progress bars via `tqdm`
- Respects a **5 GB storage limit** (`MAX_GB = 5`)
- Tracks success/failure counts
- Sequential per-series downloads to avoid overwhelming the server

### 2. Thumbnail Generator (`generate_thumbs.py`)

- Uses **PyMuPDF (`fitz`)** to extract the first page of every PDF in `all_comics/`
- Saves as **300px-wide PNG** (proportional scaling, `MAX_W = 300`)
- Skips directories that already have PNG files (idempotent)
- Generated **105 thumbnails** (~25.6 MB total)
- Run via: `python generate_thumbs.py`

### 3. Image Color Converter (`convert_fin_comics_white.py`)

- Uses **Tkinter's `PhotoImage`** to process `fin.png`
- Scans the right 35% region of the image for black pixels
- Replaces black pixels with white (for text color correction)
- Output: `fin_white_comics.png`
- Used for a decorative text asset in the scene

### 4. Video Compressor (`compress_special_video.ps1`)

- **PowerShell** script using **FFmpeg**
- Input: `the special.mp4`
- Output: `special-compressed.mp4`
- Parameters:
  - Scale: 960×540
  - Video codec: libx264 at CRF 26
  - Audio: AAC at 128 kbps

### 5. Layout Editors (`editor.html` / `editor2.html`)

Two visual 2D canvas editors for composing scene elements:

- **editor.html**: ~25,000 lines, basic layout composer
- **editor2.html**: ~55,000 lines, feature-rich version

Features:
- Add images, text, videos, and geometric shapes to a canvas
- Drag, resize, and rotate elements
- Delete individual elements
- Export layout as JSON to `localStorage` (`editor_layout`)
- Import/export layout files
- Save and load presets

Layout configurations stored as:
- `layout.json` — base64-encoded embedded image layout
- `layout (3).json` — empty layout (`{"elements":[]}`)
- `layout (4).json` — 6-image layout with local PNG references

### 6. Debug / Utility: `dump_layout.html`

A 12-line utility page that reads and displays `localStorage.getItem('editor_layout')` as raw JSON — used for inspecting saved editor layouts during development.

---

## CDN & Storage Strategy

### The Problem
- `raw.githubusercontent.com` (GitHub's raw file server) does **not** send `Access-Control-Allow-Origin: *` headers
- Canvas `drawImage()` and `texImage2D()` in WebGL require CORS headers — without them, the canvas becomes "tainted" and operations throw a SecurityError

### The Solution
- All binary assets (PDFs, PNGs, MP4s) stored in **Git LFS**
- LFS files are served via **`media.githubusercontent.com`** — GitHub's official LFS CDN
- This CDN **does** send `Access-Control-Allow-Origin: *` headers
- Result: `BABYLON.Texture`, canvas `drawImage()`, and all other cross-origin operations work without issues

### Implementation
```javascript
const CDN_URL = 'https://media.githubusercontent.com/media/aakash723/dailybugle/main/';
const thumbURL = (filename) => CDN_URL + filename.replace('.pdf', '.png')
    .replace(/#/g, '%23')
    .replace(/ /g, '%20');
```

### LFS Configuration (`.gitattributes`)
```
*.pdf filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
```

### Storage Stats
- **264 total LFS objects**
- **116 PDFs**: ~6.1 GB total, ~52 MB average
- **142+ PNGs**: ~41 MB (thumbnails + assets)
- **MP4s**: `loding.mp4`, `special.mp4`, `videoplayback.mp4`, `plane10vid.mp4`
- **GitHub Free plan**: LFS is **free and unlimited for public repositories** — no card needed

### CORS Fixes Applied
1. All `Image()` objects set `img.crossOrigin = 'anonymous'` before drawing to canvas
2. Plane textures switched from `DynamicTexture` + `ctx.drawImage()` to `BABYLON.Texture` — loads directly from CDN URL, avoids tainted canvas entirely
3. `raw.githubusercontent.com` URLs completely removed from the codebase

---

## Git Commit History

**47 commits** across the project's lifetime. Key phases:

### Phase 1: Initial Setup (Commits 1–9)
- Initial project commit with full LFS setup
- MEGA integration for cloud storage
- Local comic paths, `comics.glb` 3D model
- Layout editor with save/download functionality
- try-catch around GLB loading for graceful fallback
- Deco elements made non-interactive (`pointer-events: none`)

### Phase 2: CDN Migration (Commits 10–17)
- Switched from MEGA to `raw.githubusercontent.com`
- Added `.nojekyll` for GitHub Pages compatibility
- Migrated all assets to `media.githubusercontent.com` (LFS CDN)
- Fixed `special.mp4` gray video — used CDN_URL instead of relative path
- Fixed PNG thumbnails not loading — used RAW_URL for regular git files

### Phase 3: PNG Thumbnails & Canvas Fixes (Commits 18–24)
- `generate_thumbs.py` with proportional scaling (MAX_W=300)
- PNG thumbnails used for comic card covers
- crossOrigin='anonymous' added to all Image loads
- Switched plane textures from DynamicTexture to BABYLON.Texture (fixes tainted canvas)
- Fixed empty planes: used comicURL for plane thumbnail sources
- CDN_URL used for all editor layout images and fin.png

### Phase 4: Library & Covers (Commits 25–27)
- Fixed covers not showing in Marvel/DC sections
- Added full Library feature with localStorage persistence
- Thumbnail click opens reader via event delegation
- querySelectorAll approach for cover canvases

### Phase 5: Mobile Optimization (Commits 28–32)
- `isMobile` detection (`/Mobi|Android|iPhone|iPad|iPod/`)
- Mobile <768px: Babylon 3D scene skipped entirely
- CSS: full-width overlay, single-column grid, scrollable nav, larger fonts, scrollable reader bar
- Swipe gesture support for reader (touchstart/touchend >40px)
- `touch-action: none` on canvas, `user-scalable=no` viewport

### Phase 6: Auth Gate (Commits 33–36)
- Full-page signup overlay with Create Account / Sign In tabs
- Credentials stored in `localStorage.deco_accounts`
- Loading video (`loding.mp4`) plays on auth success
- Mobile bypasses auth entirely

### Phase 7: Deco & Plane Refinements (Commits 37–47)
- Responsive deco images: px → viewport-relative % units
- Multiple layout revert iterations for deco positioning
- Absolute px positioning for deco images (matches reference layout)
- Plane textures flipped vertically (`vScale=-1`, `vOffset=1`) instead of rotating meshes
- `overlay.png` added as edge-to-edge element (`object-fit: cover`, `100vw × 100vh`)
- `overlay.png` committed to LFS (705 KB)

---

## Project Structure

```
worldcomics/                                          # Root project directory
│
├── index.html                                        # MAIN APP: 33K lines
│   ├── Babylon.js 3D scene                           #   8 planes, GLB model, video laptop
│   ├── Auth gate (signup/signin)                     #   localStorage accounts
│   ├── Comic grid (Marvel/DC/Library)                #   PNG covers on canvas
│   ├── turn.js flipbook reader                       #   jQuery + turn.js
│   ├── PDF.js reader                                 #   Full-page PDF viewer
│   ├── Video player overlay                          #   video.js full-screen
│   ├── Admin panel (upload/delete)                   #   Browser file API
│   ├── Deco overlay (overlay.png + 2 images)         #   Non-interactable full-viewport
│   ├── Mobile CSS media queries                      #   <768px responsive breakpoint
│   └── Search/filter bar                             #   Real-time title filtering
│
├── editor.html                                       # Layout editor v1 (~25K lines)
├── editor2.html                                      # Layout editor v2 (~55K lines, feature-rich)
├── signup.html                                       # Standalone signup page
├── dump_layout.html                                  # Debug: reads localStorage editor_layout
├── index(copy).html                                  # Backup copy of main app
│
├── turn.js                                           # jQuery flipbook library (v4.1.0)
├── jquery.js                                         # jQuery core library (v3.7.1)
│
├── layout.json                                       # Scene layout (base64-encoded images)
├── layout (3).json                                   # Empty layout
├── layout (4).json                                   # 6-element image layout
│
├── .gitattributes                                    # LFS: *.pdf *.mp4 *.png *.zip
├── .gitignore                                        # Ignores *.zip
├── .nojekyll                                         # Disables Jekyll on GitHub Pages
│
├── generate_thumbs.py                                # PDF → 300px PNG thumbnail generator
├── convert_fin_comics_white.py                       # Black→white pixel converter for fin.png
├── compress_special_video.ps1                        # FFmpeg video compression script
│
├── comicdownloader_bot/                              # Python comic downloader suite
│   ├── comic_downloader.py                           #   Single series download (ThreadPoolExecutor)
│   └── mass_downloader.py                            #   Bulk downloader (all series, 5GB cap)
│
├── all_comics/                                       # Master comic library (21 series, 116 PDFs)
│   ├── Alien 3(2018)/                                #   #1–5
│   ├── Batman Secret Files(2018)/                    #   #1–2
│   ├── Batman The Devastator(2017)/                  #   #1
│   ├── batman(2025)/                                 #   #1–9
│   ├── Black Widow and Hawkeye(2024)/                #   #1–3
│   ├── Carnage Eddie Brock(2025)/                    #   #1–6
│   ├── Chandra(2018)/                                #   #1–4
│   ├── Danger Street(2022)/                          #   #1–11
│   ├── Daredevil(2023)/                              #   #1–11
│   ├── Deep Target(2021)/                            #   #1–7
│   ├── Doctor Strange of Asgard(2025)/               #   #1–5
│   ├── Edenfrost(2023)/                              #   #1–4
│   ├── Gunland(2020)/                                #   #1–12
│   ├── Hellverine(2024)/                             #   #1–4
│   ├── Legends of the Dark Knight(2021)/             #   #1–6
│   ├── Nightmare Country The Glass House(2023)/      #   #1–6
│   ├── Nils(2020)/                                   #   #1–2
│   ├── Pretty Deadly The Rat(2019)/                  #   #1–5
│   ├── Spider-Girl(2025)/                            #   #1–5
│   ├── Star Wars Target Vader(2019)/                 #   #1–6
│   └── Thor God of Thunder(2022)/                    #   #1–7
│
├── comics/                                           # Web display copies (categorized)
│   ├── dc/                                           #   DC universe
│   │   ├── batman/
│   │   ├── raven/
│   │   └── superman/
│   ├── marvel/                                       #   Marvel universe
│   │   ├── absolute-carnage/
│   │   ├── amazing-spider-man/
│   │   ├── deadpool/
│   │   ├── jessica-jones/
│   │   └── marvel-now/
│   └── ysk-comics/                                   #   General
│
├── comics.glb                                        # 3D model (Babylon.js scene centerpiece)
├── loding.mp4                                        # Loading screen video (LFS)
├── special.mp4                                       # "The special" video (LFS)
├── videoplayback.mp4                                 # Laptop playback video (LFS)
├── plane10vid.mp4                                    # Extra video asset (LFS)
├── fin.png                                           # Source: black text on right side
├── fin_white_comics.png                              # Output: black→white text conversion
│
├── heading.png                                       # Deco overlay title graphic
├── name is.png                                       # Deco UI text element
├── to do.png                                         # Deco checklist element
├── overlay.png                                       # Full-viewport overlay (705 KB, LFS)
├── font.png / font1.png / final font.png / finalfinal.png  # Typography assets
│
├── daily_bugle_comics.png                            # Branding graphic
├── Screenshot 2026-06-30 173847.png                  # Deco image
├── #collage #spiderman #marvel #marvelcomics.jpg     # Spiderman collage
├── Adjusted-7.jpg                                    # Background deco
├── The_Spectacular_Spider-Man_1968-removebg-preview.png  # Deco PNG
├── Comic_Daredevil_Wallpaper-removebg-preview.png    # Deco PNG
├── (various removebg PNGs and JPGs)                  # Additional deco assets
│
└── book-effect-20260629T174713Z-3-001/               # Standalone Pokemon flipbook project
    └── book-effect/
        ├── index.html                                #   Pokemon flipbook page
        ├── style.css                                 #   Custom styling
        ├── jquery.js                                 #   jQuery v3.7.1
        ├── turn.js                                   #   turn.js flipbook
        └── images/                                   #   5 Pokemon images
            ├── img-1.png
            ├── img-2.png
            ├── img-3.png
            ├── img-4.png
            └── img-5.png
```

---

## Mobile vs Desktop

| Feature | Desktop | Mobile (<768px) |
|---------|---------|-----------------|
| Babylon 3D scene | Rendered with 8 planes + GLB + video laptop | **Skipped entirely** (isMobile check wraps all Babylon code) |
| Auth gate | Full signup/signin overlay | **Bypassed** — goes straight to overlay |
| Comic grid | 2+ column layout (responsive) | Single column, full-width |
| Overlay width | Fits within 3D scene | 100% width, no 3D scene |
| Nav tabs | Horizontal row | Horizontal scrollable (`overflow-x: auto`, `white-space: nowrap`) |
| Font size | Standard | Larger (18px grid, 24px reader) |
| Reader top bar | Static row | Scrollable with `white-space: nowrap` |
| Swipe reader | Not needed | touchstart/touchend >40px = next/prev page |
| Canvas interaction | `touch-action: auto` | `touch-action: none` to prevent scroll conflicts |
| Viewport | `user-scalable=yes` | `user-scalable=no` to prevent zoom on double-tap |
| Hardware scaling | `1` | `2` (optimize performance) |

---

## Setup & Installation

### Prerequisites
- Git with LFS support (`git lfs`)
- Python 3.6+ (for tools)
- FFmpeg (for video compression, optional)
- A modern web browser (Chrome, Firefox, Edge)

### Clone & Run Locally

```bash
# Clone with LFS
git clone https://github.com/aakash723/dailybugle.git
cd dailybugle

# Pull LFS assets
git lfs pull

# Start a local HTTP server (required for PDF.js CORS)
python -m http.server 8000

# Open in browser
# http://localhost:8000
```

> **Note**: PDF.js requires the app to be served over HTTP, not opened via `file://` protocol. Use any local server (Python http.server, Live Server, etc.).

### Running Tools

```bash
# Generate PNG thumbnails from PDFs
python generate_thumbs.py

# Run the comic downloader bot
cd comicdownloader_bot
python comic_downloader.py

# Compress video
powershell -File compress_special_video.ps1
```

---

## Deployment

The app is deployed via **GitHub Pages**:

1. **Repository**: `github.com/aakash723/dailybugle`
2. **Live URL**: `https://aakash723.github.io/dailybugle/`
3. **Pages config**: Deploy from `main` branch, root directory
4. **`.nojekyll`**: Present in root to prevent Jekyll from processing files with `_` or `#` in names

### Deployment Checklist

| Item | Status |
|------|--------|
| All assets in LFS (PDF, PNG, MP4) | Done |
| CDN_URL uses `media.githubusercontent.com` | Done |
| `crossOrigin='anonymous'` on all Image loads | Done |
| `BABYLON.Texture` for plane covers (not DynamicTexture) | Done |
| `.nojekyll` committed | Done |
| All paths relative (start with `./`) | Done |

---

## Bonus: Pokemon Flipbook

Located in `book-effect-20260629T174713Z-3-001/book-effect/`, this is a standalone mini-project featuring a Pokemon-themed flipbook:

- Uses the same turn.js + jQuery stack as the main app
- 5 Pokemon images (`img-1.png` through `img-5.png`)
- Separate `style.css` with custom theming
- Fully independent from the main World Comics app

---

## Credits & Data Sources

- **Comic files**: Downloaded from [ysk-comics.com](http://ysk-comics.com) via the custom downloader bot
- **3D Model**: `comics.glb` — custom asset
- **turn.js**: v4.1.0 by turnjs.com (MIT-style license)
- **jQuery**: v3.7.1 by OpenJS Foundation
- **PDF.js**: Mozilla's PDF viewer library
- **Babylon.js**: 3D engine by the Babylon.js team
- **Video assets**: Various sources
- **Deco images**: Various sources (some processed with remove.bg)

---

*Generated: July 2026*
