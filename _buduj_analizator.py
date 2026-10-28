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
DYSK = re.search(r"const DYSK_URL='([^']+)'", open(os.path.join(TU, 'wycena.html'), encoding='utf-8').read()).group(1)

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
       '<link rel="apple-touch-icon" sizes="180x180" href="img/analizator-180.png?v=3">' + NL +
       '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">' + NL +
       '<meta name="apple-mobile-web-app-title" content="Analizator">')
zamien('<link rel="icon" type="image/png" sizes="192x192" href="img/ikona-192.png">',
       '<link rel="icon" type="image/png" sizes="192x192" href="img/analizator-192.png?v=3">')
s = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="#FF6A13">', s, count=1)

# 2. tryb parkieciarza zawsze + blokada PIN (zaraz po <meta viewport>, przed reszta skryptow)
BRAMKA = '''<script>window.SP_ANALIZATOR=1;
(function(){var ok=false;try{ok=localStorage.getItem('spAnalizatorPin')==='1';}catch(e){}
 if(!ok)ok=/(?:^|; )spAnalizatorPin=1/.test(document.cookie);
 if(ok)return;document.documentElement.className+=' an-zamek';
 function pokaz(){if(document.getElementById('anPin'))return;var d=document.createElement('div');d.id='anPin';
  d.innerHTML='<form id="anPinF" autocomplete="off"><img src="img/analizator-192.png?v=3" alt="" width="64" height="64"><b>Analizator</b>'+
   '<label for="anPinI">Wpisz hasło</label><input id="anPinI" type="password" autocapitalize="characters" autocorrect="off" spellcheck="false" maxlength="30" autocomplete="off">'+
   '<button type="submit">Otwórz</button><p id="anPinE" role="alert"></p></form>';
  document.body.appendChild(d);var f=document.getElementById('anPinF'),i=document.getElementById('anPinI');
  /* 22.10: PIN sprawdza serwer (nie ma go w kodzie strony) i oddaje klucz do folderu ofert */
  f.onsubmit=function(e){e.preventDefault();var E=document.getElementById('anPinE');E.textContent='Sprawdzam...';
   fetch('%s?a=klucz&pin='+encodeURIComponent(i.value.trim())).then(function(r){return r.json();}).then(function(j){
    if(!j.ok){E.textContent=j.blad==='Zły PIN'?'Nieprawidłowe hasło':(j.blad||'Błąd');i.value='';i.focus();return;}
    try{localStorage.setItem('spAnalizatorPin','1');localStorage.setItem('spKlucz',j.k);}catch(x){}
    document.cookie='spAnalizatorPin=1; max-age=31536000; path=/; SameSite=Lax';
    document.documentElement.className=document.documentElement.className.replace(/\\s*an-zamek/g,'');d.remove();
    if(window.spFolderStart)window.spFolderStart();
   }).catch(function(){E.textContent='Brak internetu - spróbuj ponownie';});};
  setTimeout(function(){i.focus();},50);}
 if(document.body)pokaz();else document.addEventListener('DOMContentLoaded',pokaz);})();</script>
<style>html.an-zamek body>*:not(#anPin){visibility:hidden!important}
html.an-zamek,html.an-zamek body{overflow:hidden!important}
#anPin{position:fixed;inset:0;z-index:2147483000;display:grid;place-items:center;background:#F4EFE8;padding:16px;font-family:"Manrope",Inter,system-ui,sans-serif}
#anPin form{width:100%%;max-width:300px;display:grid;justify-items:center;gap:10px;background:#fff;border:1px solid #E7DED3;border-radius:16px;padding:26px 22px 20px;box-shadow:0 10px 30px rgba(20,17,14,.08)}
#anPin img{border-radius:14px}
#anPin b{font-size:1.25rem;letter-spacing:.04em;color:#14110E}
#anPin label{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:#4A5058;font-weight:700}
#anPin input{width:100%%;font-size:1.4rem;text-align:center;letter-spacing:.15em;padding:10px;border:1.5px solid #3A3F45;border-radius:10px}
#anPin button{width:100%%;border:0;border-radius:10px;padding:12px;font-weight:800;font-size:1rem;background:#FF6A13;color:#fff;cursor:pointer}
#anPin p{margin:0;min-height:1.2em;font-size:.85rem;color:#B23B1E}
</style>''' % DYSK
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

