from fpdf import FPDF
import os

class ProjectReport(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.toc_entries = []
        self.toc_page = 0

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "World Comics - Project Report", align="L")
            self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        pass

    def chapter_title(self, title, level=1):
        if level == 1:
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(20, 60, 120)
            self.ln(4)
            self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(20, 60, 120)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(4)
            self.toc_entries.append((title, self.page_no()))
        elif level == 2:
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(40, 80, 140)
            self.ln(3)
            self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            self.toc_entries.append((f"    {title}", self.page_no()))
        elif level == 3:
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(60, 60, 60)
            self.ln(2)
            self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=10):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(0.5)

    def bullet_item(self, bold_part, rest="", indent=10):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(5, 5.5, "-")
        self.set_font("Helvetica", "B", 10)
        self.cell(self.get_string_width(bold_part) + 1, 5.5, bold_part)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, rest)
        self.ln(0.5)

    def table_row(self, cells, widths, bold=False, fill=False):
        self.set_font("Helvetica", "B" if bold else "", 9)
        if fill:
            self.set_fill_color(230, 237, 247)
        else:
            self.set_fill_color(255, 255, 255)
        max_h = 6
        x_start = self.get_x()
        y_start = self.get_y()
        for i, cell in enumerate(cells):
            self.set_xy(x_start + sum(widths[:i]), y_start)
            self.cell(widths[i], 6, str(cell), border=1, fill=fill, align="C" if i == 0 else "L")
        self.ln(6)

    def code_block(self, text):
        self.set_font("Courier", "", 8)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(240, 240, 245)
        y = self.get_y()
        if y > 260:
            self.add_page()
        lines = text.split("\n")
        for line in lines:
            self.set_x(self.l_margin + 5)
            self.cell(self.w - self.l_margin - self.r_margin - 10, 4.5, line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(30, 30, 30)
        self.ln(3)


def build_report():
    pdf = ProjectReport()

    # ========== TITLE PAGE ==========
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 15, "WORLD COMICS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 12, "Interactive 3D Comic Library", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(20, 60, 120)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Project Report & Technical Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 8, "July 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(40)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Repository: github.com/aakash723/dailybugle", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Live: aakash723.github.io/dailybugle", align="C", new_x="LMARGIN", new_y="NEXT")

    # ========== TABLE OF CONTENTS ==========
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.toc_page = pdf.page_no()

    # Gather TOC entries structure
    toc_structure = [
        ("1. Project Overview", ""),
        ("2. Tech Stack", ""),
        ("3. Architecture & Backend Infrastructure", ""),
        ("4. Key Features", ""),
        ("    4.1 3D Scene (Desktop Only)", ""),
        ("    4.2 Auth Gate (Desktop Only)", ""),
        ("    4.3 Comic Grid", ""),
        ("    4.4 Readers", ""),
        ("    4.5 Library", ""),
        ("    4.6 Video Player", ""),
        ("    4.7 Deco Overlay", ""),
        ("    4.8 Admin Panel", ""),
        ("5. Comic Library (21 Series, 116 Issues)", ""),
        ("    5.1 Marvel Series", ""),
        ("    5.2 DC Series", ""),
        ("    5.3 Independent Series", ""),
        ("6. Tools & Bots", ""),
        ("    6.1 Comic Downloader Bot", ""),
        ("    6.2 Thumbnail Generator", ""),
        ("    6.3 Image Color Converter", ""),
        ("    6.4 Video Compressor", ""),
        ("    6.5 Layout Editors", ""),
        ("    6.6 Debug Utility: dump_layout.html", ""),
        ("7. CDN & Storage Strategy", ""),
        ("8. Git Commit History", ""),
        ("9. Project Structure", ""),
        ("10. Mobile vs Desktop", ""),
        ("11. Setup & Installation", ""),
        ("12. Deployment", ""),
        ("13. Bonus: Pokemon Flipbook", ""),
        ("14. Credits & Data Sources", ""),
    ]

    for title, _ in toc_structure:
        indent = 5 if title.startswith("    ") else 0
        display = title.strip()
        pdf.set_x(pdf.l_margin + indent * 2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 6, display, new_x="LMARGIN", new_y="NEXT")

    # ========== 1. PROJECT OVERVIEW ==========
    pdf.add_page()
    pdf.chapter_title("1. Project Overview")
    pdf.body_text(
        "World Comics is a fully client-side web application built to showcase, browse, read, and organize "
        "digital comic books. It features a 3D scene (Babylon.js) with rotating comic planes and a laptop "
        "playing video, an auth gate (signup/signin) that controls access on desktop, a comic grid organized "
        "into Marvel and DC sections with thumbnail covers, two reader modes (turn.js flipbook with page-flip "
        "animation and PDF.js full-page viewer), a video player that opens a full-screen video.js overlay on "
        "laptop click, search and filter across the entire library, a persistent library (localStorage) for "
        "saving favorites, and an admin panel for file upload/delete."
    )
    pdf.body_text(
        "All 116 comic PDFs, 142+ PNG thumbnails, and video assets are stored in Git LFS and served via "
        "media.githubusercontent.com (GitHub's LFS CDN), which provides proper CORS headers. The app is "
        "hosted on GitHub Pages and requires no server-side processing."
    )

    # ========== 2. TECH STACK ==========
    pdf.chapter_title("2. Tech Stack")
    tech_data = [
        ("3D Rendering", "Babylon.js 4.x (WebGL)"),
        ("Flipbook Reader", "turn.js v4.1.0 (jQuery plugin)"),
        ("PDF Viewer", "PDF.js"),
        ("Video Player", "video.js (full-screen overlay)"),
        ("Layout Library", "jQuery 3.7.1"),
        ("Styling", "Vanilla CSS (no framework)"),
        ("Client Storage", "localStorage (auth, library, editor layouts)"),
        ("Asset Storage", "Git LFS (PDFs, PNGs, MP4s)"),
        ("CDN", "media.githubusercontent.com (CORS-enabled)"),
        ("Hosting", "GitHub Pages"),
        ("Downloader Scripts", "Python 3 (PyMuPDF, img2pdf, tkinter, ThreadPoolExecutor)"),
        ("Video Compression", "PowerShell + FFmpeg"),
    ]
    tech_widths = [55, 120]
    pdf.table_row(["Layer", "Technology"], tech_widths, bold=True, fill=True)
    for layer, tech in tech_data:
        pdf.table_row([layer, tech], tech_widths)

    # ========== 3. ARCHITECTURE ==========
    pdf.add_page()
    pdf.chapter_title("3. Architecture & Backend Infrastructure")
    pdf.body_text(
        "Despite being a client-side application, World Comics relies on a robust backend infrastructure - "
        "it just isn't code we wrote. The backend is entirely GitHub's infrastructure:"
    )
    arch_data = [
        ("GitHub + Git LFS", "Stores 264 LFS objects (116 PDFs ~6.1 GB, 142+ PNGs, MP4s, ZIPs). All assets version-controlled."),
        ("GitHub Pages", "Static hosting for index.html, CSS, JavaScript, and library files."),
        ("media.githubusercontent.com", "Git LFS CDN - serves all binary assets with CORS headers."),
        ("ysk-comics.com API", "Third-party backend providing comic page data for the downloader bots."),
        ("localStorage (browser)", "Client-side persistence for accounts, library, editor layouts."),
    ]
    arch_widths = [55, 120]
    pdf.table_row(["Component", "Role"], arch_widths, bold=True, fill=True)
    for comp, role in arch_data:
        pdf.table_row([comp, role], arch_widths)
    pdf.ln(3)
    pdf.body_text(
        "What we DON'T have: no custom application server (no Express, FastAPI, Flask, etc.), "
        "no SQL/NoSQL database, no server-side sessions, no custom API endpoints. "
        "Everything runs in the user's browser."
    )

    # ========== 4. KEY FEATURES ==========
    pdf.chapter_title("4. Key Features")
    pdf.chapter_title("4.1 3D Scene (Desktop Only)", level=2)
    features_3d = [
        "8 rotating comic planes positioned around a central comics.glb 3D model",
        "Each plane displays a comic cover using BABYLON.Texture (loaded directly from CDN URL)",
        "Camera: position [-4.22, 1.24, 1.59], rotation [0, pi, 0], FOV 1.27 x 0.9",
        "Laptop plane plays videoplayback.mp4; click opens full-screen video.js overlay",
        "Hover highlight: planes scale up by 1.22x on mouseenter",
        "Texture correction: PNGs flipped vertically (vScale=-1, vOffset=1) for cube map orientation",
    ]
    for f in features_3d:
        pdf.bullet(f)

    pdf.chapter_title("4.2 Auth Gate (Desktop Only)", level=2)
    auth_items = [
        "Full-page overlay shown on first visit (no deco_name in localStorage)",
        "Two tabs: Create Account (name, email, password, favorite comic) and Sign In (email + password)",
        "Credentials stored in localStorage.deco_accounts as {email: {password, name, favorite}}",
        "On success: plays loding.mp4 (loading video) as transition animation",
        "Returning visitors skip auth gate automatically",
        "Mobile (<768px) bypasses auth entirely - goes straight to overlay",
    ]
    for a in auth_items:
        pdf.bullet(a)

    pdf.chapter_title("4.3 Comic Grid", level=2)
    grid_items = [
        "Organized in Marvel and DC sections (also shows Library section)",
        "Each card shows a PNG thumbnail cover drawn on a <canvas> element",
        "Thumbnails generated from PDF first pages via generate_thumbs.py",
        "Cards show: cover, title, issue number, Read / Download / Add to Library buttons",
        "Event delegation: single document.addEventListener handles all card interactions",
        "Search bar filters comics by title in real-time",
    ]
    for g in grid_items:
        pdf.bullet(g)

    pdf.chapter_title("4.4 Readers", level=2)
    reader_items = [
        "Flipbook (turn.js) - page-flip animation, requires jQuery",
        "PDF.js - scrollable full-page view using Mozilla's PDF renderer",
        "Swipe support (mobile) - touch events detect >40px gestures for page navigation",
        "Mobile reader: scrollable top bar with white-space: nowrap",
    ]
    for r in reader_items:
        pdf.bullet(r)

    pdf.chapter_title("4.5 Library", level=2)
    lib_items = [
        "Add to Library button on each comic card",
        "Persisted in localStorage as deco_library (array of comic IDs)",
        "Separate Library section in the comic grid showing saved comics",
        "Remove from Library button for each saved comic",
    ]
    for l in lib_items:
        pdf.bullet(l)

    pdf.chapter_title("4.6 Video Player", level=2)
    pdf.bullet("Laptop in 3D scene plays videoplayback.mp4 via CDN")
    pdf.bullet("Click on laptop opens full-screen video.js overlay")
    pdf.bullet("Controls: play, pause, seek, volume, full-screen")

    pdf.chapter_title("4.7 Deco Overlay", level=2)
    deco_items = [
        "overlay.png: full-viewport edge-to-edge element (100vw x 100vh, object-fit: cover)",
        "Non-interactable (pointer-events: none)",
        "Two additional decorative images positioned with absolute px values",
        "All deco elements hidden in reader mode",
    ]
    for d in deco_items:
        pdf.bullet(d)

    pdf.chapter_title("4.8 Admin Panel", level=2)
    pdf.bullet("File upload via browser API")
    pdf.bullet("File delete capability")
    pdf.bullet("Inline in the overlay UI")

    # ========== 5. COMIC LIBRARY ==========
    pdf.add_page()
    pdf.chapter_title("5. Comic Library (21 Series, 116 Issues)")
    pdf.body_text(
        "All comics downloaded from ysk-comics.com via the custom downloader bot. "
        "Each issue stored as PDF (~30-50 MB each) with a PNG cover thumbnail (300px wide)."
    )

    pdf.chapter_title("5.1 Marvel Series", level=2)
    marvel_series = [
        ("Alien 3 (2018)", "#1-5", "Alien 3(2018)"),
        ("Carnage Eddie Brock (2025)", "#1-6", "Carnage Eddie Brock(2025)"),
        ("Daredevil (2023)", "#1-11", "Daredevil(2023)"),
        ("Doctor Strange of Asgard (2025)", "#1-5", "Doctor Strange of Asgard(2025)"),
        ("Hellverine (2024)", "#1-4", "Hellverine(2024)"),
        ("Spider-Girl (2025)", "#1-5", "Spider-Girl(2025)"),
        ("Star Wars: Target Vader (2019)", "#1-6", "Star Wars Target Vader(2019)"),
        ("Thor God of Thunder (2022)", "#1-7", "Thor God of Thunder(2022)"),
    ]
    m_widths = [58, 22, 65]
    pdf.table_row(["Series", "Issues", "Folder"], m_widths, bold=True, fill=True)
    for s, i, f in marvel_series:
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.table_row([s, i, "all_comics/" + f + "/"], m_widths)

    pdf.chapter_title("5.2 DC Series", level=2)
    dc_series = [
        ("Batman Secret Files (2018)", "#1-2", "Batman Secret Files(2018)"),
        ("Batman The Devastator (2017)", "#1", "Batman The Devastator(2017)"),
        ("batman (2025)", "#1-9", "batman(2025)"),
        ("Danger Street (2022)", "#1-11", "Danger Street(2022)"),
        ("Legends of the Dark Knight (2021)", "#1-6", "Legends of the Dark Knight(2021)"),
        ("Nightmare Country: Glass House (2023)", "#1-6", "Nightmare Country The Glass House(2023)"),
    ]
    pdf.table_row(["Series", "Issues", "Folder"], m_widths, bold=True, fill=True)
    for s, i, f in dc_series:
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.table_row([s, i, "all_comics/" + f + "/"], m_widths)

    pdf.chapter_title("5.3 Independent / Other Series", level=2)
    ind_series = [
        ("Black Widow and Hawkeye (2024)", "#1-3", "Black Widow and Hawkeye(2024)"),
        ("Chandra (2018)", "#1-4", "Chandra(2018)"),
        ("Deep Target (2021)", "#1-7", "Deep Target(2021)"),
        ("Edenfrost (2023)", "#1-4", "Edenfrost(2023)"),
        ("Gunland (2020)", "#1-12", "Gunland(2020)"),
        ("Nils (2020)", "#1-2", "Nils(2020)"),
        ("Pretty Deadly: The Rat (2019)", "#1-5", "Pretty Deadly The Rat(2019)"),
    ]
    pdf.table_row(["Series", "Issues", "Folder"], m_widths, bold=True, fill=True)
    for s, i, f in ind_series:
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.table_row([s, i, "all_comics/" + f + "/"], m_widths)

    # ========== 6. TOOLS & BOTS ==========
    pdf.add_page()
    pdf.chapter_title("6. Tools & Bots")

    pdf.chapter_title("6.1 Comic Downloader Bot", level=2)
    pdf.body_text(
        "Located in comicdownloader_bot/, this Python tool downloads comics from ysk-comics.com."
    )
    pdf.chapter_title("comic_downloader.py", level=3)
    dl_items = [
        "Connects to ysk-comics.com API with API_SECRET = '123456'",
        "Fetches comic metadata (title, issue number, page count, page URLs)",
        "Downloads all pages in parallel using ThreadPoolExecutor",
        "Converts images to PDF using img2pdf",
        "Supports single-series download",
    ]
    for d in dl_items:
        pdf.bullet(d)

    pdf.chapter_title("mass_downloader.py", level=3)
    mass_items = [
        "Scrapes all available comic slugs from site HTML pages",
        "Iterates through every series and downloads each issue",
        "Per-series progress bars via tqdm",
        "Respects a 5 GB storage limit (MAX_GB = 5)",
        "Tracks success/failure counts",
        "Sequential per-series downloads to avoid overwhelming the server",
    ]
    for m in mass_items:
        pdf.bullet(m)

    pdf.chapter_title("6.2 Thumbnail Generator (generate_thumbs.py)", level=2)
    thumb_items = [
        "Uses PyMuPDF (fitz) to extract the first page of every PDF in all_comics/",
        "Saves as 300px-wide PNG (proportional scaling, MAX_W = 300)",
        "Skips directories that already have PNG files (idempotent)",
        "Generated 105 thumbnails (~25.6 MB total)",
        "Run via: python generate_thumbs.py",
    ]
    for t in thumb_items:
        pdf.bullet(t)

    pdf.chapter_title("6.3 Image Color Converter (convert_fin_comics_white.py)", level=2)
    convert_items = [
        "Uses Tkinter's PhotoImage to process fin.png",
        "Scans the right 35% region for black pixels",
        "Replaces black pixels with white (text color correction)",
        "Output: fin_white_comics.png",
    ]
    for c in convert_items:
        pdf.bullet(c)

    pdf.chapter_title("6.4 Video Compressor (compress_special_video.ps1)", level=2)
    vid_items = [
        "PowerShell script using FFmpeg",
        "Input: the special.mp4, Output: special-compressed.mp4",
        "Scale: 960x540, Video: libx264 at CRF 26, Audio: AAC at 128 kbps",
    ]
    for v in vid_items:
        pdf.bullet(v)

    pdf.chapter_title("6.5 Layout Editors (editor.html / editor2.html)", level=2)
    pdf.body_text(
        "Two visual 2D canvas editors for composing scene elements. "
        "editor.html (~25,000 lines) is the basic version; editor2.html (~55,000 lines) is the feature-rich variant."
    )
    editor_features = [
        "Add images, text, videos, and geometric shapes to a canvas",
        "Drag, resize, and rotate elements",
        "Delete individual elements",
        "Export layout as JSON to localStorage (editor_layout)",
        "Import/export layout files",
        "Save and load presets",
    ]
    for e in editor_features:
        pdf.bullet(e)
    pdf.ln(2)
    pdf.body_text("Layout configurations stored as:")
    pdf.bullet("layout.json - base64-encoded embedded image layout")
    pdf.bullet("layout (3).json - empty layout ({elements: []})")
    pdf.bullet("layout (4).json - 6-image layout with local PNG references")

    pdf.chapter_title("6.6 Debug Utility: dump_layout.html", level=2)
    pdf.body_text(
        "A 12-line utility page that reads and displays localStorage.getItem('editor_layout') "
        "as raw JSON - used for inspecting saved editor layouts during development."
    )

    # ========== 7. CDN & STORAGE STRATEGY ==========
    pdf.add_page()
    pdf.chapter_title("7. CDN & Storage Strategy")

    pdf.chapter_title("The Problem", level=2)
    pdf.body_text(
        "raw.githubusercontent.com (GitHub's raw file server) does NOT send "
        "Access-Control-Allow-Origin: * headers. Canvas drawImage() and texImage2D() "
        "in WebGL require CORS headers - without them, the canvas becomes 'tainted' "
        "and operations throw a SecurityError."
    )

    pdf.chapter_title("The Solution", level=2)
    sol_items = [
        "All binary assets (PDFs, PNGs, MP4s) stored in Git LFS",
        "LFS files served via media.githubusercontent.com - GitHub's official LFS CDN",
        "This CDN sends Access-Control-Allow-Origin: * headers",
        "Result: BABYLON.Texture, canvas drawImage(), and all cross-origin operations work",
    ]
    for s in sol_items:
        pdf.bullet(s)

    pdf.chapter_title("Implementation", level=2)
    pdf.code_block(
        'const CDN_URL = \'https://media.githubusercontent.com/media/aakash723/dailybugle/main/\';\n'
        'const thumbURL = (filename) => CDN_URL + filename.replace(\'.pdf\', \'.png\')\n'
        '    .replace(/#/g, \'%23\')\n'
        '    .replace(/ /g, \'%20\');'
    )

    pdf.chapter_title("LFS Configuration (.gitattributes)", level=2)
    pdf.code_block(
        '*.pdf filter=lfs diff=lfs merge=lfs -text\n'
        '*.mp4 filter=lfs diff=lfs merge=lfs -text\n'
        '*.png filter=lfs diff=lfs merge=lfs -text\n'
        '*.zip filter=lfs diff=lfs merge=lfs -text'
    )

    pdf.chapter_title("Storage Stats", level=2)
    stats_items = [
        "264 total LFS objects",
        "116 PDFs: ~6.1 GB total, ~52 MB average",
        "142+ PNGs: ~41 MB (thumbnails + assets)",
        "MP4s: loding.mp4, special.mp4, videoplayback.mp4, plane10vid.mp4",
        "GitHub Free Plan: LFS is free and unlimited for public repositories - no card needed",
    ]
    for st in stats_items:
        pdf.bullet(st)

    pdf.chapter_title("CORS Fixes Applied", level=2)
    cors_items = [
        "All Image() objects set img.crossOrigin = 'anonymous' before canvas operations",
        "Plane textures switched from DynamicTexture + ctx.drawImage() to BABYLON.Texture",
        "raw.githubusercontent.com URLs completely removed from the codebase",
    ]
    for c in cors_items:
        pdf.bullet(c)

    # ========== 8. GIT COMMIT HISTORY ==========
    pdf.add_page()
    pdf.chapter_title("8. Git Commit History")
    pdf.body_text("47 commits across the project's lifetime. Key phases:")

    pdf.chapter_title("Phase 1: Initial Setup (Commits 1-9)", level=2)
    ph1 = [
        "Initial project commit with full LFS setup",
        "MEGA integration for cloud storage",
        "Local comic paths and comics.glb 3D model",
        "Layout editor with save/download functionality",
        "try-catch around GLB loading for graceful fallback",
        "Deco elements made non-interactive (pointer-events: none)",
    ]
    for p in ph1:
        pdf.bullet(p)

    pdf.chapter_title("Phase 2: CDN Migration (Commits 10-17)", level=2)
    ph2 = [
        "Switched from MEGA to raw.githubusercontent.com",
        "Added .nojekyll for GitHub Pages compatibility",
        "Migrated all assets to media.githubusercontent.com (LFS CDN)",
        "Fixed special.mp4 gray video - used CDN_URL instead of relative path",
        "Fixed PNG thumbnails not loading",
    ]
    for p in ph2:
        pdf.bullet(p)

    pdf.chapter_title("Phase 3: PNG Thumbnails & Canvas Fixes (Commits 18-24)", level=2)
    ph3 = [
        "generate_thumbs.py with proportional scaling (MAX_W=300)",
        "PNG thumbnails used for comic card covers",
        "crossOrigin='anonymous' added to all Image loads",
        "Switched plane textures from DynamicTexture to BABYLON.Texture",
        "Fixed empty planes: used comicURL for plane thumbnail sources",
        "CDN_URL used for all editor layout images and fin.png",
    ]
    for p in ph3:
        pdf.bullet(p)

    pdf.chapter_title("Phase 4: Library & Covers (Commits 25-27)", level=2)
    ph4 = [
        "Fixed covers not showing in Marvel/DC sections",
        "Added full Library feature with localStorage persistence",
        "Thumbnail click opens reader via event delegation",
        "querySelectorAll approach for cover canvases",
    ]
    for p in ph4:
        pdf.bullet(p)

    pdf.chapter_title("Phase 5: Mobile Optimization (Commits 28-32)", level=2)
    ph5 = [
        "isMobile detection (/Mobi|Android|iPhone|iPad|iPod/)",
        "Mobile <768px: Babylon 3D scene skipped entirely",
        "CSS: full-width overlay, single-column grid, scrollable nav",
        "Swipe gesture support for reader (>40px threshold)",
        "touch-action: none on canvas, user-scalable=no viewport",
    ]
    for p in ph5:
        pdf.bullet(p)

    pdf.chapter_title("Phase 6: Auth Gate (Commits 33-36)", level=2)
    ph6 = [
        "Full-page signup overlay with Create Account / Sign In tabs",
        "Credentials stored in localStorage.deco_accounts",
        "Loading video (loding.mp4) plays on auth success",
        "Mobile bypasses auth entirely",
    ]
    for p in ph6:
        pdf.bullet(p)

    pdf.chapter_title("Phase 7: Deco & Plane Refinements (Commits 37-47)", level=2)
    ph7 = [
        "Responsive deco images: px to viewport-relative % units",
        "Multiple layout revert iterations for deco positioning",
        "Absolute px positioning for deco images",
        "Plane textures flipped vertically (vScale=-1, vOffset=1)",
        "overlay.png added as edge-to-edge element (object-fit: cover)",
        "overlay.png committed to LFS (705 KB)",
    ]
    for p in ph7:
        pdf.bullet(p)

    # ========== 9. PROJECT STRUCTURE ==========
    pdf.add_page()
    pdf.chapter_title("9. Project Structure")
    pdf.set_font("Courier", "", 7)
    pdf.set_text_color(30, 30, 30)
    tree = """worldcomics/
+-- index.html                    (33K lines - main app)
+-- editor.html                   (25K lines - layout editor v1)
+-- editor2.html                  (55K lines - layout editor v2)
+-- signup.html                   (standalone signup page)
+-- dump_layout.html              (debug utility)
+-- turn.js / jquery.js           (libraries)
+-- layout.json / layout (3/4).json (scene layouts)
+-- .gitattributes / .gitignore / .nojekyll
+-- generate_thumbs.py            (PDF->PNG thumbnail tool)
+-- convert_fin_comics_white.py   (image color converter)
+-- compress_special_video.ps1    (FFmpeg video compression)
+-- comicdownloader_bot/
|   +-- comic_downloader.py       (single-series downloader)
|   +-- mass_downloader.py        (bulk downloader, 5GB cap)
+-- all_comics/                   (21 series, 116 PDFs + PNGs)
|   +-- Alien 3(2018)/ ... Thor God of Thunder(2022)/
+-- comics/                       (web display copies)
|   +-- dc/ (batman, raven, superman)
|   +-- marvel/ (absolute-carnage, amazing-spider-man, 
|   |           deadpool, jessica-jones, marvel-now)
|   +-- ysk-comics/
+-- comics.glb                    (3D model)
+-- loding.mp4 / special.mp4 / videoplayback.mp4 / plane10vid.mp4
+-- fin.png / fin_white_comics.png
+-- overlay.png (705 KB)
+-- heading.png / name is.png / to do.png
+-- font.png / font1.png / final font.png / finalfinal.png
+-- (various deco JPGs and PNGs)
+-- book-effect-.../              (Pokemon flipbook - standalone)
    +-- book-effect/
        +-- index.html / style.css / jquery.js / turn.js
        +-- images/ (5 Pokemon PNGs)"""
    pdf.multi_cell(0, 3.2, tree)
    pdf.ln(3)

    # ========== 10. MOBILE VS DESKTOP ==========
    pdf.add_page()
    pdf.chapter_title("10. Mobile vs Desktop")
    m_widths2 = [50, 62, 62]
    pdf.table_row(["Feature", "Desktop", "Mobile (<768px)"], m_widths2, bold=True, fill=True)
    mobile_data = [
        ("Babylon 3D scene", "Rendered (8 planes + GLB + video)", "Skipped entirely"),
        ("Auth gate", "Full signup/signin overlay", "Bypassed"),
        ("Comic grid", "2+ column layout", "Single column, full-width"),
        ("Overlay width", "Fits within 3D scene", "100% width"),
        ("Nav tabs", "Horizontal row", "Scrollable (overflow-x: auto)"),
        ("Font size", "Standard", "Larger (18px grid, 24px reader)"),
        ("Swipe reader", "Not needed", "touchstart/touchend >40px"),
        ("Canvas touch", "touch-action: auto", "touch-action: none"),
        ("Viewport", "user-scalable=yes", "user-scalable=no"),
        ("Hardware scaling", "1", "2"),
    ]
    for feat, desk, mob in mobile_data:
        if pdf.get_y() > 260:
            pdf.add_page()
            pdf.table_row(["Feature", "Desktop", "Mobile (<768px)"], m_widths2, bold=True, fill=True)
        pdf.table_row([feat, desk, mob], m_widths2)

    # ========== 11. SETUP & INSTALLATION ==========
    pdf.add_page()
    pdf.chapter_title("11. Setup & Installation")
    pdf.chapter_title("Prerequisites", level=2)
    prereqs = ["Git with LFS support (git lfs)", "Python 3.6+ (for tools)", "FFmpeg (for video compression, optional)", "A modern web browser"]
    for p in prereqs:
        pdf.bullet(p)

    pdf.chapter_title("Clone & Run Locally", level=2)
    pdf.code_block(
        'git clone https://github.com/aakash723/dailybugle.git\n'
        'cd dailybugle\n'
        'git lfs pull\n'
        'python -m http.server 8000\n'
        '# Open http://localhost:8000'
    )
    pdf.body_text("Note: PDF.js requires the app to be served over HTTP, not via file:// protocol.")

    pdf.chapter_title("Running Tools", level=2)
    pdf.code_block(
        '# Generate PNG thumbnails from PDFs\n'
        'python generate_thumbs.py\n\n'
        '# Run the comic downloader bot\n'
        'cd comicdownloader_bot\n'
        'python comic_downloader.py\n\n'
        '# Compress video\n'
        'powershell -File compress_special_video.ps1'
    )

    # ========== 12. DEPLOYMENT ==========
    pdf.chapter_title("12. Deployment")
    pdf.body_text("The app is deployed via GitHub Pages:")
    dep_items = [
        "Repository: github.com/aakash723/dailybugle",
        "Live URL: https://aakash723.github.io/dailybugle/",
        "Pages config: Deploy from main branch, root directory",
        ".nojekyll: prevents Jekyll from processing files with _ or # in names",
    ]
    for d in dep_items:
        pdf.bullet(d)

    pdf.chapter_title("Deployment Checklist", level=2)
    check_widths = [100, 30]
    pdf.table_row(["Item", "Status"], check_widths, bold=True, fill=True)
    checks = [
        ("All assets in LFS (PDF, PNG, MP4)", "Done"),
        ("CDN_URL uses media.githubusercontent.com", "Done"),
        ("crossOrigin='anonymous' on all Image loads", "Done"),
        ("BABYLON.Texture for plane covers", "Done"),
        (".nojekyll committed", "Done"),
        ("All paths relative (start with ./)", "Done"),
    ]
    for item, status in checks:
        pdf.table_row([item, status], check_widths)

    # ========== 13. BONUS: POKEMON FLIPBOOK ==========
    pdf.add_page()
    pdf.chapter_title("13. Bonus: Pokemon Flipbook")
    pdf.body_text(
        "Located in book-effect-.../book-effect/, this is a standalone mini-project "
        "featuring a Pokemon-themed flipbook:"
    )
    poke_items = [
        "Uses the same turn.js + jQuery stack as the main app",
        "5 Pokemon images (img-1.png through img-5.png)",
        "Separate style.css with custom theming",
        "Fully independent from the main World Comics app",
    ]
    for p in poke_items:
        pdf.bullet(p)

    # ========== 14. CREDITS ==========
    pdf.chapter_title("14. Credits & Data Sources")
    credits = [
        "Comic files: Downloaded from ysk-comics.com via the custom downloader bot",
        "3D Model: comics.glb - custom asset",
        "turn.js: v4.1.0 by turnjs.com (MIT-style license)",
        "jQuery: v3.7.1 by OpenJS Foundation",
        "PDF.js: Mozilla's PDF viewer library",
        "Babylon.js: 3D engine by the Babylon.js team",
        "Deco images: Various sources (some processed with remove.bg)",
    ]
    for c in credits:
        pdf.bullet(c)

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Generated: July 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # Save
    output_path = os.path.join(os.path.dirname(__file__), "World_Comics_Project_Report.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    return output_path


if __name__ == "__main__":
    build_report()
