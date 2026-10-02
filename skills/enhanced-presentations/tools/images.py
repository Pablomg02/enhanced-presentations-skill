#!/usr/bin/env python3
"""Manage the embedded photos (const IMG = {...}) of an HTML presentation.

  images.py topic.html list
  images.py topic.html put name photo.png [--crop x0,y0,x1,y1] [--height 420] [--color] [--quality 78]
  images.py topic.html remove name

By default: grayscale, autocontrast, JPEG, maximum height 420 px. In the HTML
it is used with <img data-img="name"> or, from JS, IMG.name.
"""
import argparse, base64, io, json, re, sys
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('order', choices=['list', 'put', 'remove'])
ap.add_argument('name', nargs='?'); ap.add_argument('photo', nargs='?')
ap.add_argument('--crop'); ap.add_argument('--height', type=int, default=420)
ap.add_argument('--color', action='store_true'); ap.add_argument('--quality', type=int, default=78)
a = ap.parse_args()

src = open(a.html, encoding='utf-8').read()
m = re.search(r'^const IMG = (\{.*\});$', src, re.M)
if not m: sys.exit('The line "const IMG = {...};" was not found in ' + a.html)
imgs = json.loads(m.group(1))

if a.order == 'list':
    for k, v in imgs.items(): print(f'{k:20s} {len(v) * 3 // 4 // 1024:4d} KB')
    print(f'Total {sum(len(v) for v in imgs.values()) // 1024} KB in base64'); sys.exit()
if not a.name: sys.exit('Missing name')
if a.order == 'remove':
    if a.name not in imgs: sys.exit(f'There is no image "{a.name}" in IMG')
    imgs.pop(a.name)
else:
    if not a.photo: sys.exit('Missing photo: images.py pres.html put name photo.png')
    im = Image.open(a.photo).convert('RGBA')
    background = Image.new('RGBA', im.size, 'white'); background.alpha_composite(im); im = background.convert('RGB')
    if a.crop: im = im.crop(tuple(int(v) for v in a.crop.split(',')))
    if not a.color: im = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=0.5)
    if im.height > a.height: im = im.resize((round(im.width * a.height / im.height), a.height), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=a.quality, optimize=True, progressive=True)
    imgs[a.name] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    print(a.name, im.size, len(b.getvalue()) // 1024, 'KB')
line = 'const IMG = ' + json.dumps(imgs, separators=(',', ':')) + ';'
src = src[:m.start()] + line + src[m.end():]
open(a.html, 'w', encoding='utf-8').write(src)
