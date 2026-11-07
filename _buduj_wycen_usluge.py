# -*- coding: utf-8 -*-
"""wycen-usluge.html = "Wyceń usługę" - uproszczone narzedzie wewnetrzne parkieciarza (Artur 06.11 15:44-16:28, 07.11).

Budowany z analizator.html (ten sam silnik wycena.html: bramka PIN z serwera, PDF, Folder ofert, Zapisz, mail /wyslij.php,
Apps Script). Skorka NIE zmienia logiki - przenosi istniejace pola (te same id) do:
  1. listy uslug: przycisk z nazwa uslugi, po nacisnieciu rozwija sie pole ilosci (m2, mb, kwota) - "robimy" = kratka uzgN
     z panelu "Zakres prac", wiec PDF, mail, arkusz i Folder ofert dostaja dokladnie te same pola co z analizatora,
  2. prostej sekcji "Dane klienta: adres, telefon, e-mail" (reszta pol w zwinietym "Zdjecia, termin, szczegoly"),
  3. dolnego paska: kwota netto + Zapisz + PDF + Wyslij.
Wersja 06.11 (kafelki z przelacznikami i zakladka "Usluga z cennika") zastapiona 07.11 - Artur: "za duzo zawijasow".

Od 07.11 w paczce produkcyjnej (build.py: noindex, poza sitemap). Uruchomienie: python _buduj_wycen_usluge.py
(po _buduj_analizator.py; build.py wywoluje oba)."""
import os, re
TU = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(TU, 'analizator.html'), encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in s else '\n'


def zamien(stare, nowe):
    global s
    if stare not in s:
        raise SystemExit('Nie znaleziono: ' + stare[:80])
    s = s.replace(stare, nowe, 1)


zamien('<title>SMARTPARKIET Analizator</title>', '<title>Wyceń usługę | SMARTPARKIET</title>')
zamien('<meta name="apple-mobile-web-app-title" content="Analizator">', '<meta name="apple-mobile-web-app-title" content="Wyceń usługę">')
# klasa od razu (przed skryptami analizatora) - analizator nie dokleja wtedy linku "Prosty widok" do samego siebie
m = re.search(r'<meta name="viewport"[^>]*>', s)
s = s[:m.end()] + NL + "<script>document.documentElement.classList.add('wu-strona')</script>" + s[m.end():]

