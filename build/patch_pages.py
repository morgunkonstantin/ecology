#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — приведение всех страниц к одному техническому стандарту.

Скрипт идемпотентный: его можно запускать сколько угодно раз, повторно
он ничего не добавит (все вставки помечены комментарием ECO:MANAGED).

Запуск из корня сайта:   python3 build/patch_pages.py
"""

import json
import os
import re
import sys
import glob

SITE = "https://morgunkonstantin.github.io/ecology"
MARK = "ECO:MANAGED"

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400"
         "&family=Jost:wght@300;400;500&display=swap")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

with open("build/pages.json", encoding="utf-8") as fh:
    META = json.load(fh)

SECTION_MAP = {
    "Философия": "section-philosophy.html", "Психология": "section-psychology.html",
    "Стиль жизни": "section-lifestyle.html", "Технологии": "section-technologies.html",
    "Питание": "section-food.html", "Компост": "section-compost.html",
    "Архитектура": "section-architecture.html", "Строительство": "section-construction.html",
    "Экономика": "section-economy.html", "Образование": "section-education.html",
    "Сообщество": "section-community.html", "Путешествия": "section-travel.html",
    "Здоровье": "section-health.html", "Наука": "section-science.html",
}


def crumb_trail(fname, info):
    """Иерархический путь: [(название, ссылка|None), ...]; последний элемент — текущая страница (ссылка None)."""
    crumbs = [("Главная", "index.html")]
    if fname == "index.html":
        return crumbs
    if fname.startswith("section-"):
        if info.get("parent"):
            crumbs.append((info.get("parent_title", ""), info["parent"]))
        else:
            sec = info.get("section_title")
            hub = SECTION_MAP.get(sec)
            if hub and hub != fname:
                crumbs.append((sec, hub))
        crumbs.append((info.get("title", fname), None))
        return crumbs
    sec = info.get("section_title")
    hub = SECTION_MAP.get(sec)
    if hub and hub != fname:
        hub_info = META.get(hub, {})
        if hub_info.get("parent"):
            crumbs.append((hub_info.get("parent_title", ""), hub_info["parent"]))
        crumbs.append((sec, hub))
    crumbs.append((info.get("title", fname), None))
    return crumbs


def build_breadcrumb_html(fname, info):
    trail = crumb_trail(fname, info)
    if fname == "index.html" or len(trail) < 2:
        return ""
    parts = []
    for nm, href in trail:
        if href is None:
            disp = nm if len(nm) <= 52 else nm[:50].rstrip() + "…"
            parts.append('<span class="bc-current">%s</span>' % esc(disp))
        else:
            parts.append('<a href="%s">%s</a>' % (href, esc(nm)))
    inner = ' <span class="bc-sep">\u2192</span> '.join(parts)
    return ('<!-- %s:breadcrumb -->\n'
            '<nav class="breadcrumb" aria-label="\u0425\u043b\u0435\u0431\u043d\u044b\u0435 \u043a\u0440\u043e\u0448\u043a\u0438">%s</nav>\n'
            '<!-- /%s:breadcrumb -->' % (MARK, inner, MARK))


# ── вспомогательные ──────────────────────────────────────────────────

def close_tag(s, start, tag="div"):
    """Найти конец блока, начинающегося в позиции start."""
    depth = 0
    for m in re.finditer(r"<%s\b|</%s>" % (tag, tag), s[start:]):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return start + m.end()
        else:
            depth += 1
    return -1


def clean(text):
    return " ".join(re.sub(r"<[^>]+>", " ", text).split())


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


# ── блоки, которые вставляем в <head> ────────────────────────────────

DEFAULT_OG_IMAGE = "assets/og-image.png"
DEFAULT_OG_ALT = "ЭкоСознание — экология как способ смотреть на реальность"


def build_head(fname, info, has_twitter_card=False):
    url = "%s/%s" % (SITE, "" if fname == "index.html" else fname)
    title = info["title"]
    desc = info["description"]
    kind = info["kind"]
    # Своя картинка превью для соцсетей: "og_image" в pages.json (путь от
    # корня сайта, строго 1200×630) и "og_image_alt". Иначе — общая заставка.
    og_image = "%s/%s" % (SITE, info.get("og_image", DEFAULT_OG_IMAGE))
    og_alt = info.get("og_image_alt", DEFAULT_OG_ALT)
    twitter_card = ('  <meta name="twitter:card" content="summary_large_image">\n'
                    if info.get("og_image") and not has_twitter_card else "")

    ld = {
        "@context": "https://schema.org",
        "@type": {"article": "Article", "section": "CollectionPage",
                  "home": "WebSite"}.get(kind, "WebPage"),
        "name": title,
        "headline": title,
        "description": desc,
        "inLanguage": "ru-RU",
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "ЭкоСознание", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "ЭкоСознание", "url": SITE + "/"},
    }
    if kind == "home":
        ld.pop("isPartOf")
        ld["name"] = "ЭкоСознание"
    if info.get("date"):
        ld["datePublished"] = info["date"]
    if info.get("og_image"):
        ld["image"] = og_image
    if kind == "article":
        ld["author"] = {"@type": "Organization", "name": "ЭкоСознание"}
        ld["articleSection"] = info.get("section_title", "")

    crumbs = []
    for pos, (nm, href) in enumerate(crumb_trail(fname, info), 1):
        item = (SITE + "/") if href == "index.html" else (url if href is None else "%s/%s" % (SITE, href))
        crumbs.append({"@type": "ListItem", "position": pos, "name": nm, "item": item})
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList",
                  "itemListElement": crumbs}

    noindex = ('  <meta name="robots" content="noindex, follow">\n'
               if info.get("noindex") else "")

    return """<!-- {mark}:head -->
{noindex}  <link rel="canonical" href="{url}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="ЭкоСознание">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{og_alt}">
{twitter_card}  <meta name="twitter:image" content="{og_image}">
  <meta name="theme-color" content="#faf6ef">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="alternate" type="application/rss+xml" title="ЭкоСознание — RSS" href="feed.xml">
  <link rel="stylesheet" href="assets/site.css">
  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{bc}</script>
