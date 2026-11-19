# -*- coding: utf-8 -*-
"""Liczba opinii Google na stronie - JEDNO miejsce do zmiany (aktualizowana recznie).

Zmien OPINIE (suma ze wszystkich wizytowek), potem: python _opinie.py
Artur 04.11: wszedzie JEDNA liczba = suma ze wszystkich wizytowek (bez liczb pojedynczych wizytowek).
Skrypt podmienia liczby we wszystkich plikach .html (poza index-biale.html - zapis 15.10).
"""
import os, re, glob

OPINIE = 272        # 18.11.2026 ~18:05: Google Maps 228 Suflerska + 23 + 15 + 6 (nowa opinia Piotra 14:46); wczesniej 271

TU = os.path.dirname(os.path.abspath(__file__))
WZORY = [
    (r'(z )\d+( opinii Google)', OPINIE),                 # gorny pasek + "srednia z N opinii Google"
    (r'(</span> )\d+( opinii klient)', OPINIE),           # hero
    (r'(Zobacz )\d+( opinii klient)', OPINIE),           # 13.11: aria-label linku w hero (czytniki ekranu)
    (r'(<b>)\d+( opinii</b>)', OPINIE),                   # sekcja opinii
    (r'(przy )\d+( opiniach)', OPINIE),                   # artykul o tradycji
    (r'(<span>)\d+( opinii łącznie)', OPINIE),
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