SKORKA = r'''<!-- wycen-usluge START -->
<style id="wycen-usluge-0711">
html.wu #wycena .sticky>*:not(h2):not(.oczko):not(.an-przel){display:none!important}
html.wu #wycena .sticky h2{margin:0!important}
html.wu #wycena .split{gap:14px!important}
html.wu form.ai-form>*:not(#wu),html.wu #aiPhoto,html.wu #aiOut,html.wu #wycena .ai>.drop,html.wu #wycena .ai>.miniatury,html.wu .cta-bar,html.wu #spTabBtn,html.wu #spDok,html.wu #zapiszBtn,html.wu #szkicInfo,html.wu .wu-up .maly-info{display:none!important}
html.wu #wycena .ai-form{display:block!important;padding:14px 12px!important}
html.wu #wycena .ai{padding:0!important;overflow:visible!important}
html.wu body{padding-bottom:96px}
#wu{font-family:Inter,system-ui,sans-serif}
#wu *{box-sizing:border-box}
.wu-h{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:18px 2px 8px;font:800 1.05rem/1.2 Inter,system-ui,sans-serif;color:#14110E}
.wu-h:first-child{margin-top:4px}
.wu-h small{font:600 .8rem/1.2 Manrope,system-ui,sans-serif;color:#6B7076}
/* uslugi */
.wu-u{border:1.5px solid #E1E3E6;border-radius:14px;background:#fff;margin:0 0 8px;scroll-margin-top:84px}
#wycena #wu button.wu-ut{all:unset;box-sizing:border-box;display:grid;grid-template-columns:40px 1fr auto;align-items:center;gap:12px;width:100%;min-height:62px;padding:10px 12px;cursor:pointer;-webkit-tap-highlight-color:transparent}
.wu-ik{width:40px;height:40px;border-radius:11px;background:#FFF1E6;color:#FF6A13;display:grid;place-items:center}
.wu-ik svg{width:23px;height:23px}
.wu-un{min-width:0;font:800 1rem/1.2 Inter,system-ui,sans-serif;color:#14110E}
.wu-un small{display:block;margin-top:2px;font:600 .8rem/1.25 Manrope,system-ui,sans-serif;color:#6B7076}
.wu-uk{font:800 .95rem Inter,system-ui,sans-serif;color:#14110E;white-space:nowrap;text-align:right}
.wu-plus{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#FF6A13;color:#fff;font:700 1.4rem/1 Inter,system-ui,sans-serif}
.wu-u.tak{border-color:#FF6A13;background:#FFF8F2}
.wu-u.tak .wu-ik{background:#FF6A13;color:#fff}
.wu-u.tak .wu-un small{color:#B03C0A;font-weight:800}
.wu-u.otw{border-color:#FF6A13;box-shadow:0 6px 20px rgba(255,106,19,.14)}
.wu-up{display:none;padding:2px 12px 12px}
.wu-u.otw .wu-up{display:block}
.wu-up>div,.wu-up>label.drop,.wu-up>.miniatury{margin-bottom:10px}
.wu-up input,.wu-up select{font-size:16px!important}
.wu-u:not(.ceny) .wu-up [id^="cw_"]{display:none!important}
.wu-info{font:600 .88rem/1.45 Manrope,system-ui,sans-serif;color:#4A5058;margin:0 0 10px}
.wu-wiersz{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#wycena #wu .wu-wiersz button{width:auto;min-height:44px;margin:0;border-radius:11px;padding:10px 14px;font:800 .9rem Inter,system-ui,sans-serif;cursor:pointer}
#wycena #wu .wu-gotowe{flex:1;border:0;background:#14110E;color:#fff}
#wycena #wu .wu-usun{border:1.5px solid #E1E3E6;background:#fff;color:#B23B1E}
#wycena #wu .wu-dodaj{flex:1;border:0;background:#FF6A13;color:#fff}
#wycena #wu .wu-cena{border:0;background:none;color:#4A5058;text-decoration:underline;padding:10px 4px;font-weight:700}
/* dane klienta */
.wu-dane{border:1.5px solid #E1E3E6;border-radius:14px;background:#fff;padding:12px 12px 2px}
.wu-dane>div{margin-bottom:10px}
.wu-dane input{font-size:16px!important}
details.wu-wiecej{border:1.5px dashed #C9CDD2;border-radius:14px;background:#fff;margin:8px 0 0}
details.wu-wiecej>summary{list-style:none;cursor:pointer;padding:14px 12px;font:800 .95rem Inter,system-ui,sans-serif;color:#14110E;display:flex;justify-content:space-between;gap:8px}
details.wu-wiecej>summary::-webkit-details-marker{display:none}
details.wu-wiecej>summary::after{content:"+";color:#FF6A13;font-size:1.3rem;line-height:1}
details.wu-wiecej[open]>summary::after{content:"−"}
details.wu-wiecej>summary small{display:block;font:600 .8rem Manrope,system-ui,sans-serif;color:#6B7076;margin-top:2px}
.wu-wiecej-in{padding:0 12px 4px}
.wu-wiecej-in>*{margin-bottom:10px}
/* folder ofert */
#wycena #wu button.wu-fol{all:unset;box-sizing:border-box;display:grid;grid-template-columns:40px 1fr auto;align-items:center;gap:12px;width:100%;padding:10px 12px;border-radius:14px;background:#14110E;color:#fff;cursor:pointer}
.wu-fol .wu-ik{background:#2E3136;color:#FF8A4C}
.wu-fol b{font:800 1rem/1.2 Inter,system-ui,sans-serif}
.wu-fol small{display:block;font:600 .8rem/1.25 Manrope,system-ui,sans-serif;color:#B9BDC3}
.wu-fol i{font-style:normal;font:800 .78rem Inter,system-ui,sans-serif;background:#1F7A4D;color:#fff;border-radius:999px;padding:4px 9px}
.wu-fol i:empty{display:none}
.wu-folp{display:none;margin:8px 0 0}
.wu-folp.otw{display:block}
.wu-folp .sms-box{margin:0!important}
html.wu .sms-box textarea#smsWklej{height:110px!important;min-height:0!important}
.wu-koniec{margin:16px 0 0}
.wu-koniec #wyslij{width:100%}
/* dolny pasek */
#wuBar{position:fixed;left:0;right:0;bottom:0;z-index:70;display:grid;grid-template-columns:minmax(0,1fr) auto auto auto;gap:6px;align-items:center;padding:8px 10px calc(8px + env(safe-area-inset-bottom));background:#14110E;color:#fff;box-shadow:0 -6px 20px rgba(0,0,0,.18)}
#wuBar small{display:block;font:700 .66rem Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#B9BDC3}
#wuBar b{display:block;font:800 1.12rem Inter,system-ui,sans-serif;color:#FF6A13;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#wuBar button{border:0;border-radius:11px;min-height:46px;padding:0 11px;font:800 .86rem Inter,system-ui,sans-serif;cursor:pointer;white-space:nowrap}
#wuBar .zap{background:#fff;color:#14110E}
#wuBar .pdf{background:#3A3F45;color:#fff}
#wuBar .wys{background:#FF6A13;color:#fff}
#wuBar button:disabled{opacity:.6}
#wuInfo{position:fixed;left:10px;right:10px;bottom:calc(72px + env(safe-area-inset-bottom));z-index:71;padding:12px 14px;border-radius:12px;font:700 .9rem/1.4 Manrope,system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.2);background:#14110E;color:#fff}
#wuInfo[hidden]{display:none}
#wuInfo.ok{background:#1F7A4D}#wuInfo.lok{background:#8A5A00}
@media(max-width:370px){#wuBar button{padding:0 8px;font-size:.8rem}#wuBar b{font-size:1rem}}
@media(min-width:720px){#wuBar{left:50%;right:auto;transform:translateX(-50%);width:min(720px,100%);border-radius:16px 16px 0 0}#wuInfo{left:50%;right:auto;transform:translateX(-50%);width:min(700px,100%)}}
</style>
<script id="wycen-usluge-0711s">
(function(){
 var SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
 var IK={
  pod:'<path d="M3 17h18M3 13h18M7 13v4M12 13v4M17 13v4M3 9l9-5 9 5"/>',
  lw:'<path d="M3 18h18M3 14h18v4H3zM7 10l3-3 3 3M10 7v7"/>',
  lo:'<path d="M3 16h18v4H3zM12 3v3M12 9v2M6.5 5.5l1.5 1.5M17.5 5.5 16 7"/>',
  na:'<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
  st:'<path d="M4 20h16M6 16h12M9 16V9h6v7M12 3v6"/>',
  ko:'<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
  do:'<path d="M12 5v14M5 12h14"/>',
  me:'<path d="M4 18v-6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6M4 15h16M6 18v2M18 18v2M7 10V7a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3"/>',
  sc:'<path d="M3 20h5v-4h4v-4h4V8h5"/>',
  fol:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'};
 /* uslugi: uz = kratka "Zakres prac" (uzgN), q = nazwa pozycji w arkuszu (p[6]), il = pole ilosci (fokus po rozwinieciu),
    f = pola przenoszone do panelu uslugi, r = radio tak/nie silnika (ustawiane samo) */
 var K=[
  {id:'pod',t:'Cyklinowanie / odnowienie podłogi',j:'m²',uz:0,q:'Renowacja parkietu',il:'m2',f:['m2','typ','wyk']},
  {id:'lw',t:'Wymiana listew',j:'mb',uz:1,q:'Wymiana listew',r:'listwy',il:'listwyMb',f:['listwyMb','@listwy']},
  {id:'lo',t:'Odświeżenie listew',j:'kpl.',uz:7,q:'Odświeżenie listew',info:'Pozycja 1 kpl., cena do uzgodnienia. Znasz kwotę? Dopisz ją w Pracach dodatkowych.'},
  {id:'st',t:'Stabilizacja',j:'m²',uz:2,q:'Stabilizacja',r:'stab',il:'stabM2',f:['stabM2']},
  {id:'na',t:'Naprawa',j:'ilość i kwota',uz:3,q:'Naprawy',r:'napr',il:'naprIl',f:['naprBlok']},
  {id:'ko',t:'Koloryzacja',j:'od metrażu podłogi',uz:4,q:'Koloryzacja',kolor:1,info:'Liczy się od metrażu z pozycji Cyklinowanie.',f:['cw_kolor']},
  {id:'me',t:'Pomoc z meblami',j:'kwota zł',uz:5,q:'Przesunięcie mebli',r:'meble',il:'mebleKw',f:['mebleKw']},
  {id:'sc',t:'Renowacja schodów',j:'kpl.',uz:6,q:'Renowacja schodów',info:'Pozycja 1 kpl., cena do uzgodnienia po wizji lokalnej.'},
  {id:'do',t:'Prace dodatkowe',j:'własna pozycja z ceną',dod:1,f:['dodBlok']}];
 var $=function(i){return document.getElementById(i);};
 var zl=function(n){return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g,' ')+' zł';};
 function ev(e,t){e.dispatchEvent(new Event(t,{bubbles:true}));}
 function blok(f){if(f.charAt(0)==='@'){var r=document.querySelector('form.ai-form input[name="'+f.slice(1)+'"]');return r&&r.closest('form.ai-form>*');}
  var e=$(f);if(!e)return null;if(/^(cw_|drop$|miniatury$)/.test(f))return e;return e.closest('form.ai-form>*')||e;}
 function radio(n,ktory){var rs=[].slice.call(document.querySelectorAll('input[name="'+n+'"]'));
  var x=rs.filter(function(r){var t=(r.closest('label')||{}).textContent||'';return ktory==='tak'?(n==='meble'?t.trim()==='tak':r.value!=='nie'):(n==='meble'?t.trim()==='nie':r.value==='nie');})[0];
  if(n==='listwy'&&ktory==='tak'){var cur=rs.filter(function(r){return r.checked;})[0];if(cur&&cur.value!=='nie')return;x=rs.filter(function(r){return r.value==='klasyczna';})[0];}
  if((n==='stab'||n==='napr')&&ktory==='tak')x=rs.filter(function(r){return r.value==='tak';})[0];
  if(x&&!x.checked){x.checked=true;ev(x,'change');ev(x,'input');}}
 function ustaw(k,v){if(k.uz!=null){var c=$('uzg'+k.uz);if(c&&c.checked!==v){c.checked=v;ev(c,'change');}}
  if(k.r)radio(k.r,v?'tak':'nie');
  if(k.kolor){var w=$('wyk');if(w&&(w.selectedIndex===4)!==v){w.selectedIndex=v?4:0;ev(w,'change');}}
  if(k.dod){if(v&&!document.querySelector('#dodLista .dod-w')){var p=$('dodPlus');p&&p.click();}
   [].forEach.call(document.querySelectorAll('#dodLista .dod-w'),function(w){var u=w.querySelector('.dod-u');if(u&&u.checked!==v&&(!v||(w.querySelector('.dod-o')||{}).value)){u.checked=v;ev(u,'change');}});}
  odswiez();}
 function jest(k){if(k.uz!=null){var c=$('uzg'+k.uz);return !!(c&&c.checked);}
  if(k.dod)return [].some.call(document.querySelectorAll('#dodLista .dod-o'),function(o){return o.value.trim();});return false;}
 function kwota(k){var A;try{A=window.spArkusz&&window.spArkusz();}catch(e){}if(!A)return '';
  var P=A.poz.filter(function(p){return k.dod?(p.length<6&&!/^\*/.test(p[0])):(p[6]===k.q||(k.id==='pod'&&/^\*/.test(p[0])));});
  var s=0,uzg=false;P.forEach(function(p){if(typeof p[1]==='number'&&p[2])s+=p[1]*p[2];else if(p[1]&&p[1]!==0)uzg=true;});
  return s>0?zl(s):(uzg?'do uzg.':'');}
 function ilosc(k){var e=k.il&&$(k.il);var v=e?String(e.value||'').trim():'';return v&&parseFloat(v.replace(',','.'))>0?v.replace('.',',')+' '+(k.j==='kwota zł'?'zł':k.j.split(' ')[0]):'';}
 /* pola przeniesione z form.ai-form nie sa juz jego dziecmi - kopia regul ".ai-form > ..." dla nowych kontenerow */
 function kopiujCss(){var out=[];function przejdz(R,med){[].forEach.call(R,function(r){
   if(r.cssRules&&r.media){przejdz(r.cssRules,r.media.mediaText);return;}
   if(!r.selectorText||!/ai-form\s*>/.test(r.selectorText))return;
   var sel=r.selectorText.split(',').filter(function(x){return /ai-form\s*>/.test(x)&&!/html\.wu|#wu/.test(x);}).map(function(x){return ['.wu-up','.wu-dane','.wu-wiecej-in'].map(function(c){return x.replace(/ai-form\s*>/g,'ai-form '+c+' >');}).join(',');}).join(',');
   if(!sel)return;var t=sel+'{'+r.style.cssText+'}';out.push(med?'@media '+med+'{'+t+'}':t);});}
  [].forEach.call(document.styleSheets,function(sh){try{przejdz(sh.cssRules,'');}catch(e){}});
  var st=document.createElement('style');st.id='wu-css-kopia';st.textContent=out.join('\n');document.body.appendChild(st);}
 function etykieta(id,t){var e=$(id),l=e&&document.querySelector('label[for="'+id+'"]');if(l)l.textContent=t;}
 var info=null,infoT=0;
 function pokazInfo(t,kl){if(!info)return;info.textContent=t;info.className=kl||'';info.hidden=false;clearTimeout(infoT);
  if(kl==='ok'||kl==='lok')infoT=setTimeout(function(){info.hidden=true;},kl==='ok'?6000:12000);}
 function zbuduj(){
  var form=document.querySelector('form.ai-form');if(!form||$('wu'))return;
  kopiujCss();
  document.documentElement.classList.add('wu');
  var h=document.querySelector('#wycena .sticky h2');if(h)h.textContent='Wyceń usługę';
  var oc=document.querySelector('#wycena .sticky .oczko');if(oc&&oc.lastChild)oc.lastChild.textContent='SMARTPARKIET · narzędzie parkieciarza';
  var st=document.querySelector('#wycena .sticky');if(st&&!st.querySelector('.an-przel')){var a=document.createElement('a');a.className='an-przel';a.href='analizator.html';a.textContent='Pełny Analizator ›';st.appendChild(a);}
  var wu=document.createElement('div');wu.id='wu';
  wu.innerHTML='<button type="button" class="wu-fol" id="wuFolB" aria-expanded="false"><span class="wu-ik">'+SVG+IK.fol+'</svg></span><span><b>Zapisane wyceny</b><small>Folder ofert - szukaj po adresie lub telefonie</small></span><i id="wuFolN"></i></button><div class="wu-folp" id="wuFolP"></div>'+
   '<p class="wu-h">Usługi <small>naciśnij i wpisz ilość</small></p><div id="wuL"></div>'+
   '<p class="wu-h">Dane klienta <small>adres, telefon, e-mail</small></p><div class="wu-dane" id="wuD"></div>'+
   '<details class="wu-wiecej" id="wuW"><summary><span>Zdjęcia, termin, szczegóły<small>opcjonalnie</small></span></summary><div class="wu-wiecej-in" id="wuWi"></div></details>'+
   '<div class="wu-koniec" id="wuKon"></div>';
  form.insertBefore(wu,form.firstChild);
  /* folder ofert + SMS (zwiniete) */
  var sb=form.querySelector('.sms-box');if(sb)$('wuFolP').appendChild(sb);
  $('wuFolB').onclick=function(){var p=$('wuFolP'),o=!p.classList.contains('otw');p.classList.toggle('otw',o);this.setAttribute('aria-expanded',o?'true':'false');
   if(o){var s=$('folSzuk');if(s)ev(s,'focus');}};
  /* uslugi */
  var L=$('wuL');
  K.forEach(function(k){var d=document.createElement('div');d.className='wu-u';d.id='wu_'+k.id;
   d.innerHTML='<button type="button" class="wu-ut" aria-expanded="false"><span class="wu-ik">'+SVG+IK[k.id]+'</svg></span><span class="wu-un">'+k.t+'<small>'+k.j+'</small></span><span class="wu-uk"><span class="wu-plus" aria-hidden="true">+</span></span></button><div class="wu-up"></div>';
   var P=d.querySelector('.wu-up');
   if(k.info){var i=document.createElement('p');i.className='wu-info';i.textContent=k.info;P.appendChild(i);}
   (k.f||[]).forEach(function(f){var b=blok(f);if(b)P.appendChild(b);});
   var w=document.createElement('div');w.className='wu-wiersz';
   w.innerHTML=(k.il||k.dod?'<button type="button" class="wu-gotowe">Gotowe</button>':'<button type="button" class="wu-dodaj">Dodaj do wyceny</button>')+'<button type="button" class="wu-usun">Usuń z wyceny</button>'+(P.querySelector('[id^="cw_"]')?'<button type="button" class="wu-cena">Zmień cenę</button>':'');
   P.appendChild(w);
   var zwin=function(){d.classList.remove('otw');d.querySelector('.wu-ut').setAttribute('aria-expanded','false');};
   var g=w.querySelector('.wu-gotowe');if(g)g.onclick=zwin;
   var dd=w.querySelector('.wu-dodaj');if(dd)dd.onclick=function(){ustaw(k,!jest(k));if(jest(k))zwin();};
   w.querySelector('.wu-usun').onclick=function(){ustaw(k,false);zwin();};
   var ce=w.querySelector('.wu-cena');if(ce)ce.onclick=function(){d.classList.toggle('ceny');ce.textContent=d.classList.contains('ceny')?'Ukryj cenę':'Zmień cenę';};
   /* wpisana ilosc = automatycznie "robimy" */
   P.addEventListener('input',function(e){var dw=e.target.closest&&e.target.closest('.dod-w');
    if(dw){var u=dw.querySelector('.dod-u');if(u&&!u.checked&&(dw.querySelector('.dod-o')||{}).value){u.checked=true;ev(u,'change');}}
    var v=parseFloat(String(e.target.value||'').replace(',','.'));
    if(((e.target.type==='number'||e.target.inputMode==='decimal')&&v>0)||(e.target.classList&&e.target.classList.contains('dod-o')&&e.target.value.trim())){if(!jest(k))ustaw(k,true);}
    odswiez();});
   /* nacisniecie uslugi = dodanie do wyceny i rozwiniecie pola ilosci (Artur 06.11 15:55) */
   d.querySelector('.wu-ut').onclick=function(){var o=!d.classList.contains('otw');
    [].forEach.call(L.querySelectorAll('.wu-u.otw'),function(x){x.classList.remove('otw');x.querySelector('.wu-ut').setAttribute('aria-expanded','false');});
    if(!o)return;
    if((k.il||k.dod)&&!jest(k))ustaw(k,true);
    d.classList.add('otw');this.setAttribute('aria-expanded','true');
    setTimeout(function(){d.scrollIntoView({block:'start',behavior:'smooth'});var q=k.il&&$(k.il);if(!q&&k.dod)q=d.querySelector('.dod-o');
     if(q&&!q.disabled&&!String(q.value||'').trim()){try{q.focus({preventScroll:true});}catch(e){}}},80);};
   k.el=d;L.appendChild(d);});
  /* dane klienta - tylko adres, telefon, e-mail (Artur 06.11 16:0x) */
  var D=$('wuD');['ulicaKl','telKl','mailKl'].forEach(function(f){var b=blok(f);if(b)D.appendChild(b);});
  etykieta('ulicaKl','Adres (ulica i numer)');etykieta('telKl','Telefon');etykieta('mailKl','E-mail');
  var W=$('wuWi');['drop','miniatury','terminKl','kodKl','miastoKl','dzielKl','pietroKl','@winda','imieKl','obiektKl','gatKl','montazKl','vatBlok','kopiaBlok'].forEach(function(f){var b=blok(f);if(b)W.appendChild(b);});
  /* koniec formularza: blad + glowny przycisk Wyslij (pokazuje tez "WYSLANE!") */
  var kon=$('wuKon');['bladForm','wyslij'].forEach(function(f){var e=$(f);if(e)kon.appendChild(e);});
  var bw=$('wyslij');if(bw&&!bw.disabled){[].forEach.call(bw.childNodes,function(n){if(n.nodeType===3&&n.textContent.trim())n.textContent=' Wyślij wycenę';});bw.dataset.oryg=bw.innerHTML;}
  /* dolny pasek: kwota + Zapisz + PDF + Wyslij */
  var bar=document.createElement('div');bar.id='wuBar';
  bar.innerHTML='<div style="min-width:0"><small>Netto</small><b id="wuSum">0 zł</b></div><button type="button" class="zap">Zapisz</button><button type="button" class="pdf">PDF</button><button type="button" class="wys">Wyślij</button>';
  document.body.appendChild(bar);
  info=document.createElement('div');info.id='wuInfo';info.hidden=true;info.setAttribute('role','status');document.body.appendChild(info);
  info.onclick=function(){info.hidden=true;};
  window.spSzkicInfo=pokazInfo;
  var bz=bar.querySelector('.zap');bz.onclick=function(){if(!window.spZapiszSzkic)return;bz.disabled=true;
   window.spZapiszSzkic().finally(function(){bz.disabled=false;});};
  bar.querySelector('.pdf').onclick=function(){var b=$('podgladOferty');b&&b.click();};
  bar.querySelector('.wys').onclick=function(){var b=$('wyslij');if(b){b.scrollIntoView({block:'center',behavior:'smooth'});if(!b.disabled)b.click();}};
  odswiez();setInterval(odswiez,800);}
 function odswiez(){K.forEach(function(k){if(!k.el)return;var t=jest(k);k.el.classList.toggle('tak',t);
   var kw=t?kwota(k):'',il=t?ilosc(k):'';
   k.el.querySelector('.wu-un small').textContent=t?('✓ '+(il||'w wycenie')):k.j;
   var u=k.el.querySelector('.wu-uk');var html=t?(kw||'✓'):'<span class="wu-plus" aria-hidden="true">+</span>';if(u.__h!==html){u.innerHTML=html;u.__h=html;}});
  var A;try{A=window.spArkusz&&window.spArkusz();}catch(e){}var e=$('wuSum');if(e&&A)e.textContent=zl(A.suma||0);
  var n=document.querySelectorAll('#folWyn button.fw-sz').length,fn=$('wuFolN');if(fn)fn.textContent=n?String(n):'';}
 window.spWuOdswiez=odswiez;
 function start(){setTimeout(zbuduj,700);}
 if(document.readyState==='complete')start();else window.addEventListener('load',start);
})();
</script>
<!-- wycen-usluge KONIEC -->'''
s = s.rstrip() + NL + SKORKA.replace('\n', NL) + NL
open(os.path.join(TU, 'wycen-usluge.html'), 'w', encoding='utf-8', newline='').write(s)
print('wycen-usluge.html gotowy', len(s), 'znakow')
