# -*- coding: utf-8 -*-
"""Buduje analizator.html z wycena.html (Artur 21.10: narzedzia parkieciarza w jednym miejscu).

analizator.html = ta sama strona co wycena.html, ale:
- tryb parkieciarza WLACZONY ZAWSZE (window.SP_ANALIZATOR, bez localStorage i ?parkieciarz),
- zablokowana PIN-em (zapamietywany na urzadzeniu: localStorage + ciasteczko),
- noindex/nofollow, poza menu i sitemap (build.py: NOINDEX),
- pomaranczowa ikona na ekran glowny i osobny manifest analizator.webmanifest,
- okienko "Wklej SMS" na ciemnym grafitowym tle z naglowkiem "Analizator".

URUCHAMIAC PO KAZDEJ ZMIANIE wycena.html:  python _buduj_analizator.py
(build.py w SMARTPARKIET_wdrozenie wywoluje go sam przed budowa paczki).
"""
import os, re

TU = os.path.dirname(os.path.abspath(__file__))
PIN = '2815'

s = open(os.path.join(TU, 'wycena.html'), encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in s else '\n'

def zamien(stare, nowe, n=1):
    global s
    if s.count(stare) < 1:
        raise SystemExit('Nie znaleziono: ' + stare[:80])
    s = s.replace(stare, nowe) if n == 0 else s.replace(stare, nowe, n)

# 1. tytul, robots, ikony, manifest
s = re.sub(r'<title>.*?</title>', '<title>SMARTPARKIET Analizator</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', s, count=1)
s = re.sub(r'<!-- podglad linku: START -->.*?<!-- podglad linku: KONIEC -->', '', s, count=1, flags=re.S)
s = re.sub(r'<script type="application/ld\+json".*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<meta name="twitter:[^>]*>\s*', '', s)
zamien('<link rel="manifest" href="site.webmanifest">', '<link rel="manifest" href="analizator.webmanifest">')
zamien('<link rel="apple-touch-icon" sizes="180x180" href="img/apple-touch-icon.png">',
       '<link rel="apple-touch-icon" sizes="180x180" href="img/analizator-180.png">' + NL +
       '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">' + NL +
       '<meta name="apple-mobile-web-app-title" content="Analizator">')
zamien('<link rel="icon" type="image/png" sizes="192x192" href="img/ikona-192.png">',
       '<link rel="icon" type="image/png" sizes="192x192" href="img/analizator-192.png">')
s = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="#F8580E">', s, count=1)

# 2. tryb parkieciarza zawsze + blokada PIN (zaraz po <meta viewport>, przed reszta skryptow)
BRAMKA = '''<script>window.SP_ANALIZATOR=1;
(function(){var ok=false;try{ok=localStorage.getItem('spAnalizatorPin')==='1';}catch(e){}
 if(!ok)ok=/(?:^|; )spAnalizatorPin=1/.test(document.cookie);
 if(ok)return;document.documentElement.className+=' an-zamek';
 function pokaz(){if(document.getElementById('anPin'))return;var d=document.createElement('div');d.id='anPin';
  d.innerHTML='<form id="anPinF" autocomplete="off"><img src="img/analizator-192.png" alt="" width="64" height="64"><b>Analizator</b>'+
   '<label for="anPinI">Wpisz PIN</label><input id="anPinI" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="8" autocomplete="off">'+
   '<button type="submit">Otwórz</button><p id="anPinE" role="alert"></p></form>';
  document.body.appendChild(d);var f=document.getElementById('anPinF'),i=document.getElementById('anPinI');
  f.onsubmit=function(e){e.preventDefault();if(i.value.trim()==='%s'){
    try{localStorage.setItem('spAnalizatorPin','1');}catch(x){}
    document.cookie='spAnalizatorPin=1; max-age=31536000; path=/; SameSite=Lax';
    document.documentElement.className=document.documentElement.className.replace(/\\s*an-zamek/g,'');d.remove();}
   else{document.getElementById('anPinE').textContent='Nieprawidłowy PIN';i.value='';i.focus();}};
  setTimeout(function(){i.focus();},50);}
 if(document.body)pokaz();else document.addEventListener('DOMContentLoaded',pokaz);})();</script>
<style>html.an-zamek body>*:not(#anPin){visibility:hidden!important}
html.an-zamek,html.an-zamek body{overflow:hidden!important}
#anPin{position:fixed;inset:0;z-index:2147483000;display:grid;place-items:center;background:#F4EFE8;padding:16px;font-family:"Manrope",Inter,system-ui,sans-serif}
#anPin form{width:100%%;max-width:300px;display:grid;justify-items:center;gap:10px;background:#fff;border:1px solid #E7DED3;border-radius:16px;padding:26px 22px 20px;box-shadow:0 10px 30px rgba(20,17,14,.08)}
#anPin img{border-radius:14px}
#anPin b{font-size:1.25rem;letter-spacing:.04em;color:#14110E}
#anPin label{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:#4A5058;font-weight:700}
#anPin input{width:100%%;font-size:1.4rem;text-align:center;letter-spacing:.4em;padding:10px;border:1.5px solid #3A3F45;border-radius:10px}
#anPin button{width:100%%;border:0;border-radius:10px;padding:12px;font-weight:800;font-size:1rem;background:#F8580E;color:#fff;cursor:pointer}
#anPin p{margin:0;min-height:1.2em;font-size:.85rem;color:#B23B1E}
</style>''' % PIN
m = re.search(r'<meta name="viewport"[^>]*>', s)
s = s[:m.end()] + NL + BRAMKA.replace('\n', NL) + s[m.end():]

# 3. bez linku do samego siebie w stopce
s = re.sub(r'\s*<p class="an-link">.*?</p>', '', s, count=1, flags=re.S)

# 4. okienko "Wklej SMS" na ciemnym tle z naglowkiem Analizator (Artur 21.10 17:27)
CSS = '''<style>/* analizator: okienko SMS wyroznione (Artur 21.10 17:27) */
html body .sms-box{background:#3A3D42!important;border:1.5px solid #3A3D42!important;color:#F4EFE8;box-shadow:0 6px 18px rgba(20,17,14,.18)}
html body .sms-box::before{content:"Analizator";display:block;font-size:1.15rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#FF8A4C;margin:0 0 6px}
html body .sms-box b{color:#FFFFFF!important}
html body .sms-box p{color:#D9D4CD!important}
html body .sms-box textarea{background:#2A2C30!important;color:#FFFFFF!important;border:1px solid #5A5E65!important}
html body .sms-box textarea::placeholder{color:#9BA0A7}
html body .sms-box button.sms-czysc{background:#55595F!important;color:#fff!important}
html body .sms-wynik .ok{color:#7EE2A8!important}html body .sms-wynik .brak{color:#FF9C85!important}
html body .sms-box .sms-wynik{color:#E9E4DD}
</style>'''
s = s.rstrip('\r\n') + NL + CSS.replace('\n', NL) + NL

open(os.path.join(TU, 'analizator.html'), 'w', encoding='utf-8', newline='').write(s)
print('analizator.html gotowy,', len(s), 'znakow')
