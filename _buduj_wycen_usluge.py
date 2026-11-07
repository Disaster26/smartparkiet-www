# -*- coding: utf-8 -*-
"""PROSTY WIDOK wyceny (Artur 06-07.11) - jeden blok skorki dla dwoch stron:

1. wycena.html (KALKULATOR - wyceń samodzielnie, klient): od 07.11 wieczor od razu prosty widok - zdjecie z laptopem,
   zakladki "Adres" / "Wklej zdjęcia", kafelki uslug z cena (jak aplikacja warsztatu), "Termin i szczegóły",
   Podglad zgloszenia przed wyslaniem i JEDEN przycisk Wyslij na dolnym pasku. Wysylka bez zmian (/wyslij.php + Apps Script,
   potwierdzenie dla klienta, Turnstile). Bez narzedzi wewnetrznych. Stary dlugi formularz: wycena.html?pelny.
2. wycen-usluge.html (parkieciarz, PIN jak analizator): to samo + Zapisane wyceny (Folder ofert i SMS) na gorze, Zapisz,
   Podglad = PDF oferty (tak dostanie klient) z Wyslij / Popraw, maly link "Pełny arkusz" (analizator.html?pelny).

Skorka NIE zmienia logiki silnika wycena.html - przenosi istniejace pola (te same id) do nowych kontenerow.
Blok jest w wycena.html miedzy <!-- prosty-widok START --> a <!-- prosty-widok KONIEC --> (ten skrypt go wpisuje/odswieza);
_buduj_analizator.py i _buduj_zamow.py go wycinaja, a wycen-usluge.html (z analizator.html) dostaje go z powrotem.

Uruchomienie: python _buduj_wycen_usluge.py  (po _buduj_analizator.py; build.py wywoluje oba)."""
import os, re
TU = os.path.dirname(os.path.abspath(__file__))

