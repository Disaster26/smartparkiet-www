# -*- coding: utf-8 -*-
"""Wstawia swieze realizacje do realizacje.html na podstawie dane/realizacje.json.

Dzieki temu dodanie nowej realizacji to edycja jednego pliku JSON i wrzucenie
dwoch zdjec, a HTML zostaje statyczny, czyli Google widzi tresc od razu, bez
czekania na JavaScript.

Uzycie:  python _buduj_realizacje.py
"""
import datetime
import html
import io
import json
import os
import re

KAT = os.path.dirname(os.path.abspath(__file__))
P_JSON = os.path.join(KAT, 'dane', 'realizacje.json')
P_HTML = os.path.join(KAT, 'realizacje.html')
START = '<!-- SWIEZE:START -->'
KONIEC = '<!-- SWIEZE:KONIEC -->'
DNI = 30   # tyle dni realizacja stoi w Najnowszych

MIESIACE = ('stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
            'lipca', 'sierpnia', 'września', 'października',
            'listopada', 'grudnia')


def po_polsku(data):
    """2026-10-08 -> 8 pazdziernika 2026"""
    try:
        r, m, d = (int(x) for x in data.split('-'))
        return '%d %s %d' % (d, MIESIACE[m - 1], r)
    except Exception:
        return data


def e(t):
    return html.escape(str(t or ''), quote=True)


def karta(w, nr):
    meta = []
    for etykieta, klucz in (('Lokalizacja', 'lokalizacja'), ('Metraż', 'metraz'),
                            ('Czas', 'czas'), ('Podłoga', 'podloga')):
        if w.get(klucz):
            meta.append('<div><dt>%s</dt><dd>%s</dd></div>' % (etykieta, e(w[klucz])))

    ma_pare = bool(w.get('zdj_przed')) and bool(w.get('zdj_po'))
    if ma_pare:
        wizual = (
            '<div class="ba r-ba" style="--x:52%">'
            '<img src="{po}" alt="{apo}" loading="lazy" decoding="async">'
            '<img class="before" src="{przed}" alt="{aprzed}" loading="lazy" decoding="async">'
            '<div class="handle"></div><div class="knob">⇔</div>'
            '<span class="lbl l">przed</span><span class="lbl r">po</span>'
            '<input type="range" min="0" max="100" value="52" '
            'aria-label="Porównanie przed i po: {tyt}">'
            '</div>'
        ).format(po=e(w['zdj_po']), przed=e(w['zdj_przed']),
                 apo=e(w.get('alt_po') or w['tytul'] + ', po renowacji'),
                 aprzed=e(w.get('alt_przed') or w['tytul'] + ', przed renowacją'),
                 tyt=e(w['tytul']))
    elif w.get('zdj_po'):
        wizual = ('<figure class="r-jedno"><img src="%s" alt="%s" loading="lazy" '
                  'decoding="async"></figure>'
                  % (e(w['zdj_po']), e(w.get('alt_po') or w['tytul'])))
    else:
        wizual = ''

    # Artur poprosil o stala kolejnosc: najpierw polaczone przed i po,
    # potem zdjecia starej podlogi, na koncu duze zdjecia nowej.
    dod = ''
    laczone = w.get('zdj_laczone') or []
    if laczone:
        dod += ('<div class="r-laczone"><h4>Przed i po</h4>'
                + ''.join('<figure><img src="%s" alt="%s" loading="lazy" '
                          'decoding="async"></figure>'
                          % (e(z.get('src')), e(z.get('alt') or w['tytul']
                             + ', zestawienie przed i po'))
                          for z in laczone)
                + '</div>')
    stare_zdj = w.get('zdj_stare') or []
    nowe_zdj = w.get('zdj_nowe') or []
    if stare_zdj:
        dod += ('<div class="r-stare"><h4>Przed renowacją</h4><div class="r-rzad">'
                + ''.join('<figure><img src="%s" alt="%s" loading="lazy" '
                          'decoding="async"></figure>'
                          % (e(z.get('src')), e(z.get('alt') or w['tytul']
                             + ', stan przed renowacj\u0105'))
                          for z in stare_zdj)
                + '</div></div>')
    if nowe_zdj:
        dod += ('<div class="r-nowe">'
                + ''.join('<figure><img src="%s" alt="%s" loading="lazy" '
                          'decoding="async"></figure>'
                          % (e(z.get('src')), e(z.get('alt') or w['tytul']
                             + ', po renowacji'))
                          for z in nowe_zdj)
                + '</div>')

    return (
        '      <article class="r-poz{odwr}{bezfot}" id="r-{rid}" data-data="{iso}">\n'
        '        <div class="r-wiz">{wizual}</div>\n'
        '        <div class="r-tresc">\n'
        '          {program}'
        '          <h3>{tytul}</h3>\n'
        '          <p>{opis}</p>\n'
        '          <dl class="r-meta">{meta}</dl>\n'
        '          <p class="r-data"><time datetime="{iso}">{data}</time></p>\n'
        '        </div>\n'
        '        <div class="r-dod">{dod}</div>\n'
        '      </article>'
    ).format(
        dod=dod,
        odwr=' odwr' if nr % 2 else '',
        bezfot='' if wizual else ' bezfot',
        rid=e(w.get('id') or nr),
        wizual=wizual,
        program=('<p class="r-program">%s</p>\n          ' % e(w['program'])
                 if w.get('program') else ''),
        tytul=e(w['tytul']),
        opis=e(w['opis']),
        meta=''.join(meta),
        iso=e(w.get('data')),
        data=po_polsku(w.get('data')),
    )


