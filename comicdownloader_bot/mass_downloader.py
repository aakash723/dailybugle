import os, re, time, shutil, random, json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import img2pdf

BASE_DIR = Path(r"C:\Users\KIIT0001\Desktop\comics\worldcomics\all_comics")
API_BASE = "https://api.ysk-comics.com/api/v1"
SITE_URL = "https://www.ysk-comics.com"
API_SECRET = "123456"
MAX_GB = 5

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "apiSecret": API_SECRET,
})


def get_total_size(path):
    total = 0
    for f in Path(path).rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total


def get_all_comic_slugs():
    """Scrape all homepage pages to get every comic slug."""
    all_slugs = set()
    page = 1
    empty_count = 0
    while empty_count < 3:
        url = f"{SITE_URL}/en?page={page}"
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                empty_count += 1
                page += 1
                continue
            slugs = re.findall(r'href="/en/comic/([^"]+)"', resp.text)
            if not slugs:
                empty_count += 1
            else:
                empty_count = 0
                before = len(all_slugs)
                all_slugs.update(slugs)
                print(f"  Page {page}: +{len(all_slugs) - before} comics (total: {len(all_slugs)})", end="\r")
            page += 1
            time.sleep(0.3)
        except:
            empty_count += 1
            page += 1
    print()
    return list(all_slugs)


def get_comic_info(slug):
    resp = session.get(f"{API_BASE}/comics/{slug}")
    data = resp.json()
    return data.get("data") if data.get("status") else None


def get_all_chapters(slug):
    url = f"{SITE_URL}/en/comic/{slug}"
    resp = session.get(url)
    chapters = re.findall(r'href="/en/chapter/([^"]+)"', resp.text)
    return list(dict.fromkeys(chapters))


def get_chapter_images(chapter_slug):
    data = session.get(f"{API_BASE}/chapters/{chapter_slug}/images").json()
    return data.get("data") if data.get("status") else None


def get_chapter_info(chapter_slug):
    data = session.get(f"{API_BASE}/chapters/{chapter_slug}").json()
    return data.get("data") if data.get("status") else None


def download_page(args):
    url, filepath, slug = args
    filepath = Path(filepath)
    if filepath.exists() and filepath.stat().st_size > 1000:
        return True
    for attempt in range(3):
        try:
            resp = session.get(url, headers={"Referer": f"{SITE_URL}/en/chapter/{slug}"}, timeout=30)
            if resp.status_code == 200:
                filepath.write_bytes(resp.content)
                return True
        except:
            time.sleep(2)
    return False


def images_to_pdf(image_dir, pdf_path):
    images = sorted(Path(image_dir).glob("page_*"))
    if not images:
        return False
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert([str(img) for img in images]))
    return True


def sanitize_folder_name(name):
    name = name.replace(":", "").replace("/", "").replace("\\", "").replace("?", "")
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def download_comic(slug):
    """Download all issues of a comic as PDFs. Returns (comic_folder, total_bytes)."""
    info = get_comic_info(slug)
    if not info:
        return None, 0

    full_name = info.get("full_name", slug)
    # Extract the base name and year: "Batman (2025)" -> name="Batman", year="2025"
    year_match = re.search(r'\((\d{4})\)', full_name)
    year = year_match.group(1) if year_match else ""
    base_name = re.sub(r'\s*\(\d{4}\)', '', full_name).strip()

    folder_name = sanitize_folder_name(f"{base_name}({year})" if year else base_name)
    comic_dir = BASE_DIR / folder_name
    comic_dir.mkdir(parents=True, exist_ok=True)

    chapters = get_all_chapters(slug)
    if not chapters:
        return folder_name, 0

    total_bytes = 0
    for idx, ch_slug in enumerate(chapters, 1):
        info = get_chapter_info(ch_slug)
        if not info:
            continue

        # Extract issue number
        issue_num = info.get("full_name", ch_slug)
        m = re.search(r'(\d+)\s*#|#(\d+)|(\d+)$', issue_num)
        if not m:
            m = re.search(r'(\d+)', ch_slug.split("-")[-1])
        issue_no = m.group(1) or m.group(2) or m.group(3) if m else str(idx)
        issue_label = f"#{issue_no}"

        # Check if PDF already exists
        pdf_path = comic_dir / f"{folder_name}{issue_label}.pdf"
        if pdf_path.exists():
            total_bytes += pdf_path.stat().st_size
            continue

        urls = get_chapter_images(ch_slug)
        if not urls:
            continue

        tmp_dir = comic_dir / f"tmp_{issue_no}"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        tasks = [(url, str(tmp_dir / f"page_{i+1:03d}{os.path.splitext(url.split('/')[-1])[1] or '.jpg'}"), ch_slug)
                 for i, url in enumerate(urls)]

        with ThreadPoolExecutor(max_workers=8) as ex:
            for f in as_completed([ex.submit(download_page, t) for t in tasks]):
                pass

        if images_to_pdf(tmp_dir, pdf_path):
            shutil.rmtree(tmp_dir)
            size = pdf_path.stat().st_size
            total_bytes += size
            print(f"    {issue_label}.pdf  ({size / 1024 / 1024:.1f} MB)")
        else:
            print(f"    {issue_label}: FAILED")

    return folder_name, total_bytes


def main():
    print("=" * 60)
    print(f"MASS COMIC DOWNLOADER - filling folder up to {MAX_GB}GB")
    print("=" * 60)

    # Step 1: Collect all comic slugs
    print("\n[1] Collecting all comic slugs from site...")
    all_slugs = get_all_comic_slugs()
    print(f"\n  Found {len(all_slugs)} unique comics on site")

    if not all_slugs:
        print("No comics found!")
        return

    # Step 2: Randomize and download
    random.shuffle(all_slugs)

    print(f"\n[2] Downloading comics until {MAX_GB}GB is reached...\n")

    downloaded = 0
    skipped = 0
    for slug in all_slugs:
        current_size = get_total_size(BASE_DIR)
        current_gb = current_size / (1024**3)

        if current_gb >= MAX_GB:
            print(f"\n  Reached {current_gb:.2f}GB limit!")
            break

        print(f"\n[{downloaded + 1}] Slug: {slug}  (total: {current_gb:.2f}GB / {MAX_GB}GB)")

        # Skip batman since already downloaded
        if slug == "batman-2025":
            print("  Skipping (already downloaded)")
            skipped += 1
            continue

        folder, added = download_comic(slug)

        if added > 0:
            downloaded += 1
            new_gb = (current_size + added) / (1024**3)
            print(f"  -> Folder: {folder}/  (+{added/1024/1024:.1f} MB, total: {new_gb:.2f}GB)")
        else:
            skipped += 1

        time.sleep(0.5)

    final_gb = get_total_size(BASE_DIR) / (1024**3)
    print(f"\n{'=' * 60}")
    print(f"Done! Downloaded: {downloaded} comics, Skipped: {skipped}")
    print(f"Total folder size: {final_gb:.2f}GB / {MAX_GB}GB")
    print(f"Location: {BASE_DIR}")


if __name__ == "__main__":
    main()
