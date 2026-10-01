
(function(){
  var POZ=[
    {n:'Oględziny, pomiar wilgotności, protokół', j:'ryczałt', s:250, il:function(d){return 1}},
    {n:'Demontaż uszkodzonej podłogi',            j:'m²',      s:35,  il:function(d){return d.m2zal}},
    {n:'Osuszanie, najem osuszacza',              j:'doba',    s:90,  il:function(d){return d.u_plesn?7:4}},
    {n:'Wywóz i utylizacja',                      j:'ryczałt', s:200, il:function(d){return d.m2zal>0?1:0}},
    {n:'Stabilizacja i naprawy',                  j:'m²',      s:65,  il:function(d){return d.u_odsp?d.m2zal:0}},
    {n:'Uzupełnienie klepki z odzysku',           j:'m²',      s:120, il:function(d){return d.u_spec?d.m2zal:0}},
    {n:'Cyklinowanie bezpyłowe',                  j:'m²',      s:130, il:function(d){return d.m2}},
    {n:'Lakierowanie lub olejowanie',             j:'m²',      s:0,   il:function(d){return d.m2}},
    {n:'Koloryzacja',                             j:'m²',      s:55,  il:function(d){return 0}},
    {n:'Listwy przypodłogowe',                    j:'mb',      s:52,  il:function(d){return d.u_listwy?Math.round(Math.sqrt(d.m2||0)*4):0}},
    {n:'Schody: stopień z podstopnicą',           j:'komplet', s:250, il:function(d){return d.u_schody?1:0}},
    {n:'Zabezpieczenie pomieszczeń i mebli',      j:'ryczałt', s:150, il:function(d){return d.m2>0?1:0}},
    {n:'Dojazd poza Warszawę',                    j:'km',      s:2,   il:function(d){return 0}}
  ];
  var KLUCZ='smartparkiet_ekspertyza_v1';
  var tb=document.getElementById('ek-poz');
  if(!tb)return;
  var reczne=[], nadpisane={};

  function zl(x){return (Math.round(x*100)/100).toFixed(2).replace('.',',')+' zł';}
  function lp(v){v=parseFloat(String(v).replace(',','.'));return isFinite(v)?v:0;}

  function dane(){
    var d={};
    document.querySelectorAll('[data-p]').forEach(function(e){
      d[e.getAttribute('data-p')] = e.type==='checkbox' ? e.checked : e.value;
    });
    d.m2=lp(d.m2); d.m2zal=lp(d.m2zal); d.rok=lp(d.rok); d.wilg=lp(d.wilg);
    if(d.m2zal>d.m2 && d.m2>0) d.m2zal=d.m2;
    return d;
  }

  function rysuj(){
    var d=dane(), html='';
    POZ.forEach(function(p,i){
      var il = (i in nadpisane) ? nadpisane[i] : p.il(d);
      il = Math.round(lp(il)*100)/100;
      var st = p._s!==undefined ? p._s : p.s;
      html+='<tr'+(il<=0?' class="ek-pusta"':'')+'>'
        +'<td>'+p.n+'</td>'
        +'<td><input type="text" data-knr="'+i+'" placeholder="&mdash;"></td>'
        +'<td class="ek-c-ile"><input type="number" step="0.1" min="0" data-il="'+i+'" value="'+il+'"></td>'
        +'<td class="ek-c-j">'+p.j+'</td>'
        +'<td class="ek-c-st"><input type="number" step="1" min="0" data-st="'+i+'" value="'+st+'"></td>'
        +'<td class="ek-c-w">'+zl(il*st)+'</td></tr>';
    });
    reczne.forEach(function(r,k){
      var pustaR=(!r.n||lp(r.il)<=0);
      html+='<tr'+(pustaR?' class="ek-pusta"':'')+'><td><input type="text" data-rn="'+k+'" value="'+(r.n||'').replace(/"/g,'&quot;')+'" placeholder="nazwa pozycji"></td>'
        +'<td><input type="text" data-rk="'+k+'" value="'+(r.k||'')+'" placeholder="&mdash;"></td>'
        +'<td class="ek-c-ile"><input type="number" step="0.1" min="0" data-ri="'+k+'" value="'+(r.il||0)+'"></td>'
        +'<td class="ek-c-j"><input type="text" data-rj="'+k+'" value="'+(r.j||'szt.')+'"></td>'
        +'<td class="ek-c-st"><input type="number" step="1" min="0" data-rs="'+k+'" value="'+(r.s||0)+'"></td>'
        +'<td class="ek-c-w">'+zl(lp(r.il)*lp(r.s))+' <button class="ek-usun ek-noprint" type="button" data-rx="'+k+'" aria-label="Usuń">&times;</button></td></tr>';
    });
    tb.innerHTML=html;
    sumuj(); pakiety(d); zapisz();
  }

  function pozycje(){
    var d=dane(), out=[];
    POZ.forEach(function(p,i){
      var il=(i in nadpisane)?lp(nadpisane[i]):lp(p.il(d));
      var st=p._s!==undefined?p._s:p.s;
      var knr=tb.querySelector('[data-knr="'+i+'"]');
      if(il>0) out.push({n:p.n,k:knr?knr.value:'',il:il,j:p.j,s:st,w:il*st});
    });
    reczne.forEach(function(r){ if(lp(r.il)>0&&r.n) out.push({n:r.n,k:r.k||'',il:lp(r.il),j:r.j||'szt.',s:lp(r.s),w:lp(r.il)*lp(r.s)}); });
    return out;
  }

  function sumuj(){
    var netto=0; pozycje().forEach(function(p){netto+=p.w;});
    var vat=lp(document.getElementById('ek-vat').value);
    document.getElementById('ek-netto').textContent=zl(netto);
    document.getElementById('ek-vat-et').textContent=vat+' %';
    document.getElementById('ek-vat-kw').textContent=zl(netto*vat/100);
    document.getElementById('ek-brutto').textContent=zl(netto*(1+vat/100));
  }

  var EXOT=['merbau','teak','iroko','doussie','jatoba'];
  function pakiety(d){
    var w=[], op='';
    if(d.m2zal>0||d.u_prze||d.u_spec||d.u_plesn){w.push(['SMART EMERGENCY™',1]);op='Szkoda wodna, więc prowadzimy to jako zgłoszenie awaryjne: oględziny do 24 h i kosztorys w formie dla ubezpieczyciela.';}
    if((d.rok>0&&d.rok<1945)||d.podloze==='na legarach'||d.podloze==='na gwoździe'){w.push(['SMART KAMIENICA RESTORE™',0]);op+=' Podłoga w starym układzie, ubytki uzupełniamy klepką z odzysku.';}
    if(EXOT.indexOf(d.gatunek)>-1){w.push(['SMART EXOTIC FLOOR™',0]);op+=' Drewno egzotyczne wymaga wykończenia dobranego do gatunku.';}
    if(d.obiekt==='biuro'||d.obiekt==='lokal usługowy'||d.obiekt==='obiekt publiczny'){w.push(['SMART PUBLIC RESTORE™',0]);op+=' Obiekt czynny, pracujemy etapami poza godzinami działalności.';}
    if(d.termin!=='zwykły'&&d.m2>0&&d.m2<=40){w.push(['SMART EXPRESS 48H™',0]);op+=' Metraż i termin mieszczą się w trybie 48-godzinnym.';}
    if(!w.length&&d.m2>0){w.push(['SMART PREMIUM FLOOR™',1]);op='Zakres bez znamion szkody wodnej, więc standardowa renowacja pełna.';}
    w.push(['SMART ZERO DUST™',0]);
    if(w.length===1){op='Proszę uzupełnić metraż i zakres szkody, program dobierze się sam.';}
    document.getElementById('ek-pakiety').innerHTML=w.map(function(x){
      return '<span class="ek-chip'+(x[1]?' ek-glow':'')+'">'+x[0]+'</span>';}).join('');
    document.getElementById('ek-pakiet-op').textContent=op.trim()+(w.length>1?' Bezpyłowo pracujemy zawsze.':'');
  }

  function zapisz(){
    try{
      var s={pola:{},knr:{},nad:nadpisane,rec:reczne,vat:document.getElementById('ek-vat').value};
      document.querySelectorAll('[data-p]').forEach(function(e){
        s.pola[e.getAttribute('data-p')]= e.type==='checkbox'?e.checked:e.value;});
      tb.querySelectorAll('[data-knr]').forEach(function(e){ if(e.value) s.knr[e.getAttribute('data-knr')]=e.value;});
      POZ.forEach(function(p,i){ if(p._s!==undefined) s['st'+i]=p._s;});
      localStorage.setItem(KLUCZ,JSON.stringify(s));
    }catch(e){}
  }
  function wczytaj(){
    try{
      var s=JSON.parse(localStorage.getItem(KLUCZ)||'null'); if(!s)return;
      document.querySelectorAll('[data-p]').forEach(function(e){
        var k=e.getAttribute('data-p'); if(!(k in s.pola))return;
        if(e.type==='checkbox') e.checked=!!s.pola[k]; else e.value=s.pola[k];});
      nadpisane=s.nad||{}; reczne=s.rec||[];
      if(s.vat) document.getElementById('ek-vat').value=s.vat;
      POZ.forEach(function(p,i){ if(('st'+i) in s) p._s=s['st'+i];});
      rysuj();
      Object.keys(s.knr||{}).forEach(function(i){
        var e=tb.querySelector('[data-knr="'+i+'"]'); if(e)e.value=s.knr[i];});
    }catch(e){}
  }

  document.addEventListener('input',function(e){
    var t=e.target;
    if(t.hasAttribute&&t.hasAttribute('data-p')){ rysuj(); return; }
    if(t.hasAttribute&&t.hasAttribute('data-il')){ nadpisane[t.getAttribute('data-il')]=t.value; odswiezWiersz(); return; }
    if(t.hasAttribute&&t.hasAttribute('data-st')){ POZ[t.getAttribute('data-st')]._s=lp(t.value); odswiezWiersz(); return; }
    if(t.hasAttribute&&t.hasAttribute('data-knr')){ zapisz(); return; }
    var m;
    if((m=t.getAttribute&&t.getAttribute('data-rn'))!==null&&m!==undefined){reczne[m].n=t.value;odswiezWiersz();return;}
    if((m=t.getAttribute&&t.getAttribute('data-rk'))!==null&&m!==undefined){reczne[m].k=t.value;zapisz();return;}
    if((m=t.getAttribute&&t.getAttribute('data-ri'))!==null&&m!==undefined){reczne[m].il=t.value;odswiezWiersz();return;}
    if((m=t.getAttribute&&t.getAttribute('data-rj'))!==null&&m!==undefined){reczne[m].j=t.value;zapisz();return;}
    if((m=t.getAttribute&&t.getAttribute('data-rs'))!==null&&m!==undefined){reczne[m].s=t.value;odswiezWiersz();return;}
  });

  // przeliczenie bez przerysowania tabeli, zeby nie uciekal kursor
  function odswiezWiersz(){
    var d=dane();
    POZ.forEach(function(p,i){
      var ie=tb.querySelector('[data-il="'+i+'"]'), se=tb.querySelector('[data-st="'+i+'"]');
      if(!ie||!se)return;
      var w=lp(ie.value)*lp(se.value);
      ie.closest('tr').querySelector('.ek-c-w').childNodes[0].nodeValue=zl(w);
    });
    reczne.forEach(function(r,k){
      var ie=tb.querySelector('[data-ri="'+k+'"]'), se=tb.querySelector('[data-rs="'+k+'"]');
      if(!ie||!se)return;
      ie.closest('tr').querySelector('.ek-c-w').childNodes[0].nodeValue=zl(lp(ie.value)*lp(se.value))+' ';
    });
    sumuj(); zapisz();
  }

  document.getElementById('ek-vat').addEventListener('change',function(){sumuj();zapisz();});
  document.getElementById('ek-dodaj').addEventListener('click',function(){reczne.push({n:'',k:'',il:0,j:'szt.',s:0});rysuj();});
  tb.addEventListener('click',function(e){
    var k=e.target.getAttribute&&e.target.getAttribute('data-rx');
    if(k!==null&&k!==undefined){reczne.splice(+k,1);rysuj();}
  });

  function komunikat(t){var i=document.getElementById('ek-info');i.textContent=t;setTimeout(function(){i.textContent='';},2600);}

  function tekst(){
    var d=dane(), p=pozycje(), netto=0; p.forEach(function(x){netto+=x.w;});
    var vat=lp(document.getElementById('ek-vat').value);
    var L=['SMARTPARKIET - kosztorys naprawy podłogi po zalaniu',''];
    L.push('Adres: '+(d.adres||'-'));
    L.push('Numer szkody: '+(d.szkoda||'-')+'   Ubezpieczyciel: '+(d.ubezp||'-'));
    L.push('Data oględzin: '+(d.data||'-')+'   Data zdarzenia: '+(d.datazal||'-'));
    L.push('Podłoga: '+d.rodzaj+', '+d.gatunek+', '+d.podloze);
    L.push('Powierzchnia: '+d.m2+' m², zalana: '+d.m2zal+' m², wilgotność: '+(d.wilg||'-')+' %');
    if(d.opis) L.push('Uwagi: '+d.opis);
    L.push('');
    p.forEach(function(x){L.push(x.n+(x.k?' ['+x.k+']':'')+' - '+x.il+' '+x.j+' x '+x.s+' zł = '+zl(x.w));});
    L.push('');
    L.push('Razem netto: '+zl(netto));
    L.push('VAT '+vat+' %: '+zl(netto*vat/100));
    L.push('Razem brutto: '+zl(netto*(1+vat/100)));
    return L.join('\n');
  }

  document.getElementById('ek-kopiuj').addEventListener('click',function(){
    var t=tekst();
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){komunikat('Skopiowane do schowka');},function(){komunikat('Nie udało się skopiować');});
    }else{
      var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();
      try{document.execCommand('copy');komunikat('Skopiowane do schowka');}catch(e){komunikat('Nie udało się skopiować');}
      document.body.removeChild(a);
    }
  });

  /* ---------- zapis .xlsx bez zadnej biblioteki ----------
     xlsx to zwykly ZIP z plikami XML. Skladamy go recznie, metoda "store"
     (bez kompresji), bo pliki sa male, a dzieki temu nie ma zaleznosci. */
  var CRC=(function(){var t=[],c,n,k;for(n=0;n<256;n++){c=n;
    for(k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}return t;})();
  function crc32(u8){var c=0xFFFFFFFF;for(var i=0;i<u8.length;i++)c=CRC[(c^u8[i])&0xFF]^(c>>>8);
    return (c^0xFFFFFFFF)>>>0;}
  function bajty(s){return new TextEncoder().encode(s);}
  function zip(pliki){
    var lok=[], cen=[], off=0;
    var d=new Date(), czas=((d.getHours()<<11)|(d.getMinutes()<<5)|(d.getSeconds()/2))&0xFFFF;
    var data=(((d.getFullYear()-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate())&0xFFFF;
    function u8(n){return [n&255];}
    function u16(n){return [n&255,(n>>>8)&255];}
    function u32(n){return [n&255,(n>>>8)&255,(n>>>16)&255,(n>>>24)&255];}
    pliki.forEach(function(p){
      var nm=bajty(p.n), tr=bajty(p.t), cr=crc32(tr);
      var h=[].concat(u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(czas),u16(data),
              u32(cr),u32(tr.length),u32(tr.length),u16(nm.length),u16(0));
      lok.push(new Uint8Array(h),nm,tr);
      cen.push(new Uint8Array([].concat(u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),
              u16(czas),u16(data),u32(cr),u32(tr.length),u32(tr.length),
              u16(nm.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(off))), nm);
      off += h.length+nm.length+tr.length;
    });
    var cs=0; cen.forEach(function(x){cs+=x.length;});
    var eocd=new Uint8Array([].concat(u32(0x06054b50),u16(0),u16(0),
              u16(pliki.length),u16(pliki.length),u32(cs),u32(off),u16(0)));
    return new Blob(lok.concat(cen,[eocd]),{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  }
  function xe(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function kol(i){var s='';i++;while(i>0){var m=(i-1)%26;s=String.fromCharCode(65+m)+s;i=(i-m-1)/26;}return s;}

  /* wiersze: [{c:[{v,t,s,f}]}] ; t: 's' tekst, 'n' liczba */
  function arkusz(wiersze, szer, scal){
    var x='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      +'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
      +'<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>'
      +'<cols>'+szer.map(function(w,i){return '<col min="'+(i+1)+'" max="'+(i+1)+'" width="'+w+'" customWidth="1"/>';}).join('')+'</cols>'
      +'<sheetData>';
    wiersze.forEach(function(r,ri){
      if(!r||!r.c||!r.c.length){x+='<row r="'+(ri+1)+'"/>';return;}
      x+='<row r="'+(ri+1)+'"'+(r.h?' ht="'+r.h+'" customHeight="1"':'')+'>';
      r.c.forEach(function(c,ci){
        if(c==null)return;
        var ref=kol(ci)+(ri+1), st=' s="'+(c.s||0)+'"';
        if(c.f!==undefined){x+='<c r="'+ref+'"'+st+'><f>'+xe(c.f)+'</f><v>'+(c.v||0)+'</v></c>';}
        else if(c.t==='n'){x+='<c r="'+ref+'"'+st+'><v>'+(isFinite(c.v)?c.v:0)+'</v></c>';}
        else if(c.v===''||c.v==null){x+='<c r="'+ref+'"'+st+'/>';}
        else{x+='<c r="'+ref+'" t="inlineStr"'+st+'><is><t xml:space="preserve">'+xe(c.v)+'</t></is></c>';}
      });
      x+='</row>';
    });
    x+='</sheetData>';
    if(scal&&scal.length)x+='<mergeCells count="'+scal.length+'">'+scal.map(function(m){return '<mergeCell ref="'+m+'"/>';}).join('')+'</mergeCells>';
    x+='<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>'
      +'<pageSetup paperSize="9" orientation="portrait" fitToWidth="1" fitToHeight="0"/></worksheet>';
    return x;
  }

  var STYLE='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
   +'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
   +'<numFmts count="4">'
   +'<numFmt numFmtId="164" formatCode="#,##0.00&quot; zł&quot;"/>'
   +'<numFmt numFmtId="165" formatCode="#,##0.00"/>'
   +'<numFmt numFmtId="166" formatCode="0.0%"/>'
   +'<numFmt numFmtId="167" formatCode="#,##0.0"/></numFmts>'
   +'<fonts count="7">'
   +'<font><sz val="10"/><name val="Calibri"/></font>'
   +'<font><b/><sz val="10"/><name val="Calibri"/></font>'
   +'<font><b/><sz val="18"/><name val="Calibri"/></font>'
   +'<font><b/><sz val="9"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
   +'<font><sz val="9"/><color rgb="FF707176"/><name val="Calibri"/></font>'
   +'<font><b/><sz val="11"/><color rgb="FFB83C06"/><name val="Calibri"/></font>'
   +'<font><b/><sz val="14"/><color rgb="FFB83C06"/><name val="Calibri"/></font></fonts>'
   +'<fills count="5"><fill><patternFill patternType="none"/></fill>'
   +'<fill><patternFill patternType="gray125"/></fill>'
   +'<fill><patternFill patternType="solid"><fgColor rgb="FF1B2A3A"/><bgColor indexed="64"/></patternFill></fill>'
   +'<fill><patternFill patternType="solid"><fgColor rgb="FFF6F4F1"/><bgColor indexed="64"/></patternFill></fill>'
   +'<fill><patternFill patternType="solid"><fgColor rgb="FFFDE7D8"/><bgColor indexed="64"/></patternFill></fill></fills>'
   +'<borders count="3"><border><left/><right/><top/><bottom/><diagonal/></border>'
   +'<border><left/><right/><top/><bottom style="thin"><color rgb="FFE7E3DD"/></bottom><diagonal/></border>'
   +'<border><left style="thin"><color rgb="FFCCCCCC"/></left><right style="thin"><color rgb="FFCCCCCC"/></right>'
   +'<top style="thin"><color rgb="FFCCCCCC"/></top><bottom style="thin"><color rgb="FFCCCCCC"/></bottom><diagonal/></border></borders>'
   +'<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
   +'<cellXfs count="16">'
   +'<xf xfId="0" numFmtId="0" fontId="0" fillId="0" borderId="0"/>'                                        /*0 zwykly*/
   +'<xf xfId="0" numFmtId="0" fontId="1" fillId="0" borderId="0" applyFont="1"/>'                          /*1 pogrubiony*/
   +'<xf xfId="0" numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/>'                          /*2 tytul*/
   +'<xf xfId="0" numFmtId="0" fontId="3" fillId="2" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>' /*3 naglowek tabeli*/
   +'<xf xfId="0" numFmtId="164" fontId="0" fillId="0" borderId="1" applyNumberFormat="1" applyBorder="1"/>' /*4 kwota*/
   +'<xf xfId="0" numFmtId="164" fontId="1" fillId="0" borderId="0" applyNumberFormat="1" applyFont="1"/>'   /*5 kwota pogrubiona*/
   +'<xf xfId="0" numFmtId="0" fontId="4" fillId="0" borderId="0" applyFont="1"/>'                           /*6 etykieta*/
   +'<xf xfId="0" numFmtId="167" fontId="0" fillId="0" borderId="1" applyNumberFormat="1" applyBorder="1"/>'  /*7 liczba 1 miejsce*/
   +'<xf xfId="0" numFmtId="166" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'                 /*8 procent*/
   +'<xf xfId="0" numFmtId="164" fontId="6" fillId="0" borderId="0" applyNumberFormat="1" applyFont="1"/>'   /*9 kwota duza*/
   +'<xf xfId="0" numFmtId="0" fontId="5" fillId="0" borderId="0" applyFont="1"/>'                           /*10 naglowek sekcji*/
   +'<xf xfId="0" numFmtId="0" fontId="0" fillId="0" borderId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>' /*11 zawijanie*/
   +'<xf xfId="0" numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1"/>'                         /*12 komorka tabeli*/
   +'<xf xfId="0" numFmtId="0" fontId="1" fillId="3" borderId="2" applyFont="1" applyFill="1" applyBorder="1"/>' /*13 panel naglowek*/
   +'<xf xfId="0" numFmtId="164" fontId="0" fillId="3" borderId="2" applyNumberFormat="1" applyFill="1" applyBorder="1"/>' /*14 panel kwota*/
   +'<xf xfId="0" numFmtId="0" fontId="0" fillId="3" borderId="2" applyFill="1" applyBorder="1"/>'           /*15 panel tekst*/
   +'</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';

  function xlsx(nazwaArk, wiersze, szer, scal){
    return zip([
      {n:'[Content_Types].xml', t:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        +'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        +'<Default Extension="xml" ContentType="application/xml"/>'
        +'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        +'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        +'<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>'},
      {n:'_rels/.rels', t:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'},
      {n:'xl/workbook.xml', t:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        +'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        +'<sheets><sheet name="'+xe(nazwaArk)+'" sheetId="1" r:id="rId1"/></sheets></workbook>'},
      {n:'xl/_rels/workbook.xml.rels', t:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        +'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'},
      {n:'xl/styles.xml', t:STYLE},
      {n:'xl/worksheets/sheet1.xml', t:arkusz(wiersze,szer,scal)}
    ]);
  }

  var KAT=['Dokumentacja','Osuszanie i demontaż','Osuszanie i demontaż','Osuszanie i demontaż',
           'Naprawa konstrukcji','Naprawa konstrukcji','Renowacja powierzchni','Renowacja powierzchni',
           'Renowacja powierzchni','Wykończenie','Wykończenie','Pozostałe','Pozostałe'];

  document.getElementById('ek-csv').addEventListener('click',function(){
    var d=dane(), p=pozycje();
    if(!p.length){komunikat('Najpierw proszę uzupełnić metraż');return;}
    var vat=lp(document.getElementById('ek-vat').value);
    var T=function(v,s){return {v:v,s:s||0};};
    var N=function(v,s){return {v:v,t:'n',s:s===undefined?4:s};};
    var F=function(f,v,s){return {f:f,v:v,s:s===undefined?4:s};};
    var W=[];
    function r(c){W.push({c:c});}
    function pusty(){W.push(null);}

    r([T('SMARTPARKIET',2)]);
    r([T('Kosztorys naprawy podłogi po zalaniu',1)]);
    pusty();
    r([T('DANE ZLECENIA',10)]);
    r([T('Adres',6),T(d.adres)]);
    r([T('Numer szkody',6),T(d.szkoda),null,null,null,null,T('Ubezpieczyciel',6),T(d.ubezp)]);
    r([T('Zgłaszający',6),T(d.kto),null,null,null,null,T('Telefon',6),T(d.tel)]);
    r([T('Data oględzin',6),T(d.data),null,null,null,null,T('Data zdarzenia',6),T(d.datazal)]);
    r([T('Kondygnacja',6),T(d.pietro),null,null,null,null,T('Rok budowy',6),(d.rok?{v:d.rok,t:'n',s:0}:T(''))]);
    pusty();
    r([T('PODŁOGA I SZKODA',10)]);
    r([T('Rodzaj',6),T(d.rodzaj),null,null,null,null,T('Gatunek',6),T(d.gatunek)]);
    r([T('Ułożenie',6),T(d.podloze),null,null,null,null,T('Źródło',6),T(d.zrodlo)]);
    r([T('Powierzchnia',6),N(d.m2,7),T('m²',6),null,null,null,T('Zalana',6),N(d.m2zal,7)]);
    var wPow=W.length;
    r([T('Wilgotność',6),N(d.wilg,7),T('%  (norma 7-11)',6)]);
    var usz=[];
    [['u_spec','spęcznienie'],['u_odsp','odspojenie'],['u_szcz','szczeliny'],['u_prze','przebarwienia'],
     ['u_plesn','pleśń'],['u_lakier','lakier'],['u_listwy','listwy'],['u_schody','schody']]
      .forEach(function(x){if(d[x[0]])usz.push(x[1]);});
    r([T('Uszkodzenia',6),T(usz.join(', ')||'brak')]);
    if(d.opis) r([T('Uwagi',6),T(d.opis,11)]);
    pusty();
    r([T('KOSZTORYS',10)]);
    var wN=W.length+1;
    r([T('Lp.',3),T('Pozycja',3),T('Podstawa',3),T('Ilość',3),T('j.m.',3),T('Stawka netto',3),T('Wartość netto',3)]);
    var w1=W.length+1;
    p.forEach(function(x,i){
      r([{v:i+1,t:'n',s:12},T(x.n,12),T(x.k,12),N(x.il,7),T(x.j,12),N(x.s,4),F(kol(3)+(W.length+1)+'*'+kol(5)+(W.length+1), x.w, 4)]);
    });
    var w2=W.length;
    pusty();
    var rN=W.length+1;
    r([null,null,null,null,null,T('Razem netto',1),F('SUM(G'+w1+':G'+w2+')', 0, 5)]);
    r([null,null,null,null,null,T('VAT '+vat+' %',1),F('G'+rN+'*'+(vat/100), 0, 5)]);
    r([null,null,null,null,null,T('Razem brutto',1),F('G'+rN+'+G'+(rN+1), 0, 9)]);
    var rB=W.length;
    pusty();pusty();
    r([T('.....................................',6),null,null,T('.....................................',6)]);
    r([T('podpis wykonawcy',6),null,null,T('podpis zgłaszającego',6)]);

    // ---- panel statystyk z boku (kolumny I,J) ----
    var netto=0,max={n:'',w:0},grupy={};
    p.forEach(function(x,i){netto+=x.w; if(x.w>max.w)max={n:x.n,w:x.w};
      var g=(i<KAT.length&&POZ[i]&&POZ[i].n===x.n)?KAT[i]:'Pozostałe';
      grupy[g]=(grupy[g]||0)+x.w;});
    // przypisz kategorie po nazwie, zeby zgadzalo sie przy pominietych pozycjach
    grupy={};
    p.forEach(function(x){var idx=-1;POZ.forEach(function(q,qi){if(q.n===x.n)idx=qi;});
      var g=idx>=0?KAT[idx]:'Pozostałe'; grupy[g]=(grupy[g]||0)+x.w;});
    var dni=Math.max(2, Math.ceil((d.m2||0)/18) + (d.m2zal>0?4:0) + (d.u_spec?2:0));
    var S=[
      ['STATYSTYKI',null,13],
      ['Koszt za m² powierzchni', {f:'IF(B'+wPow+'=0,0,G'+rN+'/B'+wPow+')', v:netto/(d.m2||1), fs:14}, 14],
      ['Udział powierzchni zalanej', {f:'IF(B'+wPow+'=0,0,H'+wPow+'/B'+wPow+')', v:(d.m2?d.m2zal/d.m2:0), fs:8}, null],
      ['Liczba pozycji', {v:p.length, t:'n', s:15}, null],
      ['Największa pozycja', {v:max.n, s:15}, null],
      ['Wartość największej', {v:max.w, t:'n', s:14}, null],
      ['Udział największej', {v:(netto?max.w/netto:0), t:'n', s:8}, null],
      ['',null,null],
      ['STRUKTURA KOSZTÓW',null,13]
    ];
    ['Dokumentacja','Osuszanie i demontaż','Naprawa konstrukcji','Renowacja powierzchni','Wykończenie','Pozostałe']
      .forEach(function(g){ if(grupy[g]) S.push([g, {v:grupy[g], t:'n', s:14}, null]); });
    S.push(['',null,null]);
    S.push(['WSKAŹNIKI',null,13]);
    S.push(['Wilgotność zmierzona', {v:(d.wilg||0), t:'n', s:15}, null]);
    S.push(['Przekroczenie normy 11 %', {v:Math.max(0,(d.wilg||0)-11), t:'n', s:15}, null]);
    S.push(['Szacowany czas robót (dni)', {v:dni, t:'n', s:15}, null]);
    S.push(['Dobrany program', {v:(document.querySelector('.ek-chip.ek-glow')||{textContent:'-'}).textContent, s:15}, null]);
    S.push(['Standard wykonania', {v:'SMART ZERO DUST™', s:15}, null]);
    S.forEach(function(x,i){
      var ri=3+i;
      while(W.length<=ri)W.push(null);
      if(!W[ri])W[ri]={c:[]};
      var c=W[ri].c;
      while(c.length<8)c.push(null);
      c[8]={v:x[0], s:x[2]!=null?x[2]:15};
      c[9]=x[1]?(x[1].f?{f:x[1].f,v:x[1].v,s:x[1].fs||14}:{v:x[1].v,t:x[1].t,s:x[1].s==null?15:x[1].s}):{v:'',s:15};
    });

    var szer=[6,40,14,9,8,13,15,3,28,16];
    var blob=xlsx('Kosztorys', W, szer, ['A1:G1','A2:G2']);
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='kosztorys_'+((d.szkoda||d.adres||'zalanie').replace(/[^\w\-]+/g,'_').slice(0,40))+'.xlsx';
    document.body.appendChild(a);a.click();
    setTimeout(function(){URL.revokeObjectURL(a.href);document.body.removeChild(a);},1500);
    komunikat('Pobrany plik .xlsx');
  });

  document.getElementById('ek-druk').addEventListener('click',function(){window.print();});
  document.getElementById('ek-czysc').addEventListener('click',function(){
    if(!confirm('Wyczyścić cały formularz?'))return;
    try{localStorage.removeItem(KLUCZ);}catch(e){}
    document.querySelectorAll('[data-p]').forEach(function(e){
      if(e.type==='checkbox')e.checked=false; else if(e.tagName==='SELECT')e.selectedIndex=0; else e.value='';});
    nadpisane={};reczne=[];POZ.forEach(function(p){delete p._s;});
    rysuj();komunikat('Wyczyszczone');
  });

  rysuj(); wczytaj();

  /* MOST DLA WKLEJONEGO KOSZTORYSU
     Parser wklejki siedzi w osobnym module, wiec udostepniamy mu pozycje
     przez window. Wiersze z cudzego kosztorysu (np. od ubezpieczyciela)
     wchodza jako pozycje wlasne, a standardowe pozycje zerujemy, zeby
     suma odpowiadala temu, co przyszlo. Kazda liczbe i tak mozna nadpisac. */
  window.ekWczytajKosztorys=function(wiersze){
    if(!wiersze||!wiersze.length)return 0;
    reczne=wiersze.map(function(r){
      return {n:r.n||'', k:r.k||'', il:r.il||0, j:r.j||'szt.', s:r.s||0};
    });
    POZ.forEach(function(p,i){nadpisane[i]=0;});
    rysuj();
    return reczne.length;
  };

})();

/* WKLEJONY KOSZTORYS KNR
   Obsluguje przypadek, w ktorym w pole "Szybkie wypelnienie" trafia cala
   tabela kosztorysowa (skopiowana z Excela albo z wiadomosci), a nie dane
   klienta. Rozpoznaje wiersze typu:
     2.1  KNR 4-01 0819  Zerwanie zalanej klepki debowej  m2  30,00  25,00 zl  750,00 zl
   Dziala i dla wklejki z tabulatorami (prosto z Excela), i dla tekstu,
   w ktorym tabulatory sie pogubily (np. po przejsciu przez komunikator).
   Podpina sie w fazie przechwytywania, zeby przy wykrytym kosztorysie
   nie uruchamiac parsera danych kontaktowych. */
(function(){
  function lz(x){
    x=String(x||'').replace(/[  ]/g,' ').replace(/[^\d,.\- ]/g,'').replace(/\s+/g,'');
    var p=x.lastIndexOf(','), k=x.lastIndexOf('.');
    if(p>k){x=x.replace(/\./g,'').replace(',','.');}else{x=x.replace(/,/g,'');}
    var v=parseFloat(x);
    return isFinite(v)?v:0;
  }
  var JEDN=/^(m2|m²|m3|m³|mb|m|kpl\.?|szt\.?|ryc[z]?\.?|rycza[lł]t|godz\.?|rbh|doba|dni|dzie[nń]|kg|t|l|op\.?|kurs|us[lł]\.?)$/i;

  function rozdzielPodstawe(op){
    var m=op.match(/^((?:KNR|KNNR|KSNR|KNP|NNRNKB|KNR-W)[A-Za-z\-]*\s*[\d\-]+(?:\s+\d+)?)\s+(.+)$/i);
    if(m)return{k:m[1].replace(/\s+/g,' ').trim(), n:m[2].trim()};
    m=op.match(/^(Wynajem|Kalkulacja|Kalk\.?|Analiza|Wycena|Indywidualna|W[lł]asna)\s+(.+)$/i);
    if(m)return{k:m[1].trim(), n:m[2].trim()};
    return{k:'', n:op.trim()};
  }

  function czytaj(tekst){
    var out=[], linie=String(tekst||'').split(/\r?\n/);
    for(var i=0;i<linie.length;i++){
      var L=linie[i].replace(/[  ]/g,' ').replace(/\s+$/,'');
      if(!L.trim())continue;
      if(/^\s*lp\b/i.test(L))continue;            /* naglowek tabeli */
      var r=null;
      if(L.indexOf('\t')>=0){
        var c=L.split('\t').map(function(x){return x.trim();});
        c=c.filter(function(x){return x!=='';});
        if(c.length>=6)      r={op:c[1]+' '+c[2], j:c[3], il:c[4], cena:c[5]};
        else if(c.length===5)r={op:c[1],          j:c[2], il:c[3], cena:c[4]};
      }
      if(!r){
        var m=L.trim().match(
          /^(\d+(?:\.\d+)+)\s+(.+?)\s+([A-Za-z²³żźćńółęąśŻŹĆŃÓŁĘĄŚ\.]{1,9})\s+([\d ]+(?:[.,]\d+)?)\s+([\d ]+(?:[.,]\d+)?)\s*z[lł]\s+([\d ]+(?:[.,]\d+)?)\s*z[lł]\.?$/i);
        if(m)r={op:m[2], j:m[3], il:m[4], cena:m[5]};
      }
      if(!r)continue;
      var j=String(r.j||'').trim();
      if(!JEDN.test(j))continue;                  /* to nie byl wiersz pozycji */
      var il=lz(r.il), cena=lz(r.cena);
      if(!(il>0)||!(cena>0))continue;
      var p=rozdzielPodstawe(String(r.op||'').replace(/\s+/g,' ').trim());
      if(!p.n)continue;
      out.push({n:p.n, k:p.k, il:il, j:j.replace(/^m2$/i,'m²'), s:cena});
    }
    return out;
  }

  function kom(t){
    var e=document.getElementById('ek-info-wklej');
    if(!e)return;
    e.textContent=t;
    setTimeout(function(){if(e.textContent===t)e.textContent='';},6000);
  }

  document.addEventListener('click',function(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('#ek-rozbij'):null;
    if(!b)return;
    var pole=document.getElementById('ek-wklejka');
    if(!pole||!pole.value.trim())return;
    var w=czytaj(pole.value);
    if(w.length<2)return;                         /* zwykla wiadomosc od klienta */
    ev.stopPropagation();
    if(typeof window.ekWczytajKosztorys!=='function'){kom('Nie udało się wczytać kosztorysu');return;}
    var ile=window.ekWczytajKosztorys(w);
    var suma=w.reduce(function(a,x){return a+x.il*x.s;},0);
    kom('Wczytano '+ile+' pozycji z kosztorysu, razem '
        +(Math.round(suma*100)/100).toFixed(2).replace('.',',')+' zł netto');
    var kosz=document.querySelector('.ek-blok--kosz');
    if(kosz&&kosz.scrollIntoView)kosz.scrollIntoView({behavior:'smooth',block:'start'});
  },true);
})();
