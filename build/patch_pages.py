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

def build_head(fname, info):
    url = "%s/%s" % (SITE, "" if fname == "index.html" else fname)
    title = info["title"]
    desc = info["description"]
    kind = info["kind"]

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
    if kind == "article":
        ld["author"] = {"@type": "Organization", "name": "ЭкоСознание"}
        ld["articleSection"] = info.get("section_title", "")

    crumbs = [{"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"}]
    if info.get("parent"):
        crumbs.append({"@type": "ListItem", "position": 2,
                       "name": info["parent_title"],
                       "item": "%s/%s" % (SITE, info["parent"])})
    if fname != "index.html":
        crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1,
                       "name": title, "item": url})
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList",
                  "itemListElement": crumbs}

    noindex = ('  <meta name="robots" content="noindex, follow">\n'
               if info.get("noindex") else "")

    return """<!-- {mark}:head -->
{noindex}  <link rel="canonical" href="{url}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="ЭкоСознание">
  <meta property="og:image" content="{site}/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="ЭкоСознание — экология как способ смотреть на реальность">
  <meta name="twitter:image" content="{site}/assets/og-image.png">
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

    # 2. Заголовок и описание
    if info.get("title_fix"):
        s = re.sub(r"<title>.*?</title>",
                   "<title>%s</title>" % esc(info["title_full"]), s, flags=re.S)
        log.append("title")
    if "Двенадцать разделов" in s:
        s = s.replace("Двенадцать разделов", "Семнадцать разделов")
        log.append("desc-count")

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
    s = s.replace("</head>", build_head(fname, info) + "</head>", 1)

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
