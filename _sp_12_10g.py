# -*- coding: utf-8 -*-
"""Artur, 12.10.2026 23:41-23:52.

23:41 dwa przyciski tych samych wymiarow, HUMMEL miedzy nimi i widoczny, na osi,
      symetrycznie, moga byc pomaranczowe
23:42 / 23:52 bialy pasek u gory i pasek na dole (Zadzwon/WhatsApp/Wycena) wezsze,
      tego samego wymiaru
23:44 / 23:46 / 23:52 kolko logo o srednicy rownej wysokosci pomaranczowego
      przycisku z numerem; SMARTPARKIET w osi miedzy kolkiem a hamburgerem
23:44 / 23:51 Bez balaganu / Bez pylu / Bez stresu kursywa
23:48 / 23:51 Cyklinowanie SMART wyzej (odslonic zielony znaczek Lagler na worku),
      reszta rozlozona tak, zeby HUMMEL byl widoczny miedzy przyciskami, opinie
      scisniete na brazowej podlodze, nawigacja opinii mniejsza

Zdjecie 1500x1000 w kadrze hero zawsze wypelnia go na wysokosc (telefon jest
wezszy niz 3:2), wiec miejsca na zdjeciu sa stalym procentem wysokosci hero:
Lagler 13,5-24,5 %, HUMMEL 60,5-64 %, podloga od 78 %. Hero ma wysokosc
widocznego ekranu miedzy paskami, a przyciski i opinie stoja na tych procentach.
"""
import io
import os
import re

KAT = r'C:\Users\Admin\Downloads\SMARTPARKIET_www'

PASKI_START = '<!-- paski 23:52: START -->'
PASKI_KONIEC = '<!-- paski 23:52: KONIEC -->'
PASKI = PASKI_START + '''
<style>
/* 23:42/23:52 gorny i dolny pasek wezsze i tej samej wysokosci (44 px);
   23:46 kolko logo = wysokosc pomaranczowego przycisku; napis w osi
   miedzy kolkiem a hamburgerem */
@media(max-width:860px){
  :root{--pasek:44px}
  .nav .wrap{height:var(--pasek)!important;min-height:0!important;padding-top:0!important;padding-bottom:0!important}
  .nav nav{top:var(--pasek)!important}
  header.nav .brand{gap:0!important;margin-right:0!important;flex:1 1 auto!important}
  header.nav .brand img{width:var(--H)!important;height:var(--H)!important}
  header.nav .brand .brand-t{flex:1 1 auto!important;text-align:center!important}
  .cta-bar a{min-height:0!important;height:var(--pasek)!important}
}
</style>
''' + PASKI_KONIEC

HERO_START = '<!-- hero 23:52: START -->'
HERO_KONIEC = '<!-- hero 23:52: KONIEC -->'
HERO = HERO_START + '''
<style>
@media(max-width:860px){
  /* hero = widoczny ekran miedzy gornym i dolnym paskiem */
  .hero{height:calc(100svh - 2 * var(--pasek,44px))!important;min-height:520px!important;
    max-height:none!important;padding:0!important;display:block!important}
  .hero .wrap{padding-top:6px!important;position:static!important;transform:none!important}
  .hero .wrap > *:not(.cta-rowne):not(.hero-op){position:relative!important;z-index:3!important}
  .hero .cta-rowne .btn,.hero-op{z-index:3!important}
  /* nadtytul ciasniej, zeby Cyklinowanie SMART weszlo nad znaczek Lagler (13,5 %) */
  .hero .tag{font-size:.6rem!important;line-height:1.3!important;padding-top:0!important;padding-bottom:0!important}
  .hero .tag::after{display:none!important}
  .hero h1{margin-top:6px!important}
  /* 23:44 kursywa */
  .hero h1 .h-lin{font-style:italic!important}
  .hero h1 .h-lin:first-of-type{margin-top:4px!important}
  .hero-ocena{margin-top:8px!important}
  .hero-lead{margin-top:6px!important}
  .hero-lead p{margin-top:3px!important}
  /* 23:41 dwa przyciski tych samych wymiarow, na osi, HUMMEL (60,5-64 %) miedzy nimi */
  .hero .cta-rowne{position:static!important;margin:0!important;display:block!important}
  .hero .cta-rowne .btn{position:absolute!important;left:0!important;right:0!important;margin:0 auto!important;transform:none!important;
    width:min(306px,calc(100% - 32px))!important;height:36px!important;min-height:0!important;
    padding:0 12px!important;gap:10px!important;justify-content:center!important;
    font-size:.7rem!important;line-height:1!important;letter-spacing:.03em!important;white-space:nowrap!important;
    background:#E8671F!important;border:0!important;color:#fff!important;box-shadow:0 4px 14px rgba(0,0,0,.25)!important}
  .hero .cta-rowne .btn .bt,.hero .cta-rowne .btn .bs{color:#fff!important}
  .hero .cta-rowne .btn svg{stroke:#fff!important}
  .hero .cta-rowne .btn .bt br{display:none}
  .hero .cta-rowne .btn .bt{flex:0 1 auto!important}
  .hero .cta-rowne .btn .bi{width:16px!important;height:16px!important}
  .hero .cta-rowne .btn-amber{top:auto!important;bottom:calc(100% - 59.5%)!important}
  .hero .cta-rowne .btn-ghost{top:65.5%!important;bottom:auto!important}
  /* 23:48/23:51 opinie scisniete na brazowej podlodze (od 78 %), nawigacja mniejsza */
  .hero-op{position:absolute!important;left:24px!important;right:24px!important;top:77.5%!important;
    bottom:4px!important;margin:0!important;display:flex!important;flex-direction:column!important;justify-content:flex-end!important}
  .hero-op-tor{flex:0 0 auto!important}
  .hero .hero-op .hero-quote{font-size:.66rem!important;line-height:1.28!important;padding-top:0!important;padding-bottom:0!important}
  .hero .hero-op .hero-quote b{font-size:.6rem!important;line-height:1.3!important;margin-top:2px!important}
  .hero .hero-op .hero-op-nav{margin-top:6px!important;gap:8px!important}
  .hero .hero-op .hop-btn{width:24px!important;height:24px!important;min-width:0!important;min-height:0!important;font-size:.75rem!important;padding:0!important}
}
</style>
''' + HERO_KONIEC


def wstaw(s, a, b, blok):
    s = re.sub(re.escape(a) + r'.*?' + re.escape(b), '', s, flags=re.S)
    return s.rstrip() + '\n' + blok + '\n'


ile = 0
for n in sorted(os.listdir(KAT)):
    if not n.endswith('.html') or n.startswith('_') or n == 'wyslane.html':
        continue
    p = os.path.join(KAT, n)
    s = io.open(p, encoding='utf-8').read()
    if 'class="nav' not in s:
        continue
    s = wstaw(s, PASKI_START, PASKI_KONIEC, PASKI)
    if n == 'index.html':
        s = wstaw(s, HERO_START, HERO_KONIEC, HERO)
    io.open(p, 'w', encoding='utf-8').write(s)
    ile += 1
print('paski w %d plikach, hero w index.html' % ile)
