# -*- coding: utf-8 -*-
"""10.11.2026: polityka-prywatnosci.html w wygladzie poradnikow (naglowek i stopka z wzorca).
Dane administratora wylacznie ze strony (kontakt.html: SMARTPARKIET TREMBINSKI, NIP, adres Suflerska 4, telefon, e-mail).
Uruchomienie: python _buduj_polityka.py (nadpisuje polityka-prywatnosci.html)."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WZOR = 'naprawa-punktowa-parkietu-kiedy-jest-mozliwa.html'
CEL = 'polityka-prywatnosci.html'
TYTUL = 'Polityka prywatności i cookies | SMARTPARKIET'
OPIS = 'Polityka prywatności serwisu SMARTPARKIET: kto jest administratorem danych, co dzieje się z danymi z formularzy wycen, pliki cookies i narzędzia Google, prawa z RODO.'
AKT = '10.11.2026'
AKT_ISO = '2026-11-10'

TRESC = '''<section id="top" class="art-head">
  <div class="wrap">
    <p class="tag">Informacje</p>
    <h1>Polityka prywatności i cookies</h1>
    <p class="lead">Jakie dane zbiera serwis SMARTPARKIET, po co, komu je przekazujemy i jakie prawa Państwu przysługują. Bez prawniczego żargonu tam, gdzie się da.</p>
    <p class="art-meta">Aktualizacja <time datetime="''' + AKT_ISO + '''">''' + AKT + '''</time></p>
  </div>
</section>

<section class="art-body">
  <div class="wrap art">

    <h2>1. Administrator danych</h2>
    <p>Administratorem danych osobowych przekazywanych przez serwis smartparkiet.com.pl jest właściciel serwisu SMARTPARKIET: <strong>SMARTPARKIET TREMBIŃSKI</strong> (Artur Trembiński), NIP 527 158 81 14, ul. Suflerska 4, 04-471 Warszawa.</p>
    <p>Kontakt w sprawach danych osobowych: e-mail <a href="mailto:smartparkiet@gmail.com">smartparkiet@gmail.com</a>, telefon <a href="tel:+48602242815">602 242 815</a>. Adresy wszystkich oddziałów są na stronie <a href="kontakt.html">Kontakt</a>.</p>

    <h2>2. Formularze, wyceny i zamówienia online</h2>
    <p>Gdy wysyłają Państwo formularz wyceny, zamówienie z koszyka, zgłoszenie ekspertyzy albo zdjęcia podłogi, przetwarzamy dane podane w formularzu: zwykle imię, telefon, e-mail, adres realizacji, metraż, opis i zdjęcia podłogi oraz preferowany termin.</p>
    <ul>
      <li><strong>Cel:</strong> przygotowanie wyceny, kontakt w sprawie zlecenia, ustalenie terminu i wykonanie usługi.</li>
      <li><strong>Podstawa:</strong> podjęcie działań na Państwa prośbę przed zawarciem umowy i wykonanie umowy (art. 6 ust. 1 lit. b RODO), a po zakończeniu współpracy nasz prawnie uzasadniony interes w obronie przed roszczeniami i obowiązki księgowe (art. 6 ust. 1 lit. c i f RODO).</li>
      <li><strong>Jak to działa technicznie:</strong> zgłoszenie z formularza trafia na naszą skrzynkę e-mail oraz do arkusza zgłoszeń prowadzonego w usługach Google (Arkusze Google). Na życzenie wysyłamy kopię wyceny na adres e-mail podany w formularzu.</li>
      <li><strong>Wstępna analiza zdjęć:</strong> zdjęcia przesłane do automatycznej wstępnej oceny podłogi są przekazywane do usługi analizy działającej w chmurze (Cloudflare) i modelu AI dostawcy Google. Wynik jest orientacyjny, ostateczną wycenę przygotowuje człowiek.</li>
      <li><strong>Jak długo:</strong> przez czas potrzebny do przygotowania wyceny i realizacji zlecenia, a potem przez okres przedawnienia roszczeń i okres wymagany przepisami podatkowymi.</li>
    </ul>
    <p>Podanie danych jest dobrowolne, ale bez numeru telefonu lub adresu e-mail nie odeślemy wyceny.</p>

    <h2>3. Kontakt telefoniczny, e-mail i WhatsApp</h2>
    <p>Jeśli piszą Państwo do nas e-mailem lub przez WhatsApp albo dzwonią, przetwarzamy dane potrzebne do odpowiedzi i obsługi sprawy. Przyciski WhatsApp otwierają aplikację WhatsApp (Meta), która działa według własnych zasad prywatności.</p>

    <h2>4. Pliki cookies i pamięć przeglądarki</h2>
    <p>Serwis zapisuje w przeglądarce niewielkie informacje (pliki cookies i pamięć lokalna przeglądarki). Dzielimy je na trzy grupy:</p>
    <ul>
      <li><strong>Niezbędne</strong> - zawsze włączone. Zapamiętują Państwa wybór dotyczący cookies (przez 12 miesięcy), zapisane w przeglądarce wyceny i ustawienia narzędzi wyceny. Bez nich strona nie działa prawidłowo.</li>
      <li><strong>Analityczne</strong> - tylko po zgodzie. Statystyki odwiedzin (Google Analytics): które strony są czytane i skąd przychodzą odwiedzający. Dane są zbiorcze, nie służą do rozpoznawania konkretnych osób.</li>
      <li><strong>Marketingowe</strong> - tylko po zgodzie. Pomiar skuteczności reklam Google Ads (czy reklama doprowadziła do wysłania wyceny lub telefonu) oraz remarketing, czyli wyświetlanie naszych reklam osobom, które odwiedziły stronę.</li>
    </ul>
    <p>Przy pierwszej wizycie pokazujemy okno z wyborem: <em>Akceptuję wszystkie</em>, <em>Tylko niezbędne</em> albo <em>Ustawienia</em> (analityka i marketing osobno). Decyzję można w każdej chwili zmienić linkiem <em>Ustawienia cookies</em> w stopce strony albo przyciskiem poniżej. Cofnięcie zgody nie wpływa na zgodność z prawem tego, co działo się przed jej cofnięciem.</p>
    <p><button type="button" class="btn btn-amber sp-zgody-link">Zmień ustawienia cookies</button></p>

    <h2>5. Narzędzia Google</h2>
    <ul>
      <li><strong>Google Tag Manager</strong> - narzędzie, przez które uruchamiamy pozostałe tagi. Działa w trybie zgody Google (Consent Mode): dopóki nie wyrażą Państwo zgody, tagi analityczne i reklamowe nie zapisują plików cookies, a do Google trafiają co najwyżej sygnały bez identyfikatorów.</li>
      <li><strong>Google Analytics</strong> - statystyki odwiedzin, po zgodzie na cookies analityczne.</li>
      <li><strong>Google Ads</strong> - pomiar konwersji i remarketing, po zgodzie na cookies marketingowe.</li>
      <li><strong>Mapy Google</strong> - na stronach oddziałów i w kontakcie osadzamy mapy Google, a przyciski <em>Nawiguj</em> prowadzą do Map Google. Przy wyświetleniu mapy Google otrzymuje adres IP i informacje o przeglądarce.</li>
    </ul>
    <p>Dostawcą tych narzędzi jest Google Ireland Limited (Gordon House, Barrow Street, Dublin 4, Irlandia). Część danych może być przekazywana do Google LLC w USA na podstawie decyzji Komisji Europejskiej (EU-US Data Privacy Framework) i standardowych klauzul umownych. Więcej: <a href="https://policies.google.com/privacy?hl=pl" rel="noopener">polityka prywatności Google</a> i <a href="https://policies.google.com/technologies/partner-sites?hl=pl" rel="noopener">jak Google wykorzystuje dane ze stron partnerów</a>.</p>
    <p>Podstawą przetwarzania w celach analitycznych i marketingowych jest Państwa zgoda (art. 6 ust. 1 lit. a RODO oraz art. 399 Prawa komunikacji elektronicznej).</p>

    <h2>6. Komu przekazujemy dane</h2>
    <p>Danych nie sprzedajemy. Dostęp do nich mają wyłącznie podmioty, które pomagają nam prowadzić serwis i obsługiwać zlecenia: firma hostingowa serwera strony, dostawcy poczty i usług Google, dostawca usług chmurowych Cloudflare, a także obsługa techniczna strony. Przy realizacji zlecenia dane adresowe i kontaktowe otrzymuje ekipa wykonująca usługę.</p>

    <h2>7. Państwa prawa</h2>
    <p>Na zasadach RODO mają Państwo prawo do:</p>
    <ul>
      <li>dostępu do swoich danych i otrzymania ich kopii,</li>
      <li>sprostowania danych nieprawidłowych,</li>
      <li>usunięcia danych lub ograniczenia ich przetwarzania,</li>
      <li>przeniesienia danych,</li>
      <li>sprzeciwu wobec przetwarzania opartego na prawnie uzasadnionym interesie,</li>
      <li>cofnięcia zgody w dowolnym momencie (dla cookies: link <em>Ustawienia cookies</em> w stopce),</li>
      <li>wniesienia skargi do Prezesa Urzędu Ochrony Danych Osobowych (ul. Stawki 2, 00-193 Warszawa).</li>
    </ul>
    <p>W sprawie swoich danych prosimy pisać na <a href="mailto:smartparkiet@gmail.com">smartparkiet@gmail.com</a>.</p>

    <h2>8. Zmiany polityki</h2>
    <p>Gdy zmienią się narzędzia używane na stronie, zaktualizujemy ten dokument. Data ostatniej aktualizacji jest na górze strony.</p>

  </div>
</section>
'''

s = open(os.path.join(HERE, WZOR), encoding='utf-8').read()
a = s.index('</header>') + len('</header>')
b = s.index('<footer class="site">')
s = s[:a] + '\n' + TRESC + '\n' + s[b:]
# naglowek: tytul, opis, adresy, typ strony
stary_tytul = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
stary_opis = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
s = s.replace(stary_tytul, TYTUL).replace(stary_opis, OPIS)
s = s.replace(WZOR, CEL)
s = s.replace('og/' + WZOR[:-5] + '.jpg?v=2', 'img/og-smartparkiet-artur.jpg?v=2')
s = s.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
s = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Polityka prywatności SMARTPARKIET">', s)
# dane strukturalne poradnika -> tylko okruszki
s = re.sub(r'<script type="application/ld\+json"[^>]*>\s*\{"@context": "https://schema.org", "@type": "Article".*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'(<script type="application/ld\+json"[^>]*>\s*\{"@context": "https://schema.org", "@type": "BreadcrumbList").*?(</script>)',
           lambda m: m.group(1) + ', "itemListElement": [{"@type": "ListItem", "position": 1, "name": "SMARTPARKIET", "item": "https://disaster26.github.io/smartparkiet-www/"}, '
                     '{"@type": "ListItem", "position": 2, "name": "Polityka prywatności", "item": "https://disaster26.github.io/smartparkiet-www/' + CEL + '"}]}' + m.group(2), s, flags=re.S)
assert '"@type": "Article"' not in s
assert '—' not in TRESC
open(os.path.join(HERE, CEL), 'w', encoding='utf-8', newline='\n').write(s)
print('OK', CEL, len(s))
