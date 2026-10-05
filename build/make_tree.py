#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭкоСознание — древовидная карта всех материалов (tree.html).

Строит два дерева из build/pages.json: по разделам и по рубрикам.
Переключение и раскрытие ветвей — на стороне браузера, данные
встроены в страницу, внешних запросов нет.

Отличие от map.html: та показывает связи между разделами,
эта — состав и иерархию.

Запуск из корня сайта:   python3 build/make_tree.py
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
META = json.load(open("build/pages.json", encoding="utf-8"))

SEC_ORDER = ["Философия", "Психология", "Стиль жизни", "Технологии", "Питание", "Компост",
             "Архитектура", "Строительство", "Экономика", "Образование",
             "Сообщество", "Путешествия", "Здоровье", "Наука"]

RUB_ORDER = ["Эссе", "Лаборатория", "Биография вещи", "Одно число",
             "Одно место во времени", "Понятие", "Что не подтвердилось",
             "Раздел", "Служебное"]

SERVICE = {"about.html", "glossary.html", "map.html", "contents.html", "thinkers.html",
           "search.html", "corrections.html", "method.html", "revisions.html", "tree.html"}


def rubric_of(f):
    m = META[f]
    if m.get("rubric"):
        return m["rubric"]
    if f.startswith("lab-"):
        return "Лаборатория"
    if f.startswith("section-"):
        return "Раздел"
    if f in SERVICE:
        return "Служебное"
    if f.startswith("essay-"):
        return "Эссе"
    return "Служебное"


def build_data():
    items = []
    for f in sorted(META):
        m = META[f]
        if m.get("noindex") or f in ("index.html", "ecolife-landing.html"):
            continue
        items.append({
            "u": f,
            "t": m.get("title", f),
            "d": (m.get("description", "") or "")[:160],
            "s": m.get("section_title", ""),
            "r": rubric_of(f),
            "y": m.get("date", ""),
            "a": bool(m.get("date_approx")),
        })

    by_sec = []
    for s in SEC_ORDER:
        kids = [i for i in items if i["s"] == s and i["r"] != "Раздел"]
        head = next((i for i in items if i["r"] == "Раздел" and i["t"] == s), None)
        if kids or head:
            by_sec.append({"n": s, "u": head["u"] if head else "", "c": kids})
    rest = [i for i in items if not i["s"] and i["r"] != "Раздел"]
    if rest:
        by_sec.append({"n": "Вне разделов", "u": "", "c": rest})

    by_rub = []
    for r in RUB_ORDER:
        kids = [i for i in items if i["r"] == r]
        if kids:
            by_rub.append({"n": r, "u": "", "c": kids})

    return {"sec": by_sec, "rub": by_rub, "total": len(items)}


