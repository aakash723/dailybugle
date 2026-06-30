import os, re, time, shutil
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import img2pdf

BASE_DIR = Path(r"C:\Users\KIIT0001\Desktop\comics\worldcomics\all_comics")
API_BASE = "https://api.ysk-comics.com/api/v1"
SITE_URL = "https://www.ysk-comics.com"
API_SECRET = "123456"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "apiSecret": API_SECRET,
})

def get_comic_info(comic_slug):
    data = session.get(f"{API_BASE}/comics/{comic_slug}").json()
    return data.get("data") if data.get("status") else None

def get_all_chapters(comic_slug):
    resp = session.get(f"{SITE_URL}/en/comic/{comic_slug}")
    chapters = re.findall(r'href=["\']/en/chapter/([^"\']+)["\']', resp.text)
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
        return filepath.name, True
    for attempt in range(3):
        try:
            resp = session.get(url, headers={"Referer": f"{SITE_URL}/en/chapter/{slug}"}, timeout=30)
            if resp.status_code == 200:
                filepath.write_bytes(resp.content)
                return filepath.name, True
        except:
            time.sleep(2)
    return filepath.name, False

def images_to_pdf(image_dir, pdf_path):
    image_dir = Path(image_dir)
    images = sorted(image_dir.glob("page_*"))
    if not images:
        return
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert([str(img) for img in images]))

def main():
    comic_slug = "batman-2025"
    folder_name = "batman(2025)"

    print(f"Downloading {folder_name}...")
    base_output = BASE_DIR / folder_name
    base_output.mkdir(parents=True, exist_ok=True)

    chapters = get_all_chapters(comic_slug)
    if not chapters:
        print("No chapters found")
        return

    for idx, slug in enumerate(chapters, 1):
        print(f"  [{idx}/{len(chapters)}] {slug}")
        info = get_chapter_info(slug)
        if not info:
            continue

        issue_match = re.search(r'#(\d+)', info.get("full_name", slug))
        issue = f"{folder_name}#{issue_match.group(1)}" if issue_match else slug
        chapter_dir = base_output / issue

        urls = get_chapter_images(slug)
        if not urls:
            continue

        chapter_dir.mkdir(parents=True, exist_ok=True)
        tasks = []
        for i, url in enumerate(urls):
            ext = os.path.splitext(url.split("/")[-1])[1] or ".jpg"
            tasks.append((url, str(chapter_dir / f"page_{i+1:03d}{ext}"), slug))

        with ThreadPoolExecutor(max_workers=8) as ex:
            for f in as_completed([ex.submit(download_page, t) for t in tasks]):
                pass

        pdf_path = base_output / f"{issue}.pdf"
        images_to_pdf(chapter_dir, pdf_path)
        shutil.rmtree(chapter_dir)
        print(f"    -> {pdf_path.name}")

    print(f"\nDone! PDFs in: {base_output}")

if __name__ == "__main__":
    main()
