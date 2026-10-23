"""Generates the scene specs (JSON) for every PPWR Smart ad version. Run: python3 build-specs.py
Paths are relative to this folder. Hooks differ per version; the body is shared per audience."""
import json, copy, os
HERE = os.path.dirname(os.path.abspath(__file__))
C = '../../../assets/clips/'; CA = '../../../assets/clips-ads/'; VO = '../voice/'; SC = '../screens/'
REC = '../../../assets/recordings/prototype-neutral.webm'
PPWR = {'tone': 'ppwr', 'text': 'PPWR · od 12.08.2026'}
BAD = {'tone': 'bad', 'text': 'Dziś, bez systemu'}
GOOD = {'tone': 'good', 'text': 'Z PPWR Smart'}
def clip(src, vo, cap, chip=BAD, **kw): return dict(kind='clip', src=src, vo=VO + vo, cap=cap, chip=chip, **kw)
def rec(a, b, vo, step, cap, pane='a', **kw): return dict(kind='rec', src=REC, **{'from': a}, to=b, vo=VO + vo, step=step, cap=cap, pane=pane, chip=GOOD, **kw)
def still(src, vo, step, cap, **kw): return dict(kind='still', src=SC + src, vo=VO + vo, step=step, cap=cap, chip=GOOD, **kw)
BOARD = dict(kind='board', big='A przepisów będzie przybywać.', vo=VO + 'tago-film-7.mp3', minD=3.2)
SLOGAN = clip(CA + 'h6-tailored.mp4', 'slogan.mp3', 'Automatyzacja deklaracji PPWR <b>szyta na miarę</b> Twojego przedsiębiorstwa.', GOOD, focus=0.6)
END = dict(kind='end', vo=VO + 'cta.mp3', minD=5, slogan='Automatyzacja deklaracji PPWR<br><b>szyta na miarę</b> Twojego przedsiębiorstwa',
           offer='Bezpłatny przegląd dokumentacji · 30 min', url='ppwrsmart.com')
# modules planned for stage 1 (TAGO plan, without the client): what the buyer gets, in one place
MODULES = dict(kind='modules', vo=VO + 'modules.mp3', title='PPWR Smart — moduły',
  items=['Import z Twojego ERP', 'Portal dostawcy', 'Receptury opakowań', 'Reguły PPWR i blokady', 'Deklaracje zgodności UE', 'Karty techniczne', 'Wersje i archiwum'])
TRANSITION = clip(C + '07-przejscie.mp4', 'transition.mp3', 'Dokument wpada — system sam go przypisuje.', GOOD, focus=0.55)

# ---------- A: producent żywności ----------
FOOD_HOOKS = {
  '1-data': clip(CA + 'h2-termin.mp4', 'hook-food-1-date.mp3', 'PPWR obowiązuje od <b>12 sierpnia 2026</b>. Masz deklaracje do wszystkich opakowań?', PPWR, focus=0.62),
  '2-folia': clip(C + '05-zmiana-folii.mp4', 'hook-food-2-foil.mp3', 'PPWR obowiązuje od <b>12.08.2026</b>. A Twój dostawca właśnie zmienił folię.', PPWR, focus=0.15),
  '3-kontrola': clip(CA + 'h5-kontrola.mp4', 'hook-food-3-inspection.mp3', 'PPWR już obowiązuje. Kontrola zapyta o <b>deklaracje</b>, nie o plany.', PPWR, focus=0.4),
  '4-kazde-opakowanie': clip(CA + 'h1-sciana.mp4', 'hook-food-4-every-package.mp3', 'Od <b>12 sierpnia</b> każde opakowanie w Twoim wyrobie potrzebuje dokumentacji zgodności. Każde.', PPWR, focus=0.5),
}
# 01-skrzynka is out: the AI drew made-up company names on the monitor (no proper names in ads, 23.10)
ROUND = clip(C + '06-obchod.mp4', 'tago-film-5.mp3', 'Co miesiąc: telefony, maile, przypomnienia — ręcznie.', focus=0.5)
R1 = rec(6.6, 13.4, 'tago-film-9.mp3', 'PPWR SMART · 1', 'Brakuje dokumentu? Wyrób zablokowany. Przypomnienie wychodzi jednym kliknięciem.', 'a')
R2 = rec(13.4, 22.5, 'tago-film-10.mp3', 'PPWR SMART · 2', 'Dostawca widzi tylko swoje opakowania. Uzupełnia i wysyła.', 'b', zoomTo=1.12, ox=1)
R3 = rec(22.5, 32.3, 'tago-film-11.mp3', 'PPWR SMART · 3', 'Akceptujesz — wyrób się odblokowuje.', 'a')
R4 = rec(33.0, 37.8, 'tago-film-12.mp3', 'PPWR SMART · 4', 'Zmiana u dostawcy = nowa wersja deklaracji. Stara zostaje w historii.', 'a', ox=0.5)
# "nawet godzina" = general observation, not a measurement (decision 23.10); no client named
TIME = clip(C + '08-system-pilnuje.mp4', 'food-time-no-hires.mp3', 'Ręcznie nawet <b>godzina</b> na deklarację. Z PPWR Smart — <b>kilka minut</b>. Bez nowych etatów.', GOOD, focus=0.5)
food_full = [FOOD_HOOKS['1-data'],
  clip(C + '03-wyrob.mp4', 'tago-film-2.mp3', 'Jeden wyrób — około <b>10</b> elementów opakowania, każdy od kogoś innego.'),
  clip(C + '04-poziomy.mp4', 'tago-film-3.mp3', '<b>Trzy</b> poziomy opakowania. <b>Dwie</b> ścieżki marki.'),
  clip(C + '05-zmiana-folii.mp4', 'tago-film-4.mp3', 'Dostawca zmienia folię. Deklaracja o tym nie wie.'),
  ROUND,
  clip(C + '02-biurko.mp4', 'food-hundreds.mp3', '<b>Setki</b> komponentów. Cała wiedza w głowie jednej osoby.'),
  BOARD, TRANSITION, R1, R2, R3, R4,
  TIME, MODULES,
  SLOGAN, END]

