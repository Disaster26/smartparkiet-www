# -*- coding: utf-8 -*-
"""Cztery lokalne podstrony oddzialow + sekcja "Nasze oddzialy" na stronie glownej.

Wg wiadomosci Artura z 10.10.2026 (grupa STRONA LUKASZ): jedna silna domena,
cztery podstrony oddzialow, kazda wizytowka Google kieruje do swojej podstrony,
a strona glowna dalej lapie frazy ogolne i prowadzi do czworki nizej.

Kazda podstrona ma to, o co prosil: naglowek SEO z dzielnica, adres i dane
oddzialu, opis uslug, realizacje, opinie z tej wizytowki, mape i przycisk wyceny.
Do tego dane strukturalne LocalBusiness, zeby Google wiedzial, ze to osobna
placowka, a nie kopia strony glownej.

Uzycie:  python _sp_oddzialy.py
"""
import io
import os
import re

KAT = os.path.dirname(os.path.abspath(__file__))
WZOR = os.path.join(KAT, 'oddzialy.html')
BAZA = 'https://disaster26.github.io/smartparkiet-www'

ODDZIALY = [
    {
        'plik': 'cyklinowanie-rembertow.html', 'dz': 'Rembertów',
        'ulica': 'ul. Suflerska 4', 'kod': '04-471', 'miasto': 'Warszawa',
        'cid': '4565719495930749944',
        'rola': 'Oddział główny: biuro, magazyn maszyn i lakierów, stąd wyjeżdża ekipa wschodnia.',
        'obszar': ['Rembertów', 'Wesoła', 'Praga Południe', 'Wawer', 'Sulejówek'],
        'eta': 'ok. 15-25 min',
        'opinia': ('„Oględziny na miejscu, wycena, ustalenie terminu na za 2 tygodnie. '
                   'Po 2 dniach pracy parkiet otrzymał drugie życie."',
                   'Mateusz Głębicki, opinia Google'),
    },
    {
        'plik': 'cyklinowanie-ochota.html', 'dz': 'Ochota',
        'ulica': 'ul. Grójecka 208, lok. 229', 'kod': '02-390', 'miasto': 'Warszawa',
        'cid': '4435256749743705982',
        'rola': 'Ekipa zachodnia. Najkrótszy dojazd na Ochotę, Wolę i Włochy.',
        'obszar': ['Ochota', 'Wola', 'Włochy', 'Bemowo', 'Ursus'],
        'eta': 'ok. 10-20 min',
        'opinia': ('„Mogę śmiało polecić firmę smartparkiet. Doskonały, szybki, '
                   'przejrzysty kontakt."', 'opinia Google, wizytówka Ochota'),
    },
    {
        'plik': 'cyklinowanie-targowek.html', 'dz': 'Targówek',
        'ulica': 'ul. Turmoncka 17A, lok. 21', 'kod': '03-254', 'miasto': 'Warszawa',
        'cid': '3093966538504001070',
        'rola': 'Ekipa północna. Obsługuje prawy brzeg i północ miasta.',
        'obszar': ['Targówek', 'Bródno', 'Białołęka', 'Praga Północ', 'Żoliborz', 'Bielany'],
        'eta': 'ok. 10-25 min',
        'opinia': ('„Firma rzetelna, terminowa i profesjonalna. Potrafi doradzić '
                   'przy starych parkietach."', 'opinia Google, wizytówka Targówek'),
    },
    {
        'plik': 'cyklinowanie-mokotow.html', 'dz': 'Mokotów',
        'ulica': 'ul. Belwederska 23', 'kod': '00-761', 'miasto': 'Warszawa',
        'cid': '8329908770735610659',
        'rola': 'SMARTPARKIET | BLVD 23. Ekipa południowa, dużo kamienic i jodełki.',
        'obszar': ['Mokotów', 'Śródmieście', 'Ursynów', 'Wilanów', 'Sadyba'],
        'eta': 'ok. 10-20 min',
        'opinia': ('„Podłoga wygląda świetnie, cyklinowanie z uzupełnieniem '
                   'przestrzeni między deskami."', 'opinia Google, wizytówka Mokotów'),
    },
]

