#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — единый источник навигации.

Шапка и подвал хранятся в build/nav.html и build/footer.html.
Скрипт разносит их по всем страницам между метками ECO:MANAGED.
После первого запуска правку навигации достаточно сделать
в одном файле и прогнать скрипт — вместо редактирования 82 страниц.

Запуск из корня сайта:   python3 build/make_nav.py
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MARK = "ECO:MANAGED"


def close_div(s, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        if m.group(0) == "</div>":
            depth -= 1
            if depth == 0:
                return start + m.end()
        else:
            depth += 1
    return -1


def grab(page):
    """Достать шапку (обёртка + оверлей) и подвал с эталонной страницы."""
    s = open(page, encoding="utf-8").read()
    i = s.find('<div class="g-nav-wrap"')
    j = close_div(s, i)
    k = s.find('<div class="g-overlay"')
    e = close_div(s, k)
    nav = s[i:j] + "\n\n" + s[k:e]
    fm = re.search(r"<footer class=\"gf\".*?</footer>", s, re.S)
    return nav, fm.group(0)


def apply(nav, footer):
    n = 0
    for f in sorted(glob.glob("*.html")):
        s = open(f, encoding="utf-8").read()
        i = s.find('<div class="g-nav-wrap"')
        if i < 0:
            continue
        k = s.find('<div class="g-overlay"')
        if k < 0:
            continue
        e = close_div(s, k)
        new = s[:i] + "<!-- %s:nav -->\n" % MARK + nav + "\n<!-- /%s:nav -->" % MARK + s[e:]
        fm = re.search(r"<footer class=\"gf\".*?</footer>", new, re.S)
        if fm:
            new = (new[:fm.start()] + "<!-- %s:footer -->\n" % MARK + footer
                   + "\n<!-- /%s:footer -->" % MARK + new[fm.end():])
        new = re.sub(r"<!-- %s:(nav|footer) -->\s*<!-- %s:\1 -->" % (MARK, MARK), "", new)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            n += 1
    return n


if __name__ == "__main__":
    if not os.path.exists("build/nav.html"):
        nav, footer = grab("index.html")
        open("build/nav.html", "w", encoding="utf-8").write(nav)
        open("build/footer.html", "w", encoding="utf-8").write(footer)
        print("эталон извлечён из index.html: nav %d Б, footer %d Б" % (len(nav), len(footer)))
    nav = open("build/nav.html", encoding="utf-8").read()
    footer = open("build/footer.html", encoding="utf-8").read()
    print("навигация разнесена на %d страниц" % apply(nav, footer))