SKORKA = r'''<!-- prosty-widok START -->
<style id="prosty-widok-0711">
html.wu-start #wycena .ai{visibility:hidden}
html.wu #wycena .sticky>*:not(h2):not(.oczko):not(.kalk-foto):not(.se-lead){display:none!important}
html.wu-strona.wu #wycena .sticky .se-lead{display:none!important}
html.wu #wycena .sticky h2{margin:0!important}
html.wu #wycena .sticky .se-lead{margin:4px 0 0!important}
html.wu #wycena .sticky .kalk-foto{margin:12px 0 0!important}
html.wu #wycena .split{gap:14px!important}
html.wu form.ai-form>*:not(#wu),html.wu #wycena .ai-body,html.wu #wycena .ai>.drop,html.wu #wycena .ai>.miniatury,html.wu .cta-bar,html.wu #spTabBtn,html.wu #spDok,html.wu #zapiszBtn,html.wu #szkicInfo,html.wu #podgladOferty,html.wu #wuKon #wyslij,html.wu .wu-up .maly-info{display:none!important}
html.wu #wycena .ai-form{display:block!important;padding:14px 12px!important}
html.wu #wycena .ai{padding:0!important;overflow:visible!important}
html.wu body{padding-bottom:96px}
#wu{font-family:Inter,system-ui,sans-serif}
#wu *{box-sizing:border-box}
.wu-h{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:18px 2px 8px;font:800 1.05rem/1.2 Inter,system-ui,sans-serif;color:#14110E}
.wu-h small{font:600 .8rem/1.2 Manrope,system-ui,sans-serif;color:#6B7076;text-align:right}
/* zakladki Adres / Wklej zdjecia */
.wu-tabs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 8px}
#wycena #wu .wu-tabs button{all:unset;box-sizing:border-box;display:flex;align-items:center;justify-content:center;gap:7px;min-height:54px;padding:8px 10px;border-radius:14px;border:1.5px solid #E1E3E6;background:#fff;font:800 .95rem Inter,system-ui,sans-serif;color:#14110E;cursor:pointer;text-align:center;-webkit-tap-highlight-color:transparent}
#wycena #wu .wu-tabs button svg{width:20px;height:20px;flex:none;color:#FF6A13}
#wycena #wu .wu-tabs button.on{border-color:#FF6A13;background:#FFF8F2;box-shadow:0 6px 20px rgba(255,106,19,.14)}
#wycena #wu .wu-tabs button.ok:not(.on)::after{content:"✓";color:#1F7A4D;font-weight:800}
.wu-tabs i{font-style:normal;font:800 .74rem Inter,system-ui,sans-serif;background:#1F7A4D;color:#fff;border-radius:999px;padding:2px 7px}
.wu-tabs i:empty{display:none}
.wu-tabp{border:1.5px solid #E1E3E6;border-radius:14px;background:#fff;padding:12px 12px 2px}
.wu-tabp[hidden]{display:none}
.wu-tabp>*{margin-bottom:10px}
.wu-tabp input{font-size:16px!important}
.wu-tabp .wu-info{margin:0 0 10px}
.wu-tabp label.drop>span:first-child{display:none!important}
.wu-tabp label.drop{padding:10px!important;min-height:0!important}
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
.wu-up input,.wu-up select,.wu-up textarea{font-size:16px!important}
.wu-u:not(.ceny) .wu-up [id^="cw_"]{display:none!important}
.wu-info{font:600 .88rem/1.45 Manrope,system-ui,sans-serif;color:#4A5058;margin:0 0 10px}
.wu-wiersz{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#wycena #wu .wu-wiersz button{width:auto;min-height:44px;margin:0;border-radius:11px;padding:10px 14px;font:800 .9rem Inter,system-ui,sans-serif;cursor:pointer}
#wycena #wu .wu-gotowe{flex:1;border:0;background:#14110E;color:#fff}
#wycena #wu .wu-usun{border:1.5px solid #E1E3E6;background:#fff;color:#B23B1E}
#wycena #wu .wu-dodaj{flex:1;border:0;background:#FF6A13;color:#fff}
#wycena #wu .wu-cena{border:0;background:none;color:#4A5058;text-decoration:underline;padding:10px 4px;font-weight:700}
/* termin i szczegoly */
details.wu-wiecej{border:1.5px dashed #C9CDD2;border-radius:14px;background:#fff;margin:8px 0 0}
details.wu-wiecej>summary{list-style:none;cursor:pointer;padding:14px 12px;font:800 .95rem Inter,system-ui,sans-serif;color:#14110E;display:flex;justify-content:space-between;gap:8px}
details.wu-wiecej>summary::-webkit-details-marker{display:none}
details.wu-wiecej>summary::after{content:"+";color:#FF6A13;font-size:1.3rem;line-height:1}
details.wu-wiecej[open]>summary::after{content:"−"}
details.wu-wiecej>summary small{display:block;font:600 .8rem Manrope,system-ui,sans-serif;color:#6B7076;margin-top:2px}
.wu-wiecej-in{padding:0 12px 4px}
.wu-wiecej-in>*{margin-bottom:10px}
.wu-wiecej-in input,.wu-wiecej-in select,.wu-wiecej-in textarea{font-size:16px!important}
/* zapisane wyceny (parkieciarz) */
#wycena #wu button.wu-fol{all:unset;box-sizing:border-box;display:grid;grid-template-columns:40px 1fr auto;align-items:center;gap:12px;width:100%;padding:10px 12px;border-radius:14px;background:#14110E;color:#fff;cursor:pointer;margin:0 0 12px}
.wu-fol .wu-ik{background:#2E3136;color:#FF8A4C}
.wu-fol b{font:800 1rem/1.2 Inter,system-ui,sans-serif}
.wu-fol small{display:block;font:600 .8rem/1.25 Manrope,system-ui,sans-serif;color:#B9BDC3}
.wu-fol i{font-style:normal;font:800 .78rem Inter,system-ui,sans-serif;background:#1F7A4D;color:#fff;border-radius:999px;padding:4px 9px}
.wu-fol i:empty{display:none}
.wu-folp{display:none;margin:-4px 0 12px}
.wu-folp.otw{display:block}
.wu-folp .sms-box{margin:0!important}
html.wu .sms-box textarea#smsWklej{height:110px!important;min-height:0!important}
/* koniec formularza */
.wu-koniec{margin:16px 0 0}
#wycena #wu .wu-podg{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;min-height:52px;margin:0 0 8px;border:0;border-radius:12px;background:#14110E;color:#fff;font:800 1rem Inter,system-ui,sans-serif;cursor:pointer}
#wycena #wu .wu-podg svg{width:21px;height:21px;color:#FF8A4C}
.wu-podg-o{margin:0 2px 6px;font:600 .82rem/1.4 Manrope,system-ui,sans-serif;color:#6B7076;text-align:center}
.wu-maly{display:block;margin:14px auto 2px;text-align:center;font:700 .82rem Manrope,system-ui,sans-serif;color:#6B7076!important;text-decoration:underline}
#wycena #wu .do-analizatora{margin:14px auto 0}
/* dolny pasek */
#wuBar{position:fixed;left:0;right:0;bottom:0;z-index:70;display:grid;grid-template-columns:minmax(0,1fr) auto auto auto;gap:6px;align-items:center;padding:8px 10px calc(8px + env(safe-area-inset-bottom));background:#14110E;color:#fff;box-shadow:0 -6px 20px rgba(0,0,0,.18)}
#wuBar.pub{grid-template-columns:minmax(0,1fr) auto auto}
#wuBar small{display:block;font:700 .66rem Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#B9BDC3}
#wuBar b{display:block;font:800 1.12rem Inter,system-ui,sans-serif;color:#FF6A13;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#wuBar button{border:0;border-radius:11px;min-height:46px;padding:0 11px;font:800 .86rem Inter,system-ui,sans-serif;cursor:pointer;white-space:nowrap}
#wuBar .zap{background:#fff;color:#14110E}
#wuBar .pdf{background:#3A3F45;color:#fff;box-shadow:inset 0 0 0 1.5px #8A9099}
#wuBar .wys{background:#FF6A13;color:#fff}
#wuBar button:disabled{opacity:.6}
#wuInfo{position:fixed;left:10px;right:10px;bottom:calc(72px + env(safe-area-inset-bottom));z-index:71;padding:12px 14px;border-radius:12px;font:700 .9rem/1.4 Manrope,system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.2);background:#14110E;color:#fff}
#wuInfo[hidden]{display:none}
#wuInfo.ok{background:#1F7A4D}#wuInfo.lok{background:#8A5A00}
#wuInfo button{display:block;margin:10px 0 0;width:100%;min-height:42px;border:0;border-radius:10px;background:#FF6A13;color:#fff;font:800 .92rem Inter,system-ui,sans-serif;cursor:pointer}
/* podglad zgloszenia (klient) */
#wuPod{position:fixed;inset:0;z-index:9999;background:rgba(20,22,26,.92);display:none;flex-direction:column;font-family:Inter,system-ui,sans-serif}
#wuPod.otw{display:flex}
#wuPod .pg-g{display:flex;gap:8px;align-items:center;justify-content:space-between;padding:10px 12px;background:#16191D;color:#fff;font:700 15px Inter,system-ui,sans-serif}
#wuPod .pg-g small{display:block;font:500 12px Manrope,system-ui,sans-serif;color:#B9BDC3}
#wuPod .pg-g span:last-child{display:flex;gap:8px}
#wuPod button{border:0;border-radius:10px;padding:10px 14px;font:800 14px Inter,system-ui,sans-serif;cursor:pointer}
#wuPod .pg-w{background:#FF6A13;color:#fff}#wuPod .pg-p{background:#fff;color:#16191D}
#wuPod .pg-s{flex:1;overflow:auto;-webkit-overflow-scrolling:touch;padding:12px}
#wuPod .pg-k{max-width:640px;margin:0 auto;background:#fff;border-radius:10px;padding:18px 16px;color:#14110E;font:500 .92rem/1.45 Manrope,system-ui,sans-serif}
#wuPod .pg-k h3{margin:0 0 2px;font:800 1.15rem Inter,system-ui,sans-serif}
#wuPod .pg-k h4{margin:16px 0 6px;font:800 .78rem Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#B03C0A}
#wuPod .pg-k table{width:100%;border-collapse:collapse}
#wuPod .pg-k td{padding:7px 0;border-bottom:1px solid #EEE9E2;vertical-align:top}
#wuPod .pg-k td+td{text-align:right;white-space:nowrap;padding-left:10px;font-weight:800}
#wuPod .pg-suma{display:flex;justify-content:space-between;gap:10px;margin:12px 0 0;padding:12px 14px;border-radius:10px;background:#FF6A13;color:#fff;font:800 1rem Inter,system-ui,sans-serif}
#wuPod .pg-uw{margin:8px 0 0;font-size:.82rem;color:#6B7076}
#wuPod .pg-brak{margin:10px 0 0;padding:10px 12px;border-radius:10px;background:#FFF1E6;color:#B03C0A;font-weight:800}
#wuPod .pg-zd{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
#wuPod .pg-zd img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px;background:#EEE9E2}
#wuPod .pg-d{padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:#16191D}
#wuPod .pg-d button{width:100%;min-height:50px;font-size:16px}
@media(max-width:370px){#wuBar button{padding:0 8px;font-size:.8rem}#wuBar b{font-size:1rem}}
@media(min-width:720px){#wuBar{left:50%;right:auto;transform:translateX(-50%);width:min(720px,100%);border-radius:16px 16px 0 0}#wuInfo{left:50%;right:auto;transform:translateX(-50%);width:min(700px,100%)}}
</style>
<script id="prosty-widok-0711s">
(function(){
 var H=document.documentElement,WEW=H.classList.contains('wu-strona');
 /* klient: wycena.html (nie analizator, nie koszyk, nie ?pelny); parkieciarz: wycen-usluge.html */
 if(!WEW&&(window.SP_ANALIZATOR||window.SP_ZAMOWIENIE||/[?&]pelny\b/.test(location.search)))return;
 var PUB=!WEW;
 H.classList.add('wu-start');setTimeout(function(){H.classList.remove('wu-start');},6000);
 var SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
 var IK={
  pod:'<path d="M3 17h18M3 13h18M7 13v4M12 13v4M17 13v4M3 9l9-5 9 5"/>',
  lw:'<path d="M3 18h18M3 14h18v4H3zM7 10l3-3 3 3M10 7v7"/>',
  lo:'<path d="M3 16h18v4H3zM12 3v3M12 9v2M6.5 5.5l1.5 1.5M17.5 5.5 16 7"/>',
  na:'<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
  st:'<path d="M4 20h16M6 16h12M9 16V9h6v7M12 3v6"/>',
  ko:'<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
  do:'<path d="M12 5v14M5 12h14"/>',
  uw:'<path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4"/>',
  me:'<path d="M4 18v-6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6M4 15h16M6 18v2M18 18v2M7 10V7a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3"/>',
  sc:'<path d="M3 20h5v-4h4v-4h4V8h5"/>',
  fol:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  adr:'<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
  zdj:'<path d="M4 7h3l2-2h6l2 2h3v12H4z"/><circle cx="12" cy="13" r="3.5"/>',
  oko:'<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'};
 /* uslugi: uz = kratka "Zakres prac" (uzgN, tylko parkieciarz), q = nazwa pozycji w arkuszu (p[6]), il = pole ilosci,
    f = pola parkieciarza, fp = pola klienta, r = radio tak/nie silnika, c = staly opis ceny (reszta z cennika silnika) */
 var K=[
  {id:'pod',t:'Cyklinowanie / odnowienie podłogi',j:'m²',uz:0,q:'Renowacja parkietu',il:'m2',f:['m2','typ','wyk'],info:'Lakier, olej i twardy wosk - bez dopłaty.'},
  {id:'lw',t:'Wymiana listew',j:'mb',uz:1,q:'Wymiana listew',r:'listwy',il:'listwyMb',f:['listwyMb','@listwy'],fp:['@listwy','listwyMb']},
  {id:'lo',t:'Odświeżenie listew',j:'kpl.',uz:7,q:'Odświeżenie listew',wew:1,c:'kpl. · do uzgodnienia',info:'Pozycja 1 kpl., cena do uzgodnienia. Znasz kwotę? Dopisz ją w Pracach dodatkowych.'},
  {id:'st',t:'Stabilizacja',j:'m²',uz:2,q:'Stabilizacja',r:'stab',il:'stabM2',f:['stabM2'],fp:['@stab','stabM2']},
  {id:'na',t:'Naprawa',j:'ilość i kwota',uz:3,q:'Naprawy',r:'napr',il:'naprIl',f:['naprBlok'],fp:['@napr'],c:PUB?'do uzgodnienia po zdjęciach':'ilość i kwota'},
  {id:'ko',t:'Koloryzacja',j:'m²',uz:4,q:'Koloryzacja',kolor:1,info:'Liczy się od metrażu z pozycji Cyklinowanie.',f:['cw_kolor'],fp:[]},
  {id:'me',t:'Pomoc z meblami',j:'zł',uz:5,q:'Przesunięcie mebli',r:'meble',il:'mebleKw',f:['mebleKw'],fp:['@meble'],c:'300 zł / do uzgodnienia zakres'},
  {id:'sc',t:'Renowacja schodów',j:'kpl.',uz:6,q:'Renowacja schodów',wew:1,c:'kpl. · do uzgodnienia',info:'Pozycja 1 kpl., cena do uzgodnienia po wizji lokalnej.'},
  {id:'do',t:'Prace dodatkowe',j:'własna pozycja z ceną',dod:1,wew:1,f:['dodBlok'],c:'własna pozycja z ceną'},
  {id:'uw',t:'Inne prace / uwagi',j:'opisz, co jeszcze',pub:1,tekst:'uwagiKl',fp:['uwagiKl'],c:'opisz, co jeszcze trzeba zrobić'}
 ].filter(function(k){return PUB?!k.wew:!k.pub;});
 var $=function(i){return document.getElementById(i);};
 var zl=function(n){return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g,' ')+' zł';};
 var esc=function(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
 function ev(e,t){e.dispatchEvent(new Event(t,{bubbles:true}));}
 function wart(i){return String(($(i)||{}).value||'').trim();}
 function blok(f){if(f.charAt(0)==='@'){var r=document.querySelector('form.ai-form input[name="'+f.slice(1)+'"]');return r&&r.closest('form.ai-form>*');}
  var e=$(f);if(!e)return null;if(/^(cw_|drop$|miniatury$)/.test(f))return e;return e.closest('form.ai-form>*')||e;}
 function zazn(n){var e=document.querySelector('form input[name="'+n+'"]:checked');return e?e.value:'';}
 function radio(n,ktory){var rs=[].slice.call(document.querySelectorAll('input[name="'+n+'"]'));
  var x=rs.filter(function(r){var t=(r.closest('label')||{}).textContent||'';return ktory==='tak'?(n==='meble'?t.trim()==='tak':r.value!=='nie'):(n==='meble'?t.trim()==='nie':r.value==='nie');})[0];
  if(n==='listwy'&&ktory==='tak'){var cur=rs.filter(function(r){return r.checked;})[0];if(cur&&cur.value!=='nie')return;x=rs.filter(function(r){return r.value==='klasyczna';})[0];}
  if((n==='stab'||n==='napr')&&ktory==='tak'){var c2=rs.filter(function(r){return r.checked;})[0];if(c2&&c2.value!=='nie')return;x=rs.filter(function(r){return r.value==='tak';})[0];}
  if(x&&!x.checked){x.checked=true;ev(x,'change');ev(x,'input');}}
 function ustaw(k,v){
  if(!PUB&&k.uz!=null){var c=$('uzg'+k.uz);if(c&&c.checked!==v){c.checked=v;ev(c,'change');}}
  if(k.r)radio(k.r,v?'tak':'nie');
  if(k.kolor){var w=$('wyk');if(w&&(w.selectedIndex===4)!==v){w.selectedIndex=v?4:0;ev(w,'change');ev(w,'input');}}
  if(PUB&&!v&&(k.id==='pod'||k.tekst)){var e=$(k.tekst||'m2');if(e){e.value='';ev(e,'input');ev(e,'change');}}
  if(k.dod){if(v&&!document.querySelector('#dodLista .dod-w')){var p=$('dodPlus');p&&p.click();}
   [].forEach.call(document.querySelectorAll('#dodLista .dod-w'),function(w){var u=w.querySelector('.dod-u');if(u&&u.checked!==v&&(!v||(w.querySelector('.dod-o')||{}).value)){u.checked=v;ev(u,'change');}});}
  odswiez();}
 function jest(k){
  if(!PUB){if(k.uz!=null){var c=$('uzg'+k.uz);return !!(c&&c.checked);}
   if(k.dod)return [].some.call(document.querySelectorAll('#dodLista .dod-o'),function(o){return o.value.trim();});return false;}
  /* klient: bez kratek zakresu - stan z pol i przelacznikow silnika */
  if(k.id==='pod')return parseFloat(wart('m2').replace(',','.'))>0;
  if(k.kolor){var w=$('wyk');return !!(w&&w.selectedIndex===4);}
  if(k.tekst)return !!wart(k.tekst);
  if(k.r==='meble'){var m=document.querySelector('input[name="meble"]:checked');return !!(m&&((m.closest('label')||{}).textContent||'').trim()==='tak');}
  if(k.r){var z=zazn(k.r);return !!z&&z!=='nie';}
  return false;}
 function ark(){try{return window.spArkusz&&window.spArkusz();}catch(e){return null;}}
 function kwota(k,A){if(!A||k.tekst)return '';
  var P=A.poz.filter(function(p){return k.dod?(p.length<6&&!/^\*/.test(p[0])):(p[6]===k.q||(k.id==='pod'&&/^\*/.test(p[0])));});
  var s=0,uzg=false;P.forEach(function(p){if(typeof p[1]==='number'&&p[2])s+=p[1]*p[2];else if(p[1]&&p[1]!==0)uzg=true;});
  return s>0?zl(s):(uzg?'do uzg.':'');}
 /* cena z cennika silnika (te same stawki co w PDF i w kalkulatorze), np. "130 zł/m²" */
 function cennik(k,A){if(k.c)return k.c;var p=A&&A.poz.filter(function(p){return p[6]===k.q;})[0];
  if(p&&typeof p[2]==='number'&&p[2]>0)return zl(p[2])+'/'+k.j;return k.j;}
 function ilosc(k){if(k.tekst)return '';var e=k.il&&$(k.il);var v=e?String(e.value||'').trim():'';return v&&parseFloat(v.replace(',','.'))>0?v.replace('.',',')+' '+k.j:'';}
 /* pola przeniesione z form.ai-form nie sa juz jego dziecmi - kopia regul ".ai-form > ..." dla nowych kontenerow */
 function kopiujCss(){var out=[];function przejdz(R,med){[].forEach.call(R,function(r){
   if(r.cssRules&&r.media){przejdz(r.cssRules,r.media.mediaText);return;}
   if(!r.selectorText||!/ai-form\s*>/.test(r.selectorText))return;
   var sel=r.selectorText.split(',').filter(function(x){return /ai-form\s*>/.test(x)&&!/html\.wu|#wu/.test(x);}).map(function(x){return ['.wu-up','.wu-tabp','.wu-wiecej-in'].map(function(c){return x.replace(/ai-form\s*>/g,'ai-form '+c+' >');}).join(',');}).join(',');
   if(!sel)return;var t=sel+'{'+r.style.cssText+'}';out.push(med?'@media '+med+'{'+t+'}':t);});}
  [].forEach.call(document.styleSheets,function(sh){try{przejdz(sh.cssRules,'');}catch(e){}});
  var st=document.createElement('style');st.id='wu-css-kopia';st.textContent=out.join('\n');document.body.appendChild(st);}
 function etykieta(id,t){var l=document.querySelector('label[for="'+id+'"]');if(l)l.textContent=t;}
 var info=null,infoT=0;
 function pokazInfo(t,kl,przycisk){if(!info)return;info.textContent=t;info.className=kl||'';info.hidden=false;clearTimeout(infoT);
  if(przycisk){var b=document.createElement('button');b.type='button';b.textContent=przycisk[0];b.onclick=function(e){e.stopPropagation();info.hidden=true;przycisk[1]();};info.appendChild(b);}
  if(kl==='ok'||kl==='lok')infoT=setTimeout(function(){info.hidden=true;},przycisk?15000:(kl==='ok'?6000:12000));}
 /* zdjecie "laptop + dlugopis" na gorze (Artur 07.11 22:20 "dla zachety to zdjecie z komputerem") */
 function zdjecie(){var st=document.querySelector('#wycena .sticky');if(!st||st.querySelector('.kalk-foto'))return;
  var f=document.createElement('figure');f.className='kalk-foto';
  f.innerHTML='<img src="img/wycena-cyklinowania-online-kalkulator-480.webp" srcset="img/wycena-cyklinowania-online-kalkulator-480.webp 480w, img/wycena-cyklinowania-online-kalkulator-900.webp 900w" sizes="(max-width:900px) calc(100vw - 32px), 520px" width="900" height="694" decoding="async" alt="Laptop z tabelą wyceny, długopis i notes na parkiecie">';
  var h=st.querySelector('h2');if(h)h.after(f);else st.appendChild(f);}
 /* zakladki zwiniete na starcie (Artur 07.11 22:21: zdjecie, dwie zakladki, potem od razu kafelki); drugie nacisniecie zwija */
 function zakladka(t){if(t&&!$(t==='a'?'wuTA':'wuTZ').hidden)t='';[].forEach.call(document.querySelectorAll('#wu .wu-tabs button'),function(b){var on=b.dataset.t===t;b.classList.toggle('on',on);b.setAttribute('aria-selected',on?'true':'false');});
  $('wuTA').hidden=t!=='a';$('wuTZ').hidden=t!=='z';}
 function podglad(){
  if(!PUB){var b=$('podgladOferty');if(b&&!b.disabled)b.click();return;}
  podgladPub();}
 function brakKontaktu(){return wart('mailKl').length<5&&wart('telKl').replace(/\D/g,'').length<9;}
 function otworzAdres(){if($('wuTA').hidden)zakladka('a');}
 function wyslij(){var b=$('wyslij');if(!b||b.disabled)return;if(brakKontaktu())otworzAdres();b.click();
  var bl=$('bladForm');setTimeout(function(){if(bl&&!bl.hidden)bl.scrollIntoView({block:'center',behavior:'smooth'});},60);}
 /* PODGLAD ZGLOSZENIA (klient): to, co trafi do biura - uslugi, orientacyjna kwota, dane, zdjecia; Wyslij / Popraw */
 var pod=null;
 function podgladPub(){
  if(!pod){pod=document.createElement('div');pod.id='wuPod';pod.setAttribute('role','dialog');pod.setAttribute('aria-modal','true');pod.setAttribute('aria-label','Podgląd zgłoszenia');
   pod.innerHTML='<div class="pg-g"><span>Podgląd zgłoszenia<small>sprawdź przed wysłaniem</small></span><span><button type="button" class="pg-w">Wyślij</button><button type="button" class="pg-p">Popraw</button></span></div><div class="pg-s"><div class="pg-k"></div></div><div class="pg-d"><button type="button" class="pg-w">Wyślij zgłoszenie</button></div>';
   document.body.appendChild(pod);
   var zam=function(){pod.classList.remove('otw');document.body.style.overflow='';};
   pod.querySelector('.pg-p').onclick=function(){zam();if(brakKontaktu()){otworzAdres();var t=$('telKl');t&&t.scrollIntoView({block:'center'});}};
   [].forEach.call(pod.querySelectorAll('.pg-w'),function(b){b.onclick=function(){zam();wyslij();var k=$('wuKon');k&&k.scrollIntoView({block:'start',behavior:'smooth'});};});}
  var A=ark()||{poz:[],suma:0};
  var poz=A.poz.filter(function(p){return p[1]!==0&&p[1]!=='0'&&p[1]!==''&&p[1]!=null&&p[1]!==false;});
  var wiersz=function(p){var n=String(p[0]).replace(/^\*\s*/,''),jm=(n.match(/\(([^()]*)\)\s*$/)||[])[1]||'';n=n.replace(/\s*\([^()]*\)\s*$/,'');
   var il=typeof p[1]==='number'?(String(p[1]).replace('.',',')+' '+jm):'';
   var kw=typeof p[1]==='number'&&p[2]?zl(p[1]*p[2]):'do uzgodnienia';
   return '<tr><td>'+esc(n)+(il?'<br><small style="color:#6B7076">'+esc(il)+'</small>':'')+'</td><td>'+kw+'</td></tr>';};
  var orient=(($('oN')||{}).textContent||'').trim();
  var uw=wart('uwagiKl'),term=wart('terminKl');
  var chce=document.querySelector('input[name="chceT"]:checked'),chceZ=$('chceZam');
  if(chceZ&&chceZ.checked)term=(term?term+' · ':'')+'chcę zamówić usługę'+(chce&&chce.value==='data'&&wart('chceData')?(' ('+wart('chceData')+')'):'');
  var dane=[['Adres',[wart('ulicaKl'),wart('kodKl'),wart('miastoKl'),wart('dzielKl')].filter(Boolean).join(', ')],['Telefon',wart('telKl')],['E-mail',wart('mailKl')],['Imię i nazwisko',wart('imieKl')],['Termin',term],['Piętro',wart('pietroKl')]].filter(function(x){return x[1];});
  var pl=window.__pliki?window.__pliki():[];
  var k=pod.querySelector('.pg-k');
  k.innerHTML='<h3>Bezpłatna wycena SMARTPARKIET</h3><p class="pg-uw" style="margin:0">Tak trafi do naszego biura. Odpowiedź w ciągu 2 godzin roboczych.</p>'+
   '<h4>Usługi</h4>'+(poz.length?'<table>'+poz.map(wiersz).join('')+'</table>':'<p class="pg-brak">Nie wybrano jeszcze żadnej usługi - wróć i naciśnij usługę na liście.</p>')+
   (orient&&orient!=='-'?'<div class="pg-suma"><span>Orientacyjnie netto</span><span>'+esc(orient)+'</span></div>':'')+
   '<p class="pg-uw">Kwota orientacyjna z cennika. Specjalista oceni zdjęcia i przekaże indywidualną wycenę.</p>'+
   (uw?'<h4>Inne prace / uwagi</h4><p style="margin:0">'+esc(uw)+'</p>':'')+
   '<h4>Dane do kontaktu</h4>'+(dane.length?'<table>'+dane.map(function(x){return '<tr><td>'+x[0]+'</td><td style="white-space:normal;font-weight:700">'+esc(x[1])+'</td></tr>';}).join('')+'</table>':'')+
   (wart('mailKl').length<5&&wart('telKl').replace(/\D/g,'').length<9?'<p class="pg-brak">Brakuje telefonu lub e-maila - bez nich nie prześlemy wyceny. Naciśnij Popraw i uzupełnij zakładkę Adres.</p>':'')+
   '<h4>Zdjęcia ('+pl.length+')</h4>'+(pl.length?'<div class="pg-zd">'+pl.map(function(f){var u='';try{u=URL.createObjectURL(f);}catch(e){}return '<img alt="" src="'+u+'">';}).join('')+'</div>':'<p class="pg-uw" style="margin:0">Bez zdjęć. Zdjęcia podłogi (4-6) pomogą przygotować dokładną wycenę - zakładka Wklej zdjęcia.</p>');
  pod.classList.add('otw');document.body.style.overflow='hidden';pod.querySelector('.pg-s').scrollTop=0;}
 function zbuduj(){
  var form=document.querySelector('form.ai-form');if(!form||$('wu'))return;
  kopiujCss();zdjecie();
  H.classList.add('wu');H.classList.remove('wu-start');
  if(!PUB){var h=document.querySelector('#wycena .sticky h2');if(h)h.textContent='Wyceń usługę';
   var oc=document.querySelector('#wycena .sticky .oczko');if(oc&&oc.lastChild)oc.lastChild.textContent='SMARTPARKIET · narzędzie parkieciarza';}
  var wu=document.createElement('div');wu.id='wu';
  wu.innerHTML=(PUB?'':'<button type="button" class="wu-fol" id="wuFolB" aria-expanded="false"><span class="wu-ik">'+SVG+IK.fol+'</svg></span><span><b>Zapisane wyceny</b><small>Folder ofert - szukaj po adresie lub telefonie</small></span><i id="wuFolN"></i></button><div class="wu-folp" id="wuFolP"></div>')+
   '<div class="wu-tabs" role="tablist"><button type="button" role="tab" data-t="a" aria-selected="false">'+SVG+IK.adr+'</svg>Adres</button><button type="button" role="tab" data-t="z" aria-selected="false">'+SVG+IK.zdj+'</svg>Wklej zdjęcia<i id="wuZn"></i></button></div>'+
   '<div class="wu-tabp" id="wuTA" role="tabpanel" hidden></div><div class="wu-tabp" id="wuTZ" role="tabpanel" hidden><p class="wu-info">'+(PUB?'Dodaj 4-6 zdjęć podłogi (przy naprawach do 12), także miejsca uszkodzeń.':'Zdjęcia podłogi klienta - trafią do PDF i do Folderu ofert.')+'</p></div>'+
   '<p class="wu-h">Usługi <small>'+(PUB?'naciśnij, co mamy zrobić':'naciśnij i wpisz ilość')+'</small></p><div id="wuL"></div>'+
   '<details class="wu-wiecej" id="wuW"><summary><span>Termin i szczegóły<small>'+(PUB?'termin, piętro, kod pocztowy - opcjonalnie':'termin, piętro, VAT, kopia - opcjonalnie')+'</small></span></summary><div class="wu-wiecej-in" id="wuWi"></div></details>'+
   '<div class="wu-koniec" id="wuKon"></div>';
  form.insertBefore(wu,form.firstChild);
  [].forEach.call(wu.querySelectorAll('.wu-tabs button'),function(b){b.onclick=function(){zakladka(b.dataset.t);};});
  /* folder ofert + SMS (parkieciarz, zwiniete) */
  if(!PUB){var sb=form.querySelector('.sms-box');if(sb)$('wuFolP').appendChild(sb);
   $('wuFolB').onclick=function(){var p=$('wuFolP'),o=!p.classList.contains('otw');p.classList.toggle('otw',o);this.setAttribute('aria-expanded',o?'true':'false');
    if(o){var s=$('folSzuk');if(s)ev(s,'focus');}};}
  /* zakladka Adres: adres, telefon, e-mail (Artur 06.11 16:0x); Wklej zdjecia: dodawanie zdjec */
  var TA=$('wuTA');['ulicaKl','telKl','mailKl'].forEach(function(f){var b=blok(f);if(b)TA.appendChild(b);});
  etykieta('ulicaKl',PUB?'Adres realizacji (ulica i numer)':'Adres (ulica i numer)');etykieta('telKl','Telefon');etykieta('mailKl',PUB?'E-mail (tu wyślemy wycenę)':'E-mail');
  if(PUB){var pi=document.createElement('p');pi.className='wu-info';pi.textContent='Wystarczy telefon albo e-mail.';TA.appendChild(pi);}
  var TZ=$('wuTZ');['drop','miniatury'].forEach(function(f){var b=blok(f);if(b)TZ.appendChild(b);});
  /* uslugi */
  var L=$('wuL');
  K.forEach(function(k){var d=document.createElement('div');d.className='wu-u';d.id='wu_'+k.id;
   d.innerHTML='<button type="button" class="wu-ut" aria-expanded="false"><span class="wu-ik">'+SVG+IK[k.id]+'</svg></span><span class="wu-un">'+k.t+'<small>'+(k.c||k.j)+'</small></span><span class="wu-uk"><span class="wu-plus" aria-hidden="true">+</span></span></button><div class="wu-up"></div>';
   var P=d.querySelector('.wu-up');
   if(k.info){var i=document.createElement('p');i.className='wu-info';i.textContent=k.info;P.appendChild(i);}
   ((PUB&&k.fp)?k.fp:(k.f||[])).forEach(function(f){var b=blok(f);if(b)P.appendChild(b);});
   var w=document.createElement('div');w.className='wu-wiersz';
   var pole=k.il||k.dod||k.tekst||(PUB&&k.r);
   w.innerHTML=(pole?'<button type="button" class="wu-gotowe">Gotowe</button>':'<button type="button" class="wu-dodaj">Dodaj do wyceny</button>')+'<button type="button" class="wu-usun">Usuń z wyceny</button>'+(P.querySelector('[id^="cw_"]')?'<button type="button" class="wu-cena">Zmień cenę</button>':'');
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
   P.addEventListener('change',function(){setTimeout(odswiez,30);});
   /* nacisniecie uslugi = dodanie do wyceny i rozwiniecie pola ilosci (Artur 06.11 15:55) */
   d.querySelector('.wu-ut').onclick=function(){var o=!d.classList.contains('otw');
    [].forEach.call(L.querySelectorAll('.wu-u.otw'),function(x){x.classList.remove('otw');x.querySelector('.wu-ut').setAttribute('aria-expanded','false');});
    if(!o)return;
    if((k.il||k.dod||k.r)&&!k.tekst&&k.id!=='pod'&&!jest(k))ustaw(k,true);
    d.classList.add('otw');this.setAttribute('aria-expanded','true');
    setTimeout(function(){d.scrollIntoView({block:'start',behavior:'smooth'});var q=$(k.tekst||k.il||'');if(!q&&k.dod)q=d.querySelector('.dod-o');
     if(q&&!q.disabled&&!String(q.value||'').trim()&&d.contains(q)){try{q.focus({preventScroll:true});}catch(e){}}},80);};
   k.el=d;L.appendChild(d);});
  /* termin i szczegoly */
  var W=$('wuWi');(PUB?['terminKl','chceBlok','kodKl','miastoKl','dzielKl','pietroKl','@winda','obiektKl','imieKl','gatKl','montazKl']
   :['terminKl','kodKl','miastoKl','dzielKl','pietroKl','@winda','imieKl','obiektKl','gatKl','montazKl','vatBlok','kopiaBlok']).forEach(function(f){var b=blok(f);if(b)W.appendChild(b);});
  /* koniec: blad, Turnstile, Podglad (JEDEN przycisk wysylki jest na dolnym pasku i w podgladzie), potwierdzenie wyslania */
  var kon=$('wuKon');
  var pg=document.createElement('button');pg.type='button';pg.className='wu-podg';pg.innerHTML=SVG+IK.oko+'</svg>'+(PUB?'Podgląd zgłoszenia':'Podgląd oferty (PDF)');pg.onclick=podglad;
  var po=document.createElement('p');po.className='wu-podg-o';po.textContent=PUB?'Zobacz, co do nas trafi, i wyślij z podglądu albo przyciskiem Wyślij na dole.':'Tak zobaczy ją klient. Z podglądu: Wyślij albo Popraw.';
  ['bladForm','ts'].forEach(function(f){var e=$(f);if(e)kon.appendChild(e);});
  kon.appendChild(pg);kon.appendChild(po);
  ['wyslij','wyslano'].forEach(function(f){var e=$(f);if(e)kon.appendChild(e);});
  var bw=$('wyslij');if(bw){bw.dataset.oryg=bw.innerHTML;}
  if(PUB){var da=form.querySelector('.do-analizatora');if(da)kon.appendChild(da);}
  else{var a=document.createElement('a');a.className='wu-maly';a.href='analizator.html?pelny';a.textContent='Pełny arkusz (wszystkie pola) ›';kon.appendChild(a);}
  /* dolny pasek */
  var bar=document.createElement('div');bar.id='wuBar';if(PUB)bar.className='pub';
  bar.innerHTML='<div style="min-width:0"><small>'+(PUB?'Orientacyjnie':'Netto')+'</small><b id="wuSum">'+(PUB?'-':'0 zł')+'</b></div>'+(PUB?'':'<button type="button" class="zap">Zapisz</button>')+'<button type="button" class="pdf">Podgląd</button><button type="button" class="wys">Wyślij</button>';
  document.body.appendChild(bar);
  info=document.createElement('div');info.id='wuInfo';info.hidden=true;info.setAttribute('role','status');document.body.appendChild(info);
  info.onclick=function(){info.hidden=true;};
  if(!PUB){window.spSzkicInfo=pokazInfo;
   var bz=bar.querySelector('.zap');bz.onclick=function(){if(!window.spZapiszSzkic)return;bz.disabled=true;
    window.spZapiszSzkic().finally(function(){bz.disabled=false;});};
   /* Artur 07.11 22:24: po otwarciu zapisanej wyceny od razu widac, gdzie jest podglad */
   var sw=window.spWczytaj;if(sw&&!sw.__wu){var nw=function(){var r=sw.apply(this,arguments);var p=$('wuFolP');if(p&&p.classList.contains('otw'))$('wuFolB').click();
     setTimeout(function(){odswiez();pokazInfo('Wycena wczytana. Sprawdź usługi i zobacz, jak wygląda dla klienta.','ok',['Zobacz podgląd oferty',podglad]);},400);return r;};nw.__wu=1;window.spWczytaj=nw;}}
  bar.querySelector('.pdf').onclick=podglad;
  bar.querySelector('.wys').onclick=wyslij;
  odswiez();setInterval(odswiez,800);}
 var bylWys=false;
 function odswiez(){var A=ark();
  K.forEach(function(k){if(!k.el)return;var t=jest(k);k.el.classList.toggle('tak',t);
   var kw=t?kwota(k,A):'',il=t?ilosc(k):'';
   var sm=t?('✓ '+(il||(k.tekst?'opisane':'w wycenie'))):cennik(k,A);var s=k.el.querySelector('.wu-un small');if(s.textContent!==sm)s.textContent=sm;
   var u=k.el.querySelector('.wu-uk');var html=t?(kw||'✓'):'<span class="wu-plus" aria-hidden="true">+</span>';if(u.__h!==html){u.innerHTML=html;u.__h=html;}});
  var e=$('wuSum');
  if(e){if(PUB){try{window.spEst&&window.spEst();}catch(x){}var o=(($('oN')||{}).textContent||'').trim();e.textContent=o&&o!=='-'?o:'-';}else if(A)e.textContent=zl(A.suma||0);}
  var n=document.querySelectorAll('#folWyn button.fw-sz').length,fn=$('wuFolN');if(fn)fn.textContent=n?String(n):'';
  var pl=window.__pliki?window.__pliki().length:0,zn=$('wuZn');if(zn)zn.textContent=pl?String(pl):'';
  var ta=document.querySelector('#wu .wu-tabs [data-t="a"]');if(ta)ta.classList.toggle('ok',!!wart('ulicaKl')&&!brakKontaktu());
  /* jeden przycisk Wyslij: stan glownego przycisku silnika na pasku */
  var bw=$('wyslij'),bb=document.querySelector('#wuBar .wys');if(bw&&bb){var wy=bw.classList.contains('wyslane');bb.disabled=!!bw.disabled;var tx=wy?'Wysłane ✓':(bw.disabled?'Wysyłam…':'Wyślij');if(bb.textContent!==tx)bb.textContent=tx;}
  var ws=bw&&bw.classList.contains('wyslane')?bw:$('wyslano');if(ws){var vis=ws===bw||!ws.hidden;if(vis&&!bylWys)setTimeout(function(){ws.scrollIntoView({block:'center',behavior:'smooth'});},100);bylWys=vis;}}
 window.spWuOdswiez=odswiez;
 function start(){setTimeout(zbuduj,700);}
 if(document.readyState==='complete')start();else window.addEventListener('load',start);
})();
</script>
<!-- prosty-widok KONIEC -->'''