STYL = '''
<style>
/* === podstrony oddzialow === */
.odz-hero{padding:34px 0 10px}
.odz-hero .oczko{margin-bottom:10px}
.odz-hero h1{font-size:clamp(1.7rem,5vw,2.5rem);line-height:1.12;margin:0 0 10px;letter-spacing:-.02em}
.odz-hero h1 em{font-style:normal;color:var(--pom)}
.odz-hero .lead{max-width:62ch}
.odz-dane{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:22px 0 6px}
.odz-dane div{background:var(--bg2);border:1px solid rgba(26,21,18,.08);border-radius:12px;padding:13px 15px}
.odz-dane dt{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);margin-bottom:5px}
.odz-dane dd{margin:0;font-weight:600;line-height:1.4}
.odz-dane a{color:inherit}
.odz-obszar{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0 0}
.odz-obszar span{background:var(--bg2);border:1px solid rgba(26,21,18,.08);border-radius:999px;padding:5px 12px;font-size:.84rem}
.odz-usl{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}
.odz-usl article{border-top:2px solid var(--pom);padding-top:12px}
.odz-usl h3{margin:0 0 6px;font-size:1.02rem}
.odz-usl p{margin:0;color:var(--mut);font-size:.93rem;line-height:1.55}
.odz-mapa{border:0;width:100%;height:330px;border-radius:14px;margin-top:16px;filter:saturate(.9)}
.odz-op{background:var(--bg2);border-radius:14px;padding:18px 20px;margin-top:18px;border-left:3px solid var(--pom)}
.odz-op p{margin:0 0 6px;font-size:1.02rem;line-height:1.55}
.odz-op b{font-weight:600;font-size:.86rem;color:var(--mut);display:flex;align-items:center;gap:8px}
.odz-op b span{color:var(--pom);letter-spacing:.1em}
.odz-cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
.odz-inne{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.odz-inne a{background:var(--bg2);border:1px solid rgba(26,21,18,.08);border-radius:10px;padding:8px 13px;
  text-decoration:none;color:inherit;font-size:.9rem}
.odz-inne a:hover{border-color:var(--pom);color:var(--pom-tekst)}
/* kafle oddzialow na stronie glownej */
.odz-siatka{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:14px;margin-top:18px}
.odz-kafel{display:block;text-decoration:none;color:inherit;background:var(--bg2);border:1px solid rgba(26,21,18,.08);
  border-radius:14px;padding:16px 17px;transition:border-color .18s cubic-bezier(.23,1,.32,1),transform .18s cubic-bezier(.23,1,.32,1)}
.odz-kafel:hover{border-color:var(--pom);transform:translateY(-2px)}
.odz-kafel b{display:block;font-size:1.06rem;margin-bottom:3px}
.odz-kafel span{display:block;color:var(--mut);font-size:.88rem;line-height:1.5}
.odz-kafel i{display:block;font-style:normal;color:var(--pom-tekst);font-size:.84rem;margin-top:9px;font-weight:600}
@media(max-width:600px){.odz-mapa{height:250px}}
</style>
'''


def czytaj(p):
    return io.open(os.path.join(KAT, p), encoding='utf-8').read()


def pisz(p, s):
    io.open(os.path.join(KAT, p), 'w', encoding='utf-8').write(s)


def szkielet():
    w = czytaj(WZOR)
    gora = w[:w.index('</header>') + len('</header>')]
    dol = w[w.index('<footer class="site">'):]
    return gora, dol


