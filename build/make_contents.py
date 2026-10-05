#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — сборка страницы «Все материалы» (contents.html).

Берёт состав из build/pages.json, шапку и подвал — из about.html,
поэтому навигация всегда совпадает с остальным сайтом.
Запускать ПОСЛЕ добавления новых страниц в pages.json,
а затем прогнать patch_pages.py и make_feeds.py.

Запуск из корня сайта:   python3 build/make_contents.py
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

META = json.load(open("build/pages.json", encoding="utf-8"))

SEC_ORDER = ["philosophy", "psychology", "lifestyle", "technologies", "food", "compost",
             "architecture", "construction", "economy", "education", "community",
             "travel", "health", "science", "humanities", "natural-sciences"]

STYLE = """
<style>
.idx-hero{padding:9rem 4rem 3rem;max-width:1100px;margin:0 auto;}
.idx-tag{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--moss);margin-bottom:1.6rem;}
.idx-hero h1{font-family:'Cormorant Garamond',serif;font-size:clamp(2.6rem,5.5vw,4.4rem);font-weight:300;line-height:1.05;margin-bottom:1.6rem;}
.idx-hero h1 em{font-style:italic;color:var(--moss);}
.idx-lead{font-size:1rem;line-height:1.9;color:var(--ink-light);max-width:620px;}
.idx-body{max-width:1100px;margin:0 auto;padding:2rem 4rem 6rem;}
.idx-group{margin-bottom:4rem;}
.idx-group h2{font-family:'Cormorant Garamond',serif;font-size:1.9rem;font-weight:300;margin-bottom:.4rem;}
.idx-group h2 em{font-style:italic;color:var(--moss);}
.idx-count{font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--sage-text);margin-bottom:1.8rem;}
.idx-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1px;background:rgba(74,124,89,.15);border:1px solid rgba(74,124,89,.15);}
.idx-item{background:var(--paper);padding:1.3rem 1.5rem;text-decoration:none;color:inherit;display:block;transition:background .2s;}
.idx-item:hover{background:var(--warm);}
.idx-name{font-family:'Cormorant Garamond',serif;font-size:1.16rem;line-height:1.3;color:var(--ink);margin-bottom:.45rem;}
.idx-desc{font-size:.8rem;line-height:1.65;color:var(--ink-light);}
@media(max-width:720px){.idx-hero{padding:7rem 1.5rem 2rem;}.idx-body{padding:1rem 1.5rem 4rem;}}
</style>
"""

T = "Все материалы"
D = ("Полный указатель «ЭкоСознания»: семнадцать разделов, эссе, лаборатории "
     "и разборы рубрики «Что не подтвердилось» — все материалы сайта на одной странице.")


def plural(n):
    if n % 10 == 1 and n % 100 != 11:
        return "материал"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return "материала"
    return "материалов"


def item(f):
    m = META[f]
    d = m["description"]
    if len(d) > 150:
        d = d[:147].rsplit(" ", 1)[0] + "…"
    return ('    <a class="idx-item" href="%s">\n      <div class="idx-name">%s</div>\n'
            '      <div class="idx-desc">%s</div>\n    </a>\n' % (f, m["title"], d))


def group(title, em, files):
    if not files:
        return ""
    return ('  <section class="idx-group">\n    <h2>%s <em>%s</em></h2>\n'
            '    <div class="idx-count">%d %s</div>\n'
            '    <div class="idx-list">\n%s    </div>\n  </section>\n'
            % (title, em, len(files), plural(len(files)),
               "".join(item(f) for f in files)))


def build():
    shell = open("about.html", encoding="utf-8").read()
    a = shell.find('<main id="content" tabindex="-1">') + len('<main id="content" tabindex="-1">')
    b = shell.find("</main>")
    pre, post = shell[:a], shell[b:]

    pre = re.sub(r"<!-- ECO:MANAGED:head -->.*?<!-- /ECO:MANAGED:head -->\n?", "", pre, flags=re.S)
    pre = re.sub(r"<title>.*?</title>", "<title>%s — ЭкоСознание</title>" % T, pre, flags=re.S)
    for attr, val in [('name="description"', D), ('property="og:title"', T),
                      ('name="twitter:title"', T), ('property="og:description"', D),
                      ('name="twitter:description"', D)]:
        pre = re.sub(r'<meta %s content="[^"]*"' % attr, '<meta %s content="%s"' % (attr, val), pre)
    pre = pre.replace("</head>", STYLE + "</head>", 1)

    sections = ["section-%s.html" % k for k in SEC_ORDER if "section-%s.html" % k in META]
    essays = sorted((f for f in META if f.startswith("essay-")
                     and not META[f].get("broken") and not META[f].get("rubric")),
                    key=lambda f: META[f]["title"])
    labs = sorted((f for f in META if f.startswith("lab-")),
                  key=lambda f: (re.search(r"№(\d+)", META[f]["title_full"]) or ["", "99"])[1])
    def by_rubric(name):
        return sorted(f for f in META if META[f].get("rubric") == name)

    revisions = ["revisions.html"] + by_rubric("Что не подтвердилось")
    things = by_rubric("Биография вещи")
    numbers = by_rubric("Одно число")
    places = by_rubric("Одно место во времени")
    terms = by_rubric("Понятие")
    pages = [f for f in ["about.html", "glossary.html", "thinkers.html", "map.html"] if f in META]

    content = ('\n<section class="idx-hero">\n  <div class="idx-tag">Указатель</div>\n'
               '  <h1>Все <em>материалы</em></h1>\n'
               '  <p class="idx-lead">Полный список того, что есть на сайте. Если вы ищете '
               'связи между темами, а не перечень, посмотрите <a href="map.html">карту связей</a>.</p>\n'
               '</section>\n\n<div class="idx-body">\n'
               + group("Разделы", "по темам", sections)
               + group("Эссе", "длинные тексты", essays)
               + group("Лаборатории", "диалоги и мысленные эксперименты", labs)
               + group("Биография вещи", "одна вещь до самого начала", things)
               + group("Одно место во времени", "территория как аргумент", places)
               + group("Одно число", "откуда оно взялось и что значит", numbers)
               + group("Понятия", "генеалогия и сильнейшее возражение", terms)
               + group("Что не подтвердилось", "ревизия собственных ошибок", revisions)
               + group("Служебные страницы", "", pages)
               + "</div>\n")

    open("contents.html", "w", encoding="utf-8").write(pre + content + post)
    print("contents.html: разделов %d · эссе %d · лабораторий %d · разборов %d"
          % (len(sections), len(essays), len(labs), len(revisions)))


if __name__ == "__main__":
    build()
