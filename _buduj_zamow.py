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
OPIS = 'ZAMÓW USŁUGĘ SMART ONLINE™: podaj metraż i zdjęcia, zobacz cenę z kalkulatora, wybierz preferowany termin i wyślij do potwierdzenia. Biuro SMARTPARKIET potwierdza termin SMS-em lub e-mailem.'
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
zamien('<a href="wycena.html" class="akt">KALKULATOR - wyceń samodzielnie</a>', '<a href="wycena.html">KALKULATOR - wyceń samodzielnie</a>')
zamien('<a href="zamow-online.html#koszyk" class="nav-zam">', '<a href="zamow-online.html#koszyk" class="nav-zam akt">')

# lewa kolumna: opis programu + 5 krokow
LEWA = '''    <div class="sticky zam-gora">
      <h2>ZAMÓW USŁUGĘ CYKLINOWANIE SMART ONLINE&trade;</h2>
      <ol class="zam-kroki">
        <li><b>Podaj dane</b> - adres, metraż i zdjęcia.</li>
        <li><b>Poznaj cenę</b> - kalkulacja wstępna, ostateczną kwotę zatwierdza biuro.</li>
        <li><b>Wybierz termin</b> - wskaż dogodne dni.</li>
        <li><b>Złóż zamówienie</b> - jednym kliknięciem.</li>
        <li><b>Otrzymaj potwierdzenie</b> - do 2 godzin roboczych.</li>
      </ol>
      <p class="lead zam-uwaga">Termin staje się wiążący dopiero po potwierdzeniu przez biuro SMARTPARKIET&trade;.</p>
    </div>
    <div class="ai">
      <p class="koszyk-tyt" id="koszyk">Koszyk SMART</p>'''
s = re.sub(r'    <div class="sticky">.*?</div>\s*<div class="ai">', lambda m: LEWA.replace('\n', NL), s, count=1, flags=re.S)

# Artur 27.10 03:48-03:51: tekst o zamowieniach online - pod koszykiem (nad nim zostaja krotkie kroki, zeby koszyk byl wysoko)
TEKST = """<section class="zam-tekst" id="jak-to-dziala">
  <div class="wrap">
    <h2>ZAMÓW CYKLINOWANIE SMART ONLINE&trade; + EKSPRES 48H</h2>
    <p class="zt-start"><b>Renowacja parkietu jeszcze nigdy nie była tak prosta!</b></p>
    <p>Bez telefonów, oględzin i oczekiwania na wycenę.</p>
    <p class="zt-lead">Teraz to my dostosowujemy się do Twojego harmonogramu!</p>
    <p><b>Zamów CYKLINOWANIE SMART&trade; online, poznaj wstępną wycenę i wybierz dogodne terminy.</b></p>
    <p><b>Potrzebujesz szybkiego startu?</b> W koszyku zaznacz tryb ekspres 48h (start w 24-48 h, do 40 m²).</p>
    <p><b>Złóż zamówienie online!</b> W ciągu 2 godzin roboczych potwierdzimy dostępność wybranego terminu i szczegóły realizacji.</p>
    <p class="zt-haslo"><i>Twój parkiet. Twój termin. Twoja wycena.<br>My tylko robimy robotę!</i></p>
    <p><a class="btn btn-amber btn-kosz" href="#koszyk"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h2.5l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.3a1.5 1.5 0 0 0 1.5-1.1L21 8H7"/><circle cx="10" cy="19.5" r="1.4"/><circle cx="17" cy="19.5" r="1.4"/></svg>Przejdź do Koszyka SMART</a></p>
  </div>
</section>
"""
i = s.index('id="wycena">'); j = s.index('</section>', i) + len('</section>')
s = s[:j] + NL + TEKST.replace('\n', NL) + s[j:]

CSS = '''<style id="zamow-strona">/* zamow-online.html: kroki i tytul koszyka */
html body a.btn.btn-kosz,html body a.btn.btn-kosz:visited{display:inline-flex!important;align-items:center;gap:8px;background:#FF6A13!important;color:#fff!important;border-radius:999px!important;font-weight:800!important;text-decoration:none!important} /* Artur 30.10 01:38: bialy napis + koszyk jak "Zamow online" */
html body a.btn.btn-kosz:hover{background:#F25F0C!important;color:#fff!important}
html body a.btn.btn-kosz svg{width:20px;height:20px;flex:0 0 auto}
html body .zam-kroki{list-style:none;counter-reset:zk;margin:14px 0 0;padding:0;display:grid;gap:7px}
html body .zam-kroki li{counter-increment:zk;position:relative;padding:1px 0 1px 36px;min-height:26px;font-size:.92rem;line-height:1.35;color:#fff}
html body .zam-kroki li::before{content:counter(zk);position:absolute;left:0;top:0;width:26px;height:26px;font-size:.85rem!important;border-radius:50%;background:#fff;color:#FF6A13;font-weight:900;display:grid;place-items:center;font-size:1rem}
html body .zam-kroki li b{color:#fff;font-weight:800}
html body .zam-uwaga{margin-top:12px!important;line-height:1.4!important;font-size:.92rem!important;font-style:italic;color:#fff!important}
html body .koszyk-tyt{scroll-margin-top:72px;margin:4px 0 12px;font-weight:900;font-size:1.4rem;line-height:1.15;letter-spacing:.03em;white-space:nowrap;text-transform:uppercase;color:#FF6A13;text-align:center} /* Artur 27.10 03:21: na srodku, pomaranczowy, wiekszy */
html body .koszyk-tyt::before{content:"";display:inline-block;width:22px;height:22px;margin:0 8px -3px 0;background:no-repeat center/contain url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FF6A13' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 4h2.5l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.3a1.5 1.5 0 0 0 1.5-1.1L21 8H7'/%3E%3Ccircle cx='10' cy='19.5' r='1.4'/%3E%3Ccircle cx='17' cy='19.5' r='1.4'/%3E%3C/svg%3E")}
@media(max-width:700px){
  html body #wycena{padding-top:22px!important}
  html body #wycena .zam-gora h2{font-size:1.2rem!important;line-height:1.2!important;margin:0!important} /* Artur 27.10 03:20: mniejsza czcionka */
  html body .zam-gora .se-lead{margin-top:8px!important;font-size:1rem!important}
  html body .zam-gora .zam-uwaga{font-size:.85rem!important}
  html body #wycena .split{gap:18px!important}
}
html body #wycena .zam-gora h2{font-size:clamp(1.2rem,1.9vw,1.6rem)!important;line-height:1.2!important}
html body .zam-tekst{background:#fff;padding:44px 0 52px}
html body .zam-tekst .wrap{max-width:760px}
html body .zam-tekst h2{margin:0 0 12px;font-size:clamp(1.25rem,3vw,1.8rem);line-height:1.2;color:#14110E}
html body .zam-tekst .zt-lead{font-size:1.15rem;font-weight:800;color:#FF6A13;margin:0 0 14px}
html body .zam-tekst p{font-size:1.02rem;line-height:1.6;color:#3A3F45;margin:0 0 12px}
html body .zam-tekst .zt-haslo{margin:18px 0 22px;font:900 1.3rem/1.3 Inter,system-ui,sans-serif;color:#14110E;border-left:4px solid #FF6A13;padding-left:14px}
</style>'''
s = s.rstrip() + NL + CSS.replace('\n', NL) + NL

open(os.path.join(TU, 'zamow-online.html'), 'w', encoding='utf-8', newline='').write(s)
print('zamow-online.html gotowy,', len(s), 'znakow')
