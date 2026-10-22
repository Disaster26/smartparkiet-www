# -*- coding: utf-8 -*-
"""Liczba opinii Google na stronie - JEDNO miejsce do zmiany (aktualizowana recznie).

Zmien OPINIE (suma ze wszystkich wizytowek) i ewentualnie SUFLERSKA (liczba pokazana
przy oddziale Rembertow na oddzialy.html), potem: python _opinie.py
Skrypt podmienia liczby we wszystkich plikach .html (poza index-biale.html - zapis 15.10).
"""
import os, re, glob

OPINIE = 252        # 22.10.2026: Suflerska 216 + Belwederska 23 + Grojecka 12 + Turmoncka 1
SUFLERSKA = 216     # oddzialy.html, karta Rembertow

TU = os.path.dirname(os.path.abspath(__file__))
WZORY = [
    (r'(z )\d+( opinii Google)', OPINIE),                 # gorny pasek + "srednia z N opinii Google"
    (r'(</span> )\d+( opinii klient)', OPINIE),           # hero
    (r'(<b>)\d+( opinii</b>)', OPINIE),                   # sekcja opinii
    (r'(przy )\d+( opiniach)', OPINIE),                   # artykul o tradycji
    (r'(<span>)\d+( opinii łącznie)', OPINIE),
    (r'(biuro\. )\d+( opinii Google\.)', SUFLERSKA),      # oddzialy.html
]
zm = 0
for p in sorted(glob.glob(os.path.join(TU, '*.html'))):
    if os.path.basename(p) == 'index-biale.html':
        continue
    s = open(p, encoding='utf-8', newline='').read()
    t = s
    for w, n in WZORY:
        t = re.sub(w, lambda m: m.group(1) + str(n) + m.group(2), t)
    if t != s:
        open(p, 'w', encoding='utf-8', newline='').write(t)
        zm += 1
print('pliki zmienione:', zm, '| opinii:', OPINIE)