def naglowek(gora, o):
    """Podmienia tytul, opis, canonical i og: na dane oddzialu."""
    tytul = 'Cyklinowanie %s - SMARTPARKIET&trade; | renowacja parkietu %s' % (o['dz'], o['dz'])
    opis = ('Cyklinowanie bezpyłowe i renowacja parkietu, %s. Oddział %s, %s. '
            'Wycena ze zdjęć w 2 godziny, typowe mieszkanie w 2 dni.'
            % (o['dz'], o['dz'], o['ulica']))
    url = '%s/%s' % (BAZA, o['plik'])
    g = re.sub(r'(?is)<title>.*?</title>', '<title>%s</title>' % tytul, gora, count=1)
    g = re.sub(r'(?is)(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % opis, g, count=1)
    g = re.sub(r'(?is)(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % tytul, g, count=1)
    g = re.sub(r'(?is)(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % opis, g, count=1)
    g = re.sub(r'(?is)(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\g<2>' % url, g, count=1)
    g = re.sub(r'(?is)(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\g<2>' % url, g, count=1)
    g = g.replace('<a href="oddzialy.html">Oddziały</a>',
                  '<a href="oddzialy.html" class="akt">Oddziały</a>')
    return g


def dane_strukturalne(o):
    return ('<script type="application/ld+json">{"@context":"https://schema.org",'
            '"@type":"HomeAndConstructionBusiness","name":"SMARTPARKIET %s",'
            '"description":"Cyklinowanie bezpyłowe i renowacja parkietu, oddział %s.",'
            '"url":"%s/%s","telephone":"+48602242815","email":"smartparkiet@gmail.com",'
            '"image":"%s/img/og-smartparkiet.jpg",'
            '"address":{"@type":"PostalAddress","streetAddress":"%s","addressLocality":"Warszawa",'
            '"postalCode":"%s","addressCountry":"PL"},'
            '"areaServed":[%s],'
            '"sameAs":["https://maps.google.com/?cid=%s"],'
            '"priceRange":"$$","parentOrganization":{"@type":"Organization","name":"SMARTPARKIET Trembiński"}}'
            '</script>'
            % (o['dz'], o['dz'], BAZA, o['plik'], BAZA, o['ulica'].replace('ul. ', ''),
               o['kod'], ','.join('{"@type":"Place","name":"%s"}' % x for x in o['obszar']),
               o['cid']))


def tresc(o, inne):
    mapa = ('https://www.google.com/maps?q=%s&output=embed'
            % ('SMARTPARKIET+' + o['ulica'].replace('ul. ', '').replace(' ', '+')
               + '+Warszawa').replace(',', ''))
    linki = ''.join('<a href="%s">Cyklinowanie %s</a>' % (x['plik'], x['dz']) for x in inne)
    return '''<section class="odz-hero">
  <div class="wrap">
    <p class="oczko"><span></span>Oddział %(dz)s</p>
    <h1>Cyklinowanie <em>%(dz)s</em><br>i renowacja parkietu</h1>
    <p class="lead">%(rola)s Pracujemy bezpyłowo, z odpylaniem Festool, a typowe mieszkanie
    oddajemy w dwa dni. Wycenę przygotowujemy ze zdjęć, bez wizyty na start.</p>

    <div class="odz-dane">
      <div><dt>Adres oddziału</dt><dd>%(ulica)s<br>%(kod)s Warszawa</dd></div>
      <div><dt>Telefon</dt><dd><a href="tel:+48602242815">602 242 815</a><br>
        <span style="font-weight:400;color:var(--mut);font-size:.88rem">jeden numer do wszystkich oddziałów</span></dd></div>
      <div><dt>Godziny kontaktu</dt><dd>pon-pt 7:00-19:00<br>sob 8:00-15:00</dd></div>
      <div><dt>Dojazd do Państwa</dt><dd>%(eta)s</dd></div>
    </div>

    <h2 style="margin-top:30px">Gdzie dojeżdża ten oddział</h2>
    <div class="odz-obszar">%(obszar)s</div>

    <h2 style="margin-top:30px">Co robimy na miejscu</h2>
    <div class="odz-usl">
      <article><h3>Cyklinowanie SMART&trade;</h3><p>Diagnoza podłogi, dobór technologii pod
        konkretne drewno, szlif w trzech gradacjach i uzupełnienie szczelin masą z pyłu tej
        samej podłogi. Trzy warstwy lakieru wodnego albo olej twardy.</p></article>
      <article><h3>SMART ZERO DUST&trade;</h3><p>Szlifowanie z systemem odpylania Festool
        SYS-AIR. Pył idzie do worka, nie na meble i nie na Państwa rzeczy. Po pracy zostaje
        podłoga, a nie sprzątanie przez tydzień.</p></article>
      <article><h3>Renowacja desek warstwowych</h3><p>Cienka warstwa użytkowa wymaga innego
        podejścia niż lita klepka. Mierzymy ją przed startem i mówimy wprost, ile jeszcze
        cykli wytrzyma podłoga.</p></article>
    </div>

    <h2 style="margin-top:30px">Opinia z wizytówki %(dz)s</h2>
    <div class="odz-op">
      <p>%(opinia)s</p>
      <b><span>&#9733;&#9733;&#9733;&#9733;&#9733;</span>%(autor)s</b>
      <p style="margin-top:10px;font-size:.9rem"><a href="https://maps.google.com/?cid=%(cid)s"
        target="_blank" rel="noopener">Zobacz wizytówkę i wszystkie opinie oddziału %(dz)s &rarr;</a></p>
    </div>

    <h2 style="margin-top:30px">Realizacje</h2>
    <p class="lead">Zdjęcia przed i po, z metrażem i czasem wykonania, zbieramy w jednym
    miejscu dla wszystkich oddziałów. Najnowsze są na górze.</p>
    <div class="odz-cta">
      <a class="btn btn-ghost" href="realizacje.html">Zobacz realizacje przed i po &rarr;</a>
    </div>

    <h2 style="margin-top:30px">Jak do nas trafić</h2>
    <iframe class="odz-mapa" src="%(mapa)s" loading="lazy"
      referrerpolicy="no-referrer-when-downgrade" title="Mapa dojazdu, oddział %(dz)s"></iframe>

    <div class="odz-cta">
      <a class="btn btn-amber" href="wycena.html">Bezpłatna wycena online &rarr;</a>
      <a class="btn btn-ghost" href="tel:+48602242815">602 242 815</a>
      <a class="btn btn-ghost" href="https://wa.me/48602242815">WhatsApp</a>
    </div>

    <h2 style="margin-top:30px">Pozostałe oddziały</h2>
    <div class="odz-inne">%(linki)s</div>
  </div>
</section>
''' % {'dz': o['dz'], 'rola': o['rola'], 'ulica': o['ulica'], 'kod': o['kod'],
       'eta': o['eta'], 'cid': o['cid'], 'mapa': mapa, 'linki': linki,
       'opinia': o['opinia'][0], 'autor': o['opinia'][1],
       'obszar': ''.join('<span>%s</span>' % x for x in o['obszar'])}


def main():
    gora, dol = szkielet()
    for o in ODDZIALY:
        inne = [x for x in ODDZIALY if x['plik'] != o['plik']]
        strona = (naglowek(gora, o) + tresc(o, inne) + dol.rstrip()
                  + '\n' + dane_strukturalne(o) + STYL)
        pisz(o['plik'], strona)
        print('zapisane:', o['plik'])

    # --- sekcja "Nasze oddzialy" na stronie glownej
    s = czytaj('index.html')
    S, K = '<!-- oddzialy: START -->', '<!-- oddzialy: KONIEC -->'
    s = re.sub(re.escape(S) + r'.*?' + re.escape(K), '', s, flags=re.S)
    kafle = ''.join(
        '<a class="odz-kafel" href="%s"><b>%s</b><span>%s<br>%s</span>'
        '<i>Zobacz oddział &rarr;</i></a>'
        % (o['plik'], o['dz'], o['ulica'], ', '.join(o['obszar'][:4])) for o in ODDZIALY)
    blok = (S + '\n<section class="oddzialy-home"><div class="wrap">'
            '<p class="oczko"><span></span>Nasze oddziały w Warszawie</p>'
            '<h2>Cztery ekipy, jeden numer telefonu</h2>'
            '<p class="lead">Każdy oddział ma swoją stronę z adresem, obszarem dojazdu '
            'i opiniami z własnej wizytówki Google. Proszę wybrać ten najbliżej Państwa.</p>'
            '<div class="odz-siatka">' + kafle + '</div></div></section>\n' + K)
    kotwica = '<div class="facts">'
    if kotwica in s:
        s = s.replace(kotwica, blok + '\n\n' + kotwica, 1)
    else:
        raise SystemExit('nie znalazlem miejsca na sekcje oddzialow')
    if '.odz-siatka{' not in s:
        s = s.rstrip() + '\n' + STYL
    pisz('index.html', s)
    print('index.html: sekcja Nasze oddzialy')

    # --- stopka na wszystkich stronach prowadzi juz do podstron oddzialow
    stara = ('<div class="c-oddzialy"><h4>Oddziały</h4><a href="oddzialy.html">Suflerska 4, Rembertów</a>'
             '<a href="oddzialy.html">Grójecka 208, Ochota</a><a href="oddzialy.html">Turmoncka 17A, Targówek</a>'
             '<a href="oddzialy.html">Belwederska 23, Mokotów</a></div>')
    nowa = ('<div class="c-oddzialy"><h4>Oddziały</h4>'
            + ''.join('<a href="%s">%s, %s</a>' % (o['plik'], o['ulica'].replace('ul. ', ''), o['dz'])
                      for o in ODDZIALY) + '</div>')
    ile = 0
    for p in os.listdir(KAT):
        if not p.endswith('.html'):
            continue
        t = czytaj(p)
        if stara in t:
            pisz(p, t.replace(stara, nowa))
            ile += 1
    print('stopka zaktualizowana w %d plikach' % ile)

    # --- karty na oddzialy.html dostaja odnosnik do swojej podstrony
    t = czytaj('oddzialy.html')
    for o in ODDZIALY:
        wzor = 'Wizytówka i opinie Google →</a>'
        klucz = o['ulica'].replace('ul. ', '')
        i = t.find(klucz)
        if i < 0:
            continue
        j = t.find(wzor, i)
        if j < 0:
            continue
        j += len(wzor)
        dodatek = ('<a class="opinie-link" href="%s" style="margin-left:14px">'
                   'Strona oddziału %s &rarr;</a>' % (o['plik'], o['dz']))
        if dodatek not in t:
            t = t[:j] + dodatek + t[j:]
    pisz('oddzialy.html', t)
    print('oddzialy.html: odnosniki do podstron')


main()