STYLE = """
<style>
.tr-hero{padding:9rem 4rem 2rem;max-width:1100px;margin:0 auto;}
.tr-tag{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--moss);margin-bottom:1.4rem;}
.tr-hero h1{font-family:'Cormorant Garamond',serif;font-size:clamp(2.4rem,5vw,3.8rem);font-weight:300;line-height:1.05;margin-bottom:1.2rem;}
.tr-hero h1 em{font-style:italic;color:var(--moss);}
.tr-lead{font-size:.95rem;line-height:1.85;color:var(--ink-light);max-width:620px;}
.tr-bar{max-width:1100px;margin:0 auto;padding:1.5rem 4rem 0;display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;}
.tr-btn{font-family:'Jost',sans-serif;font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;
  padding:.6rem 1.1rem;border:1px solid rgba(74,124,89,.35);background:none;color:var(--ink-light);cursor:pointer;}
.tr-btn[aria-pressed="true"]{background:var(--ink);color:var(--cream);border-color:var(--ink);}
.tr-btn:hover{border-color:var(--moss);}
.tr-note{font-size:.72rem;color:var(--sage-text);margin-left:auto;}
.tr-wrap{max-width:1100px;margin:0 auto;padding:1.5rem 4rem 6rem;overflow-x:auto;}
.tr-wrap svg{display:block;}
.tr-link{fill:none;stroke:rgba(74,124,89,.35);}
.tr-grp{font-family:'Cormorant Garamond',serif;font-size:19px;fill:var(--ink);cursor:pointer;}
.tr-grp:hover{fill:var(--moss);}
.tr-cnt{font-family:'Jost',sans-serif;font-size:10px;letter-spacing:1.2px;fill:var(--sage-text);cursor:pointer;}
.tr-leaf{font-family:'Cormorant Garamond',serif;font-size:15px;fill:var(--ink-light);cursor:pointer;}
.tr-leaf:hover{fill:var(--moss);text-decoration:underline;}
.tr-kind{font-family:'Jost',sans-serif;font-size:9px;letter-spacing:1.1px;fill:var(--clay-text);}
.tr-root{font-family:'Cormorant Garamond',serif;font-size:24px;fill:var(--ink);}
@media(max-width:820px){.tr-hero{padding:7rem 1.5rem 1.5rem;}.tr-bar,.tr-wrap{padding-left:1.5rem;padding-right:1.5rem;}}
</style>
"""

SCRIPT = """
<script>
(function(){
  var DATA = __DATA__;
  var mode='sec', open={}, host=document.getElementById('tree');
  var W=1020, XG=120, XL=330, RG=18, RL=22;

  function groups(){ return mode==='sec' ? DATA.sec : DATA.rub; }

  function draw(){
    var gs=groups(), y=60, rows=[], links=[];
    gs.forEach(function(g,gi){
      var key=mode+':'+g.n, isOpen=!!open[key];
      var gy=y;
      rows.push({type:'g',x:XG,y:gy,g:g,key:key,open:isOpen});
      y+=RG+8;
      if(isOpen){
        g.c.forEach(function(it){
          rows.push({type:'l',x:XL,y:y,it:it});
          links.push([XG+6,gy+5,XL-10,y-4]);
          y+=RL;
        });
        y+=10;
      }
      links.push([46,34,XG-8,gy-4]);
    });
    var H=Math.max(y+40,240);
    var s=['<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="Дерево материалов сайта">'];
    s.push('<text x="30" y="40" class="tr-root">ЭкоСознание</text>');
    links.forEach(function(l){
      var mx=(l[0]+l[2])/2;
      s.push('<path class="tr-link" d="M'+l[0]+','+l[1]+' C'+mx+','+l[1]+' '+mx+','+l[3]+' '+l[2]+','+l[3]+'"/>');
    });
    rows.forEach(function(r,i){
      if(r.type==='g'){
        var mark=r.open?'−':'+';
        s.push('<g data-i="'+i+'"><text x="'+r.x+'" y="'+r.y+'" class="tr-grp">'+mark+' '+esc(r.g.n)+'</text>');
        s.push('<text x="300" y="'+r.y+'" text-anchor="end" class="tr-cnt">'+r.g.c.length+'</text></g>');
      } else {
        var t=r.it.t.length>58 ? r.it.t.slice(0,56)+'…' : r.it.t;
        s.push('<g data-i="'+i+'"><title>'+esc(r.it.t)+(r.it.d?' — '+esc(r.it.d):'')+'</title>');
        s.push('<text x="'+r.x+'" y="'+r.y+'" class="tr-leaf">'+esc(t)+'</text>');
        s.push('<text x="1000" y="'+r.y+'" text-anchor="end" class="tr-kind">'+esc(mode==='sec'?r.it.r:(r.it.s||''))+'</text></g>');
      }
    });
    s.push('</svg>');
    host.innerHTML=s.join('');
    host.querySelectorAll('g[data-i]').forEach(function(el){
      var r=rows[+el.getAttribute('data-i')];
      el.addEventListener('click',function(){
        if(r.type==='g'){ open[r.key]=!open[r.key]; draw(); }
        else if(r.it.u){ location.href=r.it.u; }
      });
    });
  }
  function esc(x){return String(x).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}

  function setMode(m){
    mode=m;
    document.getElementById('bs').setAttribute('aria-pressed', m==='sec');
    document.getElementById('br').setAttribute('aria-pressed', m==='rub');
    draw();
  }
  document.getElementById('bs').addEventListener('click',function(){setMode('sec');});
  document.getElementById('br').addEventListener('click',function(){setMode('rub');});
  document.getElementById('ba').addEventListener('click',function(){
    var all=true; groups().forEach(function(g){ if(!open[mode+':'+g.n]) all=false; });
    groups().forEach(function(g){ open[mode+':'+g.n]=!all; });
    draw();
  });
  setMode('sec');
})();
</script>
"""


