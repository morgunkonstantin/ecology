#!/usr/bin/env python3
"""Миниатюры обложек в карточках-ссылках.

    python3 build/make_card_thumbs.py

1. Для каждой страницы с обложкой (поле og_image в build/pages.json) делает
   assets/img/<имя>-thumb.webp — 640×360 (16:9), кадр по той же точке, что
   обложка на телефоне (--cover-x-mobile в <figure class="hero-cover">).
2. Во всех страницах в карточки-ссылки (классы из CARD_CLASSES), которые
   ведут на страницу с обложкой, первым элементом вставляет
   <img class="card-thumb">. Повторный запуск заменяет миниатюры, а не
   добавляет новые; карточки на страницы без обложки не трогает.

Запускать после make_cover.py, make_section_lists.py и make_paths.py:
эти скрипты пересобирают карточки и стирают миниатюры.
"""
import json
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
CARD_CLASSES = ("rel-card", "related-card", "sec-mat-card", "fc", "pt-card")
W, H = 640, 360


def covers():
    """страница → имя файлов обложки ('cob' для assets/img/cob-*)"""
    pages = json.load(open(os.path.join(ROOT, "build", "pages.json"), encoding="utf-8"))
    out = {}
    for page, info in pages.items():
        m = re.match(r"assets/img/(.+)-og\.jpg$", info.get("og_image", ""))
        if m and os.path.exists(os.path.join(IMG, m.group(1) + "-hero-2000.webp")):
            out[page] = m.group(1)
    return out


def focus_x(page):
    path = os.path.join(ROOT, page)
    if not os.path.exists(path):
        return 50
    m = re.search(r'class="hero-cover[^"]*"[^>]*--cover-x-mobile:(\d+)%',
                  open(path, encoding="utf-8").read())
    return int(m.group(1)) if m else 50


def make_thumb(name, x_pct):
    src = os.path.join(IMG, name + "-hero-2000.webp")
    dst = os.path.join(IMG, name + "-thumb.webp")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    cw = min(w, round(h * W / H))
    x0 = round((w - cw) * x_pct / 100)       # как object-position: x%
    im.crop((x0, 0, x0 + cw, h)).resize((W, H), Image.LANCZOS).save(
        dst, "WEBP", quality=78, method=6)


THUMB_RE = re.compile(r'\s*<img class="card-thumb"[^>]*>')
OPEN_RE = re.compile(r'<a\s[^>]*>')


def patch_html(path, cov):
    s = open(path, encoding="utf-8").read()
    out, pos, n = [], 0, 0
    for m in OPEN_RE.finditer(s):
        tag = m.group(0)
        cls = re.search(r'class="([^"]*)"', tag)
        href = re.search(r'href="([^"#?]+)', tag)
        if not cls or not href or cls.group(1).split()[0] not in CARD_CLASSES:
            continue
        out.append(s[pos:m.end()])
        rest = s[m.end():]
        old = THUMB_RE.match(rest)
        pos = m.end() + (old.end() if old else 0)
        target = href.group(1)
        if target in cov:
            out.append('<img class="card-thumb" src="assets/img/%s-thumb.webp" '
                       'width="%d" height="%d" alt="" loading="lazy" decoding="async">'
                       % (cov[target], W, H))
            n += 1
    out.append(s[pos:])
    new = "".join(out)
    if new != s:
        open(path, "w", encoding="utf-8").write(new)
    return n


def main():
    cov = covers()
    for page, name in cov.items():
        make_thumb(name, focus_x(page))
    total = 0
    for f in sorted(os.listdir(ROOT)):
        if f.endswith(".html"):
            total += patch_html(os.path.join(ROOT, f), cov)
    print("миниатюр: %d файлов, %d карточек" % (len(cov), total))


if __name__ == "__main__":
    main()
