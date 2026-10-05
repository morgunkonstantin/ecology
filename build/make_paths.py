#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — тропы чтения (paths.html).

Кураторские маршруты по 5–7 материалов. Заголовки, рубрики и время
чтения подтягиваются из реестра и пересчитываются при сборке;
переходы между материалами написаны вручную и живут здесь же —
в этом весь смысл формата: не список, а объяснение, почему дальше
читать именно это.

Запуск из корня сайта:   python3 build/make_paths.py
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
META = json.load(open("build/pages.json", encoding="utf-8"))

PATHS = [
    {
        "id": "nachalo", "label": "Тропа 01",
        "title": "С чего начать",
        "premise": "Если вы здесь впервые и не знаете, за что взяться",
        "intro": "Шесть материалов, дающих представление о том, чем этот сайт занимается "
                 "и по каким правилам говорит. Порядок не по важности, а по нарастанию: "
                 "от общего утверждения к способу его проверять.",
        "steps": [
            ("essay-truth-and-climate.html",
             "Начать логично с текста, который задаёт всё остальное: почему главный "
             "вопрос экологии — это вопрос об истине, а не о том, кто больше беспокоится."),
            ("thing-battery.html",
             "Теперь то же самое, но на предмете, который лежит у вас в ящике. Самый "
             "дешёвый способ понять метод сайта — посмотреть, как он применяется к вещи "
             "весом двадцать три грамма."),
            ("essay-doughnut.html",
             "Дальше нужен масштаб. Здесь появляется рамка, в которой держится "
             "большая часть остальных разговоров, — и сразу же возражения против неё."),
            ("revisions.html",
             "Прежде чем читать дальше, стоит узнать, что на этом сайте есть рубрика, "
             "разбирающая ошибки собственной стороны. Без неё всё предыдущее было бы "
             "проповедью."),
            ("essay-place-based.html",
             "Возвращение к личному масштабу: шесть вопросов, на которые почти никто "
             "не отвечает, и честное объяснение, почему одного места всё-таки мало."),
            ("method.html",
             "И напоследок — правила, по которым всё это написано, включая признание "
             "слабого места самого метода."),
        ],
    },
    {
        "id": "instrumenty", "label": "Тропа 02",
        "title": "Инструменты и зависимость",
        "premise": "Как вещь перестаёт служить и начинает требовать",
        "intro": "Сквозная линия Ивана Иллича, растянутая по сайту от философского "
                 "понятия до законов о запасных частях. Пожалуй, самый связный сюжет "
                 "из всех, что здесь есть.",
        "steps": [
            ("term-conviviality.html",
             "Сначала понятие целиком: откуда взялось, против чего сформулировано "
             "и почему у него нет порога — самое серьёзное возражение названо сразу."),
            ("lab-illich-social.html",
             "Теперь то же в разговоре. Иллич встречает разработчика социальной сети, "
             "и радикальная монополия оказывается описанием вполне современной вещи."),
            ("essay-right-to-repair.html",
             "От диалога к юриспруденции: спор о том, кому принадлежит вещь после "
             "покупки, и почему «чинить, а не выбрасывать» — плохое правило."),
            ("thing-battery.html",
             "Мягкая версия той же схемы. Устройство, спроектированное так, чтобы "
             "избавить вас от необходимости думать, заодно лишает и выбора."),
            ("thing-server.html",
             "И крайний случай: вещь, чья невидимость не побочный эффект, а продукт."),
            ("lab-illich-benyus.html",
             "Финал — спор, в котором Илличу возражают всерьёз и он не может ответить. "
             "Выясняется, что монополия возникает не из материала и не из патента."),
        ],
    },
    {
        "id": "mesto", "label": "Тропа 03",
        "title": "Место как учебник",
        "premise": "Что можно узнать, оставаясь на одном участке земли",
        "intro": "Маршрут о территории: сначала как об источнике знания, потом "
                 "как о единственной точке отсчёта, потом как об аргументе. "
                 "Заканчивается тремя местами, где эта мысль проверялась на практике.",
        "steps": [
            ("essay-place-based.html",
             "Гэри Снайдер и шесть вопросов, на которые вы, скорее всего, не ответите. "
             "И возражение Урсулы Хайзе, которое портит всё удовольствие."),
            ("term-shifting-baseline.html",
             "Почему утрата, происходящая медленнее одного поколения, не воспринимается "
             "как утрата. Одна страница Полая 1995 года объясняет больше, чем библиотека."),
            ("essay-zapovednik.html",
             "Отсюда прямо следует идея Кожевникова: участок, изъятый не для людей, "
             "а от людей. Единственный природоохранный институт, не предъявляющий счёта."),
            ("place-curonian.html",
             "Первая проверка. Ландшафт, разрушенный до движущейся пустыни и возвращённый "
             "к лесу за полтора столетия ручной работы. Восстановление работает — "
             "и не заканчивается никогда."),
            ("essay-aral-zone.html",
             "Вторая. Два места, где сравниваются плановая катастрофа и случайный "
             "заповедник, — и вывод, который из каждого по отдельности не следует."),
            ("place-kola.html",
             "Третья, и она достраивает предыдущую: что происходит, когда люди остаются, "
             "а поток вещества останавливают."),
            ("essay-slow-travel.html",
             "И под конец — про то, как выглядит внимание к месту, если вы туда приехали "
             "ненадолго."),
        ],
    },
    {
        "id": "schitat", "label": "Тропа 04",
        "title": "Как считать",
        "premise": "Откуда берутся числа, которыми меряют мир",
        "intro": "Маршрут об измерении. Каждый следующий текст показывает новый способ, "
                 "которым показатель расходится с явлением. Заканчивается тем, что "
                 "измерить нельзя в принципе.",
        "steps": [
            ("essay-doughnut.html",
             "Начало — с прибора, который восемьдесят лет вешают на место компаса. "
             "ВВП честно показывает скорость и ничего не говорит о направлении."),
            ("number-15.html",
             "Дальше — самое цитируемое число климатического разговора и порядок его "
             "появления, обратный привычному: сначала требование, потом обязательство, "
             "потом наука."),
            ("number-third.html",
             "Здесь видно, что бывает, когда число переживает собственного автора: "
             "ООН заменила эту оценку, а она продолжает ходить по презентациям."),
            ("number-embodied.html",
             "Величина, которая переставляет вопросы местами. Чем эффективнее здание, "
             "тем важнее становится, строить ли его вообще."),
            ("essay-carbon-markets.html",
             "Теперь про то, что происходит, когда торгуют величиной, которую нельзя "
             "измерить, — и почему с диоксидом серы получилось, а с углеродом нет."),
            ("essay-greenwashing.html",
             "Следующий шаг той же логики: как только за показатель начинают "
             "вознаграждать, возникает индустрия по производству показателя в обход явления."),
            ("term-hyperobject.html",
             "И предел всего маршрута: сущность, которая целиком не является нигде "
             "и потому не поддаётся ни одному прибору."),
        ],
    },
    {
        "id": "oshibki", "label": "Тропа 05",
        "title": "Где мы ошибались",
        "premise": "Ревизия собственной стороны, без скидок",
        "intro": "Самая неудобная тропа на сайте. Пять разборов подряд, в которых "
                 "разбирается не оппонент, а своя традиция, и завершение, где сайт "
                 "берётся за собственные ошибки.",
        "steps": [
            ("revisions.html",
             "Сначала правила: пять способов оказаться неправым и обязательный "
             "противовес — предупреждения, не сбывшиеся потому, что сработали."),
            ("revision-ehrlich.html",
             "Классический случай неверного прогноза, с самой тяжёлой частью — "
             "тем, во что риторика перенаселения обошлась конкретным людям."),
            ("revision-limits.html",
             "Здесь ошиблись обе стороны спора, причём зеркально: одни приписали книге "
             "предсказание, другие защищали его как пророчество."),
            ("revision-nuclear.html",
             "Самый неудобный разбор. Тревога была верной, ошибка была в сравнении: "
             "альтернативой оказался не отказ от станции, а уголь."),
            ("revision-organic.html",
             "Случай, где ничего не провалилось, но локально верное утверждение "
             "распространили на планету — и Шри-Ланка получила счёт."),
            ("corrections.html",
             "И финал, без которого всё предыдущее не стоило бы ничего: журнал ошибок "
             "самого сайта и перечень того, что здесь пока не проверено."),
        ],
    },
    {
        "id": "nesoglasny", "label": "Тропа 06",
        "title": "Если вы не согласны",
        "premise": "Маршрут для скептического читателя",
        "intro": "Собрано специально для тех, кто считает экологическую повестку "
                 "преувеличенной или идеологизированной. Здесь нет ни одного текста, "
                 "написанного для того, чтобы вас переубедить, — только те, где сайт "
                 "спорит сам с собой и проигрывает.",
        "steps": [
            ("revision-nuclear.html",
             "Начать стоит с прямого признания: движение десятилетиями воевало не с тем "
             "противником, и это стоило вполне исчисляемых жизней."),
            ("lab-degrowth-ecomodern.html",
             "Дальше — спор, в котором обеим сторонам предъявляют их цену, и выясняется, "
             "что по двум решениям из трёх они сходятся за четыре минуты."),
            ("term-hyperobject.html",
             "Здесь модную философскую конструкцию разбирают по существу, включая довод "
             "Мальма о том, что она удобна тем, кому выгодно, чтобы виноватых не нашли."),
            ("essay-place-based.html",
             "Аргумент о привязанности к месту вместе с его тёмной стороной: "
             "локализм легко становится исключающим, а укоренённость — имущественным тестом."),
            ("revision-organic.html",
             "Разбор того, как хорошая практика превращается в завышенное притязание, "
             "написанный без всякой снисходительности к своим."),
            ("method.html",
             "И правила, по которым всё это устроено, — с признанием, что метод "
             "превращается в формулу, а сайт остаётся компиляцией, а не источником."),
        ],
    },
    {
        "id": "russkaya", "label": "Тропа 07",
        "title": "Русская линия",
        "premise": "Традиция, которой обычно нет в экологических списках чтения",
        "intro": "Четверо мыслителей и три места. Ни один из этих сюжетов не является "
                 "местным колоритом: каждый ставит вопрос, который в западной традиции "
                 "либо был поставлен позже, либо не поставлен вовсе.",
        "steps": [
            ("essay-kropotkin.html",
             "Человек, поехавший в Сибирь проверять Дарвина и вернувшийся с результатом, "
             "которого не ожидал. Плюс объяснение, почему география наблюдателя определила теорию."),
            ("essay-vernadsky.html",
             "Дальше — тот, кто превратил «биосферу» из места обитания жизни в утверждение "
             "о геологической силе. И то, почему вторая половина его мысли не подтвердилась."),
            ("essay-aral-zone.html",
             "Проверка этой второй половины, проведённая в той же стране через полвека "
             "после её формулировки. Результат отрицательный."),
            ("essay-zapovednik.html",
             "Идея 1908 года, философски более радикальная, чем всё, что предлагала "
             "природоохрана XX века, — и дважды разгромленная именно за это."),
            ("place-kola.html",
             "Место, где эта идея проверяется наоборот: не изъятие человека, "
             "а остановка потока при сохранении присутствия."),
            ("thinkers.html",
             "И указатель имён, где эта линия видна целиком: Кропоткин, Докучаев, "
             "Вернадский и Кожевников идут в хронологии подряд."),
        ],
    },
]

