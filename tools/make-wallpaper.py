#!/usr/bin/env python3
"""Render the Ruist neon wallpaper and badge from the official mark using Pillow."""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SIZE = (1920, 1080)


def make_badge():
    mark = Image.open(ROOT / "branding/ruist-logo-mark.png").convert("RGBA")
    ink = ImageOps.invert(mark.convert("L"))
    ink = Image.composite(ink, Image.new("L", mark.size), mark.getchannel("A"))
    ink = ink.crop(ink.getbbox()).resize((420, 420), Image.Resampling.LANCZOS)
    badge = Image.new("RGBA", (512, 512))
    draw = ImageDraw.Draw(badge)
    draw.ellipse((12, 12, 499, 499), fill="#080f23", outline="#245b94", width=5)
    draw.arc((12, 12, 499, 499), -78, 26, fill="#31caff", width=6)
    draw.arc((12, 12, 499, 499), 104, 172, fill="#8972ff", width=6)
    seal = ImageOps.colorize(ink, black="#080f23", white="#080f23").convert("RGBA")
    shape = Image.new("RGBA", ink.size, "#f0f7ff")
    mask = Image.new("L", ink.size)
    ImageDraw.Draw(mask).ellipse((0, 0, 419, 419), fill=255)
    shape.putalpha(mask)
    seal.putalpha(ink)
    badge.alpha_composite(shape, (46, 46))
    badge.alpha_composite(seal, (46, 46))
    return badge


def make_wallpaper(badge, output):
    wallpaper = Image.new("RGB", SIZE, "#070b16")
    draw = ImageDraw.Draw(wallpaper)
    draw.polygon([(0, 820), (1920, 250), (1920, 1080), (0, 1080)], fill="#0a1326")
    draw.polygon([(530, 1080), (1920, 663), (1920, 1080)], fill="#0c1932")
    glow = Image.new("RGBA", SIZE)
    light = ImageDraw.Draw(glow)
    light.line((0, 820, 1920, 250), fill="#127ae0", width=11)
    light.line((530, 1080, 1920, 663), fill="#7c47e0", width=9)
    wallpaper = Image.alpha_composite(wallpaper.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(33)))
    draw = ImageDraw.Draw(wallpaper)
    draw.line((0, 820, 1920, 250), fill="#2086bd", width=2)
    draw.line((530, 1080, 1920, 663), fill="#5640a4", width=2)
    for x in range(72, 1850, 36):
        for y in range(74, 1005, 36):
            draw.point((x, y), fill="#263751")
    draw.line((70, 150, 70, 72, 148, 72), fill="#30caff", width=3)
    draw.line((1772, 1008, 1850, 1008, 1850, 930), fill="#8972ff", width=3)
    wallpaper.alpha_composite(badge.resize((212, 212), Image.Resampling.LANCZOS), (854, 377))
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 51)
    draw.text((960, 625), "R U I S T   O S", font=font, fill="#f0f7ff", anchor="mm")
    wallpaper.convert("RGB").save(output, optimize=True)


if __name__ == "__main__":
    mark = make_badge()
    make_wallpaper(mark, sys.argv[1] if len(sys.argv) > 1 else "ruist-neon.png")
    if len(sys.argv) > 2:
        mark.save(sys.argv[2], optimize=True)
