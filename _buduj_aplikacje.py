# -*- coding: utf-8 -*-
"""Buduje aplikacje Katalog + Grafik (aplikacja/index.html) z zatwierdzonej makiety.

Zrodlo ukladu: Downloads/smartparkiet-katalog-podglad/index.html (makieta, w ktorej Artur zglasza uwagi).
Skrypt podmienia warstwe danych (dane przykladowe -> backend Apps Script katalog.gs), dokłada logowanie,
synchronizacje, tryb offline i PWA. Kazda zamiana jest sprawdzana (assert) - gdy makieta sie zmieni
i ktorys fragment nie pasuje, skrypt zatrzyma sie z nazwa fragmentu.

Uruchomienie: python _buduj_aplikacje.py   (potem build.py w SMARTPARKIET_wdrozenie\\narzedzia)
"""
import os, re, sys

TU = os.path.dirname(os.path.abspath(__file__))
MAKIETA = os.path.join(os.path.dirname(TU), 'smartparkiet-katalog-podglad', 'index.html')
CEL = os.path.join(TU, 'aplikacja', 'index.html')
API_PROD = 'https://script.google.com/macros/s/AKfycbxC1j9MytYHxqD-ONdcd8Bar5SxnAVnmr8pxP1_pdEEIZzB1hbh9AXRDtXEg5hX0QXzDA/exec'

s = open(MAKIETA, encoding='utf-8').read()


