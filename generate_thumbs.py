import fitz
import os

MAX_W = 300

def generate_thumbnails():
    base = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(os.path.join(base, 'all_comics')):
        for f in files:
            if not f.lower().endswith('.pdf'):
                continue
            pdf_path = os.path.join(root, f)
            png_path = pdf_path[:-4] + '.png'
            if os.path.exists(png_path):
                continue
            rel = os.path.relpath(png_path, base)
            print(f"Generating: {rel}")
            try:
                doc = fitz.open(pdf_path)
                page = doc[0]
                r = page.rect
                scale = MAX_W / r.width
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat)
                pix.save(png_path)
                doc.close()
            except Exception as e:
                print(f"  FAILED: {e}")

if __name__ == '__main__':
    generate_thumbnails()
