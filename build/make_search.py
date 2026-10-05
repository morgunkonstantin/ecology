#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — статический индекс для поиска по сайту.

Собирает assets/search-index.json: по одной записи на материал,
с заголовком, рубрикой, разделом, описанием и сжатым текстом.
Поиск выполняется целиком в браузере, без сервера.

Запуск из корня сайта:   python3 build/make_search.py
"""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
META = json.load(open("build/pages.json", encoding="utf-8"))

STOP = set("и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по "
           "только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли если "
           "уже или ни быть был него до вас нибудь опять уж вам ведь там потом себя ничего ей "
           "может они тут где есть надо ней для мы тебя их чем была сам чтоб без будто чего раз "
           "тоже себе под будет ж тогда кто этот того потому этого какой совсем ним здесь этом "
           "один почти мой тем чтобы нее сейчас были куда зачем всех никогда можно при наконец "
           "два об другой хоть после над больше тот через эти нас про всего них какая много "
           "разве три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой "
           "им более всегда конечно всю между это то же как".split())


def text_of(path):
    s = open(path, encoding="utf-8").read()
    i, j = s.find("<article"), s.rfind("</article>")
    if i < 0:
        i, j = s.find("<main"), s.rfind("</main>")
    body = s[i:j] if j > i else s
    body = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r'<section class="sources">.*?</section>', " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return " ".join(body.split())


def build():
    docs = []
    for f in sorted(glob.glob("*.html")):
        m = META.get(f)
        if not m or m.get("noindex") or f in ("index.html", "contents.html", "map.html"):
            continue
        body = text_of(f)
        words = [w for w in re.findall(r"[а-яёa-z0-9-]{3,}", body.lower()) if w not in STOP]
        docs.append({
            "u": f,
            "t": m.get("title", f),
            "r": m.get("rubric") or ("Лаборатория" if f.startswith("lab-")
                                     else "Раздел" if f.startswith("section-")
                                     else "Эссе" if f.startswith("essay-") else "Страница"),
            "s": m.get("section_title", ""),
            "d": m.get("description", "")[:180],
            "w": " ".join(dict.fromkeys(words))[:2000],
        })
    out = "assets/search-index.json"
    json.dump(docs, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("assets/search-index.json: %d материалов, %.0f КБ"
          % (len(docs), os.path.getsize(out) / 1024))


if __name__ == "__main__":
    build()