<!-- /{mark}:head -->
""".format(mark=MARK, url=url, site=SITE, noindex=noindex,
           og_image=og_image, og_alt=esc(og_alt), twitter_card=twitter_card,
           ld=json.dumps(ld, ensure_ascii=False, separators=(",", ":")),
           bc=json.dumps(breadcrumb, ensure_ascii=False, separators=(",", ":")))


# ── основная обработка одного файла ──────────────────────────────────

def patch(fname):
    src = open(fname, encoding="utf-8").read()
    s = src
    log = []

    info = META[fname]

    # 1. Снять предыдущую версию управляемых блоков (идемпотентность)
    s = re.sub(r"<!-- %s:head -->.*?<!-- /%s:head -->\n?" % (MARK, MARK), "", s, flags=re.S)
    s = re.sub(r"\n?<!-- %s:js -->.*?<!-- /%s:js -->" % (MARK, MARK), "", s, flags=re.S)
    s = re.sub(r'\s*<a class="skip-link"[^>]*>.*?</a>', "", s, flags=re.S)
    s = re.sub(r"<!-- %s:breadcrumb -->.*?<!-- /%s:breadcrumb -->\n?" % (MARK, MARK), "", s, flags=re.S)

    # 1a. Старые картинки превью вне управляемого блока (например,
    #     ecosoznanie.ru/og-image.jpg): соцсети берут первую, а правильную
    #     ставит блок head ниже.
    s, n = re.subn(r'[ \t]*<meta (?:property="og:image(?::[a-z]+)?"|name="twitter:image")[^>]*>\n', "", s)
    if n:
        log.append("old og:image")

    # 2. Заголовок и описание
    if info.get("title_fix"):
        s = re.sub(r"<title>.*?</title>",
                   "<title>%s</title>" % esc(info["title_full"]), s, flags=re.S)
        log.append("title")

    # 3. Единый набор шрифтов + preconnect на gstatic
    s = re.sub(r'https://fonts\.googleapis\.com/css2\?[^"]+', FONTS, s)
    if "fonts.gstatic.com" not in s:
        s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
                      '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                      '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>', 1)
        log.append("preconnect")

    # 4. Убрать старую RSS-ссылку (она вернётся внутри управляемого блока)
    s = re.sub(r'\s*<link rel="alternate" type="application/rss\+xml"[^>]*>', "", s)

    # 5. class="no-js" на <html> + мгновенное снятие
    s = re.sub(r"<html lang=\"ru\"(?: class=\"[^\"]*\")?>", '<html lang="ru" class="no-js">', s, 1)
    if "classList.replace('no-js'" not in s:
        s = s.replace("<head>",
                      "<head>\n<script>document.documentElement.classList."
                      "replace('no-js','js');</script>", 1)

    # 6. Управляемый блок в <head>
    s = s.replace("</head>", build_head(fname, info, "twitter:card" in s) + "</head>", 1)

    # 7. skip-link сразу после <body>
    s = re.sub(r"(<body[^>]*>)",
               r'\1\n<a class="skip-link" href="#content">Перейти к содержанию</a>',
               s, 1)

    # 8. <main id="content"> ... </main>
    if 'id="content"' not in s.split("</head>")[1]:
        i = s.find('<div class="g-overlay"')
        end = close_tag(s, i) if i >= 0 else -1
        j = s.find("<footer")
        if end > 0 and j > end:
            s = (s[:end] + '\n<main id="content" tabindex="-1">\n'
                 + s[end:j] + "</main>\n" + s[j:])
            log.append("main")

    # 8.5 Видимая полоса хлебных крошек — сразу после <main id="content">
    bc = build_breadcrumb_html(fname, info)
    if bc:
        s = re.sub(r'(<main id="content"[^>]*>)', lambda m: m.group(1) + "\n" + bc, s, count=1)

    # 9. Скрипты: убрать все встроенные общие, подключить общий файл
    def drop(m):
        body = m.group(1)
        generic = ("g-drop-btn" in body and "gBurger" in body)      # общая навигация
        reveal = ("IntersectionObserver" in body and "reveal" in body)
        bar = ("readingBar" in body or "getElementById('rb')" in body)
        return "" if (generic or reveal or bar) else m.group(0)

    s = re.sub(r"<script(?![^>]*src)[^>]*>(.*?)</script>", drop, s, flags=re.S)
    s = re.sub(r"\n{3,}", "\n\n", s)

    tag = ('\n<!-- %s:js -->\n<script src="assets/global.js" defer></script>\n'
           '<!-- /%s:js -->' % (MARK, MARK))
    s = s.replace("</body>", tag + "\n</body>", 1)

    if s != src:
        open(fname, "w", encoding="utf-8").write(s)
    return log


if __name__ == "__main__":
    files = sorted(glob.glob("*.html"))
    for f in files:
        if f not in META:
            print("  ! нет метаданных для %s — пропуск" % f)
            continue
        log = patch(f)
        print("  %-38s %s" % (f, ", ".join(log) if log else "ok"))
    print("\nОбработано файлов: %d" % len(files))
