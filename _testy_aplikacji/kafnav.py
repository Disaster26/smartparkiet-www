"""19.11: w aplikacji nie ma juz dolnego paska (.tabs) - nawigacja przez ekran z kafelkami.
Import w starych testach: klikniecie '.tabs button[data-v=X]' / '.tabs [data-act=szybki]' / '.tabs a.tab-anl'
= powrot do ekranu kafelkow (przycisk z logo w naglowku) + stukniecie kafelka."""
import re
from playwright.sync_api._generated import Page

_orig = Page.click
_RE = re.compile(r'^\.tabs (?:button\[data-v=(\w+)\]|(\[data-act=szybki\])|(a\.tab-anl))$')


def do_kafelkow(pg):
    if pg.evaluate("window.__spk?window.__spk().S.v:''") == 'start':
        return
    _orig(pg, '.top-r .home-b >> visible=true')
    pg.wait_for_timeout(250)


def kafelek_sel(v):
    if v == 'szybki':
        return '.kaf-dod'
    return '.kaf[data-v=%s]' % v


def _click(self, selector, *a, **k):
    m = _RE.match(selector) if isinstance(selector, str) else None
    if not m:
        return _orig(self, selector, *a, **k)
    v = m.group(1) or ('szybki' if m.group(2) else 'anl')
    do_kafelkow(self)
    return _orig(self, kafelek_sel(v), *a, **k)


Page.click = _click
