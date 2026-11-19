/* SMARTPARKIET - automat "pierwsza kopia zostaje, kolejne do kosza" (Artur WA 19.11 23:3x:
   "wszystko zapisuje sie raz, a wszystko co potem sie pojawia idzie z automatu do kosza").

   Dziala NA KONCIE ARTURA (skrzynka, do ktorej przychodza maile "Kopia: ..." z wycen).
   Co 10 minut przeglada maile z tekstem "Kopia wyceny z narzędzia" z ostatnich 60 dni.
   Klient = ostatnie 9 cyfr telefonu albo adres (bez spacji i znakow) z tresci kopii.
   Najstarsza kopia danego klienta zostaje, kazda nowsza idzie do KOSZA pojedynczo (nie caly watek),
   wiec mozna ja odzyskac przez 30 dni. Nic nie jest usuwane trwale.

   Wdrozenie (raz): script.google.com na koncie Artura -> Nowy projekt -> wklej ten plik -> zapisz ->
   wybierz funkcje kopieUstaw -> Uruchom -> zezwol na dostep do Gmaila. Gotowe (wyzwalacz co 10 min).
   Podglad bez wyrzucania: kopieSucho. Wylaczenie: kopieWylacz. */

const KOPIE_ZAPYTANIE = '"Kopia wyceny z narzędzia" newer_than:60d -in:trash';
const KOPIE_DNI = 60;

function kopieKlucze(tresc) {
  const t = String(tresc || '');
  const k = [];
  const tel = (t.match(/tel\.\s*([+\d][\d\s-]{7,})/) || [])[1];
  const cyfry = String(tel || '').replace(/\D/g, '');
  if (cyfry.length >= 9) k.push('t' + cyfry.slice(-9));
  const adr = (t.match(/Adres:\s*([^·\n]+)/) || [])[1];
  const a = String(adr || '').toLowerCase().replace(/[^0-9a-ząćęłńóśźż]/g, '');
  if (a.length >= 5 && a !== '-') k.push('a' + a);
  return k;
}

/* zwraca liste {msg, klucze, kiedy} wszystkich kopii, od najstarszej */
function kopieLista() {
  const out = [];
  let start = 0;
  while (true) {
    const watki = GmailApp.search(KOPIE_ZAPYTANIE, start, 100);
    if (!watki.length) break;
    watki.forEach(function (w) {
      w.getMessages().forEach(function (m) {
        if (m.isInTrash()) return;
        const body = m.getPlainBody();
        if (body.indexOf('Kopia wyceny z narzędzia') < 0) return;
        out.push({ msg: m, klucze: kopieKlucze(body), kiedy: m.getDate().getTime(), temat: m.getSubject() });
      });
    });
    if (watki.length < 100) break;
    start += 100;
  }
  out.sort(function (x, y) { return x.kiedy - y.kiedy; });
  return out;
}

function kopiePrzejrzyj(naSucho) {
  const p = PropertiesService.getScriptProperties();
  /* pamiec "pierwszych" kopii (klucz -> czas), zeby pierwsza zostala, nawet gdy wypadnie z okna wyszukiwania */
  let znane = {};
  try { znane = JSON.parse(p.getProperty('KOPIE_ZNANE') || '{}'); } catch (e) { znane = {}; }
  const granica = Date.now() - KOPIE_DNI * 864e5;
  Object.keys(znane).forEach(function (k) { if (znane[k] < granica) delete znane[k]; });
  const wyrzucone = [];
  kopieLista().forEach(function (x) {
    if (!x.klucze.length) return; /* bez telefonu i adresu - nie ruszamy */
    const pierwsza = x.klucze.map(function (k) { return znane[k]; }).filter(function (t) { return t && t < x.kiedy; });
    if (pierwsza.length) {
      wyrzucone.push(Utilities.formatDate(new Date(x.kiedy), 'Europe/Warsaw', 'yyyy-MM-dd HH:mm') + ' ' + x.temat);
      if (!naSucho) x.msg.moveToTrash();
    } else {
      x.klucze.forEach(function (k) { if (!znane[k] || znane[k] > x.kiedy) znane[k] = x.kiedy; });
    }
  });
  if (!naSucho) {
    p.setProperty('KOPIE_ZNANE', JSON.stringify(znane));
    if (wyrzucone.length) {
      let log = [];
      try { log = JSON.parse(p.getProperty('KOPIE_LOG') || '[]'); } catch (e) { log = []; }
      const teraz = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd HH:mm');
      log = wyrzucone.map(function (w) { return teraz + ' -> kosz: ' + w; }).concat(log).slice(0, 200);
      p.setProperty('KOPIE_LOG', JSON.stringify(log));
    }
  }
  wyrzucone.forEach(function (w) { Logger.log((naSucho ? 'DO KOSZA (na sucho): ' : 'do kosza: ') + w); });
  Logger.log('Kopii do kosza: ' + wyrzucone.length);
  return wyrzucone;
}

function kopieDoKosza() { return kopiePrzejrzyj(false); }
function kopieSucho() { return kopiePrzejrzyj(true); }
function kopieLog() { Logger.log((JSON.parse(PropertiesService.getScriptProperties().getProperty('KOPIE_LOG') || '[]')).join('\n') || 'pusto'); }

function kopieUstaw() {
  kopieWylacz();
  ScriptApp.newTrigger('kopieDoKosza').timeBased().everyMinutes(10).create();
  kopieDoKosza();
}
function kopieWylacz() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'kopieDoKosza') ScriptApp.deleteTrigger(t); });
}
