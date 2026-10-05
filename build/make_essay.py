#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка страницы эссе из файла с содержимым.

    python3 build/make_essay.py <имя-файла.html> <файл-с-body> "Заголовок" "Описание" "Раздел"

Берёт шапку и подвал у essay-commons.html (там полный набор стилей эссе),
подставляет своё содержимое, прописывает заголовки и регистрирует страницу
в build/pages.json. Дальше нужно прогнать patch_pages.py и make_feeds.py.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TEMPLATE = "essay-commons.html"

# Стили, общие для новых текстов: блок источников и ссылки на термины глоссария.
EXTRA_STYLE = """
<style>
/* ── Источники: единый блок для всех эссе и лабораторий ── */
.sources{margin:5rem 0 0;padding-top:2.5rem;border-top:1px solid rgba(74,124,89,.2);}
.src-title{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;margin-bottom:1.6rem;}
.src-title small{display:block;font-family:'Jost',sans-serif;font-size:.65rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--clay-text);font-weight:400;margin-bottom:.6rem;}
.src-list{list-style:none;counter-reset:src;padding:0;margin:0;}
.src-list li{position:relative;padding-left:2.4rem;margin-bottom:1.1rem;font-size:.86rem;
  line-height:1.7;color:var(--ink-light);}
.src-list li::before{counter-increment:src;content:counter(src,decimal-leading-zero);
  position:absolute;left:0;top:.15rem;font-family:'Jost',sans-serif;font-size:.66rem;
  letter-spacing:.1em;color:var(--sage-text);}
.src-a{color:var(--ink);}
/* ── Ссылка на термин глоссария ── */
a.term{color:inherit;text-decoration:none;border-bottom:1px dotted var(--fern-text);}
a.term:hover{border-bottom-style:solid;color:var(--moss);}
/* ── Вопросы-врезка ── */
.quiz{background:var(--warm);padding:2.2rem 2.4rem;margin:2.5rem 0;border-left:3px solid var(--moss);}
.quiz ol{margin:0;padding-left:1.4rem;}
.quiz li{font-family:'Cormorant Garamond',serif;font-size:1.1rem;line-height:1.6;
  color:var(--ink);margin-bottom:.9rem;}
.quiz li:last-child{margin-bottom:0;}
</style>
"""


def build(fname, bodyfile, title, desc, section, date="2026-07-26", reg=True):
    src = open(TEMPLATE, encoding="utf-8").read()
    i = src.find("<main")
    j = src.find("</main>") + 7
    head, tail = src[:i], src[j:]

    head = re.sub(r"<!-- ECO:MANAGED:head -->.*?<!-- /ECO:MANAGED:head -->\n?",
                  "", head, flags=re.S)
    head = re.sub(r"\n?<!-- ECO:MANAGED:js -->.*?<!-- /ECO:MANAGED:js -->",
                  "", head, flags=re.S)

    def meta(pattern, value):
        nonlocal head
        head = re.sub(pattern % r'[^"]*', pattern % value.replace("\\", ""), head)

    head = re.sub(r"<title>.*?</title>",
                  "<title>%s — ЭкоСознание</title>" % title, head, flags=re.S)
    for p in [r'<meta name="description" content="%s"',
              r'<meta property="og:description" content="%s"',
              r'<meta name="twitter:description" content="%s"']:
        meta(p, desc)
    for p in [r'<meta property="og:title" content="%s"',
              r'<meta name="twitter:title" content="%s"']:
        meta(p, title)

    if "a.term{" not in head:
        head = head.replace("</head>", EXTRA_STYLE + "</head>", 1)

    body = open(bodyfile, encoding="utf-8").read()
    open(fname, "w", encoding="utf-8").write(head + body + tail)

    if reg:
        p = json.load(open("build/pages.json", encoding="utf-8"))
        e = p.get(fname, {})
        for k in ("noindex", "broken", "title_fix"):
            e.pop(k, None)
        e.update({"title": title, "title_full": title + " — ЭкоСознание",
                  "description": desc, "kind": "article",
                  "date": date, "section_title": section})
        p[fname] = e
        json.dump(p, open("build/pages.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    words = len(re.sub(r"<[^>]+>", " ", body).split())
    print("  %-34s %5d слов" % (fname, words))
    return words


if __name__ == "__main__":
    build(*sys.argv[1:6])
