# Generate responsive JPEG variants for every gallery image.
import json, os, sys
from PIL import Image, ImageOps
SRC = sys.argv[1]   # _scrape dir
OUT = sys.argv[2]   # site/images
WIDTHS = [150, 300, 400, 550, 700, 900, 1200, 1600, 2500]
LB = (2400, 1800)   # lightbox box (Format used 1600x1200; bigger for retina)
os.makedirs(OUT, exist_ok=True)
meta = []
for x in json.load(open(os.path.join(SRC, 'images.json'))):
    order = x['order']
    name = 'cover' if order == 'cover' else '%02d' % order
    im = Image.open(os.path.join(SRC, x['local']))
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[-1]); im = bg
    elif im.mode != 'RGB':
        im = im.convert('RGB')
    W, H = im.size
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    def save(img, fn):
        kw = dict(quality=88, optimize=True, progressive=True)
        if icc: kw['icc_profile'] = icc
        img.save(os.path.join(d, fn), 'JPEG', **kw)
    variants = []
    for w in WIDTHS:
        if w > W and w != WIDTHS[0]:
            continue
        h = round(H * w / W)
        save(im.resize((w, h), Image.LANCZOS), '%d.jpg' % w)
        variants.append([w, h])
    if W not in [v[0] for v in variants] and W < 2500:
        save(im, '%d.jpg' % W); variants.append([W, H])
    lb = im.copy(); lb.thumbnail(LB, Image.LANCZOS); save(lb, 'lightbox.jpg')
    meta.append(dict(order=order, name=name, width=W, height=H, variants=variants, lightbox=list(lb.size)))
    print(name, W, H, len(variants), flush=True)
json.dump(meta, open(os.path.join(OUT, '..', 'image-variants.json'), 'w'), indent=1)
