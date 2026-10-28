# -*- coding: utf-8 -*-
"""Platynowy przycisk ZAMOW ONLINE (#zamFab w #spDok) - proba z 28.10.2026 wieczor (Artur: "platynowy przycisk").

Wyglad srebrny jest JEDNYM blokiem <style id="fab-platyna-2810"> doklejonym na koncu kazdej strony z #zamFab.
Pomaranczowy oryginal (blok zam-fab-2710) zostal nietkniety, wiec:

  python _fab_platyna.py --usun   -> usuwa blok ze wszystkich stron = powrot do pomaranczowego jednym ruchem
  python _fab_platyna.py          -> pokazuje, na ilu stronach blok jest

Po --usun: python _buduj_zamow.py / _buduj_analizator.py nie sa potrzebne (tam przycisku nie ma), potem commit + build.py.
"""
import io, os, re, sys

KAT = os.path.dirname(os.path.abspath(__file__))
WZ = re.compile(r'\r?\n?<style id="fab-platyna-2810">.*?</style>', re.S)

ile = 0
for f in sorted(os.listdir(KAT)):
    if not f.endswith('.html'):
        continue
    p = os.path.join(KAT, f)
    s = io.open(p, encoding='utf-8', newline='').read()
    if 'id="fab-platyna-2810"' not in s:
        continue
    ile += 1
    if '--usun' in sys.argv:
        io.open(p, 'w', encoding='utf-8', newline='').write(WZ.sub('', s))
print(('usuniety z %d stron' if '--usun' in sys.argv else 'blok platynowy na %d stronach') % ile)
