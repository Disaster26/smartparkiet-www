# -*- coding: utf-8 -*-
"""wycen-usluge.html = PROJEKT do akceptacji Artura (06.11): uproszczony widok analizatora "Wyceń usługę".

Budowany z analizator.html (ten sam silnik wycena.html: PIN, PDF, Folder ofert, mail /wyslij.php, Apps Script).
Skorka NIE zmienia logiki - przenosi istniejace pola (te same id) do kafelkow-uslug, ktore rozwijaja sie po
nacisnieciu, i dodaje widok "Usluga z cennika" (lista z cena i przyciskiem Dodaj) oraz dolny pasek z kwota netto.
Kafelek "w wycenie" = kratka uzgN z panelu "Zakres prac" (zaznaczone = robimy), wiec PDF, mail, arkusz i Folder
ofert dostaja dokladnie te same pola co z analizatora.

Tylko podglad na GitHub Pages - build.py pomija ten plik (nie trafia na smartparkiet.com.pl).
Uruchomienie: python _buduj_wycen_usluge.py (po _buduj_analizator.py)."""
import os, re
TU = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(TU, 'analizator.html'), encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in s else '\n'
s = s.replace('<title>SMARTPARKIET Analizator</title>', '<title>Wyceń usługę | SMARTPARKIET</title><meta name="robots" content="noindex,nofollow">', 1)