def build():
    shell = open("about.html", encoding="utf-8").read()
    a = shell.find('<main id="content" tabindex="-1">') + len('<main id="content" tabindex="-1">')
    b = shell.find("</main>")
    pre, post = shell[:a], shell[b:]
    pre = re.sub(r"<!-- ECO:MANAGED:head -->.*?<!-- /ECO:MANAGED:head -->\n?", "", pre, flags=re.S)

    T = "Дерево материалов"
    D = ("Все материалы «ЭкоСознания» одним деревом: по разделам или по рубрикам, "
         "с раскрывающимися ветвями. Дополнение к карте связей — та показывает "
         "отношения, эта показывает состав.")
    pre = re.sub(r"<title>.*?</title>", "<title>%s — ЭкоСознание</title>" % T, pre, flags=re.S)
    for attr, val in [('name="description"', D), ('property="og:title"', T),
                      ('name="twitter:title"', T), ('property="og:description"', D),
                      ('name="twitter:description"', D)]:
        pre = re.sub(r'<meta %s content="[^"]*"' % attr,
                     '<meta %s content="%s"' % (attr, val), pre)
    pre = pre.replace("</head>", STYLE + "</head>", 1)

    data = build_data()
    content = ('\n<section class="tr-hero">\n  <div class="tr-tag">Карта состава</div>\n'
               '  <h1>Дерево <em>материалов</em></h1>\n'
               '  <p class="tr-lead">Всё, что есть на сайте, одним деревом. '
               'Переключается между двумя способами группировки: по разделам — что о чём, '
               'и по рубрикам — что каким способом сказано. Ветви раскрываются нажатием.<br><br>'
               'Если вы ищете связи между темами, а не состав, смотрите '
               '<a href="map.html">карту связей</a>; если нужен плоский список — '
               '<a href="contents.html">указатель</a>.</p>\n</section>\n\n'
               '<div class="tr-bar">\n'
               '  <button class="tr-btn" id="bs" aria-pressed="true">По разделам</button>\n'
               '  <button class="tr-btn" id="br" aria-pressed="false">По рубрикам</button>\n'
               '  <button class="tr-btn" id="ba">Раскрыть всё</button>\n'
               '  <span class="tr-note">%d материалов</span>\n</div>\n\n'
               '<div class="tr-wrap"><div id="tree"></div></div>\n' % data["total"]
               + SCRIPT.replace("__DATA__", json.dumps(data, ensure_ascii=False,
                                                       separators=(",", ":"))))

    open("tree.html", "w", encoding="utf-8").write(pre + content + post)
    META["tree.html"] = {"title": T, "title_full": T + " — ЭкоСознание",
                         "description": D, "kind": "page"}
    json.dump(META, open("build/pages.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("tree.html: %d материалов, %d разделов, %d рубрик, %.0f КБ"
          % (data["total"], len(data["sec"]), len(data["rub"]),
             os.path.getsize("tree.html") / 1024))


if __name__ == "__main__":
    build()