BLOK = re.compile(r'<!-- prosty-widok START -->.*?<!-- prosty-widok KONIEC -->', re.S)

# 1. wycena.html (zrodlo) - wpisanie / odswiezenie bloku
p = os.path.join(TU, 'wycena.html')
w = open(p, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in w else '\n'
blok = SKORKA.replace('\n', NL)
w2 = BLOK.sub(lambda m: blok, w, count=1) if BLOK.search(w) else w.rstrip('\r\n') + NL + blok + NL
if w2 != w:
    open(p, 'w', encoding='utf-8', newline='').write(w2)
    print('wycena.html: blok prosty-widok odswiezony (uruchom tez _buduj_analizator.py i _buduj_zamow.py, jesli zmieniales inne czesci)')

# 2. wycen-usluge.html z analizator.html (bez bloku) + blok
s = open(os.path.join(TU, 'analizator.html'), encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in s else '\n'
s = BLOK.sub('', s)


def zamien(stare, nowe):
    global s
    if stare not in s:
        raise SystemExit('Nie znaleziono: ' + stare[:80])
    s = s.replace(stare, nowe, 1)


zamien('<title>SMARTPARKIET Analizator</title>', '<title>Wyceń usługę | SMARTPARKIET</title>')
zamien('<meta name="apple-mobile-web-app-title" content="Analizator">', '<meta name="apple-mobile-web-app-title" content="Wyceń usługę">')
# klasa od razu (przed skryptami analizatora): bramka nie przekierowuje, analizator nie dokleja linku "Prosty widok"
m = re.search(r'<meta name="viewport"[^>]*>', s)
s = s[:m.end()] + NL + "<script>document.documentElement.classList.add('wu-strona')</script>" + s[m.end():]
s = s.rstrip() + NL + SKORKA.replace('\n', NL) + NL
open(os.path.join(TU, 'wycen-usluge.html'), 'w', encoding='utf-8', newline='').write(s)
print('wycen-usluge.html gotowy', len(s), 'znakow')
