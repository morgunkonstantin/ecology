#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — значки разделов (α, ψ, шестерёнка, листик, колонны, $, перевёрнутая книга, крест).

Заменяет внутренности SVG-значков восьми разделов в источниках навигации
(build/nav.html, build/footer.html), на главной, в hero-знаках страниц разделов
и в библиотеке значков. Идемпотентен. После запуска прогнать build/make_nav.py,
чтобы разнести шапку и подвал по всем страницам.

Запуск из корня сайта:   python3 build/make_icons.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ICONS = {
    'philosophy': '<circle cx="50" cy="50" r="45"/><path d="M 72 35 C 60 35, 54 49, 46 59 C 40 66, 29 67, 27 57 C 25 47, 35 38, 46 40 C 56 42, 62 56, 72 66" stroke-linecap="round" stroke-linejoin="round"/>',
    'psychology': '<circle cx="50" cy="50" r="45"/><line x1="50" y1="27" x2="50" y2="74" stroke-linecap="round"/><path d="M 31 33 C 31 55, 39 62, 50 62 C 61 62, 69 55, 69 33" stroke-linecap="round"/>',
    'technologies': '<circle cx="50" cy="50" r="45"/><path d="M 73.9 42.6 L 82.3 43.4 L 82.3 56.6 L 73.9 57.4 L 72.1 61.7 L 77.5 68.2 L 68.2 77.5 L 61.7 72.1 L 57.4 73.9 L 56.6 82.3 L 43.4 82.3 L 42.6 73.9 L 38.3 72.1 L 31.8 77.5 L 22.5 68.2 L 27.9 61.7 L 26.1 57.4 L 17.7 56.6 L 17.7 43.4 L 26.1 42.6 L 27.9 38.3 L 22.5 31.8 L 31.8 22.5 L 38.3 27.9 L 42.6 26.1 L 43.4 17.7 L 56.6 17.7 L 57.4 26.1 L 61.7 27.9 L 68.2 22.5 L 77.5 31.8 L 72.1 38.3 Z" stroke-linejoin="round"/><circle cx="50" cy="50" r="9"/>',
    'food': '<circle cx="50" cy="50" r="45"/><path d="M 50 25 Q 35 35,38 50 Q 42 65,50 70" stroke-linecap="round"/><path d="M 50 25 Q 65 35,62 50 Q 58 65,50 70" stroke-linecap="round"/>',
    'architecture': '<circle cx="50" cy="50" r="45"/><path d="M 28 46 L 50 26 L 72 46" stroke-linecap="round" stroke-linejoin="round"/><line x1="30" y1="51" x2="70" y2="51" stroke-linecap="round"/><line x1="35" y1="56" x2="35" y2="69" stroke-linecap="round"/><line x1="45" y1="56" x2="45" y2="69" stroke-linecap="round"/><line x1="55" y1="56" x2="55" y2="69" stroke-linecap="round"/><line x1="65" y1="56" x2="65" y2="69" stroke-linecap="round"/><line x1="30" y1="74" x2="70" y2="74" stroke-linecap="round"/>',
    'economy': '<circle cx="50" cy="50" r="45"/><line x1="50" y1="25" x2="50" y2="75" stroke-linecap="round"/><path d="M 61 38 C 61 31, 39 30, 39 40 C 39 50, 61 50, 61 60 C 61 70, 39 69, 39 62" stroke-linecap="round"/>',
    'education': '<circle cx="50" cy="50" r="45"/><g transform="translate(0 100) scale(1 -1)"><line x1="50" y1="32" x2="50" y2="72" stroke-linecap="round"/><path d="M 30 38 L 50 32 L 70 38 L 70 68 L 50 62 L 30 68 Z" stroke-linejoin="round"/></g>',
    'health': '<circle cx="50" cy="50" r="45"/><path d="M 42 27 H 58 V 42 H 73 V 58 H 58 V 73 H 42 V 58 H 27 V 42 H 42 Z" stroke-linejoin="round"/>',
}

CONCEPTS = {
    'Философия': 'Альфа — начало, первый вопрос',
    'Психология': 'Пси — психика, душа',
    'Технологии': 'Шестерёнка — механизм, который стоит понимать',
    'Питание': 'Листок — живая еда',
    'Архитектура': 'Колоннада — каркас и опора дома',
    'Экономика': 'Доллар — деньги и обмен',
    'Образование': 'Книга вверх ногами — взгляд с другой стороны',
    'Здоровье': 'Крест — забота о теле',
}
NAMES = {
    'Философия': 'philosophy', 'Психология': 'psychology', 'Технологии': 'technologies',
    'Питание': 'food', 'Архитектура': 'architecture', 'Экономика': 'economy',
    'Образование': 'education', 'Здоровье': 'health',
}

def sub(path, pattern, slug, flags=re.S):
    s = open(path, encoding="utf-8").read()
    new = re.sub(pattern, lambda m: m.group(1) + ICONS[slug] + m.group(3), s, flags=flags)
    if new != s:
        open(path, "w", encoding="utf-8").write(new)
    return new != s

def main():
    n = 0
    for slug in ICONS:
        link = r'(<a href="section-%s\.html" class="(?:g-dd-link|g-ov-link|gf-sec-link)">.*?<svg[^>]*>)(.*?)(</svg>)' % slug
        for p in ("build/nav.html", "build/footer.html"):
            n += sub(p, link, slug)
        card = r'(<a href="section-%s\.html" class="card[^"]*">\s*<div class="card-icon"><svg[^>]*>)(.*?)(</svg>)' % slug
        for p in ("index.html", "ecolife-landing.html"):
            if os.path.exists(p): n += sub(p, card, slug)
        hero = r'(<div class="hero-mark-svg"><svg[^>]*>)(.*?)(</svg>)'
        p = "section-%s.html" % slug
        if os.path.exists(p): n += sub(p, hero, slug)
    # библиотека значков: ячейка находится по названию раздела
    p = "section-icons-library.html"
    s = open(p, encoding="utf-8").read()
    for name, slug in NAMES.items():
        cell = r'(<div class="cell">\s*<svg[^>]*>)((?:(?!</svg>).)*)(</svg>\s*<div class="cell-num">[^<]*</div><div class="cell-name">%s</div>\s*<div class="cell-concept">)[^<]*(</div>)' % name
        s = re.sub(cell, lambda m: m.group(1) + "\n      " + ICONS[slug] + "\n    " + m.group(3) + CONCEPTS[name] + m.group(4), s, flags=re.S)
    open(p, "w", encoding="utf-8").write(s)
    print("значки обновлены (файлов изменено: %d + библиотека)" % n)

if __name__ == "__main__":
    main()