def main():
    dane = json.load(io.open(P_JSON, encoding='utf-8'))
    widoczne = [w for w in dane if not w.get('szkic')]
    widoczne.sort(key=lambda w: w.get('data', ''), reverse=True)

    granica = (datetime.date.today() - datetime.timedelta(days=DNI)).isoformat()
    swieze = [w for w in widoczne if (w.get('data') or '') >= granica]
    if not swieze and widoczne:          # zawsze cos stoi w Najnowszych
        swieze = widoczne[:1]
    archiwum = [w for w in widoczne if w not in swieze]

    if widoczne:
        blok = (
            '    <div class="r-naglowek">\n'
            '      <h2>Najnowsze realizacje</h2>\n'
            '      <p>Podłogi z ostatniego miesiąca, prosto spod naszych maszyn. '
            'Zdjęcia bez obróbki, ten sam kadr przed i po.</p>\n'
            '    </div>\n'
            '    <div class="r-lista" id="rLstNowe">\n'
            + '\n'.join(karta(w, i) for i, w in enumerate(swieze))
            + '\n    </div>\n'
            '    <div class="r-naglowek r-naglowek-arch" id="rNagArch"'
            + ('' if archiwum else ' hidden') + '>\n'
            '      <h2>Portfolio</h2>\n'
            '      <p>Wcześniejsze realizacje. Każda zostaje tu na stałe, '
            'razem ze zdjęciami przed i po.</p>\n'
            '    </div>\n'
            '    <div class="r-lista" id="rLstArch">\n'
            + '\n'.join(karta(w, i) for i, w in enumerate(archiwum))
            + '\n    </div>'
        )
    else:
        blok = ''

    s = io.open(P_HTML, encoding='utf-8').read()
    if START not in s or KONIEC not in s:
        raise SystemExit('Brak znacznikow %s / %s w realizacje.html' % (START, KONIEC))
    nowy = re.sub(
        re.escape(START) + r'.*?' + re.escape(KONIEC),
        START + '\n' + blok + '\n    ' + KONIEC,
        s, flags=re.S)
    io.open(P_HTML, 'w', encoding='utf-8').write(nowy)

    print('realizacji w pliku:', len(dane))
    print('wstawionych na strone:', len(widoczne))
    szkice = [w for w in dane if w.get('szkic')]
    if szkice:
        print('czeka na zdjecia (szkic):')
        for w in szkice:
            print('   -', w.get('tytul'), '|', w.get('lokalizacja'))


main()