STYLE = """
<style>
.pt-hero{padding:9rem 4rem 2rem;max-width:1000px;margin:0 auto;}
.pt-tag{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--moss);margin-bottom:1.4rem;}
.pt-hero h1{font-family:'Cormorant Garamond',serif;font-size:clamp(2.4rem,5vw,3.8rem);font-weight:300;line-height:1.05;margin-bottom:1.4rem;}
.pt-hero h1 em{font-style:italic;color:var(--moss);}
.pt-lead{font-size:.98rem;line-height:1.9;color:var(--ink-light);max-width:620px;}
.pt-jump{max-width:1000px;margin:0 auto;padding:1.5rem 4rem 0;display:flex;flex-wrap:wrap;gap:1px;
  background:rgba(74,124,89,.15);border:1px solid rgba(74,124,89,.15);}
.pt-jump{padding:0;margin:2.5rem auto 0;max-width:1000px;}
.pt-jump a{flex:1 1 200px;background:var(--paper);padding:1rem 1.2rem;text-decoration:none;color:inherit;transition:background .2s;}
.pt-jump a:hover{background:var(--warm);}
.pt-jump .j-l{font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--sage-text);margin-bottom:.35rem;}
.pt-jump .j-n{font-family:'Cormorant Garamond',serif;font-size:1.12rem;color:var(--ink);}
.pt-body{max-width:1000px;margin:0 auto;padding:1rem 4rem 6rem;}
.pt-path{margin:5rem 0 0;padding-top:3rem;border-top:1px solid rgba(74,124,89,.22);}
.pt-label{font-size:.64rem;letter-spacing:.2em;text-transform:uppercase;color:var(--clay-text);margin-bottom:.9rem;}
.pt-path h2{font-family:'Cormorant Garamond',serif;font-size:2.3rem;font-weight:300;line-height:1.1;margin-bottom:.5rem;}
.pt-prem{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.25rem;color:var(--moss);margin-bottom:1.4rem;}
.pt-intro{font-size:.92rem;line-height:1.85;color:var(--ink-light);max-width:600px;margin-bottom:1rem;}
.pt-time{font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--sage-text);margin-bottom:2.5rem;}
.pt-step{display:grid;grid-template-columns:46px 1fr;gap:1.4rem;margin-bottom:2rem;}
.pt-num{font-family:'Jost',sans-serif;font-size:.68rem;letter-spacing:.1em;color:var(--sage-text);padding-top:.35rem;
  border-top:1px solid rgba(74,124,89,.3);}
.pt-why{font-size:.88rem;line-height:1.8;color:var(--ink-light);margin-bottom:.7rem;max-width:600px;}
.pt-card{display:block;text-decoration:none;color:inherit;border-left:2px solid rgba(74,124,89,.35);
  padding:.55rem 0 .55rem 1.1rem;transition:border-color .2s;}
.pt-card:hover{border-color:var(--moss);}
.pt-card:hover .pt-name{color:var(--moss);}
.pt-kind{font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:var(--clay-text);margin-bottom:.3rem;}
.pt-name{font-family:'Cormorant Garamond',serif;font-size:1.24rem;line-height:1.3;color:var(--ink);transition:color .2s;}
@media(max-width:820px){.pt-hero{padding:7rem 1.5rem 1.5rem;}.pt-body{padding:1rem 1.5rem 4rem;}
  .pt-step{grid-template-columns:1fr;gap:.5rem;}.pt-num{border-top:none;padding-top:0;}}
</style>
"""


