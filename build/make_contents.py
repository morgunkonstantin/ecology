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
.idx-group h2 a.idx-sec-link{color:var(--ink);text-decoration:none;}
.idx-group h2 a.idx-sec-link:hover{color:var(--moss);}
.idx-sub{margin-top:1.9rem;margin-left:1.4rem;padding-left:1.5rem;border-left:2px solid rgba(74,124,89,.22);}
.idx-sub h3{font-family:'Cormorant Garamond',serif;font-size:1.32rem;font-weight:400;margin-bottom:1rem;color:var(--ink);}
.idx-sub h3 a{color:inherit;text-decoration:none;}.idx-sub h3 a:hover{color:var(--moss);}
.idx-sub h3 .idx-arrow{color:var(--sage);margin-right:.4rem;}
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

    from collections import defaultdict
    by_section = defaultdict(list)
    for fn, m in META.items():
        if fn.startswith("section-") or fn == "index.html" or m.get("noindex"):
            continue
        st = m.get("section_title")
        if st:
            by_section[st].append(fn)
    for st in by_section:
        by_section[st].sort(key=lambda fn: META[fn]["title"])
    for sh in ("section-humanities.html", "section-natural-sciences.html"):
        if sh in META:
            by_section.setdefault("Наука", [])
            if sh not in by_section["Наука"]:
                by_section["Наука"].insert(0, sh)

    HIER = [
        ("Философия", "section-philosophy.html", []),
        ("Психология", "section-psychology.html", []),
        ("Стиль жизни", "section-lifestyle.html", [("Компост", "section-compost.html")]),
        ("Технологии", "section-technologies.html", []),
        ("Питание", "section-food.html", []),
        ("Архитектура", "section-architecture.html", [("Строительство", "section-construction.html")]),
        ("Экономика", "section-economy.html", []),
        ("Образование", "section-education.html", []),
        ("Сообщество", "section-community.html", []),
        ("Путешествия", "section-travel.html", []),
        ("Здоровье", "section-health.html", []),
        ("Наука", "section-science.html", []),
    ]

    def sub_block(title, hub, files):
        if not files:
            return ""
        head = ('    <div class="idx-sub">\n      <h3><span class="idx-arrow">\u21b3</span>'
                '<a href="%s">%s</a></h3>\n      <div class="idx-list">\n%s      </div>\n    </div>\n'
                % (hub, title, "".join(item(fn) for fn in files)))
        return head

    def sec_group(title, hub, files, subs):
        n = len(files) + sum(len(by_section.get(st, [])) for st, _ in subs)
        body = ('  <section class="idx-group">\n'
                '    <h2><a class="idx-sec-link" href="%s">%s</a> <em>раздел</em></h2>\n'
                '    <div class="idx-count">%d %s</div>\n'
                '    <div class="idx-list">\n%s    </div>\n'
                % (hub, title, n, plural(n), "".join(item(fn) for fn in files)))
        for st, shub in subs:
            body += sub_block(st, shub, by_section.get(st, []))
        return body + "  </section>\n"

    def by_rubric(name):
        return sorted(fn for fn in META if META[fn].get("rubric") == name)
    revisions = ["revisions.html"] + sorted(by_section.get("Ревизия", []))
    pages = [fn for fn in ["about.html", "method.html", "glossary.html", "thinkers.html",
                           "map.html", "tree.html", "paths.html", "search.html",
                           "corrections.html"] if fn in META]

    hier_html = "".join(sec_group(t, hub, by_section.get(t, []), subs) for t, hub, subs in HIER)

    content = ('\n<section class="idx-hero">\n  <div class="idx-tag">Указатель</div>\n'
               '  <h1>Все <em>материалы</em></h1>\n'
               '  <p class="idx-lead">Полный состав сайта по разделам, в той же иерархии, '
               'что и хлебные крошки: подразделы вложены в свои разделы. Если нужна '
               'сворачиваемая карта — <a href="tree.html">дерево материалов</a>; если связи '
               'между темами — <a href="map.html">карта связей</a>.</p>\n'
               '</section>\n\n<div class="idx-body">\n'
               + hier_html
               + group("Что не подтвердилось", "ревизия собственных ошибок", revisions)
               + group("Служебные страницы", "", pages)
               + "</div>\n")

    open("contents.html", "w", encoding="utf-8").write(pre + content + post)
    print("contents.html: иерархия по разделам · %d разделов · %d материалов · %d ревизий"
          % (len(HIER), sum(len(v) for v in by_section.values()), len(revisions)))


if __name__ == "__main__":
    build()
