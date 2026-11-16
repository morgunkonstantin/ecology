#!/usr/bin/env python3
"""Обложка статьи: картинка в начале страницы и превью для соцсетей.

    python3 build/make_cover.py ИСХОДНИК СТРАНИЦА --alt "описание" \
        [--name имя] [--mobile-x 20] [--og-center 0.3]

ИСХОДНИК — широкая картинка примерно 3:1 (лучше 2000×666).
СТРАНИЦА — файл статьи в корне сайта, например essay-cob.html.

Что делает:
  1. assets/img/<имя>-hero-1200.webp и -hero-2000.webp — обложка;
     assets/img/<имя>-og.jpg — превью 1200×630 для соцсетей.
  2. Вставляет <figure class="hero-cover"> перед первым блоком заголовка
     (<section class="hero">, "essay-hero" или "lab-hero"). Повторный
     запуск заменяет прежнюю обложку, а не добавляет вторую.
  3. Убирает бледный значок .hero-mark-svg в шапке: его роль берёт картинка.
  4. Прописывает og_image и og_image_alt в build/pages.json.

После него запустить python3 build/patch_pages.py, чтобы обновились
мета-теги превью в <head>.

--mobile-x   горизонтальная точка обрезки на телефоне (картинка там 16:9),
             в процентах: 0 — левый край, 100 — правый. По умолчанию 50.
--og-center  где центр кадра превью по ширине исходника, от 0 до 1.
"""
import argparse
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
PAGES = os.path.join(ROOT, "build", "pages.json")


def make_images(src, name, og_center):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    os.makedirs(IMG_DIR, exist_ok=True)
    out = {}
    for width in (1200, 2000):
        path = os.path.join(IMG_DIR, "%s-hero-%d.webp" % (name, width))
        img = im if w == width else im.resize((width, round(h * width / w)), Image.LANCZOS)
        img.save(path, "WEBP", quality=82, method=6)
        out[width] = img.size
    # превью 1200×630: вырезаем кусок нужной пропорции вокруг og_center
    crop_w = min(w, round(h * 1200 / 630))
    x0 = max(0, min(w - crop_w, round(w * og_center - crop_w / 2)))
    og = im.crop((x0, 0, x0 + crop_w, h)).resize((1200, 630), Image.LANCZOS)
    og.save(os.path.join(IMG_DIR, "%s-og.jpg" % name), "JPEG",
            quality=84, optimize=True, progressive=True)
    return out


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def patch_page(page, name, alt, mobile_x, size2000):
    path = os.path.join(ROOT, page)
    s = open(path, encoding="utf-8").read()

    # прежняя обложка — убрать (идемпотентность)
    s = re.sub(r'<figure class="hero-cover[^"]*".*?</figure>\n\n?', "", s, flags=re.S)

    m = re.search(r'<section class="(hero|essay-hero|lab-hero)"', s)
    if not m:
        sys.exit("В %s не найден <section class=\"hero\">, \"essay-hero\" или \"lab-hero\"" % page)
    extra = "" if m.group(1) == "hero" else " hero-cover--essay"
    w, h = size2000
    figure = (
        '<figure class="hero-cover%s" style="--cover-x-mobile:%s%%;">\n'
        '  <img src="assets/img/%s-hero-2000.webp"\n'
        '       srcset="assets/img/%s-hero-1200.webp 1200w, assets/img/%s-hero-2000.webp 2000w"\n'
        '       sizes="100vw" width="%d" height="%d" fetchpriority="high" decoding="async"\n'
        '       alt="%s">\n'
        '</figure>\n\n'
    ) % (extra, mobile_x, name, name, name, w, h, esc(alt))
    s = s[:m.start()] + figure + s[m.start():]

    s = re.sub(r'\n\s*<div class="hero-mark-svg">.*?</svg></div>', "", s, count=1, flags=re.S)
    open(path, "w", encoding="utf-8").write(s)


def update_pages(page, name, alt):
    text = open(PAGES, encoding="utf-8").read()
    data = json.loads(text)
    if page not in data:
        sys.exit("%s нет в build/pages.json" % page)
    data[page]["og_image"] = "assets/img/%s-og.jpg" % name
    data[page]["og_image_alt"] = alt
    indent = 1 if text.startswith("{\n \"") else 2
    with open(PAGES, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n" if text.endswith("\n") else "")


def main():
    ap = argparse.ArgumentParser(description="Обложка статьи и превью для соцсетей")
    ap.add_argument("src")
    ap.add_argument("page")
    ap.add_argument("--alt", required=True)
    ap.add_argument("--name", help="имя файлов; по умолчанию из имени страницы")
    ap.add_argument("--mobile-x", type=int, default=50)
    ap.add_argument("--og-center", type=float, default=0.5)
    a = ap.parse_args()
    name = a.name or re.sub(r"^(essay|lab|section|place|thing|term|number|revision)-", "",
                            a.page[:-5] if a.page.endswith(".html") else a.page)
    # имя файлов не должно совпадать с обложкой другой страницы
    data = json.load(open(PAGES, encoding="utf-8"))
    mine = "assets/img/%s-og.jpg" % name
    for other, info in data.items():
        if other != a.page and info.get("og_image") == mine:
            sys.exit("Имя «%s» уже занято обложкой %s — задайте другое через --name" % (name, other))
    sizes = make_images(a.src, name, a.og_center)
    patch_page(a.page, name, a.alt, a.mobile_x, sizes[2000])
    update_pages(a.page, name, a.alt)
    print("  %-30s → assets/img/%s-*" % (a.page, name))


if __name__ == "__main__":
    main()