# ---------- B: producent kartonów ----------
CARTON_HOOKS = {
  '1-klient-pyta': clip(CA + 'k1-client-asks.mp4', 'hook-carton-1-client-asks.mp3', 'PPWR obowiązuje od <b>12 sierpnia 2026</b>. Klient pyta o deklarację do każdego zamówienia.', PPWR, focus=0.35),
  '2-word': clip(CA + 'k5-word-60-min.mp4', 'hook-carton-2-word.mp3', 'PPWR obowiązuje od <b>12.08.2026</b>. A Ty wciąż składasz deklaracje ręcznie, w Wordzie?', PPWR, focus=0.5),
  '3-tektura': clip(CA + 'k4-board-change.mp4', 'hook-carton-3-board-change.mp3', 'PPWR obowiązuje od <b>12.08.2026</b>. Dostawca tektury zmienił jej skład — Twoja deklaracja o tym nie wie.', PPWR, focus=0.35),
}
CARD1 = still('card-karta-robocza-maksymalna.png', 'carton-system-card.mp3', 'PPWR SMART · 1', 'Tektura z kartoteki surowców — karta techniczna składa się sama.', cropX=[0.2, 0.8], panFrom=0, panTo=0.45)
CARD2 = still('card-karta-wystawiona.png', 'carton-system-grouping.mp3', 'PPWR SMART · 2', 'Te same właściwości — jedna deklaracja. Zmiana surowca? System wskaże, co odnowić.', cropX=[0.2, 0.8], panFrom=0.4, panTo=0.62, zoomTo=1.08)
CARD3 = still('card-karta-wystawiona.png', 'carton-system-ready.mp3', 'PPWR SMART · 3', 'Karta i deklaracja gotowe dla klienta. Wszystko zostaje w archiwum.', cropX=[0.2, 0.8], panFrom=0, panTo=0.18)
RAW = clip(CA + 'k3-raw-materials.mp4', 'carton-raw-materials.mp3', 'Tektura, klej, farby — <b>każdy surowiec</b> z osobną dokumentacją.', focus=0.5)
THREE = clip(CA + 'k7-card-declaration.mp4', 'carton-3-min-no-hires.mp3', '<b>3 minuty</b> na deklarację — zmierzone u producenta kartonów. <b>Bez nowych etatów.</b>', GOOD, focus=0.45)
carton_full = [CARTON_HOOKS['1-klient-pyta'],
  clip(CA + 'k2-every-order.mp4', 'carton-every-order.mp3', 'Każde zamówienie to <b>inny karton</b>.', focus=0.5),
  RAW,
  clip(CA + 'k4-board-change.mp4', 'carton-board-change.mp3', 'Dostawca tektury zmienia jej skład. Deklaracja o tym nie wie.', focus=0.35),
  clip(CA + 'k5-word-60-min.mp4', 'carton-manual-hour.mp3', 'Deklaracja ręcznie, w Wordzie — nawet <b>godzina</b> na jedną.', focus=0.5),
  clip(CA + 'k6-archive.mp4', 'carton-archive.mp3', 'Archiwum na <b>5–10 lat</b>.', focus=0.5),
  BOARD, TRANSITION, CARD1, CARD2, CARD3, THREE, MODULES, SLOGAN, END]

def write(name, fmt, scenes):
  with open(os.path.join(HERE, name + '.json'), 'w') as f:
    json.dump({'format': fmt, 'scenes': copy.deepcopy(scenes)}, f, ensure_ascii=False, indent=1)
write('food-16x9-full', '16x9', food_full)
write('carton-16x9-full', '16x9', carton_full)
for k, h in FOOD_HOOKS.items():
  write(f'food-9x16-reel-{k}', '9x16', [h, TRANSITION, R1, R3, TIME, MODULES, SLOGAN, END])
for k, h in CARTON_HOOKS.items():
  write(f'carton-9x16-reel-{k}', '9x16', [h, RAW if k != '2-word' else clip(CA + 'k2-every-order.mp4', 'carton-every-order.mp3', 'Każde zamówienie to <b>inny karton</b>.', focus=0.5), TRANSITION, CARD1, THREE, MODULES, SLOGAN, END])
print(sorted(f for f in os.listdir(HERE) if f.endswith('.json')))
