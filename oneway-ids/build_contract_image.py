#!/usr/bin/env python3
"""Render the observability contract as a single memorable image.

The deck's headline is that five of the features the problem statement
requests are impossible under its own first constraint. That idea is much
stronger shown than described: the requirement space, with a visible hole
punched in it. This draws that picture directly from core/observability.py
so it can never drift from the contract it depicts.

Usage:  .venv/bin/python build_contract_image.py  # -> contract.png
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "contract.png")

W, H = 1600, 900

BG = (13, 17, 23)
INK = (230, 237, 243)
MUTED = (157, 165, 176)
ACCENT = (88, 166, 255)
GOOD = (63, 185, 80)
WARN = (210, 153, 34)
BAD = (248, 84, 70)
PANEL = (22, 27, 34)
LINE = (48, 56, 68)

STATUS_COLOR = {"OBSERVABLE": GOOD, "IMPOSSIBLE": BAD, "SUBSTITUTED": WARN}


def _font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/nix/store/*/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    import glob
    for p in paths:
        for f in (glob.glob(p) if "*" in p else [p]):
            if os.path.exists(f):
                return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    import sys
    sys.path.insert(0, HERE)
    from core.observability import CONTRACT

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = _font(44, bold=True)
    f_sub = _font(24)
    f_head = _font(22, bold=True)
    f_cell = _font(20)
    f_small = _font(18)

    d.text((60, 40), "The one-way observability contract", font=f_title, fill=INK)
    d.text((60, 104), "21 features the problem statement requests — 15 are observable, "
                      "1 is substituted, and 5 cannot exist at all",
           font=f_sub, fill=MUTED)

    # ---- the punchline band -------------------------------------------
    by = 165
    d.rectangle([60, by, W - 60, by + 96], fill=(30, 18, 18), outline=BAD, width=2)
    d.text((84, by + 14), "Five requested features are impossible under the PS's own "
                          "constraint (a)", font=f_head, fill=BAD)
    d.text((84, by + 50), "JA3S server fingerprint · negotiated cipher + server "
                          "certificate · round-trip time · NXDOMAIN ratio · "
                          "outbound:inbound byte ratio", font=f_cell, fill=(240, 200, 195))

    # ---- table of all 21 rows -----------------------------------------
    tx, tw = 60, W - 120
    y = by + 112
    row_h = 24
    cols = [(0.00, 0.44), (0.44, 0.56), (0.56, 1.00)]  # feature, class, status/reason

    d.rectangle([tx, y, tx + tw, y + 34], fill=PANEL)
    for (a, b), label in zip(cols, ["Feature the PS requests", "Class", "Status"]):
        d.text((tx + tw * a + 10, y + 6), label, font=f_head, fill=ACCENT)
    d.line([tx, y + 34, tx + tw, y + 34], fill=LINE, width=1)
    y += 34

    for r in sorted(CONTRACT, key=lambda r: (r["ps_class"], r["status"] != "IMPOSSIBLE")):
        st = r["status"]
        col = STATUS_COLOR[st]
        # status dot
        cx = tx + tw * cols[1][0] + 18
        cy = y + row_h // 2
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=col)
        d.text((tx + tw * cols[0][0] + 10, y + 2), r["feature"], font=f_cell, fill=INK)
        d.text((tx + tw * cols[1][0] + 34, y + 2), f"({r['ps_class']})", font=f_cell, fill=MUTED)
        label = {"OBSERVABLE": "observable", "IMPOSSIBLE": "IMPOSSIBLE",
                 "SUBSTITUTED": "substituted"}[st]
        d.text((tx + tw * cols[2][0] + 10, y + 2), label, font=f_cell, fill=col)
        y += row_h

    # ---- legend ---------------------------------------------------------
    y += 8
    lx = 60
    for label, col in [("15 observable — row cites the consuming function", GOOD),
                       ("1 substituted — impossible signal, one-way proxy used", WARN),
                       ("5 IMPOSSIBLE — information-theoretically absent", BAD)]:
        d.ellipse([lx, y + 6, lx + 12, y + 18], fill=col)
        d.text((lx + 22, y + 2), label, font=f_small, fill=MUTED)
        lx += 22 + d.textlength(label, font=f_small) + 48

    img.save(OUT)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
