#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — блок «Материалы раздела» на страницах section-*.html.

Раздел материала определяется автоматически по плашке .essay-tag
(«Эссе · Экономика») или по полю section_title в build/pages.json.
Блок помечен ECO:MANAGED, поэтому скрипт можно запускать повторно —
он перезаписывает, а не дублирует.

Запуск из корня сайта:   python3 build/make_section_lists.py
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

META = json.load(open("build/pages.json", encoding="utf-8"))
MARK = "ECO:MANAGED"

# заголовок раздела -> файл страницы раздела
SECTIONS = {
    "Философия": "section-philosophy.html", "Психология": "section-psychology.html",
    "Стиль жизни": "section-lifestyle.html", "Технологии": "section-technologies.html",
    "Питание": "section-food.html", "Компост": "section-compost.html",
    "Архитектура": "section-architecture.html", "Строительство": "section-construction.html",
    "Экономика": "section-economy.html",
    "Образование": "section-education.html", "Сообщество": "section-community.html",
    "Путешествия": "section-travel.html", "Здоровье": "section-health.html",
    "Наука": "section-science.html",
}

STYLE = """
<style>
/* ECO:MANAGED — блок материалов раздела */
.sec-mat{padding:5rem 4rem 6rem;max-width:1100px;margin:0 auto;}
.sec-mat-label{font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--moss);margin-bottom:.8rem;}
.sec-mat h2{font-family:'Cormorant Garamond',serif;font-size:2.1rem;font-weight:300;
  margin-bottom:2rem;}
.sec-mat h2 em{font-style:italic;color:var(--moss);}
.sec-mat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));
  gap:1px;background:rgba(74,124,89,.15);border:1px solid rgba(74,124,89,.15);}
.sec-mat-card{background:var(--paper);padding:1.4rem 1.5rem;text-decoration:none;
  color:inherit;display:block;transition:background .2s;}
.sec-mat-card:hover{background:var(--warm);}
.sec-mat-kind{font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--clay-text);margin-bottom:.6rem;}
.sec-mat-name{font-family:'Cormorant Garamond',serif;font-size:1.18rem;line-height:1.3;
  color:var(--ink);margin-bottom:.5rem;}
.sec-mat-desc{font-size:.79rem;line-height:1.65;color:var(--ink-light);}
@media(max-width:720px){.sec-mat{padding:3rem 1.5rem 4rem;}}
</style>
"""


def section_of(fname):
    """Раздел материала: сперва из pages.json, затем из плашки на странице."""
    m = META.get(fname, {})
    if m.get("section_title") in SECTIONS:
        return m["section_title"]
    s = open(fname, encoding="utf-8").read()
    tag = re.search(r'class="(?:essay-tag|lab-tag|hero-tag)">([^<]+)<', s)
    if tag:
        parts = [p.strip() for p in tag.group(1).split("·")]
        for p in parts:
            if p in SECTIONS:
                return p
    return None


def kind_of(fname):
    r = META.get(fname, {}).get("rubric")
    if r:
        return r
    if fname.startswith("lab-"):
        s = open(fname, encoding="utf-8").read()
        n = re.search(r"Лаборатория\s*№(\d+)", s)
        return "Лаборатория №%s" % n.group(1) if n else "Лаборатория"
    if fname.startswith("revision"):
        return "Ревизия"
    if fname.startswith("thing-"):
        return "Биография вещи"
    if fname.startswith("number-"):
        return "Одно число"
    return "Эссе"


def build():
    buckets = {}
    for f in sorted(glob.glob("essay-*.html") + glob.glob("lab-*.html")
                    + glob.glob("thing-*.html") + glob.glob("number-*.html")
                    + glob.glob("place-*.html")):
        if META.get(f, {}).get("noindex"):
            continue
        sec = section_of(f)
        if sec:
            buckets.setdefault(sec, []).append(f)

    for sec, page in SECTIONS.items():
        if not os.path.exists(page):
            continue
        files = buckets.get(sec, [])
        s = open(page, encoding="utf-8").read()

        # снять предыдущую версию
        s = re.sub(r"\n?<!-- %s:seclist -->.*?<!-- /%s:seclist -->" % (MARK, MARK), "", s, flags=re.S)
        s = re.sub(r"\n?<style>\n/\* %s — блок материалов раздела \*/.*?</style>" % MARK, "", s, flags=re.S)

        if not files:
            open(page, "w", encoding="utf-8").write(s)
            print("  %-32s материалов нет" % page)
            continue

        cards = ""
        for f in files:
            m = META.get(f, {})
            d = m.get("description", "")
            if len(d) > 140:
                d = d[:137].rsplit(" ", 1)[0] + "…"
            cards += ('    <a class="sec-mat-card" href="%s">\n'
                      '      <div class="sec-mat-kind">%s</div>\n'
                      '      <div class="sec-mat-name">%s</div>\n'
                      '      <div class="sec-mat-desc">%s</div>\n    </a>\n'
                      % (f, kind_of(f), m.get("title", f), d))

        block = ('\n<!-- %s:seclist -->\n<section class="sec-mat">\n'
                 '  <div class="sec-mat-label">Материалы раздела</div>\n'
                 '  <h2>Читать <em>по теме</em></h2>\n'
                 '  <div class="sec-mat-grid">\n%s  </div>\n</section>\n'
                 '<!-- /%s:seclist -->' % (MARK, cards, MARK))

        s = s.replace("</head>", STYLE.replace("ECO:MANAGED", MARK) + "</head>", 1)
        s = s.replace("</main>", block + "\n</main>", 1)
        open(page, "w", encoding="utf-8").write(s)
        print("  %-32s %d материалов" % (page, len(files)))


if __name__ == "__main__":
    build()