def R(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, 'fragment %r wystepuje %d razy (oczekiwano %d)' % (a[:90], c, n)
    s = s.replace(a, b)


def ZAMIEN(start, koniec, nowy):
    """zamienia od 'start' (wlacznie) do 'koniec' (bez)"""
    global s
    a = s.index(start)
    b = s.index(koniec, a)
    s = s[:a] + nowy + s[b:]


# ------------------------------------------------------------------ <head>
R('<title>Katalog zapytań - SMARTPARKIET</title>',
  '<title>Katalog SMARTPARKIET</title>\n'
  '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\' \'unsafe-inline\'; style-src \'self\' \'unsafe-inline\'; '
  'img-src \'self\' data:; connect-src \'self\' https://script.google.com https://script.googleusercontent.com; worker-src \'self\'; manifest-src \'self\'; '
  'base-uri \'none\'; form-action \'none\'">\n'
  '<meta name="referrer" content="no-referrer">\n'
  '<link rel="preconnect" href="https://script.google.com">')

# ------------------------------------------------------------------ pasek stanu zamiast paska podgladu
R('.demo i{width:6px;height:6px;border-radius:50%;background:var(--pom);display:inline-block}',
  '.demo i{width:7px;height:7px;border-radius:50%;background:#8A8178;display:inline-block}\n'
  '.demo.ok i{background:#2ED47A}.demo.zap i{background:#FFC53D}.demo.off i,.demo.blad i{background:#FF4D5E}\n'
  '.demo.off{background:#5B1F1A}\n'
  '.login .err{color:#FF8C7A;min-height:18px;margin:10px 0 0}\n'
  '.login input{color:#F2EDE6}\n'
  '.wyl{display:block;margin:10px auto 0;font-size:13px;color:var(--ink3);text-decoration:underline;text-underline-offset:2px}\n'
  '.side .wyl{margin:12px 8px 0;text-align:left;color:#8A8178}\n'
  '.linki{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}\n'
  '.linki a{flex:1 1 140px;height:40px;border-radius:10px;background:var(--kosc);display:flex;align-items:center;justify-content:center;gap:6px;font-size:13px;font-weight:600;text-decoration:none;color:var(--ink)}\n'
  '.ladow{padding:60px 24px;text-align:center;color:var(--ink3)}')
R('<div class="demo"><div class="in"><i></i><span><b>Podgląd</b> - dane przykładowe</span><button type="button" data-act="reset">wyczyść zmiany</button></div></div>',
  '<div class="demo" id="pasek"><div class="in"><i></i><span id="syncTx">Łączenie...</span></div></div>')

# ------------------------------------------------------------------ logowanie
ZAMIEN('<section class="login" id="login" hidden>', '<div class="app" id="app">',
       '''<section class="login" id="login" hidden>
  <img src="img/logo-96.png" alt="" width="72" height="72">
  <h1>SMARTPARKIET</h1>
  <h2>Katalog zapytań</h2>
  <form id="loginForm" autocomplete="on">
    <input type="text" name="username" value="SMARTPARKIET" autocomplete="username" hidden>
    <input id="haslo" type="password" name="password" placeholder="Hasło" autocomplete="current-password" aria-label="Hasło" required>
    <button class="btn" type="submit" id="loginBtn">Zaloguj</button>
  </form>
  <p class="err" id="loginErr" role="alert"></p>
  <p>Telefon zapamięta logowanie. Hasło ustala Łukasz.</p>
</section>

''')

# ------------------------------------------------------------------ dane: zamiast danych przykladowych - stan z serwera
ZAMIEN('/* ---------- dane przykładowe (zmyślone) ---------- */', 'var $=function(id)', r'''/* ---------- dane z serwera (Apps Script katalog.gs) ---------- */
var API=(function(){var h=location.hostname;if(h==='localhost'||h==='127.0.0.1'){var q=new URLSearchParams(location.search).get('api');return q||location.origin+'/api';}return '__API__';})();
var KL_TOK='spk-app-token',KL_KESZ='spk-app-stan',KL_OST='spk-app-ostatnie';
function lsGet(k){try{return localStorage.getItem(k);}catch(e){return null;}}
function lsSet(k,v){try{if(v==null)localStorage.removeItem(k);else localStorage.setItem(k,v);}catch(e){}}
var TOK=lsGet(KL_TOK)||'';
var OSTATNIE=+lsGet(KL_OST)||(Date.now()-3*864e5);lsSet(KL_OST,String(Date.now()));
function m2(it){return +it.m2||0;}
function kwotaTxt(it){return it.kwota>0?zl(it.kwota):'bez wyceny';}
function adrTxt(it){return [it.ul,it.ds].filter(Boolean).join(', ');}
function adrKr(it){return it.ds||String(it.ul||'').split(',')[0];}
function pusty(){return {items:[],wpisy:[],graf:{v:2,br:[],kol:[],k:[]},rev:0};}
function zStanu(st){return {items:st.items||[],wpisy:st.wpisy||[],graf:st.graf||{v:2,br:[],kol:[],k:[]},rev:st.rev||0};}
function klon(o){return JSON.parse(JSON.stringify(o));}
var BAZA=null,POCZ=null,D=pusty();
(function(){var k=lsGet(KL_KESZ);if(TOK&&k){try{BAZA=zStanu(JSON.parse(k));POCZ=BAZA;D=klon(BAZA);}catch(e){}}})();
var S={v:'dzis',sel:null,dzien:null,fT:'all',fS:'otwarte',kt:'tydz',kd:DZIS,q:'',wyb:null};
var OTWARTE=function(i){return i.st!=='zrobione'&&i.st!=='odpadlo';};
function item(id){for(var i=0;i<D.items.length;i++)if(D.items[i].id===id)return D.items[i];return null;}
function wpis(id){for(var i=0;i<D.wpisy.length;i++)if(D.wpisy[i].id===id)return D.wpisy[i];return null;}
function czyNowe(it){return !it.widz&&it.ts>OSTATNIE;}
function log(it,x){it.hist=(it.hist||[]).concat([{ts:Date.now(),x:x}]).slice(-60);}

/* ---------- synchronizacja: zmiany liczone jako różnica względem stanu z serwera ---------- */
var LOT=null,BRUD=false,OFF=false,tZap=null,ODLOZ=false;
var POLA_ZAP=['st','nt','dz','g','widz','hist'];
function rekZap(x){if(x.reczne||x.typ==='r'){var o=klon(x);delete o.id;o.reczne=true;return o;}var p={};POLA_ZAP.forEach(function(k){p[k]=x[k]===undefined?null:x[k];});return p;}
function bezId(x){var o=klon(x);delete o.id;return o;}
function roznice(A,B){
  var ops=[];
  function por(t,a,b,f){var ma={},mb={};(a||[]).forEach(function(x){ma[x.id]=x;});(b||[]).forEach(function(x){mb[x.id]=x;});
    Object.keys(mb).forEach(function(id){var nb=f(mb[id]);if(!ma[id]||JSON.stringify(f(ma[id]))!==JSON.stringify(nb))ops.push({t:t,id:id,d:nb});});
    Object.keys(ma).forEach(function(id){if(!mb[id])ops.push({t:t,id:id,d:null});});}
  por('zap',A.items,B.items,rekZap);por('wpis',A.wpisy,B.wpisy,bezId);por('kaf',A.graf.k,B.graf.k,bezId);
  if(JSON.stringify([A.graf.br,A.graf.kol])!==JSON.stringify([B.graf.br,B.graf.kol]))ops.push({t:'ust',d:{br:B.graf.br,kol:B.graf.kol}});
  return ops;
}
function zastosuj(B,ops){
  ops.forEach(function(op){
    if(op.t==='ust'){B.graf.br=klon(op.d.br);B.graf.kol=klon(op.d.kol);return;}
    var arr=op.t==='zap'?B.items:op.t==='wpis'?B.wpisy:B.graf.k,i=-1;
    arr.forEach(function(x,j){if(x.id===op.id)i=j;});
    if(op.d===null){if(i>=0)arr.splice(i,1);return;}
    var n=Object.assign({},i>=0?arr[i]:{},klon(op.d),{id:op.id});if(i>=0)arr[i]=n;else arr.push(n);
  });
  return B;
}
function zajety(){var ae=document.activeElement;return !!(document.querySelector('.okno,.pal,.prz')||(typeof dr!=='undefined'&&dr&&dr.on)||(ae&&/^(INPUT|TEXTAREA|SELECT)$/.test(ae.tagName)&&ae.id!=='q'));}
/* stan z serwera trafia do widoku tylko, gdy nic nie jest otwarte (okno, paleta, pisanie) - inaczej czeka */
function scal(){
  if(!BAZA||POCZ===BAZA||LOT)return;
  if(zajety()){ODLOZ=true;return;}
  var L=roznice(POCZ,D);D=zastosuj(klon(BAZA),L);POCZ=BAZA;ODLOZ=false;
  if(S.sel&&!item(S.sel))S.sel=null;
  render(true);
  if(L.length){BRUD=true;planuj();}
}
setInterval(function(){if(ODLOZ)scal();},1500);
function przyjmij(st){BAZA=zStanu(st);lsSet(KL_KESZ,JSON.stringify(BAZA));}
var tSync;
function sync(stan,tx){
  var p=$('pasek');if(!p)return;p.className='demo '+stan;
  var t=new Date(),gg=('0'+t.getHours()).slice(-2)+':'+('0'+t.getMinutes()).slice(-2);
  $('syncTx').textContent=tx||(stan==='ok'?'Zapisane i aktualne · '+gg:stan==='zap'?'Zapisuję...':stan==='off'?'Brak internetu: tylko podgląd':stan==='blad'?'Nie zapisano ostatniej zmiany':'Łączenie...');
}
function api(akcja,dane){
  var body=Object.assign({akcja:akcja,token:TOK},dane||{}),ac=window.AbortController?new AbortController():null,tm=setTimeout(function(){if(ac)ac.abort();},30000);
  return fetch(API,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(body),redirect:'follow',cache:'no-store',credentials:'omit',signal:ac?ac.signal:undefined})
    .then(function(r){clearTimeout(tm);if(!r.ok)throw new Error('HTTP '+r.status);return r.json();})
    .then(function(j){if(j&&j.kod==='auth'&&akcja!=='katalog_login'){wyloguj(true);throw new Error('auth');}return j;},function(e){clearTimeout(tm);throw e;});
}
function bladSieci(e){var m=String(e&&e.message||e);return e&&(e.name==='TypeError'||e.name==='AbortError')||/^HTTP|Failed to fetch|NetworkError|Load failed/.test(m);}
function zapisz(){
  if(!BAZA)return;
  if(OFF){D=zastosuj(klon(POCZ),[]);toast('Brak internetu: zmiany są wyłączone, widzisz ostatni stan');setTimeout(function(){render(true);},0);return;}
  BRUD=true;planuj();
}
function planuj(){clearTimeout(tZap);sync('zap');tZap=setTimeout(wyslij,350);}
function wyslij(){
  if(LOT||!BAZA)return;
  var T=klon(D),ops=roznice(POCZ,T);BRUD=false;
  if(!ops.length){sync('ok');return;}
  LOT=T;sync('zap');
  api('katalog_zapisz',{ops:ops}).then(function(st){
    if(!st||!st.ok)throw new Error((st&&st.blad)||'Błąd zapisu');
    przyjmij(st);LOT=null;
    var poz=roznice(T,D);
    if(zajety()){POCZ=T;ODLOZ=true;}else{D=zastosuj(klon(BAZA),poz);POCZ=BAZA;render(true);}
    if(poz.length||BRUD){BRUD=false;planuj();}else sync('ok');
  }).catch(function(e){
    LOT=null;if(String(e.message)==='auth')return;
    D=zastosuj(klon(POCZ),roznice(T,D));render(true);sync('blad');
    toast((bladSieci(e)?'Brak połączenia':'Nie zapisano: '+e.message)+'. Zmiana cofnięta, spróbuj jeszcze raz.');
    if(bladSieci(e)){OFF=true;sync('off');}
  });
}
function pobierz(){
  if(!TOK)return Promise.resolve();
  if(LOT||BRUD)return Promise.resolve();
  if(!BAZA)sync('','Wczytuję dane...');
  return api('katalog_stan').then(function(st){
    if(!st||!st.ok)throw new Error((st&&st.blad)||'Błąd serwera');
    OFF=false;var stary=BAZA&&JSON.stringify(BAZA);przyjmij(st);
    if(!POCZ){POCZ=BAZA;D=klon(BAZA);render();}
    else if(stary!==JSON.stringify(BAZA))scal();
    sync('ok');
  }).catch(function(e){
    if(String(e.message)==='auth')return;
    if(bladSieci(e)){OFF=true;sync('off');if(!BAZA)$('view').innerHTML='<div class="ladow">Brak internetu i brak zapisanych danych.<br>Połącz się i odśwież.</div>';}
    else{sync('blad','Błąd serwera: '+e.message);}
  });
}
setInterval(function(){if(document.visibilityState==='visible')pobierz();},60000);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')pobierz();});
window.addEventListener('online',function(){pobierz();});
function wyloguj(auto){
  if(!auto&&TOK)api('katalog_wyloguj').catch(function(){});
  TOK='';lsSet(KL_TOK,null);lsSet(KL_KESZ,null);BAZA=null;POCZ=null;D=pusty();
  $('login').hidden=false;$('loginErr').textContent=auto?'Sesja wygasła. Zaloguj się ponownie.':'';
  try{$('haslo').value='';}catch(x){}
}

''')

# ------------------------------------------------------------------ nawigacja: wyloguj w panelu bocznym
R("""+'<button type="button" class="nv plus-s" data-act="szybki">'+ik('plus')+'Szybki wpis</button>';""",
  """+'<button type="button" class="nv plus-s" data-act="szybki">'+ik('plus')+'Szybki wpis</button><button type="button" class="wyl" data-act="wyloguj">Wyloguj</button>';""")

# ------------------------------------------------------------------ karta, szukaj, dziś, kalendarz: adres zamiast dzielnicy przykładowej
R("ad=q?hl(it.ds+', '+it.ul,q):esc(it.ds+', '+it.ul);", "ad=q?hl(adrTxt(it),q):esc(adrTxt(it));")
R("var hay=bezPl([it.kl,it.ul,it.ds,it.nr,it.em,it.nt,it.pod].join(' '));", "var hay=bezPl([it.kl,it.ul,it.ds,it.nr,it.em,it.nt,it.info].join(' '));")
R("""'<div class="chips" style="margin-top:8px">'+['Ostrowska','601','Mokotów','Puławska'].map(function(x){return '<button type="button" class="chip" data-act="przykl" data-q="'+x+'">'+x+'</button>';}).join('')+'</div></div>'+""",
  """'</div>'+""")
R("""<span class="x">'+esc(it.kl.split(' ').slice(-1)[0])+' <small>'+esc(it.ds)+(mm?' · '+mm+' m²':'')+'</small></span>""",
  """<span class="x">'+esc(String(it.kl||it.tel).split(' ').slice(-1)[0])+' <small>'+esc(adrKr(it))+(mm?' · '+mm+' m²':'')+'</small></span>""")
R("""'</b><span>'+esc(it.ds)+(mm?' · '+mm+' m²':'')+' · '+kwotaTxt(it)""", """'</b><span>'+esc(adrKr(it))+(mm?' · '+mm+' m²':'')+' · '+kwotaTxt(it)""")
R("""<span class="x">'+esc(x.o.kl)+' <small>'+esc(x.o.ds)+' · '+ST[x.o.st].n+'</small></span>""", """<span class="x">'+esc(x.o.kl)+' <small>'+esc(adrKr(x.o))+' · '+ST[x.o.st].n+'</small></span>""")
R("""'<option value="'+i.id+'">'+esc(i.kl)+' - '+esc(i.ds)+""", """'<option value="'+i.id+'">'+esc(i.kl||i.tel)+' - '+esc(adrKr(i))+""")
R("""var tx=e.k==='i'?e.o.kl.split(' ').slice(-1)[0]:e.o.x;""", """var tx=e.k==='i'?String(e.o.kl||e.o.tel).split(' ').slice(-1)[0]:e.o.x;""")
R("""toast(it.kl.split(' ').slice(-1)[0]+' → '+krotko(s));""", """toast(String(it.kl||it.tel).split(' ').slice(-1)[0]+' → '+krotko(s));""")
R("""h+='<button type="button" class="przew-lk" data-act="przew">Pokaż przewodnik jeszcze raz</button></div>';""",
  """h+='<button type="button" class="przew-lk" data-act="przew">Pokaż przewodnik jeszcze raz</button><button type="button" class="wyl" data-act="wyloguj">Wyloguj z tego urządzenia</button></div>';""")

# ------------------------------------------------------------------ karta zapytania
ZAMIEN('function detZapytanie(it){', 'function detDzien(s){', r'''function bezpLink(u,re){return re.test(String(u||''))?String(u):'';}
function detZapytanie(it){
  var T=TYPY[it.typ]||TYPY.w,q=[],d1=plus(DZIS,1),pn=pon(plus(DZIS,7)),reczne=it.typ==='r';
  q.push(['Dziś',DZIS_I],['Jutro',iso(d1)],[krotko(iso(pn)),iso(pn)]);
  var ark=bezpLink(it.arkusz,/^https:\/\/(docs|drive)\.google\.com\//),anl=bezpLink(it.analizator,/^https:\/\/(smartparkiet\.com\.pl|disaster26\.github\.io)\//);
  var mapa=String(it.ul||'').replace(/ m\. \d+/,'');if(mapa.indexOf(',')<0)mapa+=', Warszawa';
  var h='<div class="det-h"><button type="button" class="wst" data-act="zamknij">'+ik('wst')+'Wróć</button><span class="t">'+esc(it.nr||T.k)+' · '+kiedy(it.ts)+'</span></div><div class="det-b">';
  h+='<div class="hd"><span class="typ" style="--tc:'+T.c+'">'+T.n+'</span><h2>'+esc(it.kl||'Bez nazwiska')+'</h2><div class="adr">'+esc(adrTxt(it))+'</div>'+
    '<div class="kw"><b>'+kwotaTxt(it)+'</b><span>'+(it.kwota>0?'netto':'')+(m2(it)?(it.kwota>0?' · ':'')+m2(it)+' m²':'')+'</span></div></div>';
  h+='<div class="akcje">'+(it.tel?'<a class="tel" href="tel:+48'+cyfry(it.tel)+'">'+ik('tel')+'Zadzwoń</a>':'<button type="button" class="tel" style="opacity:.5" data-act="beztel">'+ik('tel')+'Brak tel.</button>')+
    '<a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(mapa)+'" target="_blank" rel="noopener noreferrer">'+ik('mapa')+'Mapa</a>'+
    (ark?'<button type="button" data-act="pdf" data-id="'+it.id+'">'+ik('pdf')+'PDF oferty</button>':'<button type="button" data-act="bezpdf" style="opacity:.55">'+ik('pdf')+'Brak PDF</button>')+
    '<button type="button" data-act="dane" data-id="'+it.id+'">'+ik('os')+'Dane klienta</button></div>';
  if(it.tel)h+='<div class="tel-n"><a href="tel:+48'+cyfry(it.tel)+'">'+esc(it.tel)+'</a></div>';
  h+='<div class="sek"><h3>Status</h3><div class="stg">'+STATUSY.map(function(x){return '<button type="button" style="--sc:'+x[2]+'" class="'+(it.st===x[0]?'on':'')+'" data-act="st" data-id="'+it.id+'" data-s="'+x[0]+'">'+x[1]+'</button>';}).join('')+'</div></div>';
  h+='<div class="sek"><h3>Termin w kalendarzu</h3>'+(it.dz?'<div class="term-info">'+ik('kal')+'<b>'+dlugo(it.dz)+(it.g?', '+esc(it.g):'')+'</b></div>':'')+
    '<div class="term"><input type="date" id="tDz" value="'+(it.dz||'')+'" aria-label="Dzień"><input type="time" id="tG" value="'+(it.g?('0'+it.g).slice(-5):'')+'" aria-label="Godzina"></div>'+
    '<div class="szyb">'+q.map(function(x){return '<button type="button" data-act="szybDz" data-id="'+it.id+'" data-d="'+x[1]+'">'+x[0]+'</button>';}).join('')+(it.dz?'<button type="button" class="usun" data-act="usunDz" data-id="'+it.id+'">Zdejmij z kalendarza</button>':'')+'</div></div>';
  h+='<div class="sek"><h3>Notatka <span class="ok" id="ntOk">zapisano</span></h3><textarea id="nt" data-id="'+it.id+'" placeholder="Np. klucze u sąsiada, kolor lakieru, kiedy oddzwonić..."'+(OFF?' readonly':'')+'>'+esc(it.nt)+'</textarea></div>';
  if(!reczne){
    var w=[['Kwota netto',it.kwota>0?zl(it.kwota):''],['Upust',it.upust?zl(Math.abs(it.upust)):''],['Metraż',m2(it)?m2(it)+' m²':''],['Zakres',(it.zakres||[]).join(', ')],
      ['Termin klienta',it.termin],['Informacje',it.info],['Nr zamówienia',it.nr]].filter(function(x){return x[1];});
    h+='<div class="sek"><h3>Wycena</h3>'+(w.length?'<dl class="dane">'+w.map(function(x){return '<dt>'+x[0]+'</dt><dd>'+esc(x[1])+'</dd>';}).join('')+'</dl>':'<div style="color:var(--ink3);font-size:14px">Brak szczegółów w Rejestrze.</div>')+
      ((ark||anl)?'<div class="linki">'+(ark?'<a href="'+esc(ark)+'" target="_blank" rel="noopener noreferrer">'+ik('lista')+'Arkusz wyceny</a>':'')+(anl?'<a href="'+esc(anl)+'" target="_blank" rel="noopener noreferrer">'+ik('pdf')+'Otwórz w analizatorze</a>':'')+'</div>':'')+'</div>';
  }
  var hs=(reczne?[]:[{ts:it.ts,x:T.k+': zapytanie wpadło do katalogu'}]).concat(it.hist||[]);
  h+='<div class="sek"><h3>Historia</h3><ul class="hist">'+hs.slice().reverse().map(function(x){return '<li><time>'+kiedy(x.ts)+'</time> · '+esc(x.x)+'</li>';}).join('')+'</ul></div>';
  return h+'</div>';
}
''')

# ------------------------------------------------------------------ okna PDF i dane klienta
ZAMIEN('function oknoPdf(it){', 'var ostatniDrag=0;', r'''function otworzPdf(it){
  var w=null;try{w=window.open('about:blank','_blank');}catch(x){}
  toast('Szukam PDF oferty...');
  api('katalog_pdf',{id:it.id}).then(function(r){
    var u=r&&r.ok?bezpLink(r.url,/^https:\/\/(docs|drive)\.google\.com\//):'';
    if(!u){if(w)w.close();toast((r&&r.blad)||'Nie znalazłem PDF');return;}
    if(w){try{w.opener=null;}catch(x){}w.location.href=u;}else location.href=u;
    if(r.brakPdf)toast('Nie znalazłem PDF, otwieram arkusz wyceny');
  }).catch(function(e){if(w)w.close();if(String(e.message)!=='auth')toast('Brak połączenia');});
}
function oknoDane(it){
  okno('<h3><span>Dane klienta</span><button type="button" class="zam" data-zam aria-label="Zamknij">'+ik('x')+'</button></h3>'+
  '<dl class="dane"><dt>Klient</dt><dd>'+esc(it.kl||'-')+'</dd><dt>Telefon</dt><dd>'+(it.tel?'<a href="tel:+48'+cyfry(it.tel)+'">'+esc(it.tel)+'</a>':'-')+'</dd><dt>Adres</dt><dd>'+esc(adrTxt(it)||'-')+'</dd>'+
  (it.em?'<dt>E-mail</dt><dd>'+esc(it.em)+'</dd>':'')+(m2(it)?'<dt>Metraż</dt><dd>'+m2(it)+' m²</dd>':'')+(it.info?'<dt>Informacje</dt><dd>'+esc(it.info)+'</dd>':'')+
  '<dt>Źródło</dt><dd>'+(TYPY[it.typ]||TYPY.w).n+'</dd>'+(it.nr?'<dt>Nr zamówienia</dt><dd>'+esc(it.nr)+'</dd>':'')+'</dl>'+
  '<button type="button" class="btn-p pom" data-act="kopiuj" data-id="'+it.id+'">'+ik('kop')+'Kopiuj dane</button>');
}

''')
R("""    case 'pdf':oknoPdf(item(id));break;""", """    case 'pdf':otworzPdf(item(id));break;\n    case 'beztel':toast('Brak numeru telefonu');break;\n    case 'wyloguj':if(confirm('Wylogować z tego urządzenia?'))wyloguj(false);break;""")
R("""    case 'bezpdf':toast('Dopisane z ręki - bez oferty PDF');break;""", """    case 'bezpdf':toast('To zapytanie nie ma oferty PDF');break;""")
R("""    case 'druk':window.print();break;\n""", "")
R("""tx=i3.kl+'\\n'+i3.tel+'\\n'+i3.ul+', '+i3.ds+', Warszawa'+(i3.em?'\\n'+i3.em:'');""", """tx=[i3.kl,i3.tel,adrTxt(i3),i3.em].filter(Boolean).join('\\n');""")

# ------------------------------------------------------------------ wpis z ręki
R("""      var nz={id:'z'+Date.now(),typ:'r',ts:Date.now(),nr:'R/'+DZIS.getFullYear()+'/'+('0'+(DZIS.getMonth()+1)).slice(-2)+'/'+('00'+(D.items.filter(function(i){return i.typ==='r';}).length+5)).slice(-3),
        kl:kl||'Bez nazwiska',tel:tl,ul:ul||'adres do uzupełnienia',ds:ds||'Warszawa',pod:'do ustalenia',em:'',pz:[],m2:parseInt($('sM2').value,10)||0,st:'rozmowa',nt:$('sNt').value.trim(),dz:$('sDz').value||null,g:'',hist:[{ts:Date.now(),x:'Dopisane z ręki'}],widz:true};""",
  """      var nz={id:'r'+Date.now().toString(36)+Math.random().toString(36).slice(2,6),typ:'r',reczne:true,ts:Date.now(),nr:'',
        kl:kl||'Bez nazwiska',tel:tl,ul:ul||'adres do uzupełnienia',ds:ds,em:'',m2:parseInt($('sM2').value,10)||0,kwota:0,zakres:[],info:'',st:'rozmowa',nt:$('sNt').value.trim(),dz:$('sDz').value||null,g:'',hist:[{ts:Date.now(),x:'Dopisane z ręki'}],widz:true};""")
R("""    case 'reset':if(confirm('Przywrócić przykładowe dane? Twoje zmiany w podglądzie znikną.')){try{localStorage.removeItem(KLUCZ);}catch(x){}D=seed();D.graf=seedGraf();D.wpisy=D.wpisy.concat(seedSprawy());zapisz();S.sel=null;S.dzien=null;S.wyb=null;S.gwyb=null;render();toast('Przywrócono dane przykładowe');}break;\n""", "")

# ------------------------------------------------------------------ grafik: bez danych przykładowych, rodzaj z zakresu wyceny
ZAMIEN('function seedKol(){', 'function kaf(id){', '''S.gd=DZIS;S.gwyb=null;

''')
ZAMIEN('function rodzajZ(it){', 'function naGrafikuZ(id){', '''function rodzajZ(it){return (it.zakres||[]).join(' + ').toUpperCase();}
''')
R("""  var mm=m2(it),ul=it.ul.replace(/^(ul\\.|al\\.|os\\.|pl\\.)\\s*/i,''),mi='',mt=ul.match(/\\s+m\\.\\s*(\\S+)$/i);
  if(mt){mi=mt[1];ul=ul.slice(0,mt.index);}""",
  """  var mm=m2(it),cz=String(it.ul||'').split(','),ul=cz[0].trim().replace(/^(ul\\.|al\\.|os\\.|pl\\.)\\s*/i,''),mi='',mt=ul.match(/(?:\\s*\\/\\s*|\\s+m\\.\\s*)([0-9A-Za-z]+)$/i);
  if(mt){mi=mt[1];ul=ul.slice(0,mt.index);}
  var miasto=cz.length>1?cz[cz.length-1].replace(/\\d{2}-\\d{3}/,'').trim():'';if(miasto&&!/^warszawa$/i.test(miasto))ul+=' '+miasto;""")
R("""info:(it.ds+', '+rodzajZ(it)).toUpperCase(),""", """info:[it.ds,rodzajZ(it)].filter(Boolean).join(', ').toUpperCase(),""")
R("""<span>'+esc(i.kl)+' <small>'+esc(i.ds)+(mm?' · '+mm+' m²':'')+' · '+TYPY[i.typ].k+'</small></span>""",
  """<span>'+esc(i.kl||i.tel)+' <small>'+esc(adrKr(i))+(mm?' · '+mm+' m²':'')+' · '+(TYPY[i.typ]||TYPY.w).k+'</small></span>""")
R("""wn=nm[0]==='i'?(item(nm[1])||{}).kl:""", """wn=nm[0]==='i'?(item(nm[1])||{}).kl||(item(nm[1])||{}).tel:""")

# ------------------------------------------------------------------ logowanie i start
ZAMIEN('/* ---------- logowanie ---------- */', '})();\n</script>', r'''/* ---------- logowanie i start ---------- */
var przew=lsGet('spk-katalog-przew')==='1';
$('loginForm').addEventListener('submit',function(e){
  e.preventDefault();var h=$('haslo').value,b=$('loginBtn');if(!h)return;
  b.disabled=true;b.textContent='Sprawdzam...';$('loginErr').textContent='';
  api('katalog_login',{haslo:h}).then(function(r){
    if(!r||!r.ok)throw new Error((r&&r.blad)||'Nie udało się zalogować');
    TOK=r.token;lsSet(KL_TOK,TOK);$('haslo').value='';$('login').hidden=true;
    return pobierz().then(function(){if(!przew&&BAZA){przew=true;przewodnik(true);}});
  }).catch(function(x){$('loginErr').textContent=bladSieci(x)?'Brak połączenia z serwerem. Sprawdź internet.':x.message;})
  .then(function(){b.disabled=false;b.textContent='Zaloguj';});
});
DESK.addEventListener&&DESK.addEventListener('change',function(){render(true);});
if(!TOK){$('login').hidden=false;sync('','Zaloguj się');}
render();
if(TOK){if(!BAZA)$('view').innerHTML='<div class="ladow">Wczytuję zapytania...</div>';pobierz();}
if('serviceWorker' in navigator&&location.protocol!=='file:'){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}
window.spkApp={stan:function(){return {D:D,BAZA:BAZA,POCZ:POCZ,LOT:!!LOT,BRUD:BRUD,OFF:OFF};},pobierz:pobierz};
''')

# przewodnik: pierwszy krok mowi o zapytaniach z wycen
R("x:'Wyceny z analizatora, wyceny klientów ze strony i zamówienia z koszyka wpadają same, z oznaczeniem NOWE, źródłem i godziną. Klient zadzwonił? Przycisk z plusem i dopisujesz z ręki.'",
  "x:'Wyceny z analizatora, wyceny klientów ze strony i zamówienia z koszyka wpadają same (z Rejestru wycen), z oznaczeniem NOWE, źródłem i godziną. Klient zadzwonił? Przycisk z plusem i dopisujesz z ręki.'")
R("x:'Stukasz zapytanie, otwiera się karta. Status zmieniasz jednym kliknięciem, niżej termin, notatka, PDF oferty i dane klienta.'",
  "x:'Stukasz zapytanie, otwiera się karta. Status zmieniasz jednym kliknięciem, niżej termin, notatka, PDF oferty, arkusz wyceny i dane klienta. Wszystko zapisuje się samo i widać to też na komputerze.'")

s = s.replace('__API__', API_PROD)

# kontrola: nic z danych przykladowych nie zostalo
for zakazane in ('seed(', 'SEED', 'WPISY_SEED', 'seedGraf', 'seedSprawy', 'migrujGraf', 'Podgląd</b>', 'spk-katalog-podglad', '.pz', 'suma(', 'it.pod', 'oknoPdf'):
    assert zakazane not in s, 'zostal fragment makiety: ' + zakazane

os.makedirs(os.path.dirname(CEL), exist_ok=True)
open(CEL, 'w', encoding='utf-8', newline='\n').write(s)
print('OK', CEL, len(s.encode('utf-8')) // 1024, 'KB')
