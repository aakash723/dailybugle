import os
import tkinter as tk

os.chdir(os.path.dirname(__file__))
root = tk.Tk()
root.withdraw()

src = 'fin.png'
dst = 'fin_white_comics.png'
img = tk.PhotoImage(file=src)
w = img.width()
h = img.height()
print('loaded', src, 'size', w, h)

# Scan only the right-side region where COMICS appears.
x_start = int(w * 0.65)
black_pixels = []
for y in range(h):
    for x in range(x_start, w):
        px = img.get(x, y)
        if isinstance(px, tuple):
            r, g, b = px
        else:
            parts = px.split()
            if len(parts) >= 3:
                r, g, b = map(int, parts[:3])
            else:
                continue
        if r < 80 and g < 80 and b < 80:
            black_pixels.append((x, y))

if not black_pixels:
    raise RuntimeError('No black text pixels found in the COMICS region.')

xs = [x for x, _ in black_pixels]
ys = [y for _, y in black_pixels]
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
print('black pixel bbox:', min_x, min_y, max_x, max_y, 'count', len(black_pixels))

# Replace only black pixels within the bounding box with white.
threshold = 80
for y in range(min_y, max_y + 1):
    for x in range(min_x, max_x + 1):
        px = img.get(x, y)
        if isinstance(px, tuple):
            r, g, b = px
        else:
            parts = px.split()
            if len(parts) >= 3:
                r, g, b = map(int, parts[:3])
            else:
                continue
        if r < threshold and g < threshold and b < threshold:
            img.put('#ffffff', (x, y))

img.write(dst, format='png')
print('saved', dst)
