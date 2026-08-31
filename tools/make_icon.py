"""Attenuation Auditor 아이콘 생성기.

콘셉트: 소리 원점(중심점) + 바깥으로 갈수록 옅어지는 동심원 링.
링이 멀어질수록 흐려지는 것 자체가 '거리 감쇠(attenuation)'를 뜻한다.

작은 크기에서 얇은 링이 뭉개지므로 크기대별로 링 수를 줄여 그린다.
각 크기는 8배 supersample 후 LANCZOS 축소 → 경계가 깨끗하다.

  python tools/make_icon.py

출력:
  assets/icon.ico          Tkinter 창 / 작업표시줄용 (다중 크기)
  assets/icon_256.png      미리보기용
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "assets")

ICO_SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256]
SS = 8  # supersample 배율

DISC = (16, 23, 32, 255)        # 바탕 원 — 어두운 네이비
RIM = (58, 92, 124, 255)        # 바탕 원 테두리 (실루엣이 배경에 묻히지 않게)
CORE = (234, 247, 249, 255)     # 소리 원점
GLOW = (93, 208, 216, 90)       # 원점 주변 번짐

# (반지름, 선두께, 색) — 반지름/두께는 아이콘 지름 대비 비율.
# 바깥 링일수록 알파가 낮다 = 감쇠.
RINGS_FULL = [
    (0.235, 0.052, (110, 224, 230, 235)),
    (0.335, 0.044, (77, 166, 200, 175)),
    (0.435, 0.036, (52, 110, 150, 120)),
]
RINGS_MID = [
    (0.265, 0.090, (120, 228, 234, 245)),
    (0.415, 0.066, (78, 158, 194, 180)),
]
# 16~20px 은 창 제목표시줄 크기. 링 하나만 굵게 + 중심을 크게 잡아야 형태가 남는다.
RINGS_SMALL = [
    (0.355, 0.150, (120, 228, 234, 248)),
]


def ring_set(size: int):
    if size >= 48:
        return RINGS_FULL, 0.105
    if size >= 24:
        return RINGS_MID, 0.135
    return RINGS_SMALL, 0.195


def render(size: int) -> Image.Image:
    rings, core_r = ring_set(size)
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2.0

    # 바탕 원 + 테두리
    pad = s * 0.012
    d.ellipse([pad, pad, s - pad, s - pad], fill=DISC,
              outline=RIM, width=max(1, int(s * 0.014)))

    # 감쇠 링 — 바깥으로 갈수록 옅고 얇게
    for rel_r, rel_w, color in rings:
        r = s * rel_r
        w = max(1, int(round(s * rel_w)))
        d.ellipse([c - r, c - r, c + r, c + r], outline=color, width=w)

    # 원점 주변 번짐 (링과 중심을 시각적으로 잇는다)
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gr = s * core_r * 2.1
    gd.ellipse([c - gr, c - gr, c + gr, c + gr], fill=GLOW)
    glow = glow.filter(ImageFilter.GaussianBlur(s * 0.045))
    img = Image.alpha_composite(img, glow)

    # 소리 원점
    d = ImageDraw.Draw(img)
    cr = s * core_r
    d.ellipse([c - cr, c - cr, c + cr, c + cr], fill=CORE)

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    frames = [render(n) for n in ICO_SIZES]

    # append_images 로 크기별로 따로 그린 그림을 그대로 넣는다.
    # sizes= 만 주면 Pillow 가 가장 큰 그림을 축소해 채우므로,
    # 작은 크기용으로 단순화한 그림이 버려진다.
    ico_path = os.path.join(OUT_DIR, "icon.ico")
    frames[-1].save(ico_path, format="ICO",
                    sizes=[(n, n) for n in ICO_SIZES],
                    append_images=frames[:-1])

    png_path = os.path.join(OUT_DIR, "icon_256.png")
    frames[-1].save(png_path, format="PNG")

    print("created:", ico_path)
    print("  sizes:", ", ".join(f"{n}x{n}" for n in ICO_SIZES))
    print("created:", png_path)


if __name__ == "__main__":
    main()
