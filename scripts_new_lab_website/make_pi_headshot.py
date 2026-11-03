"""Build the PI headshot from IMG_5391.HEIC.

Removes the stray gray hair below the left ear (masked to light, low-saturation
pixels inside a hand-placed polygon, then filled by diffusion from the
surrounding background), levels the head tilt, and crops to a square that
excludes the second person at the lower right.

Usage:
    python scripts_new_lab_website/make_pi_headshot.py [project_root]
Writes IMG_5391_headshot.jpg (full resolution) and
assets/img/people/casola.jpg (600 x 750). Requires ffmpeg for HEIC decoding.
"""

import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROTATE_DEG = 14
# Tuft region in original-image pixels (1326 x 1710), traced around the wisps
# below the ear; the neck edge is the right side of the polygon.
TUFT = [(205, 845), (300, 830), (395, 860), (392, 940), (372, 1005),
        (345, 1040), (205, 1030)]
# Dark archway texture left of the tuft, used to fill it (x range, same rows).
ARCH_X = (60, 200)
# 4:5 portrait crop after rotation: left, top, width, height (rotated-image
# pixels). No square holds the whole head, chin included, without part of the
# second person; this is the largest 4:5 box that does, searched at this angle.
CROP = (328, 315, 1038, 1298)


def decode_heic(path):
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        out = os.path.join(d, "frame.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path,
                        "-frames:v", "1", out], check=True)
        return Image.open(out).convert("RGB").copy()


def hair_mask(rgb, polygon):
    region = Image.new("L", (rgb.shape[1], rgb.shape[0]), 0)
    ImageDraw.Draw(region).polygon(polygon, fill=255)
    region = np.asarray(region) > 0
    r, g, b = (rgb[..., i].astype(float) for i in range(3))
    bright = (r + g + b) / 3
    sat = np.max(rgb, axis=2).astype(float) - np.min(rgb, axis=2)
    skin = (r - b) > 28
    shirt = ((r - g) > 6) & ((b - g) > 4)
    mask = region & (bright > 55) & (sat < 50) & ~skin & ~shirt
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    return np.asarray(m) > 0


def texture_fill(rgb, mask):
    """Fill with archway texture from the same rows, then feather the edges."""
    out = rgb.astype(float)
    ys, xs = np.nonzero(mask)
    x0, x1 = ARCH_X
    src_x = x0 + (xs - TUFT[0][0]) % (x1 - x0)
    patch = out.copy()
    patch[ys, xs] = out[ys, src_x]
    alpha = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(2.5))).astype(float)[..., None] / 255
    return np.clip(patch * alpha + out * (1 - alpha), 0, 255).astype(np.uint8)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    src = os.path.join(root, "IMG_5391.HEIC")
    if not os.path.exists(src):
        sys.exit(f"error: {src} not found")
    im = decode_heic(src)
    assert im.size == (1326, 1710), f"unexpected size {im.size}; recheck TUFT and CROP"
    rgb = np.asarray(im)
    mask = hair_mask(rgb, TUFT)
    print(f"retouched {int(mask.sum())} pixels", file=sys.stderr)
    fixed = Image.fromarray(texture_fill(rgb, mask))
    rot = fixed.rotate(ROTATE_DEG, resample=Image.BICUBIC, expand=True)
    x, y, w, h = CROP
    assert x + w <= rot.width and y + h <= rot.height, "crop outside rotated image"
    head = rot.crop((x, y, x + w, y + h))
    full = os.path.join(root, "IMG_5391_headshot.jpg")
    head.save(full, quality=92)
    web = os.path.join(root, "assets", "img", "people", "casola.jpg")
    head.resize((600, 750), Image.LANCZOS).save(web, quality=88, optimize=True)
    print(full)
    print(web)


if __name__ == "__main__":
    main()
