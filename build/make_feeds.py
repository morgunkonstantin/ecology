#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — генерация feed.xml, sitemap.xml и robots.txt.

Порядок материалов в RSS берётся из блока «свежее» на главной:
это авторская очерёдность, она надёжнее, чем даты в подписях.
Даты берутся из build/pages.json (поле "date"); там, где их нет,
материал всё равно попадает в фид, но без даты публикации.

Запуск из корня сайта:   python3 build/make_feeds.py
"""

import glob
import json
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime

SITE = "https://morgunkonstantin.github.io/ecology"
TITLE = "ЭкоСознание"
SUBTITLE = "Экология как способ смотреть на реальность"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

META = json.load(open("build/pages.json", encoding="utf-8"))


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def indexable(f):
    return not META[f].get("noindex")


# ── порядок материалов по блоку «свежее» на главной ──────────────────
home = open("index.html", encoding="utf-8").read()
order = []
for m in re.finditer(r'<a href="([a-z0-9-]+\.html)" class="fc', home):
    if m.group(1) not in order:
        order.append(m.group(1))

articles = [f for f in order if f in META and indexable(f)]
# всё остальное, чего в блоке «свежее» не оказалось
for f in sorted(META):
    if META[f].get("kind") == "article" and indexable(f) and f not in articles:
        articles.append(f)


# ── RSS ──────────────────────────────────────────────────────────────
def pubdate(f, i):
    d = META[f].get("date")
    if d:
        y, mo, day = (int(x) for x in d.split("-"))
        return format_datetime(datetime(y, mo, day, 9, 0, tzinfo=timezone.utc))
    return None


now = format_datetime(datetime.now(timezone.utc))
items = []
for i, f in enumerate(articles):
    m = META[f]
    kind = ("Лаборатория" if f.startswith("lab-") else
            "Ревизия" if f.startswith("revision-") else
            "Биография вещи" if f.startswith("thing-") else
            "Одно число" if f.startswith("number-") else "Эссе")
    pd = pubdate(f, i)
    items.append(
        "  <item>\n"
        "    <title>%s</title>\n"
        "    <link>%s/%s</link>\n"
        "    <guid isPermaLink=\"true\">%s/%s</guid>\n"
        "    <description>%s</description>\n"
        "    <category>%s</category>\n"
        "%s"
        "  </item>" % (
            esc(m["title"]), SITE, f, SITE, f, esc(m["description"]), kind,
            "    <pubDate>%s</pubDate>\n" % pd if pd else ""))

rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>%s</title>
  <link>%s/</link>
  <atom:link href="%s/feed.xml" rel="self" type="application/rss+xml"/>
  <description>%s</description>
  <language>ru</language>
  <lastBuildDate>%s</lastBuildDate>
  <image>
    <url>%s/assets/og-image.png</url>
    <title>%s</title>
    <link>%s/</link>
  </image>
%s
</channel>
</rss>
""" % (TITLE, SITE, SITE, SUBTITLE, now, SITE, TITLE, SITE, "\n".join(items))

open("feed.xml", "w", encoding="utf-8").write(rss)


# ── sitemap ──────────────────────────────────────────────────────────
PRIORITY = {"home": "1.0", "section": "0.8", "article": "0.7", "page": "0.5"}
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

urls = []
for f in sorted(META):
    if not indexable(f):
        continue
    loc = "%s/%s" % (SITE, "" if f == "index.html" else f)
    urls.append(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
        % (loc, today,
           "weekly" if META[f]["kind"] in ("home", "section") else "monthly",
           PRIORITY.get(META[f]["kind"], "0.5")))

open("sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(urls) + "\n</urlset>\n")


# ── robots.txt ───────────────────────────────────────────────────────
noindex = sorted(f for f in META if META[f].get("noindex"))
open("robots.txt", "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\n"
    "# Страницы, закрытые от индексации, помечены meta robots=noindex\n"
    "# в самих файлах — Disallow здесь не ставим, иначе робот не увидит\n"
    "# noindex и страница может остаться в выдаче.\n"
    "# ВНИМАНИЕ: для project-сайта на github.io этот файл поисковиками\n"
    "# не читается — robots.txt берётся с корня домена. Он начнёт\n"
    "# работать после подключения собственного домена.\n\n"
    "Sitemap: %s/sitemap.xml\n" % SITE)

open(".nojekyll", "w").write("")

print("feed.xml     — %d материалов (%d с датой)"
      % (len(articles), sum(1 for f in articles if META[f].get("date"))))
print("sitemap.xml  — %d адресов" % len(urls))
print("robots.txt   — закрыто от индексации: %d" % len(noindex))
print(".nojekyll    — создан")
