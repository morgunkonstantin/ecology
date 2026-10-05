#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — вынос общего CSS в assets/base.css.

Задача: убрать дублирование, НЕ изменив ни одного вычисленного стиля.

Как это делается безопасно:

  1. CSS каждой страницы разбирается на блоки верхнего уровня
     (правило либо целиком @media{...}), порядок сохраняется.
  2. Кандидаты в общий файл — блоки, встречающиеся не реже, чем
     в MIN_FILES страницах, дословно совпадающие.
  3. Для каждой страницы отдельно проверяется каскад: блок можно
     вынести только если ни один остающийся блок ВЫШЕ него не
     объявляет то же свойство для того же селектора. Иначе после
     переноса выиграет не тот блок, что раньше.
  4. После записи выполняется сверка: для каждой страницы считается,
     какое объявление побеждает для каждой пары «селектор + свойство»,
     до и после. Расхождения выводятся как ошибки.

Порядок подключения в <head>: base.css → встроенные стили страницы →
site.css (слой доступности, должен оставаться последним).

Запуск из корня сайта:   python3 build/extract_css.py
"""

import glob
import os
import re
import collections

MIN_FILES = 40

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def split_blocks(css):
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        m = re.compile(r"\S").search(css, i)
        if not m:
            break
        start = m.start()
        if css.startswith("@", start) and "{" in css[start:]:
            j = css.find("{", start)
            head = css[start:j]
            if re.match(r"@(media|supports|layer)\b", head.strip()):
                depth, k = 0, j
                while k < n:
                    if css[k] == "{":
                        depth += 1
                    elif css[k] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    k += 1
                out.append(css[start:k + 1])
                i = k + 1
                continue
        j = css.find("}", start)
        if j < 0:
            break
        out.append(css[start:j + 1])
        i = j + 1
    return [" ".join(b.split()) for b in out if b.strip()]


def decls(block, media=""):
    """Пары «(медиа, селектор, свойство) -> значение» внутри блока."""
    res = []
    if re.match(r"@(media|supports|layer)\b", block):
        head = block[:block.find("{")].strip()
        inner = block[block.find("{") + 1:block.rfind("}")]
        for b in split_blocks(inner):
            res += decls(b, media + "|" + head)
        return res
    if "{" not in block:
        return res
    sel_part, body = block.split("{", 1)
    body = body.rsplit("}", 1)[0]
    sels = [s.strip() for s in sel_part.split(",") if s.strip()]
    for d in body.split(";"):
        if ":" not in d:
            continue
        prop, val = d.split(":", 1)
        for s in sels:
            res.append(((media, s, prop.strip()), val.strip()))
    return res


def winners(block_list):
    """Кто побеждает для каждой пары «селектор + свойство»."""
    w = {}
    for b in block_list:
        for key, val in decls(b):
            w[key] = val
    return w


def main():
    files = sorted(glob.glob("*.html"))
    per = {}
    for f in files:
        s = open(f, encoding="utf-8").read()
        per[f] = split_blocks("".join(re.findall(r"<style[^>]*>(.*?)</style>", s, re.S)))

    cnt = collections.Counter()
    for bs in per.values():
        for b in set(bs):
            cnt[b] += 1
    candidates = {b for b, c in cnt.items() if c >= MIN_FILES}

    # порядок для base.css — из страницы, где кандидатов больше всего
    ref = max(files, key=lambda f: sum(1 for b in per[f] if b in candidates))
    order = [b for b in per[ref] if b in candidates]
    for b in sorted(candidates, key=lambda x: -cnt[x]):
        if b not in order:
            order.append(b)

    # проверка каскада и выбор выносимых блоков для каждой страницы
    extracted = {}
    for f in files:
        bs = per[f]
        take, keep = [], []
        for idx, b in enumerate(bs):
            if b not in candidates:
                keep.append(b)
                continue
            props = {k for k, _ in decls(b)}
            clash = any(props & {k for k, _ in decls(kb)} for kb in bs[:idx] if kb not in candidates)
            (keep if clash else take).append(b)
        extracted[f] = (take, keep)

    open("assets/base.css", "w", encoding="utf-8").write(
        "/* ЭкоСознание — общий слой стилей.\n"
        "   Собран скриптом build/extract_css.py из блоков, повторявшихся\n"
        "   не менее чем на %d страницах. Подключается ПЕРЕД встроенными\n"
        "   стилями страницы, поэтому страница по-прежнему может\n"
        "   переопределить любое правило. */\n\n" % MIN_FILES
        + "\n".join(order) + "\n")

    saved = 0
    for f in files:
        take, keep = extracted[f]
        if not take:
            continue
        s = open(f, encoding="utf-8").read()
        before = winners(per[f])

        styles = list(re.finditer(r"<style[^>]*>(.*?)</style>", s, re.S))
        first = styles[0]
        # вычищаем вынесенные блоки из всех <style> страницы
        for m in reversed(styles):
            css = m.group(1)
            kept = [b for b in split_blocks(css) if b not in take]
            new = "\n".join(kept)
            s = s[:m.start(1)] + ("\n" + new + "\n" if new.strip() else "") + s[m.end(1):]
        s = re.sub(r"<style[^>]*>\s*</style>\n?", "", s)
        if 'assets/base.css' not in s:
            i = s.find("<style")
            if i < 0:
                i = s.find("</head>")
            s = s[:i] + '<link rel="stylesheet" href="assets/base.css">\n' + s[i:]

        after = list(order) + [b for b in per[f] if b in keep]
        aw = winners(after)
        diff = {k for k in before if before[k] != aw.get(k)}
        if diff:
            print("  !! %s: расхождение в %d правилах — файл не изменён" % (f, len(diff)))
            continue

        saved += sum(len(b) for b in take)
        open(f, "w", encoding="utf-8").write(s)

    print("assets/base.css: %d блоков, %.0f КБ" % (len(order), os.path.getsize("assets/base.css") / 1024))
    print("убрано дублирования: %.0f КБ" % (saved / 1024))


if __name__ == "__main__":
    main()
