#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — схемы.

Шесть диаграмм собираются как встроенный SVG и вставляются в нужные
страницы между метками ECO:MANAGED:fig. Встроенный SVG выбран вместо
отдельных файлов по трём причинам: он берёт цвета из переменных сайта,
масштабируется без потерь при печати и доступен скринридеру через
<title> и <desc>.

Скрипт идемпотентный.

Запуск из корня сайта:   python3 build/make_figures.py
"""

import glob
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MARK = "ECO:MANAGED:fig"

CSS = """
<style>
/* ECO:MANAGED — схемы */
.fig{margin:3.5rem 0;}
.fig svg{width:100%;height:auto;display:block;}
.fig figcaption{margin-top:1rem;font-size:.78rem;line-height:1.7;color:var(--ink-light);
  padding-left:1rem;border-left:2px solid rgba(74,124,89,.3);}
.fig figcaption b{color:var(--ink);font-weight:400;}
.fig-t{font-family:'Jost',sans-serif;font-size:12px;fill:var(--ink-light);}
.fig-s{font-family:'Jost',sans-serif;font-size:10px;letter-spacing:1.4px;
  text-transform:uppercase;fill:var(--moss);}
.fig-n{font-family:'Cormorant Garamond',serif;font-size:22px;fill:var(--ink);}
.fig-l{stroke:var(--moss);fill:none;}
.fig-d{stroke:rgba(74,124,89,.3);fill:none;stroke-dasharray:3 4;}
</style>
"""


def arc(cx, cy, r0, r1, a0, a1):
    """Кольцевой сектор."""
    ra0, ra1 = math.radians(a0), math.radians(a1)
    x0, y0 = cx + r0 * math.cos(ra0), cy + r0 * math.sin(ra0)
    x1, y1 = cx + r0 * math.cos(ra1), cy + r0 * math.sin(ra1)
    x2, y2 = cx + r1 * math.cos(ra1), cy + r1 * math.sin(ra1)
    x3, y3 = cx + r1 * math.cos(ra0), cy + r1 * math.sin(ra0)
    big = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{x0:.1f},{y0:.1f} A{r0},{r0} 0 {big} 1 {x1:.1f},{y1:.1f} "
            f"L{x2:.1f},{y2:.1f} A{r1},{r1} 0 {big} 0 {x3:.1f},{y3:.1f} Z")


def fig_doughnut():
    cx, cy, ri, ro = 300, 250, 95, 165
    p = [f'<svg viewBox="0 0 600 500" role="img" aria-labelledby="dgt dgd">',
         '<title id="dgt">Схема экономики пончика</title>',
         '<desc id="dgd">Два концентрических кольца: внутреннее — социальный фундамент, '
         'внешнее — экологический потолок. Между ними безопасное и справедливое пространство. '
         'Нехватка показана внутрь, перерасход наружу.</desc>']
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{(ri+ro)/2}" fill="none" '
             f'stroke="rgba(74,124,89,.13)" stroke-width="{ro-ri}"/>')
    # перерасход: четыре сектора наружу
    for a0, a1 in [(-100, -55), (-40, 5), (30, 70), (110, 150)]:
        p.append(f'<path d="{arc(cx,cy,ro,ro+34,a0,a1)}" fill="rgba(122,79,46,.5)"/>')
    # нехватка: три сектора внутрь
    for a0, a1 in [(150, 205), (215, 250), (60, 100)]:
        p.append(f'<path d="{arc(cx,cy,ri-30,ri,a0,a1)}" fill="rgba(148,102,60,.45)"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{ri}" class="fig-l" stroke-width="1.6"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{ro}" class="fig-l" stroke-width="1.6"/>')
    p.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" class="fig-n">безопасное</text>')
    p.append(f'<text x="{cx}" y="{cy+18}" text-anchor="middle" class="fig-n">пространство</text>')
    p.append(f'<text x="{cx}" y="{cy+42}" text-anchor="middle" class="fig-t">здесь экономика и должна работать</text>')
    p.append(f'<text x="{cx}" y="42" text-anchor="middle" class="fig-s">экологический потолок · 9 границ</text>')
    p.append(f'<text x="{cx}" y="62" text-anchor="middle" class="fig-t">перерасход: климат, азот и фосфор, землепользование…</text>')
    p.append(f'<text x="{cx}" y="463" text-anchor="middle" class="fig-s">социальный фундамент · 12 оснований</text>')
    p.append(f'<text x="{cx}" y="483" text-anchor="middle" class="fig-t">нехватка: жильё, доход, политический голос…</text>')
    p.append('</svg>')
    return ("".join(p),
            "Конструкция Кейт Раворт в нашей перерисовке. Существенно, что "
            "<b>обе стрелки — провалы</b>: и наружу, и внутрь. Цель не «расти», "
            "а попасть в полосу и остаться в ней. Девять границ нарисованы "
            "одинаково твёрдыми, хотя доказательная база у них очень разная — "
            "об этом отдельно в тексте.")


def fig_windows():
    p = ['<svg viewBox="0 0 640 400" role="img" aria-labelledby="wnt wnd">',
         '<title id="wnt">Четыре окна городского портрета</title>',
         '<desc id="wnd">Матрица два на два: локальное и глобальное по горизонтали, '
         'социальное и экологическое по вертикали. Четвёртое окно, глобально-экологическое, '
         'внедряется хуже остальных.</desc>']
    cells = [(60, 70, "Локально · социально", "Как живут наши жители", "рассчитано"),
             (330, 70, "Глобально · социально", "На кого мы влияем в мире", "частично"),
             (60, 225, "Локально · экологически", "Что с природой здесь", "рассчитано"),
             (330, 225, "Глобально · экологически", "След наших цепочек поставок", "не финансируется")]
    for x, y, t, s, st in cells:
        fill = "rgba(122,79,46,.09)" if st == "не финансируется" else "var(--paper)"
        p.append(f'<rect x="{x}" y="{y}" width="250" height="130" fill="{fill}" '
                 f'stroke="rgba(74,124,89,.35)"/>')
        p.append(f'<text x="{x+20}" y="{y+32}" class="fig-s">{t}</text>')
        p.append(f'<text x="{x+20}" y="{y+62}" class="fig-n" font-size="17">{s}</text>')
        col = "var(--rust)" if st == "не финансируется" else "var(--moss)"
        p.append(f'<text x="{x+20}" y="{y+96}" class="fig-t" fill="{col}">{st}</text>')
    p.append('<text x="320" y="382" text-anchor="middle" class="fig-t">'
             'Четвёртое окно — единственное, где рамка признаёт нелокальность</text>')
    p.append('</svg>')
    return ("".join(p),
            "Метод амстердамского городского портрета. Первые три окна показывают город; "
            "четвёртое показывает, что <b>города как отдельной вещи не существует</b>. "
            "Оно же единственное, за которое город никто не похвалит, — и потому "
            "внедряется хуже всех.")


def fig_kola():
    p = ['<svg viewBox="0 0 660 340" role="img" aria-labelledby="klt kld">',
         '<title id="klt">Градиент нарушения вокруг комбината</title>',
         '<desc id="kld">По мере удаления от источника выбросов растительный покров '
         'восстанавливается: пустошь, редколесье, повреждённый лес, нормальная тайга.</desc>']
    zones = [(70, 175, "пустошь", "0–8 км"), (175, 285, "редколесье", "8–15"),
             (285, 430, "повреждённый лес", "15–30"), (430, 610, "тайга", "30–40")]
    shades = [".06", ".14", ".26", ".42"]
    for (x0, x1, name, d), sh in zip(zones, shades):
        p.append(f'<rect x="{x0}" y="70" width="{x1-x0}" height="150" '
                 f'fill="rgba(74,124,89,{sh})"/>')
        p.append(f'<text x="{(x0+x1)/2}" y="250" text-anchor="middle" class="fig-t">{name}</text>')
        p.append(f'<text x="{(x0+x1)/2}" y="268" text-anchor="middle" class="fig-t" '
                 f'fill="var(--sage-text)">{d}</text>')
    pts = [(70, 210), (120, 205), (175, 190), (230, 165), (285, 138), (350, 112),
           (430, 95), (520, 84), (610, 80)]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    p.append(f'<path d="{d}" class="fig-l" stroke-width="2"/>')
    p.append('<line x1="70" y1="220" x2="610" y2="220" stroke="rgba(74,124,89,.35)"/>')
    p.append('<line x1="70" y1="70" x2="70" y2="220" stroke="rgba(74,124,89,.35)"/>')
    p.append('<rect x="50" y="222" width="40" height="26" fill="var(--rust)" opacity=".75"/>')
    p.append('<text x="70" y="292" text-anchor="middle" class="fig-t">комбинат</text>')
    p.append('<text x="70" y="52" class="fig-s">растительный покров</text>')
    p.append('<text x="610" y="318" text-anchor="end" class="fig-t">расстояние от трубы →</text>')
    p.append('</svg>')
    return ("".join(p),
            "Схематично, по многолетним работам о градиенте вокруг медно-никелевых "
            "комбинатов Кольского полуострова. Именно эта шкала сделала место "
            "катастрофы <b>одной из самых изученных площадок в мире</b>: длинный ряд "
            "наблюдений вдоль контролируемой нагрузки — то, чего в экологии почти не бывает.")


def fig_biomimicry():
    p = ['<svg viewBox="0 0 640 340" role="img" aria-labelledby="bmt bmd">',
         '<title id="bmt">Три уровня подражания живому</title>',
         '<desc id="bmd">Форма, процесс, экосистема. Публичная известность '
         'сосредоточена на первом уровне, практический потенциал — на втором и третьем.</desc>']
    rows = [(70, "Форма", "скопировать структуру: крючок, ребро, рельеф", 210, 55),
            (170, "Процесс", "воспроизвести способ производства: вырастить, а не выплавить", 80, 190),
            (270, "Экосистема", "отход одного звена — сырьё другого", 45, 235)]
    p.append('<text x="330" y="34" class="fig-s">известность</text>')
    p.append('<text x="500" y="34" class="fig-s">потенциал</text>')
    for y, name, desc, fame, pot in rows:
        p.append(f'<text x="30" y="{y}" class="fig-n" font-size="19">{name}</text>')
        p.append(f'<text x="30" y="{y+22}" class="fig-t">{desc}</text>')
        p.append(f'<rect x="330" y="{y-14}" width="{fame*0.55}" height="14" fill="rgba(122,79,46,.45)"/>')
        p.append(f'<rect x="500" y="{y-14}" width="{pot*0.55}" height="14" fill="rgba(74,124,89,.5)"/>')
    p.append('<text x="320" y="325" text-anchor="middle" class="fig-t">'
             'Несоответствие между этими столбцами и есть источник разочарования</text>')
    p.append('</svg>')
    return ("".join(p),
            "Разделение по Дженин Бенюс. Клюв зимородка и липучка — первый уровень, "
            "и на нём построена вся публичная слава. Мицелиальные материалы и замкнутые "
            "циклы — второй и третий, и <b>на них построено всё, что действительно работает</b>. "
            "Длина столбиков — оценка, а не измерение.")


def fig_embodied():
    p = ['<svg viewBox="0 0 660 380" role="img" aria-labelledby="ebt ebd">',
         '<title id="ebt">Накопленные выбросы: снос против реконструкции</title>',
         '<desc id="ebd">Снос и новое строительство дают крупный выброс сразу и меньший '
         'наклон дальше; реконструкция начинается почти с нуля. Линии пересекаются '
         'через несколько десятилетий.</desc>']
    x0, y0, x1, y1 = 70, 300, 610, 60
    p.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="rgba(74,124,89,.35)"/>')
    p.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="rgba(74,124,89,.35)"/>')
    for i, lab in enumerate(["0", "20", "40", "60 лет"]):
        x = x0 + i * (x1 - x0) / 3
        p.append(f'<text x="{x}" y="{y0+22}" text-anchor="middle" class="fig-t">{lab}</text>')
    # снос: скачок + пологая
    p.append(f'<path d="M{x0},{y0} L{x0},150 L{x1},108" class="fig-l" '
             f'stroke="var(--rust)" stroke-width="2.2"/>')
    # реконструкция: с нуля, круче
    p.append(f'<path d="M{x0},{y0} L{x0},282 L{x1},80" class="fig-l" stroke-width="2.2"/>')
    p.append('<circle cx="516" cy="115" r="5" fill="none" stroke="var(--ink)" stroke-width="1.6"/>')
    p.append('<line x1="516" y1="120" x2="516" y2="300" class="fig-d"/>')
    p.append('<text x="516" y="99" text-anchor="middle" class="fig-t">окупаемость</text>')
    p.append(f'<text x="{x0+14}" y="142" class="fig-t" fill="var(--rust)">снос и новое здание</text>')
    p.append(f'<text x="{x0+14}" y="274" class="fig-t" fill="var(--moss)">реконструкция</text>')
    p.append(f'<text x="{x0}" y="44" class="fig-s">накопленные выбросы</text>')
    p.append('</svg>')
    return ("".join(p),
            "Схема, а не расчёт: точка окупаемости по разным оценкам лежит между двумя "
            "и восемью десятилетиями. Существенно другое: климатическая арифметика "
            "<b>кумулятивна</b> — важна площадь под кривой, а не положение в 2085 году. "
            "Поэтому решение может быть верным к концу века и неверным для ближайших "
            "тридцати лет, которые как раз и решают.")


def fig_baseline():
    p = ['<svg viewBox="0 0 660 340" role="img" aria-labelledby="blt bld">',
         '<title id="blt">Сдвиг базовой линии</title>',
         '<desc id="bld">Реальный запас непрерывно падает, но каждое поколение '
         'принимает за норму то состояние, которое застало в начале, и потому '
         'фиксирует лишь небольшое ухудшение.</desc>']
    x0, x1 = 70, 610
    p.append(f'<line x1="{x0}" y1="290" x2="{x1}" y2="290" stroke="rgba(74,124,89,.35)"/>')
    p.append(f'<path d="M{x0},70 C220,110 380,200 {x1},262" class="fig-l" stroke-width="2.2"/>')
    gens = [(x0, 250, 70, "дед", 105), (250, 420, 128, "отец", 168), (420, 590, 196, "внук", 226)]
    for gx0, gx1, y, name, y2 in gens:
        p.append(f'<line x1="{gx0}" y1="{y}" x2="{gx1}" y2="{y}" class="fig-d"/>')
        if name == "дед":
            p.append(f'<text x="{gx0+6}" y="{y-8}" class="fig-t" fill="var(--sage-text)">'
                     f'«норма», от которой отсчитывает поколение</text>')
        p.append(f'<text x="{(gx0+gx1)/2}" y="312" text-anchor="middle" class="fig-t">{name}</text>')
        p.append(f'<line x1="{gx1-14}" y1="{y}" x2="{gx1-14}" y2="{y2}" '
                 f'stroke="var(--clay-text)" stroke-width="1.4"/>')
        if name == "дед":
            p.append(f'<text x="{gx1-8}" y="{(y+y2)/2+4}" class="fig-t" fill="var(--clay-text)">'
                     f'замеченное за жизнь</text>')
    p.append(f'<text x="{x0}" y="46" class="fig-s">реальный запас</text>')
    p.append('</svg>')
    return ("".join(p),
            "Каждый из троих субъективно честен и фиксирует небольшое ухудшение за свою "
            "жизнь. <b>Суммарное падение в разы не регистрирует никто</b>, потому что "
            "точка отсчёта едет вместе с наблюдателем.")


FIGURES = {
    "essay-doughnut.html": [("<div class=\"sb\">\n    <h2><small>Другая рамка</small>", fig_doughnut)],
    "lab-morton-raworth.html": [("<div class=\"lab-section\">\n    <div class=\"lab-section-label\">Сдвиг третий", fig_windows)],
    "place-kola.html": [("<div class=\"sb\">\n    <h2><small>Соседи</small>", fig_kola)],
    "essay-biomimicry.html": [("<div class=\"sb\">\n    <h2><small>Ревизия</small>", fig_biomimicry)],
    "number-embodied.html": [("<div class=\"sb\">\n    <h2><small>Следствие</small>", fig_embodied)],
    "term-shifting-baseline.html": [("<div class=\"sb\">\n    <h2><small>Защита</small>", fig_baseline)],
}


def main():
    n = 0
    for fname, items in FIGURES.items():
        if not os.path.exists(fname):
            print("  нет файла:", fname)
            continue
        s = open(fname, encoding="utf-8").read()
        s = re.sub(r"\n?<!-- %s -->.*?<!-- /%s -->" % (MARK, MARK), "", s, flags=re.S)
        s = re.sub(r"\n?<style>\n/\* ECO:MANAGED — схемы \*/.*?</style>", "", s, flags=re.S)
        for anchor, fn in items:
            svg, cap = fn()
            block = ('\n<!-- %s -->\n<figure class="fig">%s<figcaption>%s</figcaption></figure>\n'
                     '<!-- /%s -->\n' % (MARK, svg, cap, MARK))
            i = s.find(anchor)
            if i < 0:
                print("  якорь не найден в", fname)
                continue
            s = s[:i] + block + s[i:]
            n += 1
        s = s.replace("</head>", CSS + "</head>", 1)
        open(fname, "w", encoding="utf-8").write(s)
    print("схем вставлено: %d" % n)


if __name__ == "__main__":
    main()
