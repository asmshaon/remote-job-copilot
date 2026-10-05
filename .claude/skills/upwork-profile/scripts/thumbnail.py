"""Make a catalog (Project Catalog) or portfolio thumbnail for the Upwork profile of the person in `.me`.

  python .claude/skills/upwork-profile/scripts/thumbnail.py \
      --headline "Stripe subscription billing" \
      --sub "Plans, webhooks, failed-payment recovery" \
      --proof "Built for a platform 200+ teams use" \
      --tags "Node.js,Stripe,Webhooks" \
      --theme blue --out upwork/<me>/profile/2026-10-02/catalogs/1-stripe-billing/thumbnail.png

Options:
  --size 1000x750   pixel size; use the size the Upwork upload box asks for (default 1000x750, 4:3)
  --photo           put their profile photo in the corner (faces get more clicks in search)
  --theme           blue | green | purple | dark | orange (pick a different one per catalog)

Rules the skill follows: 3-6 words in the headline, readable at a small size, real facts only
(from the accomplishments PDF), no client logos or screenshots of client products.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS = Path("C:/Windows/Fonts")
BOLD = [FONTS / "segoeuib.ttf", FONTS / "arialbd.ttf", FONTS / "calibrib.ttf"]
REGULAR = [FONTS / "segoeui.ttf", FONTS / "arial.ttf", FONTS / "calibri.ttf"]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "job-apply-shared" / "scripts"))
import me  # noqa: E402

MAC_LINUX_FONTS = [Path("/Library/Fonts"), Path("/System/Library/Fonts/Supplemental"), Path.home() / "Library/Fonts",
                   Path("/usr/share/fonts/truetype/msttcorefonts"), Path("/usr/share/fonts/truetype/dejavu")]
BOLD += [d / n for d in MAC_LINUX_FONTS for n in ("Arial Bold.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf")]
REGULAR += [d / n for d in MAC_LINUX_FONTS for n in ("Arial.ttf", "arial.ttf", "DejaVuSans.ttf")]


def photo_path():
    return me.ROOT / me.paths()["profile_picture"] if me.paths()["profile_picture"] else None
THEMES = {  # background, accent, headline, body text
    "blue": ("#0f2a4a", "#3b9eff", "#ffffff", "#c9dcf2"),
    "green": ("#0f3324", "#2fd08a", "#ffffff", "#c6ead9"),
    "purple": ("#24183f", "#a77bff", "#ffffff", "#dcd0f7"),
    "dark": ("#16181d", "#ffb020", "#ffffff", "#d6d8de"),
    "orange": ("#3a1d0c", "#ff8a3d", "#ffffff", "#f3d9c7"),
    "teal": ("#0c2f33", "#2ec4c4", "#ffffff", "#c4e8e8"),
}


def font(paths, size):
    for p in paths:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=fnt) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--headline", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--proof", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--theme", default="blue", choices=THEMES)
    ap.add_argument("--size", default="1000x750")
    ap.add_argument("--photo", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if len(a.headline.split()) > 7:
        sys.exit("headline too long: keep it to 3-6 words so it reads at thumbnail size")
    w, h = (int(x) for x in a.size.lower().split("x"))
    bg, accent, head_c, body_c = THEMES[a.theme]
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    pad = int(w * 0.07)
    text_w = w - 2 * pad - (int(h * 0.30) if a.photo else 0)

    d.rectangle([0, 0, int(w * 0.018), h], fill=accent)  # accent bar on the left

    y = int(h * 0.14)
    hf = font(BOLD, int(h * 0.105))
    for line in wrap(d, a.headline, hf, text_w):
        d.text((pad, y), line, font=hf, fill=head_c)
        y += int(hf.size * 1.12)

    if a.sub:
        y += int(h * 0.03)
        sf = font(REGULAR, int(h * 0.048))
        for line in wrap(d, a.sub, sf, text_w):
            d.text((pad, y), line, font=sf, fill=body_c)
            y += int(sf.size * 1.3)

    if a.proof:
        y += int(h * 0.04)
        pf = font(BOLD, int(h * 0.046))
        d.text((pad, y), "✓", font=font([FONTS / "seguisym.ttf"] + BOLD, int(h * 0.046)), fill=accent)
        for line in wrap(d, a.proof, pf, text_w - int(h * 0.06)):
            d.text((pad + int(h * 0.06), y), line, font=pf, fill=head_c)
            y += int(pf.size * 1.3)

    if a.tags:  # chips along the bottom
        tf = font(BOLD, int(h * 0.04))
        x, ty = pad, h - pad - int(tf.size * 1.8)
        for tag in [t.strip() for t in a.tags.split(",") if t.strip()][:4]:
            tw = d.textlength(tag, font=tf)
            box = [x, ty, x + tw + tf.size * 1.2, ty + tf.size * 1.8]
            if box[2] > w - pad:
                break
            d.rounded_rectangle(box, radius=int(tf.size * 0.9), outline=accent, width=3)
            d.text((x + tf.size * 0.6, ty + tf.size * 0.35), tag, font=tf, fill=head_c)
            x = box[2] + tf.size * 0.6

    photo = photo_path()
    if a.photo and photo and photo.exists():
        size = int(h * 0.26)
        face = ImageOps.fit(Image.open(photo).convert("RGB"), (size, size))
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
        px, py = w - pad - size, int(h * 0.14)
        d.ellipse([px - 6, py - 6, px + size + 6, py + size + 6], fill=accent)
        img.paste(face, (px, py), mask)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"saved {out} ({w}x{h})")


if __name__ == "__main__":
    main()
