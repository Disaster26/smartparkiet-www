# -*- coding: utf-8 -*-
"""Buduje zamow-online.html z wycena.html (Artur 27.10: ZAMÓW USŁUGĘ SMART ONLINE™, formularz "Koszyk SMART").

zamow-online.html = ten sam arkusz i kalkulator co wycena.html (zadnej zdublowanej logiki), ale:
- window.SP_ZAMOWIENIE=1 wlacza w wycena.html: mniej pol, 1-3 preferowane terminy, przycisk WYŚLIJ DO POTWIERDZENIA,
  status "Oczekuje na potwierdzenie", temat maila "... - ZAMÓWIENIE ONLINE - Nowa wycena SMARTPARKIET",
- lewa kolumna: opis programu i 5 krokow zamiast opisu kalkulatora,
- wlasny tytul, opis i adres kanoniczny.

URUCHAMIAC PO KAZDEJ ZMIANIE wycena.html:  python _buduj_zamow.py
(build.py w SMARTPARKIET_wdrozenie wywoluje go sam przed budowa paczki).
"""
import os, re

TU = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(TU, 'wycena.html'), encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in s else '\n'

def zamien(stare, nowe, n=1):
    global s
    if s.count(stare) < 1:
        raise SystemExit('Nie znaleziono: ' + stare[:80])
    s = s.replace(stare, nowe, n)

TYT = 'Zamów usługę SMART online - cyklinowanie parkietu Warszawa | SMARTPARKIET'
OPIS = 'ZAMÓW USŁUGĘ SMART ONLINE™: podaj metraż i zdjęcia, zobacz cenę z kalkulatora, wybierz preferowany termin i wyślij do potwierdzenia. Centrala SMARTPARKIET potwierdza termin SMS-em lub e-mailem.'
s = re.sub(r'<title>.*?</title>', '<title>' + TYT + '</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + OPIS + '">', s, count=1)
s = s.replace('smartparkiet-www/wycena.html"', 'smartparkiet-www/zamow-online.html"').replace('smartparkiet.com.pl/wycena.html"', 'smartparkiet.com.pl/zamow-online.html"')
s = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*"', r'\1Zamów usługę SMART online | SMARTPARKIET"', s)
s = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*"', r'\1' + OPIS + '"', s)
s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*"', r'\1ZAMÓW USŁUGĘ SMART ONLINE"', s)
s = s.replace('/og/wycena.jpg?v=2', '/img/og-smartparkiet-artur.jpg?v=2')
s = re.sub(r'<script type="application/ld\+json" id="ld-okruszki">.*?</script>\s*', '', s, flags=re.S)

# tryb zamowienia - zanim wystartuja skrypty strony
m = re.search(r'<meta name="viewport"[^>]*>', s)
s = s[:m.end()] + NL + '<script>window.SP_ZAMOWIENIE=1;</script>' + s[m.end():]

# menu: aktywna nowa zakladka
zamien('<a href="wycena.html" class="akt">Kalkulator online</a>', '<a href="wycena.html">Kalkulator online</a>')
zamien('<a href="zamow-online.html">Zamów online</a>', '<a href="zamow-online.html" class="akt">Zamów online</a>')

# lewa kolumna: opis programu + 5 krokow
LEWA = '''    <div class="sticky zam-gora">
      <h2>ZAMÓW USŁUGĘ CYKLINOWANIE SMART ONLINE&trade;</h2>
      <p class="lead se-lead">Wycena i zamówienie bez wychodzenia z domu.</p>
      <ol class="zam-kroki">
        <li><b>Podaj dane</b> - adres, metraż i zdjęcia.</li>
        <li><b>Poznaj cenę</b> - kalkulacja wstępna, ostateczną kwotę zatwierdza centrala.</li>
        <li><b>Wybierz termin</b> - wskaż dogodne dni.</li>
        <li><b>Złóż zamówienie</b> - jednym kliknięciem.</li>
        <li><b>Otrzymaj potwierdzenie</b> - do 2 godzin roboczych.</li>
      </ol>
      <p class="lead zam-uwaga">Termin staje się wiążący dopiero po potwierdzeniu przez centralę SMARTPARKIET&trade;.</p>
    </div>
    <div class="ai">
      <p class="koszyk-tyt">Koszyk SMART</p>'''
s = re.sub(r'    <div class="sticky">.*?</div>\s*<div class="ai">', lambda m: LEWA.replace('\n', NL), s, count=1, flags=re.S)

CSS = '''<style id="zamow-strona">/* zamow-online.html: kroki i tytul koszyka */
html body .zam-kroki{list-style:none;counter-reset:zk;margin:14px 0 0;padding:0;display:grid;gap:7px}
html body .zam-kroki li{counter-increment:zk;position:relative;padding:1px 0 1px 36px;min-height:26px;font-size:.92rem;line-height:1.35;color:#fff}
html body .zam-kroki li::before{content:counter(zk);position:absolute;left:0;top:0;width:26px;height:26px;font-size:.85rem!important;border-radius:50%;background:#fff;color:#E8580E;font-weight:900;display:grid;place-items:center;font-size:1rem}
html body .zam-kroki li b{color:#fff;font-weight:800}
html body .zam-uwaga{margin-top:12px!important;line-height:1.4!important;font-size:.92rem!important;font-style:italic;color:#fff!important}
html body .koszyk-tyt{margin:0 0 10px;font-weight:900;font-size:1.35rem;letter-spacing:.04em;text-transform:uppercase;color:#14110E}
html body .koszyk-tyt::before{content:"";display:inline-block;width:22px;height:22px;margin:0 8px -3px 0;background:no-repeat center/contain url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23F8580E' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 4h2.5l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.3a1.5 1.5 0 0 0 1.5-1.1L21 8H7'/%3E%3Ccircle cx='10' cy='19.5' r='1.4'/%3E%3Ccircle cx='17' cy='19.5' r='1.4'/%3E%3C/svg%3E")}
@media(max-width:700px){
  html body #wycena{padding-top:22px!important}
  html body .zam-gora h2{font-size:1.45rem!important;line-height:1.15!important;margin:0!important}
  html body .zam-gora .se-lead{margin-top:8px!important;font-size:1rem!important}
  html body .zam-gora .zam-uwaga{font-size:.85rem!important}
  html body #wycena .split{gap:18px!important}
}
</style>'''
s = s.rstrip() + NL + CSS.replace('\n', NL) + NL

open(os.path.join(TU, 'zamow-online.html'), 'w', encoding='utf-8', newline='').write(s)
print('zamow-online.html gotowy,', len(s), 'znakow')