SKORKA = r'''<!-- wycen-usluge START -->
<style id="wycen-usluge-0611">
html.wu #wycena .sticky>*:not(h2):not(.oczko){display:none!important}
html.wu #wycena .sticky h2{margin:0 0 4px!important}
html.wu #wycena .ai-out,html.wu #uzgPanel,html.wu form.ai-form>.est,html.wu form.ai-form>.sekcja-form,html.wu .cta-bar,html.wu #spTabBtn,html.wu #spDok,html.wu p.pod-przyc{display:none!important}
html.wu body{padding-bottom:84px}
#wu{margin:0 0 18px}
.wu-seg{display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:4px;background:#EEF0F2;border-radius:14px;margin:0 0 14px}
.wu-seg button{border:0;border-radius:11px;padding:12px 6px;font:800 .95rem/1.15 Inter,system-ui,sans-serif;color:#3A3F45;background:transparent;cursor:pointer}
.wu-seg button.on{background:#fff;color:#14110E;box-shadow:0 2px 8px rgba(20,17,14,.12)}
.wu-h{font:800 .78rem/1.2 Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#4A5058;margin:4px 2px 10px}
.wu-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;grid-auto-flow:row dense}
.wu-k{position:relative;border:1.5px solid #E1E3E6;border-radius:16px;background:#fff;min-width:0;scroll-margin-top:96px}
.wu-k>button.wu-t{all:unset;box-sizing:border-box;display:flex;flex-direction:column;align-items:flex-start;gap:4px;width:100%;min-height:118px;padding:12px;cursor:pointer;-webkit-tap-highlight-color:transparent}
.wu-ik{width:44px;height:44px;border-radius:12px;background:#FFF1E6;color:#FF6A13;display:grid;place-items:center;margin-bottom:4px}
.wu-n{overflow-wrap:anywhere;hyphens:auto}
.wu-ik svg{width:26px;height:26px}
.wu-n{font:800 .95rem/1.2 Inter,system-ui,sans-serif;color:#14110E}
.wu-s{font:600 .78rem/1.25 Manrope,system-ui,sans-serif;color:#6B7076}
.wu-k.tak{border-color:#FF6A13;background:#FFF8F2}
.wu-k.tak .wu-ik{background:#FF6A13;color:#fff}
.wu-k.tak .wu-s{color:#B03C0A;font-weight:800}
.wu-k.otw{grid-column:1/-1;border-color:#FF6A13;box-shadow:0 8px 24px rgba(255,106,19,.14)}
.wu-k.wu-szer{grid-column:1/-1}
.wu-k.wu-szer>button.wu-t{min-height:64px;display:grid;grid-template-columns:44px 1fr;align-items:center;gap:2px 12px}
.wu-k.wu-szer .wu-ik{grid-row:span 2;margin:0}
.wu-k.otw>button.wu-t{min-height:0;display:grid;grid-template-columns:44px 1fr;align-items:center;gap:2px 12px}
.wu-k.otw .wu-ik{grid-row:span 2;margin:0}
.wu-k.wu-szer .wu-ik{background:#14110E;color:#fff}
.wu-p{display:none;padding:0 12px 14px}
.wu-k.otw .wu-p{display:block}
.wu-p>div,.wu-p>label.drop,.wu-p>.miniatury{margin-bottom:10px}
#wycena .wu-p label.wu-sw span{font:800 .95rem Inter,system-ui,sans-serif!important;color:#fff!important;text-transform:none!important;letter-spacing:0!important}
#wycena .wu-p label.wu-sw{margin:0 0 12px!important}
.wu-sw{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 12px;padding:12px 14px;border-radius:12px;background:#14110E;color:#fff;font:800 .95rem Inter,system-ui,sans-serif;cursor:pointer}
.wu-sw input{appearance:none;-webkit-appearance:none;width:52px;height:30px;border-radius:30px;background:#5A5F66;position:relative;flex:none;margin:0;cursor:pointer;transition:background .2s}
.wu-sw input::after{content:"";position:absolute;top:3px;left:3px;width:24px;height:24px;border-radius:50%;background:#fff;transition:transform .2s}
.wu-sw input:checked{background:#FF6A13}
.wu-sw input:checked::after{transform:translateX(22px)}
.wu-info{font:600 .85rem/1.45 Manrope,system-ui,sans-serif;color:#4A5058;margin:0 0 10px}
.wu-zamk{display:block;width:100%;margin-top:4px;border:0;border-radius:12px;padding:12px;background:#EEF0F2;font:800 .9rem Inter,system-ui,sans-serif;color:#14110E;cursor:pointer}
.wu-szuk{width:100%;box-sizing:border-box;padding:13px 14px;border:1.5px solid #C9CDD2;border-radius:12px;font:600 1rem Manrope,system-ui,sans-serif;margin:0 0 10px}
.wu-chips{display:flex;gap:6px;overflow-x:auto;padding:0 0 10px;scrollbar-width:none}
.wu-chips::-webkit-scrollbar{display:none}
#wycena #wu .wu-chips button,#wycena #wu .wu-r button,#wycena #wu .wu-seg button{width:auto;min-height:0;margin:0}
#wycena #wu .wu-seg button{width:100%}
.wu-chips button{flex:none;border:1.5px solid #E1E3E6;background:#fff;border-radius:999px;padding:8px 14px;font:700 .85rem Inter,system-ui,sans-serif;color:#3A3F45;cursor:pointer}
.wu-chips button.on{background:#14110E;border-color:#14110E;color:#fff}
.wu-kat{border:1.5px solid #E1E3E6;border-radius:16px;background:#fff;margin:0 0 10px;overflow:hidden}
.wu-kat>b{display:block;padding:12px 14px;font:800 .95rem Inter,system-ui,sans-serif;color:#14110E;background:#F6F7F8}
.wu-r{display:grid;grid-template-columns:1fr auto;gap:2px 12px;align-items:center;padding:12px 14px;border-top:1px solid #EEF0F2}
.wu-r .rn{font:700 .92rem/1.25 Inter,system-ui,sans-serif;color:#14110E}
.wu-r .rd{grid-column:1;font:500 .78rem/1.3 Manrope,system-ui,sans-serif;color:#6B7076}
.wu-r .rc{grid-column:1;font:800 .9rem Inter,system-ui,sans-serif;color:#B03C0A}
.wu-r button{grid-column:2;grid-row:1/span 3;border:0;border-radius:10px;padding:11px 16px;background:#FF6A13;color:#fff;font:800 .88rem Inter,system-ui,sans-serif;cursor:pointer}
.wu-r.jest button{background:#1F7A4D}
#wuBar{position:fixed;left:0;right:0;bottom:0;z-index:70;display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:center;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:#14110E;color:#fff;box-shadow:0 -6px 20px rgba(0,0,0,.18)}
#wuBar small{display:block;font:700 .68rem Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#B9BDC3}
#wuBar b{font:800 1.25rem Inter,system-ui,sans-serif;color:#FF6A13;white-space:nowrap}
#wuBar button{border:0;border-radius:11px;padding:12px 12px;font:800 .86rem Inter,system-ui,sans-serif;cursor:pointer;white-space:nowrap}
#wuBar .pdf{background:#3A3F45;color:#fff}
#wuBar .wys{background:#FF6A13;color:#fff}
@media(min-width:720px){.wu-grid{grid-template-columns:repeat(3,1fr)}#wuBar{left:50%;right:auto;transform:translateX(-50%);width:min(720px,100%);border-radius:16px 16px 0 0}}
</style>
<script id="wycen-usluge-0611s">
(function(){
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
  kl:'<path d="M20 21a8 8 0 1 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>',
  sms:'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'};
 /* kafelki: uz = numer kratki "Zakres prac" (uzgN), q = nazwa pozycji w arkuszu (q[6]), f = pola przenoszone do kafelka */
 var K=[
  {id:'pod',t:'Odnowienie podłogi',uz:0,q:'Renowacja parkietu',f:['m2','typ','wyk','gatKl','montazKl']},
  {id:'lw',t:'Wymiana listew',uz:1,q:'Wymiana listew',r:'listwy',f:['@listwy','listwyMb']},
  {id:'lo',t:'Odświeżenie listew',uz:7,q:'Odświeżenie listew',info:'Pozycja 1 kpl., cena do uzgodnienia. Znasz kwotę? Dopisz ją w Pracach dodatkowych.'},
  {id:'na',t:'Naprawa',uz:3,q:'Naprawy',r:'napr',f:['@napr','naprBlok']},
  {id:'st',t:'Stabilizacja',uz:2,q:'Stabilizacja',r:'stab',f:['@stab','stabM2']},
  {id:'ko',t:'Koloryzacja',uz:4,q:'Koloryzacja',kolor:1,info:'Koloryzacja liczy się od metrażu z kafelka Odnowienie podłogi.',f:['cw_kolor']},
  {id:'do',t:'Prace dodatkowe',dod:1,f:['dodBlok']},
  {id:'me',t:'Pomoc z meblami',uz:5,q:'Przesunięcie mebli',r:'meble',f:['@meble','mebleKw']},
  {id:'sc',t:'Renowacja schodów',uz:6,q:'Renowacja schodów',info:'Pozycja 1 kpl., cena do uzgodnienia po wizji lokalnej.'},
  {id:'kl',t:'Klient, adres i zdjęcia',szer:1,f:['drop','miniatury','imieKl','ulicaKl','kodKl','miastoKl','dzielKl','obiektKl','pietroKl','@winda','terminKl','telKl','mailKl','kopiaBlok','vatBlok']},
  {id:'sms',t:'Folder ofert i SMS klienta',szer:1,sms:1}];
 var CENNIK=[
  ['Podłoga',[['Odnowienie podłogi','cyklinowanie bezpyłowe + 3 warstwy lakieru','130 zł/m²','pod'],['Ryczałt SMART','poniżej 10 m², na gotowo - liczy się sam z metrażu','1 500 zł','pod','auto'],['Dopłata do małego metrażu','od 10 do 22 m² - liczy się sama z metrażu','+30 zł/m²','pod','auto'],['Twardy wosk zamiast lakieru','dopłata do odnowienia podłogi','+12 zł/m²','pod','wosk'],['Koloryzacja','barwienie przed lakierem','70 zł/m²','ko']]],
  ['Listwy',[['Wymiana listew','klasyczna lub MDF, z montażem','50 zł/mb','lw'],['Odświeżenie listew','zmatowienie i lakier','do uzgodnienia','lo']]],
  ['Naprawy',[['Stabilizacja','iniekcja luźnych, skrzypiących klepek','70 zł/m²','st'],['Naprawa ubytków','wymiana lub uzupełnienie klepek','wg wyceny','na']]],
  ['Inne',[['Pomoc z meblami','przesunięcie mebli przez ekipę','300 zł','me'],['Renowacja schodów','po wizji lokalnej','do uzgodnienia','sc'],['Prace dodatkowe','własna pozycja z ceną','wpisujesz sam','do']]]];
 var $=function(i){return document.getElementById(i);};
 var zl=function(n){return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g,' ')+' zł';};
 function blok(f){if(f.charAt(0)==='@'){var r=document.querySelector('form.ai-form input[name="'+f.slice(1)+'"]');return r&&r.closest('form.ai-form>*');}
  var e=$(f);if(!e)return null;if(/^(cw_|drop$|miniatury$)/.test(f))return e;return e.closest('form.ai-form>*')||e;}
 function radio(n,ktory){var rs=[].slice.call(document.querySelectorAll('input[name="'+n+'"]'));
  var x=rs.filter(function(r){var t=(r.closest('label')||{}).textContent||'';return ktory==='tak'?(n==='meble'?t.trim()==='tak':r.value!=='nie'):(n==='meble'?t.trim()==='nie':r.value==='nie');})[0];
  if(n==='listwy'&&ktory==='tak'){var cur=rs.filter(function(r){return r.checked;})[0];if(cur&&cur.value!=='nie')return;x=rs.filter(function(r){return r.value==='klasyczna';})[0];}
  if(n==='stab'||n==='napr'){if(ktory==='tak')x=rs.filter(function(r){return r.value==='tak';})[0];}
  if(x&&!x.checked){x.checked=true;x.dispatchEvent(new Event('change',{bubbles:true}));x.dispatchEvent(new Event('input',{bubbles:true}));}}
 function ustaw(k,v){if(k.uz!=null){var c=$('uzg'+k.uz);if(c&&c.checked!==v){c.checked=v;c.dispatchEvent(new Event('change',{bubbles:true}));}}
  if(k.r)radio(k.r,v?'tak':'nie');
  if(k.kolor){var w=$('wyk');if(w){var i=v?4:0;if((w.selectedIndex===4)!==v){w.selectedIndex=i;w.dispatchEvent(new Event('change',{bubbles:true}));}}}
  if(k.dod){if(v&&!document.querySelector('#dodLista .dod-w')){var p=$('dodPlus');p&&p.click();}
   [].forEach.call(document.querySelectorAll('#dodLista .dod-w'),function(w){var u=w.querySelector('.dod-u');if(u&&u.checked!==v&&(!v||(w.querySelector('.dod-o')||{}).value)){u.checked=v;u.dispatchEvent(new Event('change',{bubbles:true}));}});}
  odswiez();}
 function jest(k){if(k.uz!=null){var c=$('uzg'+k.uz);return !!(c&&c.checked);}
  if(k.dod)return [].some.call(document.querySelectorAll('#dodLista .dod-o'),function(o){return o.value.trim();});return false;}
 function kwota(k){var A;try{A=window.spArkusz&&window.spArkusz();}catch(e){}if(!A)return '';
  var P=A.poz.filter(function(p){return k.dod?(p.length<6&&!/^\*/.test(p[0])):(p[6]===k.q||(k.id==='pod'&&/^\*/.test(p[0])));});
  var s=0,uzg=false;P.forEach(function(p){if(typeof p[1]==='number'&&p[2])s+=p[1]*p[2];else if(p[1]&&p[1]!==0)uzg=true;});
  return s>0?zl(s):(uzg?'do uzgodnienia':'');}
 /* pola przeniesione do kafelkow nie sa juz dziecmi form.ai-form - kopia regul ".ai-form > ..." dla ".wu-p > ..." */
 function kopiujCss(){var out=[];function przejdz(R,med){[].forEach.call(R,function(r){
   if(r.cssRules&&r.media){przejdz(r.cssRules,r.media.mediaText);return;}
   if(!r.selectorText||!/ai-form\s*>/.test(r.selectorText))return;
   var sel=r.selectorText.split(',').filter(function(x){return /ai-form\s*>/.test(x);}).map(function(x){return x.replace(/ai-form\s*>/g,'ai-form .wu-p >');}).join(',');
   var t=sel+'{'+r.style.cssText+'}';out.push(med?'@media '+med+'{'+t+'}':t);});}
  [].forEach.call(document.styleSheets,function(sh){try{przejdz(sh.cssRules,'');}catch(e){}});
  var st=document.createElement('style');st.id='wu-css-kopia';st.textContent=out.join('\n');document.body.appendChild(st);}
 function zbuduj(){
  var form=document.querySelector('form.ai-form');if(!form||$('wu'))return;
  kopiujCss();
  document.documentElement.classList.add('wu');
  var h=document.querySelector('#wycena .sticky h2');if(h)h.textContent='Wyceń usługę';
  var oc=document.querySelector('#wycena .sticky .oczko');if(oc)oc.lastChild.textContent='SMARTPARKIET · Analizator';
  var wu=document.createElement('div');wu.id='wu';
  wu.innerHTML='<div class="wu-seg" role="tablist"><button type="button" class="on" data-v="k">Wyceń usługę</button><button type="button" data-v="c">Usługa z cennika</button></div>'+
   '<div id="wuK"><p class="wu-h">Co robimy u klienta?</p><div class="wu-grid" id="wuG"></div></div>'+
   '<div id="wuC" hidden><input class="wu-szuk" id="wuSz" type="search" placeholder="Szukaj usługi, np. listwy" autocomplete="off"><div class="wu-chips" id="wuCh"></div><div id="wuL"></div></div>';
  form.insertBefore(wu,form.firstChild);
  var G=$('wuG');
  K.forEach(function(k){var d=document.createElement('div');d.className='wu-k'+(k.szer?' wu-szer':'');d.id='wu_'+k.id;
   d.innerHTML='<button type="button" class="wu-t" aria-expanded="false"><span class="wu-ik"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+IK[k.id]+'</svg></span><span class="wu-n">'+k.t+'</span><span class="wu-s">'+(k.szer?(k.sms?'wklej wiadomość, otwórz zapisaną ofertę':'kontakt, adres, termin, zdjęcia'):'dotknij, aby dodać')+'</span></button><div class="wu-p"></div>';
   var P=d.querySelector('.wu-p');
   if(!k.szer){var sw=document.createElement('label');sw.className='wu-sw';sw.innerHTML='<span>Robimy - w wycenie</span><input type="checkbox">';P.appendChild(sw);
    var cb=sw.querySelector('input');cb.onchange=function(){ustaw(k,cb.checked);};k.cb=cb;}
   if(k.info){var i=document.createElement('p');i.className='wu-info';i.textContent=k.info;P.appendChild(i);}
   (k.f||[]).forEach(function(f){var b=blok(f);if(b)P.appendChild(b);});
   if(k.sms){var sb=form.querySelector('.sms-box');if(sb)P.appendChild(sb);}
   var z=document.createElement('button');z.type='button';z.className='wu-zamk';z.textContent='Gotowe - zwiń';P.appendChild(z);
   z.onclick=function(){d.classList.remove('otw');d.scrollIntoView({block:'nearest',behavior:'smooth'});};
   /* wpisana ilosc / cena w kafelku = automatycznie "robimy" */
   P.addEventListener('input',function(e){if(!k.cb||e.target===k.cb)return;
    /* prace dodatkowe: wpisana pozycja = "robimy (w zakresie)" przy tej pozycji */
    var dw=e.target.closest&&e.target.closest('.dod-w');if(dw){var u=dw.querySelector('.dod-u');if(u&&!u.checked&&(dw.querySelector('.dod-o')||{}).value){u.checked=true;u.dispatchEvent(new Event('change',{bubbles:true}));}}var v=parseFloat(String(e.target.value||'').replace(',','.'));
    if((e.target.type==='number'&&v>0)||(e.target.classList&&e.target.classList.contains('dod-o')&&e.target.value.trim())){if(!jest(k))ustaw(k,true);}});
   d.querySelector('.wu-t').onclick=function(){var o=!d.classList.contains('otw');
    [].forEach.call(G.querySelectorAll('.wu-k.otw'),function(x){x.classList.remove('otw');x.querySelector('.wu-t').setAttribute('aria-expanded','false');});
    if(o){d.classList.add('otw');this.setAttribute('aria-expanded','true');setTimeout(function(){d.scrollIntoView({block:'start',behavior:'smooth'});},60);}};
   k.el=d;G.appendChild(d);});
  /* cennik */
  var ch=$('wuCh'),L=$('wuL'),kat='Wszystkie';
  ['Wszystkie'].concat(CENNIK.map(function(c){return c[0];})).forEach(function(n,i){var b=document.createElement('button');b.type='button';b.textContent=n;if(!i)b.className='on';
   b.onclick=function(){kat=n;[].forEach.call(ch.children,function(x){x.classList.toggle('on',x===b);});lista();};ch.appendChild(b);});
  function lista(){var q=($('wuSz').value||'').toLowerCase().trim();L.innerHTML='';
   CENNIK.forEach(function(c){if(kat!=='Wszystkie'&&kat!==c[0])return;var R=c[1].filter(function(r){return !q||(r[0]+' '+r[1]).toLowerCase().indexOf(q)>=0;});if(!R.length)return;
    var s=document.createElement('div');s.className='wu-kat';s.innerHTML='<b>'+c[0]+'</b>';
    R.forEach(function(r){var k=K.filter(function(x){return x.id===r[3];})[0],w=document.createElement('div');w.className='wu-r'+(jest(k)?' jest':'');
     var wy=$('wyk'),ma=r[4]==='auto'?false:(r[4]==='wosk'?!!(wy&&wy.selectedIndex===3):jest(k));w.className='wu-r'+(ma?' jest':'');
     w.innerHTML='<span class="rn">'+r[0]+'</span><span class="rd">'+r[1]+'</span><span class="rc">'+r[2]+'</span><button type="button">'+(r[4]==='auto'?'Otwórz':(ma?'✓ Jest':'Dodaj'))+'</button>';
     w.querySelector('button').onclick=function(){if(r[4]==='wosk'&&wy&&wy.selectedIndex!==3){wy.selectedIndex=3;wy.dispatchEvent(new Event('change',{bubbles:true}));}
      if(r[4]!=='auto'&&!jest(k))ustaw(k,true);widok('k');if(!k.el.classList.contains('otw'))k.el.querySelector('.wu-t').click();};s.appendChild(w);});
    L.appendChild(s);});}
  $('wuSz').oninput=lista;
  function widok(v){[].forEach.call(wu.querySelectorAll('.wu-seg button'),function(b){b.classList.toggle('on',b.dataset.v===v);});$('wuK').hidden=v!=='k';$('wuC').hidden=v!=='c';if(v==='c')lista();}
  [].forEach.call(wu.querySelectorAll('.wu-seg button'),function(b){b.onclick=function(){widok(b.dataset.v);};});
  /* dolny pasek: kwota + podglad PDF + wyslij (klikaja oryginalne przyciski silnika) */
  var bar=document.createElement('div');bar.id='wuBar';
  bar.innerHTML='<div><small>Netto</small><b id="wuSum">0 zł</b></div><button type="button" class="pdf">Podgląd PDF</button><button type="button" class="wys">Wyślij</button>';
  document.body.appendChild(bar);
  bar.querySelector('.pdf').onclick=function(){var b=$('podgladOferty');b&&b.click();};
  bar.querySelector('.wys').onclick=function(){var b=$('wyslij');if(b){b.scrollIntoView({block:'center',behavior:'smooth'});b.click();}};
  odswiez();setInterval(odswiez,800);}
 function odswiez(){K.forEach(function(k){if(!k.el||k.szer)return;var t=jest(k);k.el.classList.toggle('tak',t);if(k.cb)k.cb.checked=t;
   var s=k.el.querySelector('.wu-s'),kw=t?kwota(k):'';s.textContent=t?('✓ '+(kw||'w wycenie')):'dotknij, aby dodać';});
  var A;try{A=window.spArkusz&&window.spArkusz();}catch(e){}var e=$('wuSum');if(e&&A)e.textContent=zl(A.suma||0);}
 window.spWuOdswiez=odswiez;
 function start(){setTimeout(zbuduj,700);}
 if(document.readyState==='complete')start();else window.addEventListener('load',start);
})();
</script>
<!-- wycen-usluge KONIEC -->'''
s = s.rstrip() + NL + SKORKA.replace('\n', NL) + NL
open(os.path.join(TU, 'wycen-usluge.html'), 'w', encoding='utf-8', newline='').write(s)
print('wycen-usluge.html gotowy', len(s), 'znakow')
