#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — автолинковка терминов глоссария.

Находит в тексте материалов первое упоминание понятия и превращает его
в ссылку на соответствующую карточку глоссария. Работает осторожно:

  • только ПЕРВОЕ вхождение на страницу;
  • только если на странице ещё нет ссылки на этот якорь;
  • не трогает заголовки, подписи, блок источников, уже существующие
    ссылки, содержимое <style>, <script> и значения атрибутов;
  • формы слов задаются вручную в таблице ALIASES — автоматическая
    морфология здесь опаснее, чем полезна.

Скрипт идемпотентный: повторный запуск ничего не добавит.

Запуск из корня сайта:   python3 build/make_termlinks.py
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SLUGS = json.load(open("build/glossary-slugs.json", encoding="utf-8"))

# slug -> формы, которые считаем упоминанием понятия.
# Порядок важен: длинные формы идут первыми.
ALIASES = {
    "konvivialnost": ["конвивиальность", "конвивиальности", "конвивиальностью"],
    "radikalnaya-monopoliya": ["радикальная монополия", "радикальной монополии",
                               "радикальную монополию"],
    "giperobekt": ["гиперобъекта", "гиперобъектом", "гиперобъекты", "гиперобъект"],
    "planetarnye-granicy": ["планетарных границ", "планетарные границы",
                            "планетарная граница", "планетарной границы"],
    "degrowth": ["degrowth"],
    "commons": ["commons"],
    "solastalgiya": ["соластальгию", "соластальгии", "соластальгия"],
    "topofiliya": ["топофилию", "топофилии", "топофилия"],
    "biofiliya": ["биофилию", "биофилии", "биофилия"],
    "biomimikriya": ["биомимикрию", "биомимикрии", "биомимикрия"],
    "voploschennaya-energiya": ["воплощённая энергия", "воплощённой энергии",
                                "воплощённую энергию"],
    "flaygskam": ["флайгскам"],
    "slow-food": ["slow food"],
    "aleteyya": ["алетейя", "алетейи"],
    "pfas": ["pfas"],
}

# страницы, которые не трогаем
SKIP = {"glossary.html", "map.html", "contents.html", "index.html",
        "thinkers.html", "ecolife-landing.html", "section-icons-library.html"}


def protected_spans(html):
    """Участки, внутри которых заменять нельзя."""
    spans = []
    patterns = [
        r"<style[^>]*>.*?</style>", r"<script[^>]*>.*?</script>",
        r"<a\b[^>]*>.*?</a>", r"<h[1-6][^>]*>.*?</h[1-6]>",
        r'<section class="sources">.*?</section>',
        r'<div class="essay-meta">.*?</div>\s*</section>',
        r"<!--.*?-->", r"<[^>]+>",
    ]
    for p in patterns:
        for m in re.finditer(p, html, re.S | re.I):
            spans.append((m.start(), m.end()))
    return spans


def inside(pos, spans):
    return any(a <= pos < b for a, b in spans)


def process(fname):
    html = open(fname, encoding="utf-8").read()
    body_start = html.find("<article")
    if body_start < 0:
        body_start = html.find("<main")
    if body_start < 0:
        return 0

    added = 0
    for slug, forms in ALIASES.items():
        if slug not in SLUGS.values():
            continue
        if "glossary.html#%s" % slug in html:
            continue  # ссылка уже есть — не дублируем

        spans = protected_spans(html)
        best = None
        for form in forms:
            for m in re.finditer(r"(?<![\w-])(%s)(?![\w-])" % re.escape(form),
                                 html[body_start:], re.I):
                pos = body_start + m.start()
                if inside(pos, spans):
                    continue
                if best is None or pos < best[0]:
                    best = (pos, body_start + m.end(), m.group(1))
                break
        if best:
            s, e, text = best
            html = (html[:s] + '<a class="term" href="glossary.html#%s">%s</a>' % (slug, text)
                    + html[e:])
            added += 1

    if added:
        open(fname, "w", encoding="utf-8").write(html)
    return added


if __name__ == "__main__":
    total = 0
    for f in sorted(glob.glob("*.html")):
        if f in SKIP:
            continue
        n = process(f)
        if n:
            print("  %-32s +%d" % (f, n))
            total += n
    print("\nдобавлено ссылок на глоссарий: %d" % total)