def minutes(f):
    s = open(f, encoding="utf-8").read()
    i, j = s.find("<main"), s.rfind("</main>")
    body = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", s[i:j], flags=re.S)
    return max(3, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 150))


def kind_of(f):
    m = META.get(f, {})
    if m.get("rubric"):
        return m["rubric"]
    if f.startswith("lab-"):
        return "Лаборатория"
    if f.startswith("essay-"):
        return "Эссе"
    return "Служебное"


def build():
    shell = open("about.html", encoding="utf-8").read()
    a = shell.find('<main id="content" tabindex="-1">') + len('<main id="content" tabindex="-1">')
    b = shell.find("</main>")
    pre, post = shell[:a], shell[b:]
    pre = re.sub(r"<!-- ECO:MANAGED:head -->.*?<!-- /ECO:MANAGED:head -->\n?", "", pre, flags=re.S)

    T = "Тропы чтения"
    D = ("Семь кураторских маршрутов по материалам «ЭкоСознания»: с чего начать, "
         "инструменты и зависимость, место как учебник, как считать, где мы ошибались, "
         "если вы не согласны, русская линия.")
    pre = re.sub(r"<title>.*?</title>", "<title>%s — ЭкоСознание</title>" % T, pre, flags=re.S)
    for attr, val in [('name="description"', D), ('property="og:title"', T),
                      ('name="twitter:title"', T), ('property="og:description"', D),
                      ('name="twitter:description"', D)]:
        pre = re.sub(r'<meta %s content="[^"]*"' % attr,
                     '<meta %s content="%s"' % (attr, val), pre)
    pre = pre.replace("</head>", STYLE + "</head>", 1)

    jump = "".join(
        '<a href="#%s"><div class="j-l">%s</div><div class="j-n">%s</div></a>'
        % (p["id"], p["label"], p["title"]) for p in PATHS)

    out = ['\n<section class="pt-hero">\n  <div class="pt-tag">Маршруты</div>\n'
           '  <h1>Тропы <em>чтения</em></h1>\n'
           '  <p class="pt-lead">На сайте больше восьмидесяти материалов, и это уже '
           'слишком много, чтобы просто листать список. Здесь семь маршрутов: в каждом '
           'пять-семь текстов в заданном порядке, и между ними сказано, почему дальше '
           'читать именно это.<br><br>Маршруты пересекаются — некоторые тексты входят '
           'в два и три сразу, и это нормально: один и тот же материал по-разному '
           'читается в разном соседстве.</p>\n'
           '  <nav class="pt-jump" aria-label="Список троп">%s</nav>\n</section>\n\n'
           '<div class="pt-body">\n' % jump]

    for p in PATHS:
        total = sum(minutes(f) for f, _ in p["steps"] if os.path.exists(f))
        out.append('  <section class="pt-path" id="%s">\n' % p["id"])
        out.append('    <div class="pt-label">%s</div>\n' % p["label"])
        out.append('    <h2>%s</h2>\n' % p["title"])
        out.append('    <div class="pt-prem">%s</div>\n' % p["premise"])
        out.append('    <p class="pt-intro">%s</p>\n' % p["intro"])
        out.append('    <div class="pt-time">%d материалов · примерно %d минут</div>\n'
                   % (len(p["steps"]), total))
        for n, (f, why) in enumerate(p["steps"], 1):
            if not os.path.exists(f):
                print("  нет файла:", f)
                continue
            m = META.get(f, {})
            sec = m.get("section_title", "")
            kind = kind_of(f) + (" · " + sec if sec else "")
            out.append('    <div class="pt-step">\n      <div class="pt-num">%02d</div>\n'
                       '      <div>\n        <p class="pt-why">%s</p>\n'
                       '        <a class="pt-card" href="%s">\n'
                       '          <div class="pt-kind">%s · %d мин</div>\n'
                       '          <div class="pt-name">%s</div>\n        </a>\n'
                       '      </div>\n    </div>\n'
                       % (n, why, f, kind, minutes(f), m.get("title", f)))
        out.append('  </section>\n')
    out.append('</div>\n')

    open("paths.html", "w", encoding="utf-8").write(pre + "".join(out) + post)
    META["paths.html"] = {"title": T, "title_full": T + " — ЭкоСознание",
                          "description": D, "kind": "page"}
    json.dump(META, open("build/pages.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("paths.html: %d троп, %d шагов, %.0f КБ"
          % (len(PATHS), sum(len(p["steps"]) for p in PATHS),
             os.path.getsize("paths.html") / 1024))


if __name__ == "__main__":
    build()