# 5. Artur 22.10: folder wszystkich wyslanych ofert - wczytanie dowolnej (z telefonu i laptopa),
#    poprawka i ponowna wysylka bez wpisywania i ladowania zdjec od nowa
FOLDER_JS = r"""<style>
#folOf{margin:0 0 12px;padding:12px;border-radius:10px;background:#2A2C30;border:1px solid #5A5E65}
#folOf b{display:block;color:#FF8A4C!important;font-size:.95rem;letter-spacing:.04em;margin:0 0 6px}
#folOf select{width:100%;font:inherit;font-size:.95rem;padding:10px;border-radius:8px;background:#fff;color:#14110E;border:0}
#folWyn{display:grid;gap:6px;margin:0 0 8px}#folWyn:empty{display:none}
#folWyn button{display:block;width:100%;text-align:left;font:inherit;font-size:.92rem;line-height:1.35;padding:10px 12px;border-radius:8px;border:0;background:#fff;color:#14110E;cursor:pointer}
#folWyn button small{display:block;color:#6A6F76;font-size:.78rem;margin-top:2px}
#folWyn button.st{background:#ECEDEF}
#folWyn .fw-k{display:flex;align-items:center;gap:8px;font-size:.78rem;font-weight:700;color:#4A5058;margin-bottom:2px}
#folWyn .fw-k i{font-style:normal;font-size:.68rem;letter-spacing:.06em;padding:2px 7px;border-radius:999px}
#folWyn .fw-n{background:#FF6A13;color:#fff}#folWyn .fw-s{background:#D5D8DC;color:#3A3F45}
#folWyn button.fw-old{background:#F1F2F4;color:#4A5058}
#folInfo{margin:6px 0 0;font-size:.85rem;color:#E9E4DD!important;min-height:1em}
#wycHist{display:none!important}
</style>
<script>
(function(){
 var U='__DYSK__';
 function k(){try{return localStorage.getItem('spKlucz')||'';}catch(e){return '';}}
 function info(t){var e=document.getElementById('folInfo');if(e)e.textContent=t;}
 /* brak klucza na tym urzadzeniu: pole PIN w ramce folderu (bez okienek przegladarki) */
 function pokazPin(){var e=document.getElementById('folInfo');if(!e||document.getElementById('folPin'))return;
  e.innerHTML='<span style="display:flex;gap:6px"><input id="folPin" type="password" autocapitalize="characters" autocorrect="off" spellcheck="false" placeholder="Hasło" aria-label="Hasło do folderu ofert" style="flex:1;min-width:0;padding:10px;border-radius:8px;border:0;font-size:1rem">'+
   '<button type="button" id="folPinB" style="border:0;border-radius:8px;padding:10px 14px;background:#FF6A13;color:#fff;font-weight:800">Otwórz folder</button></span>';
  var go=async function(){var v=document.getElementById('folPin').value.trim();if(!v)return;
   var j;try{j=await (await fetch(U+'?a=klucz&pin='+encodeURIComponent(v))).json();}catch(x){info('Brak internetu - spróbuj ponownie');return;}
   if(!j.ok){info(j.blad==='Zły PIN'?'Nieprawidłowe hasło':(j.blad||'Błąd'));setTimeout(pokazPin,1500);return;}
   try{localStorage.setItem('spKlucz',j.k);}catch(x){}var m=location.hash.match(/oferta=([\w-]+)/);if(m)wczytaj(m[1]);else lista();};
  document.getElementById('folPinB').onclick=go;document.getElementById('folPin').onkeydown=function(ev){if(ev.key==='Enter'){ev.preventDefault();go();}};}
 async function klucz(){var x=k();if(x)return x;pokazPin();return '';}
 async function api(q){var x=await klucz();if(!x)return null;
  var j=await (await fetch(U+'?'+q+'&k='+encodeURIComponent(x)+'&_='+Date.now(),{cache:'no-store'})).json(); /* 28.10: bez cache przegladarki */
  if(!j.ok&&j.blad==='Brak dostępu'){try{localStorage.removeItem('spKlucz');}catch(e){}}return j;}
 function plik(b,i){var s=atob(b),a=new Uint8Array(s.length);for(var n=0;n<s.length;n++)a[n]=s.charCodeAt(n);
  return new File([a],'Zdjecie_'+String(i+1).padStart(2,'0')+'.jpg',{type:'image/jpeg'});}
 async function lista(){info('Pobieram listę ofert...');var j;try{j=await api('a=lista');}catch(e){}
  if(!j)return;if(!j.ok){info(j.blad||'Nie udało się pobrać listy.');if(j.blad==='Brak dostępu')pokazPin();return;}
  WSZ=(j.lista||[]).slice().sort(function(x,y){return (y.t||0)-(x.t||0);});WSZ_T=Date.now();window.spFolderNieaktualny=false;pokazListe();
  info(j.lista.length?'Wpisz kilka liter ulicy albo wybierz z listy. Oferty od 22.10 wczytują się ze zdjęciami, starsze (szare) - same dane klienta.':'Folder jest pusty.');}
 async function wczytaj(id){info('Wczytuję ofertę...');var j;try{j=await api('a=wczytaj&id='+encodeURIComponent(id));}catch(e){}
  if(!j)return;if(!j.ok){info('Nie udało się wczytać oferty.');return;}
  if(j.stara){var sm=document.getElementById('smsWklej'),bt=document.getElementById('smsRozrzuc');
   if(sm&&bt){sm.value=j.tekst||'';bt.click();}
   info('Stara oferta z '+(j.kiedy||'przed 22.10')+' - wczytane dane klienta i metraż. Zdjęć i zaznaczeń z tamtej wyceny nie zapisywaliśmy, uzupełnij je i wyślij ponownie.'+(j.pozycje&&j.pozycje.length?' Pozycje z tamtej oferty: '+j.pozycje.join('; ')+'.':''));return;}
  var o=j.oferta;
  var pop=document.getElementById('poprawBtn');if(pop)pop.click();
  var mini=document.getElementById('miniatury'),b,n=0;
  while(mini&&(b=mini.querySelector('button[data-i]'))&&n++<20)b.click();
  window.spWczytaj(o.stan||{});
  var fi=document.getElementById('file');
  if(fi&&o.zdjecia&&o.zdjecia.length){var dt=new DataTransfer();o.zdjecia.forEach(function(z,i){dt.items.add(plik(z,i));});
   fi.files=dt.files;fi.dispatchEvent(new Event('change',{bubbles:true}));
   var pd=(o.stan&&o.stan.podpisy)||[];setTimeout(function(){[].slice.call(document.querySelectorAll('#miniatury input.podp')).forEach(function(p,i){
    if(pd[i]){p.value=pd[i];p.dispatchEvent(new Event('input',{bubbles:true}));}});},300);}
  var ok=document.getElementById('ofertaKl');if(ok&&o.mailKlienta)ok.checked=true;
  info('Wczytana oferta z '+o.kiedy+' ('+((o.zdjecia||[]).length)+' zdj.). Popraw, co trzeba, i wyślij ponownie - klient dostanie poprawioną ofertę.');}
 /* Artur 27.10 13:22-13:24: lista ofert za dluga - pole szukania (3-4 litery ulicy, telefon albo data) filtruje na zywo */
 var WSZ=[],WSZ_T=0;
 /* Artur 28.10 22:24: po korekcie i wysylce wyszukiwarka pokazywala STARA wersje - lista byla pobrana raz przy otwarciu strony
    i nigdy odswiezana (nowy zapis w Dysku byl, ale nie na liscie w telefonie). Teraz: pobieranie przy kazdym wejsciu w pole szukania
    (najwyzej co 15 s) i zawsze po wyslaniu oferty; wersje tego samego klienta oznaczone, najnowsza na gorze. */
 var LAD=null;function odswiez(){if(!LAD)LAD=lista().finally(function(){LAD=null;});return LAD;}
 function swieza(){return WSZ.length&&!window.spFolderNieaktualny&&Date.now()-WSZ_T<15000;}
 function rozbierz(o){var op=String(o.opis||''),m=op.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2})[-:](\d{2})\s*/),kiedy='',reszta=op;
  if(m){kiedy=m[3]+'.'+m[2]+' '+m[4]+':'+m[5];reszta=op.slice(m[0].length);}
  else if(o.t){var d=new Date(o.t);kiedy=('0'+d.getDate()).slice(-2)+'.'+('0'+(d.getMonth()+1)).slice(-2)+' '+('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);}
  var nt=(reszta.match(/netto (\d+) zł/)||[])[1],nr=(reszta.match(/nr (\d{8}-\d{3,5})/)||[])[1];
  reszta=reszta.replace(/netto \d+ zł\s*/,'').replace(/nr \d{8}-\d{3,5}\s*/,'').trim();
  var tel=(reszta.replace(/[\s-]/g,'').match(/(\+?48)?(\d{9})(?!.*\d{9})/)||[])[2]||'';
  var klucz=tel||bezOg(reszta).replace(/^\d+([.,]\d+)?\s*m2?\s*/,'').replace(/[^a-z0-9]/g,'').slice(0,24);
  return {kiedy:kiedy,netto:nt?(+nt).toLocaleString('pl-PL').replace(/\u00a0/g,' ')+' zł':'',nr:nr||'',reszta:reszta.replace(/</g,''),klucz:klucz};}
 function bezOg(t){return String(t||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ł/g,'l');}
 function pokazListe(){var sel=document.getElementById('folSel'),q=bezOg((document.getElementById('folSzuk')||{}).value||'').trim();
  /* Artur 28.10 wieczor: "AL.Jana" nie znajdowalo "AL. JANA PAWLA II 61/36". Kropki, przecinki, podkreslenia, ukosniki = spacje;
     kazde slowo zapytania musi byc fragmentem tekstu oferty (adres, nazwa pliku, klient, telefon, data), w dowolnej kolejnosci */
  var tnij=function(t){return bezOg(t).replace(/[.,_\/\\;:·()\-]+/g,' ').replace(/\s+/g,' ').trim();};
  var qn=tnij(q),qw=qn?qn.split(' '):[],qs=qn.replace(/\s+/g,'');
  var lis=WSZ.filter(function(o){if(!q)return true;var t=tnij(o.opis+' '+(o.plik||'')),tz=t.replace(/\s+/g,'');
   return (qw.length&&qw.every(function(w){return t.indexOf(w)>=0;}))||(qs.length>2&&tz.indexOf(qs)>=0);});
  var ile={},bylo={};lis.forEach(function(o){var r=rozbierz(o);o._r=r;ile[r.klucz]=(ile[r.klucz]||0)+1;});
  lis.forEach(function(o){var r=o._r;r.wersja=ile[r.klucz]>1?(bylo[r.klucz]?'starsza wersja':'NAJNOWSZA'):'';bylo[r.klucz]=1;});
  sel.innerHTML='<option value="">'+(q?('Znaleziono: '+lis.length+' - wybierz ofertę…'):('Wybierz ofertę do poprawki ('+WSZ.length+')…'))+'</option>'+lis.map(function(o){var r=o._r;
   return '<option value="'+o.id+'">'+[r.kiedy,r.wersja,r.netto,r.reszta].filter(Boolean).join(' · ')+'</option>';}).join('');
  var wyn=document.getElementById('folWyn');if(!wyn)return;
  if(!q){wyn.innerHTML='';return;}
  wyn.innerHTML=lis.length?lis.slice(0,8).map(function(o){var r=o._r,t=String(o.opis).replace(/</g,'').split(' · ');
   var gl=o.stara?t.slice(1,3).join(' · '):r.reszta;
   var znak=r.wersja==='NAJNOWSZA'?'<i class="fw-n">NAJNOWSZA</i>':(r.wersja?'<i class="fw-s">starsza wersja</i>':'');
   return '<button type="button" data-id="'+o.id+'"'+(o.stara?' class="st"':(r.wersja==='starsza wersja'?' class="fw-old"':''))+'><span class="fw-k">'+r.kiedy+znak+'</span>'+gl+'<small>'+[r.netto?('netto '+r.netto):'',r.nr?('nr '+r.nr):'',o.stara?'stara oferta':''].filter(Boolean).join(' · ')+'</small></button>';}).join('')
   +(lis.length>8?'<small style="color:#E9E4DD">i jeszcze '+(lis.length-8)+' - wpisz więcej liter</small>':''):'<small style="color:#E9E4DD">Nic nie znaleziono - spróbuj inaczej: 3-4 litery ulicy, końcówka telefonu albo data (np. 21.10).</small>';}
 function start(){var box=document.querySelector('.sms-box');if(document.getElementById('folOf')){if(k())lista();return;}if(!box)return;
  var w=document.createElement('div');w.id='folOf';
  w.innerHTML='<b>Folder ofert <small style="float:right;font-weight:400;color:#B9BDC3;font-size:.72rem;letter-spacing:0">wersja 28.10 23:00</small></b><input id="folSzuk" type="search" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="Szukaj: 3-4 litery ulicy, telefon lub data" aria-label="Szukaj oferty" style="width:100%;min-height:44px;font-size:16px;margin:0 0 8px;padding:8px 12px;border:1.5px solid #3A3F45;border-radius:10px;box-sizing:border-box"><div id="folWyn"></div><select id="folSel" aria-label="Wysłane oferty"><option value="">Otwórz listę wysłanych ofert…</option></select><p id="folInfo"></p>';
  box.insertBefore(w,box.firstChild);
  var sel=document.getElementById('folSel');
  sel.addEventListener('pointerdown',function(){if(sel.options.length<2)lista();},{once:true});
  sel.addEventListener('focus',function(){if(sel.options.length<2)lista();},{once:true});
  sel.addEventListener('change',function(){if(sel.value)wczytaj(sel.value);});
  document.getElementById('folWyn').addEventListener('click',function(ev){var b=ev.target.closest('button[data-id]');if(!b)return;
   document.getElementById('folWyn').innerHTML='';wczytaj(b.getAttribute('data-id'));});
  var sz=document.getElementById('folSzuk');
  sz.addEventListener('focus',function(){if(!swieza())odswiez();});
  sz.addEventListener('input',function(){if(!swieza()){odswiez();return;}pokazListe();});
  sel.addEventListener('focus',function(){if(!swieza())odswiez();});
  document.addEventListener('visibilitychange',function(){if(!document.hidden)window.spFolderNieaktualny=true;});
  sz.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();sz.blur();}});
  var m=location.hash.match(/oferta=([\w-]+)/);if(m)wczytaj(m[1]);else if(k())lista();else pokazPin();}
 window.spFolderStart=start;
 if(document.readyState!=='loading')start();else document.addEventListener('DOMContentLoaded',start);
})();
</script>""".replace('__DYSK__', DYSK)
s = s.rstrip('\r\n') + NL + FOLDER_JS.replace('\n', NL) + NL

open(os.path.join(TU, 'analizator.html'), 'w', encoding='utf-8', newline='').write(s)
print('analizator.html gotowy,', len(s), 'znakow')
