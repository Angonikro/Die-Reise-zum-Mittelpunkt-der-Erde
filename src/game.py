#!/usr/bin/env python3
"""Die Reise zum Mittelpunkt der Erde — point-and-click adventure."""
from pathlib import Path
import math, sys, os, json, wave, struct, array
import pygame

TITLE = "Die Reise zum Mittelpunkt der Erde"
VERSION = "2.3.1"
W, H, SCENE_H, FPS = 1024, 768, 620, 60
HERE = Path(__file__).resolve().parent.parent
SYSTEM_ASSETS = Path('/usr/share/reise-mittelpunkt-erde/assets')
CONFIG_DIR = Path.home() / '.config' / 'reise-mittelpunkt-erde'
CONFIG_FILE = CONFIG_DIR / 'settings.json'
SAVE_FILE = CONFIG_DIR / 'savegame.json'
MUSIC_DIR = HERE / 'assets' / 'music'
SFX_DIR = HERE / 'assets' / 'sounds'

def asset(name):
    for root in (HERE / 'assets', SYSTEM_ASSETS):
        p = root / name
        if p.is_file(): return p
    raise FileNotFoundError(f'Grafikdatei fehlt: {name}')

def main():
    # SDL-Treiber muss vor pygame.init feststehen; eine Auswahl wird gespeichert
    # und beim nächsten Start verwendet.
    try:
        cfg = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
    except Exception: cfg = {}
    requested_driver = cfg.get('sound_driver', 'system')
    if requested_driver in ('alsa', 'pulseaudio'):
        os.environ['SDL_AUDIODRIVER'] = requested_driver
    else:
        os.environ.pop('SDL_AUDIODRIVER', None)
    # Groesserer Audiopuffer reduziert Knackser/Underruns auf langsameren Systemen.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
    pygame.init()
    try:
        device = cfg.get('sound_device') or None
        if device:
            try: pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048, devicename=device)
            except (TypeError, pygame.error): pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        else: pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    except pygame.error: pass
    fullscreen = bool(cfg.get('fullscreen', False))
    flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
    screen = pygame.display.set_mode((W, H), flags)
    pygame.display.set_caption(f'{TITLE} · {VERSION}')
    clock = pygame.time.Clock()
    canvas = pygame.Surface((W, H))
    room = pygame.transform.smoothscale(pygame.image.load(str(asset('arbeitszimmer.png'))).convert(), (W, SCENE_H))
    scene_images = {name: pygame.transform.smoothscale(pygame.image.load(str(asset(name + '.jpg'))).convert(), (W, SCENE_H)) for name in ('zweites_zimmer','flur','hafen')}
    scene_images['schiff'] = pygame.transform.smoothscale(pygame.image.load(str(asset('schiff.jpg'))).convert(), (W, SCENE_H))
    # Neue, eigenständige Sturmfahrt-Szene; die vorhandenen Szenen bleiben unverändert.
    scene_images['ueberfahrt'] = pygame.transform.smoothscale(pygame.image.load(str(asset('ueberfahrt.jpg'))).convert(), (W, SCENE_H))
    # Separater Hafen nach der Überfahrt; der bisherige Ausgangshafen bleibt unangetastet.
    scene_images['island_hafen'] = pygame.transform.smoothscale(pygame.image.load(str(asset('island_hafen.jpg'))).convert(), (W, SCENE_H))
    # Eigenständiges Zimmer von Professor Fridriksson in Reykjavík.
    scene_images['fridriksson'] = pygame.transform.smoothscale(pygame.image.load(str(asset('fridriksson.jpg'))).convert(), (W, SCENE_H))
    # Neues Hintergrundbild für den Aufbruch mit Hans; Hauptfigur Axel wird wie gewohnt separat gezeichnet.
    scene_images['island_weg'] = pygame.transform.smoothscale(pygame.image.load(str(asset('island_weg.jpg'))).convert(), (W, SCENE_H))
    # Neuer, eigenständiger Küstenweg nach der Kreuzung; keine Dialoge/Figuren im Hintergrund.
    scene_images['stapi'] = pygame.transform.smoothscale(pygame.image.load(str(asset('stapi.jpg'))).convert(), (W, SCENE_H))
    stapi_chest_open_img = pygame.image.load(str(asset('vermessungskiste_offen.png'))).convert_alpha()
    stapi_chest_open_img = pygame.transform.smoothscale(stapi_chest_open_img, (210, 165))
    stapi_chest_closed_img = pygame.image.load(str(asset('vermessungskiste_geschlossen.png'))).convert_alpha()
    stapi_chest_closed_img = pygame.transform.smoothscale(stapi_chest_closed_img, (210, 165))
    # Eigenständiger Bergaufstieg: sichtbare Felsnadeln und Seilanker statt des Stapi-Hintergrunds.
    scene_images['stapi_aufstieg'] = pygame.transform.smoothscale(pygame.image.load(str(asset('stapi_aufstieg.jpg'))).convert(), (W, SCENE_H))
    scene_images['krater'] = pygame.transform.smoothscale(pygame.image.load(str(asset('krater.jpg'))).convert(), (W, SCENE_H))
    scene_images['tiefe'] = pygame.transform.smoothscale(pygame.image.load(str(asset('tiefe.jpg'))).convert(), (W, SCENE_H))
    scene_images['gaenge'] = pygame.transform.smoothscale(pygame.image.load(str(asset('unterirdische_gaenge.jpg'))).convert(), (W, SCENE_H))
    scene_images['meer'] = pygame.transform.smoothscale(pygame.image.load(str(asset('unterirdisches_meer.jpg'))).convert(), (W, SCENE_H))
    # Punkt 4 nutzt denselben figurenfreien Küstenhintergrund; Floßmaterial wird separat gezeichnet/erkundet.
    # Eigenständiger figurenfreier Hintergrund für Punkt 4: Floßlager am Ufer.
    scene_images['floss'] = pygame.transform.smoothscale(pygame.image.load(str(asset('floesslager.jpg'))).convert(), (W, SCENE_H))
    # Punkt 5: Unterirdisches Meer mit Algenfeldern und urzeitlichen Meerestieren.
    scene_images['meerfahrt'] = pygame.transform.smoothscale(pygame.image.load(str(asset('meerfahrt.jpg'))).convert(), (W, SCENE_H))
    # Punkt 5: eigener figurenfreier Hintergrund für die sichere Küste.
    # Rätsel, Klickbereiche und Übergänge bleiben unverändert.
    scene_images['meerfahrt_ende'] = pygame.transform.smoothscale(
        pygame.image.load(str(asset('sichere_kueste.jpg'))).convert(), (W, SCENE_H)
    )
    # Punkt 6: Rückkehr durch den Vulkanschlot nach Stromboli.
    scene_images['punkt6'] = pygame.transform.smoothscale(pygame.image.load(str(asset('punkt6_vulkan.jpg'))).convert(), (W, SCENE_H))
    menu = pygame.transform.smoothscale(pygame.image.load(str(asset('hauptmenue.jpg'))).convert(), (W, H))
    intro_bg = pygame.transform.smoothscale(pygame.image.load(str(asset('vorspann.jpg'))).convert(), (W, H))

    def character(name, height):
        # Neue eigenständige, photorealistische PNG-Figur mit Alpha-Kanal.
        # Nur transparente Außenränder werden entfernt; keine alte Hintergrund-Freistellung.
        im = pygame.image.load(str(asset(name))).convert_alpha()
        bounds = im.get_bounding_rect(min_alpha=8)
        im = im.subsurface(bounds).copy()
        ratio = height / max(1, im.get_height())
        return pygame.transform.smoothscale(im, (max(1, round(im.get_width()*ratio)), height))
    axel_r = character('axel.png', 417)  # Standardgroesse ausserhalb von Hafen und Schiff
    axel_l = pygame.transform.flip(axel_r, True, False)
    # Im Hafen und an Bord wird Axel um weitere 20 % verkleinert.
    # Die Fuesse bleiben beim Zeichnen am selben Bodenpunkt verankert.
    axel_harbor_r = pygame.transform.smoothscale(axel_r, (max(1, round(axel_r.get_width() * 0.8)), max(1, round(axel_r.get_height() * 0.8))))
    axel_harbor_l = pygame.transform.flip(axel_harbor_r, True, False)
    professor = character('professor.png', 417)  # Originalgröße; in Außenszenen separat verkleinert
    professor_fridriksson = character('fridriksson.png', 365)  # Eigenständige Figur
    hans_sprite = character('hans.png', 365)  # Isländischer Führer mit Wanderstab und Gepäck

    serif = pygame.font.SysFont('DejaVu Serif', 34, bold=True)
    font = pygame.font.SysFont('DejaVu Sans', 25)
    small = pygame.font.SysFont('DejaVu Sans', 19)
    tiny = pygame.font.SysFont('DejaVu Sans', 15)
    gold, cream = (229, 179, 83), (250, 236, 210)
    state, intro_start = 'intro', pygame.time.get_ticks()
    volume = max(0.0, min(1.0, float(cfg.get('volume', 0.72))))
    effects_volume = max(0.0, min(1.0, float(cfg.get('effects_volume', 0.65))))
    if pygame.mixer.get_init(): pygame.mixer.music.set_volume(volume)
    effects_channel = pygame.mixer.Channel(1) if pygame.mixer.get_init() else None
    effects_sounds = {}
    if pygame.mixer.get_init():
        for effect_name in ('fireplace', 'seagulls', 'harbor', 'wind', 'cave_drips'):
            effect_path = SFX_DIR / f'{effect_name}.ogg'
            if effect_path.is_file():
                try: effects_sounds[effect_name] = pygame.mixer.Sound(str(effect_path))
                except pygame.error: pass
        water_path = SFX_DIR / 'wasser.mp3'
        if water_path.is_file():
            try: effects_sounds['wasser'] = pygame.mixer.Sound(str(water_path))
            except pygame.error: pass
    active_effect = None
    sound_driver = requested_driver
    sound_devices = []
    try:
        from pygame._sdl2 import audio as sdl_audio
        sound_devices = sdl_audio.get_audio_device_names(False) or []
    except Exception: pass
    sound_device_index = sound_devices.index(cfg['sound_device']) if cfg.get('sound_device') in sound_devices else -1
    settings_from = 'menu'
    credits_from = 'menu'
    music_state = None
    intro_page = 0
    intro_pages = [
        ('Hamburg, 1863', 'Professor Lidenbrock entdeckt in einem alten Buch ein geheimnisvolles Pergament.'),
        ('Eine rätselhafte Schrift', 'Axel versucht, die fremdartigen Zeichen zu verstehen.'),
        ('Ein gefährliches Geheimnis', 'Die Botschaft scheint den Weg ins Erdinnere zu beschreiben.'),
    ]
    message, message_until = '', 0
    inventory, selected = [], None
    map_found = False
    compass_found = False
    course_calculated = False
    map_on_table = False
    compass_on_table = False
    px, py = 175.0, 590.0
    tx, ty, moving, facing_right, pending = px, py, False, True, None
    running = True
    last_autosave = 0
    save_notice = ''
    bookshelf_examined = False
    professor_spoken = False
    parchment_deciphered = False
    harbor_unlocked = False
    harbor_key_found = False
    crate_open = False
    sailors_spoken = []  # Rufzeichen der Matrosen, mit denen Axel gesprochen hat
    crossing_tasks = []  # Fortschritt des Sturm-Rätsels; bestehende Spielstände bleiben kompatibel
    island_workers_spoken = []
    island_rope_found = False
    hans_way_known = False
    fridriksson_spoken = False
    fridriksson_puzzle_solved = False
    hans_spoken = False
    island_route_solved = False
    stapi_crate_open = False
    stapi_fieldbook_found = False
    ascent_rope_secured = False
    ascent_route_solved = False
    crater_route_solved = False
    # Nur eine ausdrücklich in dieser Spielsitzung angewendete Seilaktion schaltet den Abstieg frei.
    crater_rope_used = False
    cave_professor_spoken = False
    cave_hans_spoken = False
    cave_passage_examined = False
    cave_enter_pending = False
    gaenge_clues = []
    gaenge_route_solved = False
    meer_clues = []
    meer_route_solved = False
    meer_holz_gesammelt = False
    meer_ranken_gesammelt = False
    floss_ready = False
    floss_wood_aligned = False
    floss_buoyancy_checked = False
    meerfahrt_clues = []
    meerfahrt_solved = False
    punkt6_clues = []
    punkt6_path_open = False

    # Koordinaten liegen auf der 1024x620-Szene; Symbole werden nur beim Hover gezeichnet.
    hotspots = [
        {'name':'Pergament','rect':pygame.Rect(475, 320, 110, 70),'kind':'eye','approach':(500,570),'text':'Auf dem Pergament stehen feine, fremdartige Zeichen.'},
        {'name':'Lupe','rect':pygame.Rect(390, 270, 36, 36),'kind':'hand','approach':(400,570),'item':'Lupe','text':'Hinter den Büchern steckt eine alte Messinglupe.'},
        {'name':'Professor','rect':pygame.Rect(735, 220, 145, 365),'kind':'talk','approach':(690,570),'text':'Professor Lidenbrock: „Dieses Pergament gibt mir Rätsel auf. Die Zeichen sind kaum zu erkennen. Sieh es dir genauer an, Axel.“'},
        {'name':'Bücherregal','rect':pygame.Rect(355, 140, 40, 40),'kind':'eye','approach':(360,570),'text':'Alte wissenschaftliche Werke füllen die Regale.'},
        {'name':'Karte','rect':pygame.Rect(680, 110, 40, 40),'kind':'eye','approach':(670,570),'text':'Die Karte zeigt Island und den Snæfellsjökull.'},
        {'name':'Kamin','rect':pygame.Rect(925, 380, 40, 40),'kind':'eye','approach':(870,570),'text':'Das Feuer knistert im alten Kamin.'},
        {'name':'Globus','rect':pygame.Rect(966, 392, 48, 48),'kind':'eye','approach':(900,570),'text':'Der Globus zeigt die bekannte Welt. Island liegt weit im Norden.'},
        {'name':'Standuhr','rect':pygame.Rect(875, 132, 48, 48),'kind':'eye','approach':(850,570),'text':'Die alte Uhr tickt ruhig. Es bleibt noch Zeit für Vorbereitungen.'},
        {'name':'Feder und Tinte','rect':pygame.Rect(668, 346, 48, 48),'kind':'eye','approach':(650,570),'text':'Eine Feder und ein Tintenfass liegen bereit. Vielleicht werden sie noch gebraucht.'},
    ]
    def save_settings():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps({'fullscreen': fullscreen, 'sound_driver': sound_driver,
            'sound_device': sound_devices[sound_device_index] if 0 <= sound_device_index < len(sound_devices) else '',
            'volume': volume, 'effects_volume': effects_volume}, indent=2))
    def set_fullscreen(value):
        nonlocal fullscreen, screen
        fullscreen = value
        screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE)
        save_settings()
    def say(text, ms=4500):
        # Dialoge und Hinweistexte bleiben sichtbar, bis links geklickt wird.
        nonlocal message, message_until
        message, message_until = text, -1
    def hit(pos):
        if state in ('room', 'chapter2'):
            route = [
                {'name':'Zum zweiten Zimmer','rect':pygame.Rect(955,120,69,470),'kind':'walk','approach':(930,570),'route':'zweites_zimmer'},
            ]
            candidates = hotspots + route
        elif state == 'zweites_zimmer':
            candidates = [
                {'name':'Zurück ins Arbeitszimmer','rect':pygame.Rect(0,100,95,500),'kind':'walk','approach':(80,570),'route':'room'},
                {'name':'Zum Flur','rect':pygame.Rect(925,100,99,500),'kind':'walk','approach':(910,570),'route':'flur'},
            ]
        elif state == 'flur':
            candidates = [
                {'name':'Zurück ins zweite Zimmer','rect':pygame.Rect(0,100,110,500),'kind':'walk','approach':(90,570),'route':'zweites_zimmer'},
            ]
            if harbor_unlocked:
                candidates.append({'name':'Zum Hafen','rect':pygame.Rect(890,100,134,500),'kind':'walk','approach':(880,570),'route':'hafen'})
        elif state == 'hafen':
            candidates = [
                {'name':'Zurück zum Flur','rect':pygame.Rect(0,100,105,500),'kind':'walk','approach':(80,570),'route':'flur'},
                {'name':'Seekarte','rect':pygame.Rect(265,300,120,100),'kind':'hand','approach':(320,570),'item':'Seekarte','text':'Zwischen den Ladungskisten steckt eine gefaltete Seekarte.'},
                {'name':'Hafenarbeiter','rect':pygame.Rect(690,185,70,190),'kind':'talk','approach':(675,570),'text':'Ein Hafenarbeiter steht halb verborgen hinter gestapelter Ladung.'},
                {'name':'Holzkiste','rect':pygame.Rect(590,330,150,135),'kind':'eye','approach':(570,570),'text':'Eine kleine Kiste ist mit einem Vorhängeschloss gesichert.'},
                {'name':'Kompass','rect':pygame.Rect(615,350,90,90),'kind':'hand','approach':(570,570),'item':'Kompass','text':'In der geöffneten Kiste liegt ein alter Messingkompass.'},
                {'name':'Schiff betreten','rect':pygame.Rect(870,110,154,480),'kind':'walk','approach':(850,570),'route':'schiff'},
            ]
        elif state == 'schiff':
            candidates = [
                {'name':'Zurück in den Hafen','rect':pygame.Rect(0,100,105,500),'kind':'walk','approach':(120,570),'route':'hafen'},
                # Die drei sichtbaren Matrosen haben großzügige Klickflächen (mindestens ca. 1 cm).
                {'name':'Matrose am linken Reling','rect':pygame.Rect(24,285,100,150),'kind':'talk','approach':(190,570),'sailor_id':'reling','text':'Matrose am linken Reling: „Der Wind steht günstig, aber der Kapitän will, dass du zuerst mit der Mannschaft sprichst.“'},
                {'name':'Matrose am Steuerrad','rect':pygame.Rect(625,35,95,130),'kind':'talk','approach':(600,570),'sailor_id':'steuerrad','text':'Matrose am Steuerrad: „Für Island müssen wir nach Nordwesten. Prüfe die Seekarte sorgfältig, bevor du den Kurs festlegst.“'},
                {'name':'Matrose an der Kiste','rect':pygame.Rect(930,265,90,150),'kind':'talk','approach':(820,570),'sailor_id':'kiste','text':'Matrose bei den Kisten: „Die Ausrüstung ist verstaut. Wenn du mit den anderen gesprochen hast, kannst du den Kurs bestimmen.“'},
                {'name':'Navigationstisch','rect':pygame.Rect(535,325,315,155),'kind':'eye','approach':(520,475),'text':'Am Navigationstisch kannst du Seekarte und Kompass auslegen. Sprich zuerst mit allen drei Matrosen. Danach kannst du mit Karte und Kompass den Kurs bestimmen.'},
            ]
            if course_calculated:
                candidates.append({'name':'Überfahrt beginnen','rect':pygame.Rect(900,120,124,470),'kind':'walk','approach':(850,570),'route':'ueberfahrt','text':'Die Mannschaft ist bereit. Beginne die stürmische Überfahrt nach Island.'})
        elif state == 'island_hafen':
            candidates = [
                {'name':'Zurück zum Schiff','rect':pygame.Rect(0,100,20,360),'kind':'walk','approach':(120,570),'route':'schiff','text':'Das Schiff liegt noch am Kai.'},
                {'name':'Hafenarbeiter 1','rect':pygame.Rect(28,225,112,175),'kind':'talk','approach':(200,570),'worker_id':'arbeiter1','text':'Der Arbeiter erklärt: „Wenn ihr einen Gelehrten sucht, fragt nach Professor Fridriksson. Sein Haus liegt oberhalb der Gasse.“'},
                {'name':'Hafenarbeiter 2','rect':pygame.Rect(170,245,75,145),'kind':'talk','approach':(380,570),'worker_id':'arbeiter2','text':'Der Arbeiter nickt: „Professor Fridriksson kennt die Reisenden und die Gegend. Sucht sein Haus bei der kleinen Kirche.“'},
                {'name':'Hafenarbeiter 3','rect':pygame.Rect(250,275,65,130),'kind':'talk','approach':(600,570),'worker_id':'arbeiter3','text':'Der Arbeiter bestätigt: „Fridriksson wird euch weiterhelfen. Hans müsst ihr jetzt noch nicht suchen.“'},
                {'name':'Alter Fischer','rect':pygame.Rect(770,245,105,165),'kind':'talk','approach':(800,570),'worker_id':'fischer','text':'Der Fischer deutet zur Stadt: „Fragt zuerst Professor Fridriksson. Er kennt einen geeigneten Führer für eure Reise.“'},
                {'name':'Altes Seil','rect':pygame.Rect(150,490,190,95),'kind':'hand','approach':(320,575),'item':'Seil','text':'Du nimmst das Seil mit.'},
            ]
            if len(set(island_workers_spoken)) >= 3:
                candidates.append({'name':'Zu Professor Fridriksson','rect':pygame.Rect(900,100,124,500),'kind':'walk','approach':(850,570),'route':'fridriksson','text':'Du hast genug Hinweise erhalten. Jetzt sucht ihr Professor Fridriksson auf.'})
        elif state == 'fridriksson':
            candidates = [
                {'name':'Zurück zum Hafen','rect':pygame.Rect(0,100,90,500),'kind':'walk','approach':(120,570),'route':'island_hafen','text':'Du gehst zurück zum Hafen von Reykjavík.'},
                {'name':'Professor Fridriksson','rect':pygame.Rect(735,200,105,265),'kind':'talk','approach':(735,570),'text':'Professor Fridriksson empfängt euch freundlich. Er hört von Lidenbrocks Plänen und erklärt, dass Hans Bjelke ein zuverlässiger Führer für die Reise zum Snæfellsjökull ist.'},
            ]
            candidates.extend([
                # Antwortflächen liegen direkt auf der Islandkarte an der Wand, nicht am Boden.
                {'name':'Mit dem Boot über die Bucht','rect':pygame.Rect(610,35,78,140),'kind':'hand','approach':(700,565)},
                {'name':'Zu Fuß entlang der Küste','rect':pygame.Rect(688,35,88,140),'kind':'hand','approach':(700,565)},
            ])
            if fridriksson_spoken and fridriksson_puzzle_solved:
                candidates.append({'name':'Hans Bjelke aufsuchen','rect':pygame.Rect(940,100,84,500),'kind':'walk','approach':(850,570),'route':'hans','text':'Fridriksson hat Hans empfohlen. Nun könnt ihr ihn aufsuchen.'})
        elif state == 'hans':
            candidates = [
                {'name':'Zurück zum Hafen','rect':pygame.Rect(0,100,90,500),'kind':'walk','approach':(120,570),'route':'island_hafen','text':'Du gehst zurück zum Hafen von Reykjavík.'},
                {'name':'Hans Bjelke','rect':pygame.Rect(735,205,150,300),'kind':'talk','approach':(690,570),'text':'Hans Bjelke: „Ihr wollt zum Snæfellsjökull? Dann brechen wir bei Tagesanbruch auf. Nehmt alles mit, was ihr unterwegs brauchen könntet.“'},
                # Das Seil bleibt auch erreichbar, wenn der Spieler Hans bereits besucht hat.
                {'name':'Altes Seil','rect':pygame.Rect(150,490,190,95),'kind':'hand','approach':(320,575),'item':'Seil','text':'Du nimmst das kräftige Seil mit.'},
            ]
            if hans_spoken:
                candidates.append({'name':'Mit Hans aufbrechen','rect':pygame.Rect(900,100,124,500),'kind':'walk','approach':(850,570),'route':'island_weg','text':'Ihr brecht mit Hans auf dem Landweg Richtung Snæfellsjökull auf.'})
        elif state == 'island_weg':
            candidates = [
                {'name':'Zurück zu Hans','rect':pygame.Rect(0,100,90,500),'kind':'walk','approach':(120,570),'route':'hans','text':'Du gehst zu Hans zurück, um die Route noch einmal zu besprechen.'},
                {'name':'Wegweiser','rect':pygame.Rect(145,95,225,180),'kind':'eye','approach':(405,570),'text':'Der Wegweiser zeigt zum Snæfellsjökull. Bevor ihr weitergeht, solltet ihr mit dem Kompass die Richtung prüfen.'},
                {'name':'Hans Bjelke am Weg','rect':pygame.Rect(735,205,150,300),'kind':'talk','approach':(690,570),'text':'Hans erklärt den Weg nach Stapi.'},
            ]
            if not island_route_solved:
                candidates.append({'name':'Küstenweg nach Stapi','rect':pygame.Rect(330,400,360,175),'kind':'hand','approach':(520,570),'text':'Hans wartet auf deine Entscheidung zur Wegführung.'})
            else:
                candidates.append({'name':'Weiter entlang der Küste','rect':pygame.Rect(330,400,360,175),'kind':'walk','approach':(520,570),'route':'stapi','text':'Ihr folgt Hans westwärts entlang der Küste nach Stapi.'})
        elif state == 'stapi':
            candidates = [
                {'name':'Zurück zum Küstenweg','rect':pygame.Rect(0,100,90,500),'kind':'walk','approach':(120,570),'route':'island_weg','text':'Ihr geht den Küstenweg zurück zur Kreuzung.'},
                {'name':'Weg zum Snæfellsjökull','rect':pygame.Rect(700,300,300,260),'kind':'walk','approach':(720,570),'route':'stapi_aufstieg','text':'Der Pfad steigt in Richtung Snæfellsjökull an.'},
                {'name':'Meer beobachten','rect':pygame.Rect(35,255,300,155),'kind':'eye','approach':(370,570),'text':'Du blickst über das Meer. Die Brandung schlägt gegen die schwarzen Lavaklippen; draußen ziehen Vögel über dem Wasser. Der Küstenweg führt weiter nach Westen.'},
                {'name':'Küste betrachten','rect':pygame.Rect(20,410,370,145),'kind':'eye','approach':(400,570),'text':'Zwischen den schwarzen Lavaklippen und dem Dorf verläuft ein schmaler Küstenpfad. Der Weg zum Gletscher steigt landeinwärts an.'},
                {'name':'Hans Bjelke','rect':pygame.Rect(735,205,150,300),'kind':'talk','approach':(690,570),'text':'Hans Bjelke: „Hier in Stapi sammeln wir unsere Kräfte. Von hier aus steigen wir zum Snæfellsjökull hinauf. Der Pfad wird steiler und das Wetter kann rasch umschlagen.“'},
                {'name':'Alte Vermessungskiste','rect':pygame.Rect(445,420,115,105),'kind':'eye','approach':(430,570),'text':'Eine verwitterte Vermessungskiste liegt halb zwischen den Steinen. Das Schloss ist rostig; im Holz sind verblasste Messzeichen eingeritzt.'},
            ]
        elif state == 'stapi_aufstieg':
            candidates = [
                {'name':'Zurück nach Stapi','rect':pygame.Rect(0,100,70,500),'kind':'walk','approach':(120,570),'route':'stapi','text':'Ihr kehrt zum Dorf Stapi zurück.'},
                # Hans hat eine eigene, eng an seinem Sprite liegende Gesprächsfläche.
                {'name':'Hans Bjelke','rect':pygame.Rect(755,260,130,315),'kind':'talk','approach':(700,570),'text':'Hans sieht sich den steilen Pfad schweigend an.'},
                # Der Weg ist ein Untersuchungsziel, kein aufnehmbarer Gegenstand.
                {'name':'Steiler Bergpfad','rect':pygame.Rect(585,330,180,175),'kind':'eye','approach':(520,570),'text':'Der schmale Pfad führt zwischen dunklem Lavagestein und losem Geröll hinauf.'},
                {'name':'Dreifach gespaltene Felsnadel','rect':pygame.Rect(820,45,155,195),'kind':'eye','approach':(690,570),'text':'Drei schmale Felsspitzen ragen aus dem Geröll. Ihre Form kommt dir bekannt vor.'},
            ]
            if ascent_route_solved:
                candidates.append({'name':'Weiter zum Kraterrand','rect':pygame.Rect(880,100,140,450),'kind':'walk','approach':(820,570),'route':'krater','text':'Der schmale Pfad führt hinauf zum Kraterrand.'})
        elif state == 'krater':
            candidates = [
                {'name':'Zurück zum Bergpfad','rect':pygame.Rect(0,100,80,500),'kind':'walk','approach':(120,570),'route':'stapi_aufstieg','text':'Ihr kehrt vom Kraterrand zum Bergpfad zurück.'},
                # Enge, getrennte Hotspots direkt auf den drei sichtbaren Öffnungen.
                {'name':'Linke Öffnung','rect':pygame.Rect(75,245,105,125),'kind':'eye','approach':(260,570),'vent':'links','text':'Du untersuchst die linke Öffnung.'},
                {'name':'Mittlere Öffnung','rect':pygame.Rect(390,230,105,125),'kind':('walk' if (crater_route_solved and crater_rope_used) else 'eye'),'approach':(500,570),'vent':'mitte','route':('tiefe' if (crater_route_solved and crater_rope_used) else None),'text':'Du untersuchst die mittlere Öffnung.'},
                {'name':'Rechte Öffnung','rect':pygame.Rect(790,250,105,125),'kind':'eye','approach':(735,570),'vent':'rechts','text':'Du untersuchst die rechte Öffnung.'},
                {'name':'Professor Lidenbrock','rect':pygame.Rect(365,230,85,235),'kind':'talk','approach':(430,570),'text':'Lidenbrock betrachtet aufmerksam den Krater und wartet auf deine Beobachtungen.'},
                {'name':'Hans Bjelke','rect':pygame.Rect(900,365,90,220),'kind':'talk','approach':(760,570),'text':'Hans blickt prüfend über die Felsen. „Wir sollten vorsichtig sein. Der Abstieg ist steil.“'},
            ]
            # Kein separater Lauf-Hotspot: Abstieg nur über die mittlere Öffnung
            # und erst nach ausdrücklicher Befestigung des Seils.
        elif state == 'tiefe':
            candidates = [
                {'name':'Zurück zum Kraterrand','rect':pygame.Rect(0,100,80,500),'kind':'walk','approach':(120,570),'route':'krater','text':'Ihr kehrt zum Kraterrand zurück.'},
                ({'name':'Dunkler Abstieg','rect':pygame.Rect(875,150,149,440),'kind':'walk','approach':(900,570),'route':'gaenge','text':'Der Weg führt rechts tiefer in die unterirdischen Gänge.'} if cave_professor_spoken and cave_hans_spoken and cave_passage_examined else {'name':'Dunkler Abstieg','rect':pygame.Rect(875,150,149,440),'kind':'eye','approach':(900,570),'text':'Rechts fällt der Gang steil ab. Aus der Tiefe dringt ein fernes, hohles Echo.'}),
                {'name':'Professor Lidenbrock in der Höhle','rect':pygame.Rect(220,110,230,445),'kind':'talk','approach':(410,570),'text':'Du sprichst mit Professor Lidenbrock über den Abstieg.'},
                {'name':'Hans Bjelke in der Höhle','rect':pygame.Rect(720,95,255,485),'kind':'talk','approach':(700,570),'text':'Du sprichst mit Hans über den Weg in die Tiefe.'},
            ]
        elif state == 'gaenge':
            candidates = [
                {'name':'Zurück zur ersten Höhlenkammer','rect':pygame.Rect(0,100,78,500),'kind':'walk','approach':(115,570),'route':'tiefe','text':'Ihr kehrt in die erste Höhlenkammer zurück.'},
                {'name':'Lidenbrock befragen','rect':pygame.Rect(285,390,48,78),'kind':'talk','approach':(345,570),'text':'Lidenbrock: „Beobachte Wasser und Luftzug genau. Die Natur zeigt uns den gangbaren Weg.“'},
                {'name':'Hans befragen','rect':pygame.Rect(745,380,48,85),'kind':'talk','approach':(710,570),'text':'Hans lauscht: „Der Luftzug kommt von dort, wo der Bach weiter in die Tiefe zieht.“'},
                {'name':'Feuchte Felswand','rect':pygame.Rect(335,300,58,55),'kind':'eye','approach':(360,570),'clue':'wasser','text':'Auf dem Gestein glänzen feuchte Spuren. Das Wasser sickert von links nach rechts.'},
                {'name':'Luftzug prüfen','rect':pygame.Rect(500,235,55,48),'kind':'eye','approach':(520,570),'clue':'luft','text':'Ein kühler Luftzug kommt aus dem mittleren Gang.'},
                {'name':'Echo prüfen','rect':pygame.Rect(825,260,58,55),'kind':'eye','approach':(760,570),'clue':'echo','text':'Das Echo klingt rechts laut, aber kurz und abgeschlossen.'},
                {'name':'Linker Gang','rect':pygame.Rect(55,165,230,250),'kind':'eye','approach':(230,570),'tunnel':'links','text':'Ein schmaler Gang verliert sich zwischen zerklüftetem Lavagestein.'},
                {'name':'Mittlerer Gang','rect':pygame.Rect(390,155,270,145),'kind':'eye','approach':(500,570),'tunnel':'mitte','text':'Aus dem mittleren Gang kommt ein leiser, gleichmäßiger Luftzug.'},
                {'name':'Rechter Gang','rect':pygame.Rect(830,185,105,82),'kind':'eye','approach':(790,570),'tunnel':'rechts','text':'Aus dem rechten Gang dringt ein deutliches Echo, doch kein frischer Luftzug.'},
                {'name':'Lidenbrock befragen','rect':pygame.Rect(285,395,48,78),'kind':'talk','approach':(350,570),'text':'Lidenbrock: „Die Hinweise müssen zusammenpassen, bevor wir dem Ufer folgen.“'},
                {'name':'Hans befragen','rect':pygame.Rect(745,390,48,85),'kind':'talk','approach':(700,570),'text':'Hans: „Am Bach entlang finden wir den Weg zum großen Wasser.“'},
                *([{'name':'Zum unterirdischen Meer','rect':pygame.Rect(930,150,94,440),'kind':'walk','approach':(900,570),'route':'meer','text':'Ihr folgt dem Gang bis zum Ufer des unterirdischen Meeres.'}] if gaenge_route_solved else []),
            ]
        elif state == 'meer':
            candidates = [
                {'name':'Zurück in die unterirdischen Gänge','rect':pygame.Rect(0,100,75,500),'kind':'walk','approach':(115,570),'route':'gaenge','text':'Ihr kehrt vom Ufer in die unterirdischen Gänge zurück.'},
                {'name':'Lidenbrock befragen','rect':pygame.Rect(285,395,48,78),'kind':'talk','approach':(350,570),'text':'Lidenbrock: „Dieses Meer scheint gewaltig. Wir müssen zuerst die Küste vermessen und einen sicheren Lagerplatz finden.“'},
                {'name':'Hans befragen','rect':pygame.Rect(745,390,48,85),'kind':'talk','approach':(700,570),'text':'Hans: „Der Fels ist am flachen Ufer fest. Dort können wir Holz sammeln und das Floß vorbereiten.“'},
                {'name':'Wasserlinie untersuchen','rect':pygame.Rect(410,410,72,44),'kind':'eye','approach':(430,570),'clue':'meer_wasser','text':'Die Wasserlinie zeigt, dass der See ruhig genug ist, doch der Uferboden ist steil.'},
                {'name':'Küstenverlauf vermessen','rect':pygame.Rect(540,365,65,48),'kind':'eye','approach':(555,570),'clue':'meer_kuste','text':'Die Felskante führt zu einer flachen Stelle am Ufer.'},
                {'name':'Holz aufnehmen','rect':pygame.Rect(130,475,100,65),'kind':'hand','approach':(230,570),'text':'Du hebst einen langen, festen Stamm vom trockenen Ufer auf.'},
                {'name':'Ranken sammeln','rect':pygame.Rect(35,300,90,115),'kind':'hand','approach':(155,570),'text':'Du sammelst zähe Ranken aus den Felsritzen. Sie eignen sich zum Verschnüren der Stämme.'},
                {'name':'Flache Anlegestelle','rect':pygame.Rect(605,430,80,48),'kind':'eye','approach':(620,570),'text':'Hier könnte das Floß sicher ins Wasser gelassen werden. Untersuche erst die Wasserlinie, Küste und das Material.'},
                *([{'name':'Zum Floßlager','rect':pygame.Rect(930,150,94,440),'kind':'walk','approach':(890,570),'route':'floss','text':'Ihr bringt das gefundene Holz zur flachen Anlegestelle und beginnt mit der Vorbereitung des Floßes.'}] if meer_route_solved else []),
            ]
        elif state == 'floss':
            candidates = [
                {'name':'Zurück zum Ufer','rect':pygame.Rect(0,100,75,500),'kind':'walk','approach':(115,570),'route':'meer','text':'Ihr kehrt vom Floßlager an das Ufer zurück.'},
                {'name':'Holzstämme ordnen','rect':pygame.Rect(205,490,95,58),'kind':'eye','approach':(270,570),'text':'Die Stämme müssen gleichmäßig nebeneinander liegen, damit das Floß nicht kippt.'},
                {'name':'Ranken festziehen','rect':pygame.Rect(410,425,90,55),'kind':'hand','approach':(430,570),'text':'Die Ranken müssen die Stämme an mehreren Stellen fest verbinden.'},
                {'name':'Floß auf Auftrieb prüfen','rect':pygame.Rect(510,480,95,60),'kind':'eye','approach':(545,570),'text':'Prüfe, ob alle Stämme gleichmäßig aufliegen und keine Bindung locker ist.'},
                {'name':'Floß ins Wasser lassen','rect':pygame.Rect(605,430,100,55),'kind':('walk' if (floss_ready and floss_wood_aligned and floss_buoyancy_checked) else 'eye'),'approach':(650,570),'route':('meerfahrt' if (floss_ready and floss_wood_aligned and floss_buoyancy_checked) else None),'text':'Erst ein gleichmäßig gebautes und fest verschnürtes Floß kann zu Wasser gelassen werden.'},
            ]
        elif state == 'meerfahrt':
            candidates = [
                {'name':'Zurück zum Floßlager','rect':pygame.Rect(0,100,75,500),'kind':'walk','approach':(115,570),'route':'floss','text':'Ihr zieht das Floß zurück zur Anlegestelle.'},
                {'name':'Riesige Algen untersuchen','rect':pygame.Rect(150,405,320,105),'kind':'eye','approach':(365,570),'clue':'algen','text':'Lange, zähe Algen treiben quer vor dem Floß. Zwischen ihnen ist eine schmale Lücke zu erkennen.'},
                {'name':'Kampf der Meerestiere beobachten','rect':pygame.Rect(90,250,300,170),'kind':'eye','approach':(310,570),'clue':'tiere','text':'Ein Ichthyosaurus und ein Plesiosaurus kämpfen im Wasser. Die Wellen treiben das Floß seitlich ab.'},
                {'name':'Strömung und Wirbel prüfen','rect':pygame.Rect(600,380,330,170),'kind':'eye','approach':(700,570),'clue':'stromung','text':'Das Wasser zieht in einem großen Kreis. Am Rand des Wirbels treibt Schaum in eine ruhigere Gegenströmung.'},
                *([{'name':'Zur sicheren Küste steuern','rect':pygame.Rect(915,100,109,500),'kind':'walk','approach':(850,570),'route':'meerfahrt_ende','text':'Mit den Beobachtungen findet ihr eine Passage durch die Algen und am Wirbel vorbei.'}] if meerfahrt_solved else []),
            ]
        elif state == 'meerfahrt_ende':
            candidates = [
                {'name':'Fossilien untersuchen','rect':pygame.Rect(80,370,220,150),'kind':'eye','approach':(280,570),'clue':'fossilien','text':'Zwischen den Felsen liegen versteinerte Knochen und Pflanzen. Die Küste bewahrt Spuren einer uralten Welt.'},
                {'name':'Riesenhafte Gestalt beobachten','rect':pygame.Rect(350,170,300,250),'kind':'eye','approach':(500,570),'clue':'gestalt','text':'In weiter Ferne bewegt sich eine riesenhafte Gestalt zwischen einer Herde Mastodonten. Ihr bleibt vorsichtig auf Abstand.'},
                {'name':'Saknussemms Zeichen finden','rect':pygame.Rect(680,350,220,160),'kind':'eye','approach':(700,570),'clue':'zeichen','text':'Unter einer dunklen Felsplatte entdeckt ihr Saknussemms eingeritztes Zeichen. Es weist auf einen versperrten Durchgang.'},
                *([{'name':'Zum Vulkanschlot','rect':pygame.Rect(760,90,264,510),'kind':'walk','approach':(800,570),'route':'punkt6','text':'Ihr öffnet den Durchgang. Wasser und Strömung reißen das Floß mit sich – der Weg führt in einen gewaltigen Vulkanschlot.'}] if len(set(punkt6_clues)) == 3 else [])
            ]
        elif state == 'punkt6':
            candidates = [
                {'name':'Vulkanischer Schlot','rect':pygame.Rect(320,140,520,420),'kind':'eye','approach':(600,570),'clue':'schlot','text':'Das Floß wird von einer aufsteigenden Wasser- und Dampfströmung erfasst. Die Wände des Schlots beben.'},
                {'name':'Zum Tageslicht aufsteigen','rect':pygame.Rect(820,100,204,500),'kind':'walk','approach':(820,570),'route':'spielende','text':'Die Strömung schleudert euch durch den Krater ins Freie. Ihr landet auf Stromboli – am Ende der Reise.'}
            ]
        elif state == 'ueberfahrt':
            candidates = [
                {'name':'Zurück an Bord','rect':pygame.Rect(0,100,85,500),'kind':'walk','approach':(120,570),'route':'schiff','text':'Du gehst zurück zum sicheren Bereich an Bord.'},
                {'name':'Loser Tampen','rect':pygame.Rect(590,335,315,220),'kind':'hand','approach':(730,565),'crossing_task':'tampen','text':'Ein schwerer Tampen schlägt im Wind gegen die Reling. Zuerst musst du ihn sichern.'},
                {'name':'Sturmsegel','rect':pygame.Rect(300,45,315,265),'kind':'hand','approach':(470,565),'crossing_task':'segel','text':'Das Sturmsegel muss gerefft werden, bevor es den Mast beschädigt.'},
                {'name':'Steuerrad','rect':pygame.Rect(105,110,190,180),'kind':'hand','approach':(245,565),'crossing_task':'steuerrad','text':'Das Steuerrad schlägt heftig aus. Zuletzt musst du den Kurs stabil halten.'},
            ]
            if len(set(crossing_tasks)) == 3:
                candidates.append({'name':'In Island anlegen','rect':pygame.Rect(915,100,109,500),'kind':'walk','approach':(850,570),'route':'island_hafen','text':'Der Sturm lässt nach. Reykjavík liegt vor euch – jetzt könnt ihr an Land gehen.'})
        else:
            candidates = []
        if state == 'stapi' and stapi_crate_open and not stapi_fieldbook_found:
            candidates.append({'name':'Feldbuch','rect':pygame.Rect(455,405,105,82),'kind':'hand','approach':(430,570),'text':'Ein altes Feldbuch liegt sichtbar zwischen den Messblättern.'})
        for h in candidates:
            if state == 'stapi' and h.get('name') == 'Alte Vermessungskiste' and stapi_crate_open and not stapi_fieldbook_found:
                continue
            # Der Hafenarbeiter ist erst zu entdecken, nachdem Axel die Seekarte
            # zwischen den Ladungskisten gefunden hat. So ist er nicht sofort offensichtlich.
            if state == 'hafen' and h.get('name') == 'Hafenarbeiter' and not map_found: continue
            if state == 'island_hafen' and h.get('name') == 'Zu Professor Fridriksson' and len(set(island_workers_spoken)) < 3: continue
            if state == 'fridriksson' and h.get('name') == 'Hans Bjelke aufsuchen' and not fridriksson_spoken: continue
            if state in ('island_hafen', 'hans') and h.get('name') == 'Altes Seil' and island_rope_found: continue
            if state == 'hafen' and h.get('name') == 'Kompass' and not crate_open: continue
            if state == 'hafen' and h.get('name') == 'Holzkiste' and crate_open: continue
            if h.get('name') == 'Lupe' and not bookshelf_examined: continue
            # Kleine Hotspots erhalten eine gut treffbare Fläche von rund 1 cm; große Flächen werden nicht künstlich erweitert.
            if h['rect'].width < 40 or h['rect'].height < 40:
                r=h['rect']; h=dict(h); nw=max(40,r.width); nh=max(40,r.height); h['rect']=pygame.Rect(r.centerx-nw//2,r.centery-nh//2,nw,nh)
            if h.get('name') == 'Pergament' and not professor_spoken: continue
            if h['rect'].collidepoint(pos): return h
        return None

    def change_scene(target):
        nonlocal state, px, py, tx, ty, moving, pending, selected, island_workers_spoken, island_rope_found
        previous_state = state
        # Bei der ersten Ankunft in Reykjavík müssen Gespräche wirklich neu geführt werden.
        # Rückkehr aus Fridrikssons Haus behält den bisherigen Fortschritt.
        if target == 'island_hafen' and previous_state == 'ueberfahrt':
            island_workers_spoken = []
            island_rope_found = 'Seil' in inventory
        state = target
        px, py = (175.0, 590.0) if target in ('room','chapter2') else ((650.0,590.0) if target in ('island_hafen','hans','island_weg','stapi','stapi_aufstieg','krater','tiefe','gaenge') else (512.0,590.0))
        tx, ty = px, py
        moving = False; pending = None; selected = None
        labels = {'room':'Arbeitszimmer','zweites_zimmer':'Zweites Zimmer','flur':'Flur','hafen':'Abfahrtshafen','schiff':'Schiff','ueberfahrt':'Stürmische Überfahrt','island_hafen':'Reykjavík – Island','fridriksson':'Bei Professor Fridriksson','hans':'Hans Bjelke','island_weg':'Aufbruch zum Snæfellsjökull','stapi':'Küstenweg nach Stapi','stapi_aufstieg':'Aufstieg zum Snæfellsjökull','krater':'Kraterrand · Snæfellsjökull','tiefe':'Abstieg in die Tiefe','gaenge':'Unterirdische Gänge','meer':'Große Höhle und unterirdisches Meer','floss':'Vorbereitung des Floßes','meerfahrt':'Überfahrt über das unterirdische Meer','meerfahrt_ende':'Die sichere Küste','punkt6':'Vulkanschlot · Rückkehr ans Tageslicht'}
        say(labels.get(target, ''))
        save_game()

    def save_game(show_notice=False):
        """Speichert den spielbaren Fortschritt atomar im Benutzerprofil."""
        nonlocal save_notice, last_autosave
        if state not in ('room', 'chapter2', 'zweites_zimmer', 'flur', 'hafen', 'schiff', 'ueberfahrt', 'island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6'):
            return False
        data = {
            'version': 1, 'state': state, 'player_x': float(px), 'player_y': float(py),
            'target_x': float(tx), 'target_y': float(ty), 'facing_right': bool(facing_right),
            'inventory': list(inventory), 'selected': selected,
            'map_found': bool(map_found), 'compass_found': bool(compass_found), 'course_calculated': bool(course_calculated),
            'map_on_table': bool(map_on_table), 'compass_on_table': bool(compass_on_table),
            'bookshelf_examined': bool(bookshelf_examined),
            'professor_spoken': bool(professor_spoken),
            'parchment_deciphered': bool(parchment_deciphered), 'harbor_unlocked': bool(harbor_unlocked),
            'harbor_key_found': bool(harbor_key_found), 'crate_open': bool(crate_open),
            'sailors_spoken': list(sailors_spoken), 'crossing_tasks': list(crossing_tasks),
            'island_workers_spoken': list(island_workers_spoken), 'island_rope_found': island_rope_found, 'hans_way_known': hans_way_known, 'fridriksson_spoken': fridriksson_spoken, 'fridriksson_puzzle_solved': fridriksson_puzzle_solved, 'hans_spoken': hans_spoken, 'island_route_solved': island_route_solved,
            'stapi_crate_open': stapi_crate_open, 'stapi_fieldbook_found': stapi_fieldbook_found, 'ascent_rope_secured': ascent_rope_secured, 'ascent_route_solved': ascent_route_solved, 'crater_route_solved': crater_route_solved,
            'cave_professor_spoken': cave_professor_spoken, 'cave_hans_spoken': cave_hans_spoken, 'cave_passage_examined': cave_passage_examined, 'cave_enter_pending': cave_enter_pending, 'gaenge_clues': list(gaenge_clues), 'gaenge_route_solved': gaenge_route_solved, 'meer_clues': list(meer_clues), 'meer_route_solved': meer_route_solved, 'meer_holz_gesammelt': meer_holz_gesammelt, 'meer_ranken_gesammelt': meer_ranken_gesammelt, 'floss_ready': floss_ready, 'floss_wood_aligned': floss_wood_aligned, 'floss_buoyancy_checked': floss_buoyancy_checked, 'meerfahrt_clues': list(meerfahrt_clues), 'meerfahrt_solved': meerfahrt_solved, 'punkt6_clues': list(punkt6_clues), 'punkt6_path_open': punkt6_path_open,
        }
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            tmp = SAVE_FILE.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            tmp.replace(SAVE_FILE)
            last_autosave = pygame.time.get_ticks()
            if show_notice:
                say('Spielstand automatisch gespeichert.', 2200)
            return True
        except (OSError, TypeError, ValueError) as exc:
            save_notice = f'Speichern fehlgeschlagen: {exc}'
            if show_notice: say(save_notice, 4000)
            return False

    def load_game():
        nonlocal state, px, py, tx, ty, moving, facing_right, pending, harbor_unlocked, harbor_key_found, crate_open, island_workers_spoken, island_rope_found, hans_way_known, fridriksson_spoken, fridriksson_puzzle_solved, hans_spoken, island_route_solved, stapi_crate_open, stapi_fieldbook_found, ascent_rope_secured, ascent_route_solved, crater_route_solved, crater_rope_used, cave_professor_spoken, cave_hans_spoken, cave_passage_examined, gaenge_clues, gaenge_route_solved, meer_clues, meer_route_solved, floss_ready, floss_wood_aligned, floss_buoyancy_checked, meerfahrt_clues, meerfahrt_solved
        nonlocal inventory, selected, bookshelf_examined, professor_spoken, parchment_deciphered, map_found, compass_found, course_calculated, map_on_table, compass_on_table, sailors_spoken, crossing_tasks, stapi_crate_open, stapi_fieldbook_found, ascent_rope_secured, ascent_route_solved, crater_route_solved
        try:
            data = json.loads(SAVE_FILE.read_text(encoding='utf-8'))
            if data.get('version') != 1 or data.get('state') not in ('room', 'chapter2', 'zweites_zimmer', 'flur', 'hafen', 'schiff', 'ueberfahrt', 'island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6'):
                raise ValueError('Unbekanntes Speicherformat')
            state = data['state']
            # Migrate stale saves from releases that exposed Hans directly in the harbor.
            if state == 'hans' and not bool(data.get('fridriksson_spoken', False)):
                state = 'island_hafen'
            px = float(max(35, min(W-35, data.get('player_x', 175))))
            py = float(max(500, min(SCENE_H-4, data.get('player_y', 590))))
            tx, ty = px, py
            moving, pending = False, None
            facing_right = bool(data.get('facing_right', True))
            inventory = [str(x) for x in data.get('inventory', []) if str(x) in ('Lupe','Seekarte','Kompass','Schlüssel','Seil','Feldbuch','Holz','Ranken')]
            map_found = bool(data.get('map_found', 'Seekarte' in inventory))
            compass_found = bool(data.get('compass_found', 'Kompass' in inventory))
            course_calculated = bool(data.get('course_calculated', False))
            map_on_table = bool(data.get('map_on_table', False))
            compass_on_table = bool(data.get('compass_on_table', False))
            selected = data.get('selected') if data.get('selected') in inventory else None
            bookshelf_examined = bool(data.get('bookshelf_examined', False))
            professor_spoken = bool(data.get('professor_spoken', False))
            parchment_deciphered = bool(data.get('parchment_deciphered', False))
            harbor_unlocked = bool(data.get('harbor_unlocked', False))
            harbor_key_found = bool(data.get('harbor_key_found', False))
            crate_open = bool(data.get('crate_open', False))
            sailors_spoken = [x for x in data.get('sailors_spoken', []) if x in ('reling','steuerrad','kiste')]
            crossing_tasks = [x for x in data.get('crossing_tasks', []) if x in ('tampen','segel','steuerrad')]
            island_workers_spoken = [x for x in data.get('island_workers_spoken', []) if x in ('arbeiter1','arbeiter2','arbeiter3','fischer')]
            island_rope_found = bool(data.get('island_rope_found', 'Seil' in inventory))
            hans_way_known = bool(data.get('hans_way_known', False))
            fridriksson_spoken = bool(data.get('fridriksson_spoken', False))
            fridriksson_puzzle_solved = bool(data.get('fridriksson_puzzle_solved', False))
            hans_spoken = bool(data.get('hans_spoken', False))
            island_route_solved = bool(data.get('island_route_solved', False))
            stapi_crate_open = bool(data.get('stapi_crate_open', False))
            stapi_fieldbook_found = bool(data.get('stapi_fieldbook_found', 'Feldbuch' in inventory))
            # Reparatur älterer Spielstände: Einige Versionen markierten das Feldbuch
            # als gefunden, ohne es wirklich im Inventar zu speichern. Inventar hat Vorrang.
            if stapi_fieldbook_found and 'Feldbuch' not in inventory:
                inventory.append('Feldbuch')
            if 'Feldbuch' in inventory:
                stapi_fieldbook_found = True
            ascent_rope_secured = bool(data.get('ascent_rope_secured', False))
            ascent_route_solved = bool(data.get('ascent_route_solved', False))
            crater_route_solved = bool(data.get('crater_route_solved', False))
            cave_professor_spoken = bool(data.get('cave_professor_spoken', False))
            cave_hans_spoken = bool(data.get('cave_hans_spoken', False))
            cave_passage_examined = bool(data.get('cave_passage_examined', False))
            cave_enter_pending = bool(data.get('cave_enter_pending', False))
            gaenge_clues = [x for x in data.get('gaenge_clues', []) if x in ('wasser','luft','echo')]
            gaenge_route_solved = bool(data.get('gaenge_route_solved', False))
            meer_clues = [x for x in data.get('meer_clues', []) if x in ('meer_wasser','meer_kuste','meer_holz')]
            meer_route_solved = bool(data.get('meer_route_solved', False))
            meer_holz_gesammelt = bool(data.get('meer_holz_gesammelt', False))
            meer_ranken_gesammelt = bool(data.get('meer_ranken_gesammelt', False))
            if meer_holz_gesammelt and 'Holz' not in inventory: inventory.append('Holz')
            if meer_ranken_gesammelt and 'Ranken' not in inventory: inventory.append('Ranken')
            floss_ready = bool(data.get('floss_ready', False))
            floss_wood_aligned = bool(data.get('floss_wood_aligned', False))
            floss_buoyancy_checked = bool(data.get('floss_buoyancy_checked', False))
            meerfahrt_clues = [x for x in data.get('meerfahrt_clues', []) if x in ('algen','tiere','stromung')]
            meerfahrt_solved = bool(data.get('meerfahrt_solved', False))
            crater_rope_used = False
            # Ein gespeichertes Seil-/Inventar-Highlight zählt nicht als erneute Anwendung.
            if data.get('state') == 'krater':
                selected = None
            # Alte Spielstände konnten wegen überlappender Klickflächen alle Gespräche markieren.
            if not data.get('island_hotspots_fixed', False) and not fridriksson_spoken:
                island_workers_spoken = []
            say('Spielstand geladen.', 3000)
            return True
        except FileNotFoundError:
            say('Es gibt noch keinen gespeicherten Spielstand.', 3000)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            say(f'Spielstand konnte nicht geladen werden: {exc}', 4000)
        return False

    def begin_chapter():
        nonlocal state, px, py, tx, ty, moving, pending, inventory, selected, crater_route_solved, crater_rope_used, cave_professor_spoken, cave_hans_spoken, cave_passage_examined, cave_enter_pending, gaenge_clues, gaenge_route_solved, meer_clues, meer_route_solved, meer_holz_gesammelt, meer_ranken_gesammelt, floss_ready, floss_wood_aligned, floss_buoyancy_checked, meerfahrt_clues, meerfahrt_solved, bookshelf_examined, professor_spoken, parchment_deciphered, harbor_unlocked, map_found, compass_found, course_calculated, harbor_key_found, crate_open, map_on_table, compass_on_table, sailors_spoken, crossing_tasks, island_workers_spoken, island_rope_found, hans_way_known, fridriksson_spoken, fridriksson_puzzle_solved, hans_spoken, island_route_solved, stapi_crate_open, stapi_fieldbook_found, ascent_rope_secured, ascent_route_solved
        # Ein neues Spiel beginnt immer mit dem Pergament-Rätsel ungelöst.
        bookshelf_examined = False
        professor_spoken = False
        parchment_deciphered = False
        harbor_unlocked = False
        sailors_spoken = []
        state='room'; px,py=175.,590.; tx,ty=px,py; moving=False; pending=None; inventory=[]; selected=None; crater_route_solved=False; cave_professor_spoken=False; cave_hans_spoken=False; cave_passage_examined=False; cave_enter_pending=False; gaenge_clues=[]; gaenge_route_solved=False; meer_clues=[]; meer_route_solved=False; meer_holz_gesammelt=False; meer_ranken_gesammelt=False; floss_ready=False; floss_wood_aligned=False; floss_buoyancy_checked=False; meerfahrt_clues=[]; meerfahrt_solved=False; punkt6_clues=[]; punkt6_path_open=False; map_found=False; compass_found=False; course_calculated=False; map_on_table=False; compass_on_table=False; harbor_key_found=False; crate_open=False; sailors_spoken=[]; crossing_tasks=[]; island_workers_spoken=[]; island_rope_found=False; hans_way_known=False; fridriksson_spoken=False; fridriksson_puzzle_solved=False; hans_spoken=False; island_route_solved=False; stapi_crate_open=False; stapi_fieldbook_found=False; ascent_rope_secured=False; ascent_route_solved=False; crater_rope_used=False
        say('Kapitel 1 · Hamburg. Klicke auf den Boden, damit Axel läuft. Sprich mit Professor Lidenbrock und untersuche das geheimnisvolle Pergament.', 6000)
        save_game()
    def finish_action():
        nonlocal state, pending, selected, bookshelf_examined, professor_spoken, parchment_deciphered, harbor_unlocked, harbor_key_found, crate_open, island_workers_spoken, island_rope_found, hans_way_known, fridriksson_spoken, fridriksson_puzzle_solved, hans_spoken, island_route_solved
        nonlocal inventory, map_found, compass_found, course_calculated, map_on_table, compass_on_table, sailors_spoken
        # Zustände der Stapi-/Berg-Rätsel werden in finish_action verändert.
        # Ohne nonlocal behandelt Python sie als lokale Variablen und wirft beim Lesen UnboundLocalError.
        nonlocal stapi_crate_open, stapi_fieldbook_found, ascent_rope_secured, ascent_route_solved, crater_route_solved, crater_rope_used, cave_professor_spoken, cave_hans_spoken, cave_passage_examined, gaenge_clues, gaenge_route_solved, meer_clues, meer_route_solved, meer_holz_gesammelt, meer_ranken_gesammelt, floss_ready, floss_wood_aligned, floss_buoyancy_checked, meerfahrt_clues, meerfahrt_solved
        if not pending: return
        name, item = pending; pending=None
        if state == 'tiefe' and name == 'Professor Lidenbrock in der Höhle':
            cave_professor_spoken = True
            say('Lidenbrock betrachtet die Felswand im Schein der Laterne: „Sehen Sie, Axel: Die Schichten erzählen von der vulkanischen Vergangenheit dieses Berges. Wir müssen jeden Abzweig aufmerksam prüfen und dürfen uns nicht allein auf Vermutungen verlassen.“')
            save_game(); return
        if state == 'tiefe' and name == 'Hans Bjelke in der Höhle':
            cave_hans_spoken = True
            say('Hans lauscht in die Dunkelheit: „Der Ton kommt aus einem tieferen Gang. Ich spüre auch einen leichten Luftzug. Wir sollten erst die Umgebung prüfen, bevor wir weitergehen.“')
            save_game(); return
        if state == 'tiefe' and name == 'Dunkler Abstieg':
            cave_passage_examined = True
            if cave_professor_spoken and cave_hans_spoken:
                say('Axel hat den dunklen Gang untersucht. Die Beobachtungen passen zusammen. Am Abstieg erscheinen nun die Fußspuren zum Weitergehen.')
            else:
                say('Der Gang fällt steil ab. Aus der Tiefe dringt ein hohles Echo.')
            save_game(); return
        if state == 'gaenge' and name in ('Linker Gang','Mittlerer Gang','Rechter Gang'):
            if name == 'Mittlerer Gang' and all(clue in gaenge_clues for clue in ('wasser','luft','echo')):
                gaenge_route_solved = True
                say('Die Hinweise passen zusammen: Wasserlauf und stetiger Luftzug weisen auf den mittleren Gang. Ihr folgt ihm tiefer in den Berg.')
                save_game()
                # Nächster Abschnitt ist noch nicht freigeschaltet; der gelöste Weg bleibt sichtbar im Spielstand.
            elif name == 'Mittlerer Gang':
                say('Der Gang wirkt begehbar, aber du bist dir noch nicht sicher. Prüfe Wasserlauf, Luftzug und Echo.')
            else:
                say('Der Gang endet nach wenigen Schritten an einer Felsbarriere. Du kehrst um.')
            save_game(); return
        if state == 'gaenge' and name in ('Lidenbrock befragen','Hans befragen'):
            say('Lidenbrock: „Vergleicht Wasser, Luftzug und Echo.“' if name == 'Lidenbrock befragen' else 'Hans: „Der Bach führt weiter. Folgt ihm bis zum großen Wasser.“')
            save_game(); return
        if state == 'meer' and name in ('Lidenbrock befragen','Hans befragen'):
            say('Lidenbrock: „Vermesst erst die Küste, bevor wir die Überfahrt planen.“' if name == 'Lidenbrock befragen' else 'Hans: „Dort am flachen Ufer können wir das Floß vorbereiten.“')
            save_game(); return
        if state == 'meer' and name in ('Holz aufnehmen','Ranken sammeln'):
            if name == 'Holz aufnehmen':
                if not meer_holz_gesammelt:
                    meer_holz_gesammelt = True
                    if 'Holz' not in inventory: inventory.append('Holz')
                    say('Du nimmst die passenden Holzstämme direkt vom Ufer auf und legst sie ins Inventar.')
                else:
                    say('Das geeignete Holz hast du bereits gesammelt.')
            else:
                if not meer_ranken_gesammelt:
                    meer_ranken_gesammelt = True
                    if 'Ranken' not in inventory: inventory.append('Ranken')
                    say('Du sammelst die Ranken mit der Hand aus den Felsritzen und legst sie ins Inventar.')
                else:
                    say('Die Ranken hast du bereits gesammelt.')
            if meer_holz_gesammelt and meer_ranken_gesammelt and 'meer_holz' not in meer_clues:
                meer_clues.append('meer_holz')
                say('Holz und Ranken sind beisammen. Der Materialhinweis ist jetzt vollständig.')
            save_game(); return
        if state == 'meer' and name in ('Wasserlinie untersuchen','Küstenverlauf vermessen'):
            clue_by_name = {'Wasserlinie untersuchen':'meer_wasser','Küstenverlauf vermessen':'meer_kuste'}
            descriptions = {
                'Wasserlinie untersuchen':'Axel prüft die Wasserlinie: Die Strömung ist schwach, aber direkt unter der steilen Felskante ist das Wasser zu tief zum sicheren Einsteigen.',
                'Küstenverlauf vermessen':'Du misst die Küste Schritt für Schritt ab. Eine flache Landzunge bietet genug Platz, um ein Floß zu bauen und ins Wasser zu schieben.',
            }
            clue = clue_by_name[name]
            if clue not in meer_clues: meer_clues.append(clue)
            say(descriptions[name])
            if all(x in meer_clues for x in ('meer_wasser','meer_kuste','meer_holz')) and not meer_route_solved:
                meer_route_solved = True
                say('Die Beobachtungen passen zusammen: Die flache Landzunge ist sicher, das Wasser dort seicht genug und Holz sowie Ranken reichen aus. Der Weg zum Floßlager ist nun frei.')
            save_game(); return
        if state == 'meer' and name == 'Flache Anlegestelle':
            if not all(x in meer_clues for x in ('meer_wasser','meer_kuste','meer_holz')):
                missing = []
                if 'meer_wasser' not in meer_clues: missing.append('Wasserlinie')
                if 'meer_kuste' not in meer_clues: missing.append('Küstenverlauf')
                if 'meer_holz' not in meer_clues: missing.append('Holz und Ranken')
                say('Die Anlegestelle ist noch nicht sicher beurteilt. Es fehlen: ' + ', '.join(missing) + '.')
            else:
                meer_route_solved = True
                say('Die flache Landzunge ist der richtige Platz. Hier können wir Holz und Ranken zum Floßbau zusammenbringen.')
            save_game(); return
        if state == 'floss' and name == 'Holzstämme ordnen':
            floss_wood_aligned = True
            floss_ready = False
            floss_buoyancy_checked = False
            say('Axel richtet die Stämme parallel aus und legt die dicksten außen. Das Floß liegt nun gleichmäßig auf. Jetzt müssen die Ranken an Bug, Mitte und Heck festgezogen werden.')
            save_game(); return
        if state == 'floss' and name == 'Ranken festziehen':
            if not floss_wood_aligned:
                say('Die Stämme liegen noch schief. Ordne zuerst das Holz, bevor du die Ranken festziehst.')
            elif 'Ranken' not in inventory:
                say('Dir fehlen zähe Ranken zum Verschnüren. Suche am Ufer danach.')
            elif not floss_ready:
                floss_ready = True
                say('Du ziehst die Ranken an Bug, Mitte und Heck fest. Die Stämme sitzen zusammen. Nun prüfst du den Auftrieb, bevor ihr ablegt.')
            else:
                say('Die Bindungen sitzen bereits fest. Prüfe noch einmal den Auftrieb des Floßes.')
            save_game(); return
        if state == 'floss' and name == 'Floß auf Auftrieb prüfen':
            if not floss_wood_aligned:
                say('Das Floß liegt ungleichmäßig. Richte zuerst die Stämme aus.')
            elif not floss_ready:
                say('Ein Stamm bewegt sich noch. Ziehe zuerst die Ranken an allen drei Bindestellen fest.')
            else:
                floss_buoyancy_checked = True
                say('Du drückst nacheinander auf die Stämme: Das Floß liegt waagerecht, die Knoten halten und kein Stamm kippt weg. Es ist seetüchtig. Jetzt könnt ihr ablegen.')
            save_game(); return
        if state == 'floss' and name == 'Floß ins Wasser lassen':
            if not (floss_wood_aligned and floss_ready and floss_buoyancy_checked):
                say('Das Floß ist noch nicht sicher. Richte die Stämme aus, ziehe die Ranken fest und prüfe den Auftrieb.')
            else:
                say('Gemeinsam schiebt ihr das Floß ins Wasser. Die erste Welle hebt die Stämme gleichmäßig an. Punkt 4 ist abgeschlossen – die Überfahrt beginnt!')
                change_scene('meerfahrt')
            save_game(); return
        if state == 'meerfahrt_ende' and name in ('Fossilien untersuchen','Riesenhafte Gestalt beobachten','Saknussemms Zeichen finden'):
            clue = {'Fossilien untersuchen':'fossilien','Riesenhafte Gestalt beobachten':'gestalt','Saknussemms Zeichen finden':'zeichen'}[name]
            if clue not in punkt6_clues:
                punkt6_clues.append(clue)
            say({'fossilien':'Die Fossilien bestätigen, dass ihr eine uralte Küstenlandschaft erreicht habt.',
                 'gestalt':'Ihr erkennt Mastodonten und eine riesenhafte Gestalt in der Ferne. Eine Annäherung wäre zu gefährlich.',
                 'zeichen':'Saknussemms Zeichen weist auf einen blockierten Durchgang. Die Strömung dahinter könnte in einen Vulkanschlot führen.'}[clue])
            save_game(); return
        if state == 'punkt6' and name == 'Vulkanischer Schlot':
            say('Der Schlot ist von heißem Dampf und aufsteigendem Wasser erfüllt. Ihr müsst euch aneinander festhalten und die Strömung nutzen.')
            save_game(); return
        if state == 'meerfahrt' and name in ('Riesige Algen untersuchen','Kampf der Meerestiere beobachten','Strömung und Wirbel prüfen'):
            clue = {'Riesige Algen untersuchen':'algen','Kampf der Meerestiere beobachten':'tiere','Strömung und Wirbel prüfen':'stromung'}[name]
            messages = {
                'algen':'Axel entdeckt, dass die langen Algen mit der Strömung schwingen. In der Lücke dahinter ist das Wasser freier.',
                'tiere':'Der Kampf wirft hohe Wellen auf. Ihr haltet Abstand und wartet, bis die Tiere weiterziehen; das Floß darf nicht quer zur Welle stehen.',
                'stromung':'Hans erkennt eine ruhigere Gegenströmung am Rand des Wirbels. Dort kann das Floß aus der Kreisströmung herausgleiten.'
            }
            if clue not in meerfahrt_clues: meerfahrt_clues.append(clue)
            say(messages[clue])
            if all(c in meerfahrt_clues for c in ('algen','tiere','stromung')) and not meerfahrt_solved:
                meerfahrt_solved = True
                say('Die Hinweise passen zusammen: durch die Lücke im Algenfeld, mit dem Floß längs zur Welle und dann am Rand des Wirbels entlang. Ein sicherer Kurs zeichnet sich ab.')
            save_game(); return
        if state == 'meerfahrt' and name == 'Zur sicheren Küste steuern':
            if not meerfahrt_solved:
                say('Ihr kennt den sicheren Kurs noch nicht. Beobachtet die Algen, den Kampf der Meerestiere und die Strömung.')
            else:
                say('Ihr gleitet durch die Algenlücke und haltet euch am Rand des Wirbels. Als der Kampf der Meerestiere in der Ferne verschwindet, öffnet sich vor euch eine dunkle Küstenbucht. Die Überfahrt ist geschafft.')
                state = 'meerfahrt_ende'
            save_game(); return
        if state == 'gaenge' and name in ('Feuchte Felswand','Luftzug prüfen','Echo prüfen'): 
            clue = {'Feuchte Felswand':'wasser','Luftzug prüfen':'luft','Echo prüfen':'echo'}[name]
            if clue not in gaenge_clues: gaenge_clues.append(clue)
            descriptions = {
                'wasser':'Axel folgt den feuchten Spuren. Das Wasser fließt zum mittleren Gang.',
                'luft':'Axel hält die Hand in den Luftzug. Er kommt eindeutig aus dem mittleren Gang.',
                'echo':'Axel lauscht. Das rechte Echo klingt kurz und endet an einer Felswand.'
            }
            say(descriptions[clue]); save_game(); return
        # Der Übergang zum Schiff muss unabhängig von Inventar-/Hotspot-Logik greifen.
        if name == 'Schiff betreten':
            change_scene('schiff')
            return
        if name == 'Seekarte':
            if 'Seekarte' not in inventory: inventory.append('Seekarte'); map_found=True; say('Du findest eine alte Seekarte. Die Route nach Island ist eingezeichnet, aber ohne Kompass lässt sich der genaue Kurs nicht bestimmen.')
            else: say('Die Seekarte hast du bereits eingesteckt.')
            save_game(); return
        if name == 'Kompass':
            if 'Kompass' not in inventory: inventory.append('Kompass'); compass_found=True; say('In der Holzkiste liegt ein Messingkompass. Damit kannst du die Himmelsrichtung auf der Karte bestimmen.')
            else: say('Den Kompass hast du bereits.')
            save_game(); return
        if name == 'Navigationstisch':
            if course_calculated:
                say('Der Kurs nach Island ist bereits bestimmt: Nordwest. Die Seekarte und der Kompass liegen bereit.')
            elif item == 'Seekarte':
                if not map_found:
                    say('Du hast keine Seekarte im Inventar.')
                elif map_on_table:
                    say('Die Seekarte liegt bereits auf dem Navigationstisch.')
                else:
                    map_on_table = True
                    selected = None
                    say('Du breitest die Seekarte auf dem Navigationstisch aus. Jetzt fehlt noch der Kompass.')
            elif item == 'Kompass':
                if not compass_found:
                    say('Du hast keinen Kompass im Inventar.')
                elif compass_on_table:
                    say('Der Kompass liegt bereits auf dem Navigationstisch.')
                else:
                    compass_on_table = True
                    selected = None
                    say('Du legst den Messingkompass neben die Seekarte. Klicke ohne ausgewählten Gegenstand erneut auf den Navigationstisch, um den Kurs zu bestimmen.')
            elif item:
                say('Für die Navigation brauchst du die Seekarte und den Kompass. Wähle einen dieser Gegenstände im Inventar aus.')
            elif map_on_table and compass_on_table and len(set(sailors_spoken)) < 3:
                say('Sprich zuerst mit allen drei Matrosen, bevor du den Kurs bestimmst.')
            elif map_on_table and compass_on_table:
                course_calculated = True
                say('Du richtest den Kompass an der Seekarte aus und vergleichst Küstenlinie und Himmelsrichtung. Der richtige Kurs nach Island ist Nordwest! Professor Lidenbrock nickt: „Nun kann die Überfahrt beginnen.“')
            elif not map_on_table and not compass_on_table:
                say('Lege zuerst die Seekarte und danach den Kompass aus deinem Inventar auf den Navigationstisch.')
            elif map_on_table:
                say('Die Seekarte liegt bereit. Wähle den Kompass im Inventar aus und klicke damit auf den Navigationstisch.')
            else:
                say('Der Kompass liegt bereit. Wähle die Seekarte im Inventar aus und klicke damit auf den Navigationstisch.')
            save_game(); return
        if state == 'schiff' and name.startswith('Matrose '):
            # Matrosen werden anhand des Namens eindeutig zugeordnet.
            sailor_id = {'Matrose am linken Reling':'reling', 'Matrose am Steuerrad':'steuerrad', 'Matrose an der Kiste':'kiste'}.get(name)
            if sailor_id and sailor_id not in sailors_spoken:
                sailors_spoken.append(sailor_id)
                dialogue = {
                    'reling':'Matrose am linken Reling: „Ich beobachte Wind und Wellen. Die Überfahrt wird ruhiger, wenn wir den Kurs sorgfältig festlegen.“',
                    'steuerrad':'Matrose am Steuerrad: „Der Kompass muss an der Seekarte ausgerichtet werden. Unser Ziel ist Island, nordwestlich von hier.“',
                    'kiste':'Matrose bei den Kisten: „Die Vorräte sind gesichert. Nun fehlt nur noch, dass du mit den übrigen Matrosen sprichst.“'
                }
                if len(set(sailors_spoken)) == 3:
                    dialogue[sailor_id] += ' Die ganze Mannschaft ist nun befragt; du kannst die Navigation abschließen.'
                say(dialogue[sailor_id])
            else:
                say('Matrose: „Wir haben bereits gesprochen. Sieh nach, ob du auch die anderen Matrosen befragt hast.“')
            save_game(); return
        if state == 'ueberfahrt' and name in ('Loser Tampen', 'Sturmsegel', 'Steuerrad'):
            task = {'Loser Tampen':'tampen', 'Sturmsegel':'segel', 'Steuerrad':'steuerrad'}[name]
            order = ('tampen', 'segel', 'steuerrad')
            expected = next((t for t in order if t not in crossing_tasks), None)
            if task in crossing_tasks:
                say('Diese Aufgabe ist bereits erledigt. Konzentriere dich auf die nächste Stelle an Deck.')
            elif task != expected:
                hints = {
                    'tampen':'Der lose Tampen schlägt gefährlich gegen die Reling. Sichere zuerst das Tau!',
                    'segel':'Das Sturmsegel darf erst gerefft werden, wenn der lose Tampen gesichert ist.',
                    'steuerrad':'Stabilisiere das Steuerrad erst, nachdem Tampen und Sturmsegel gesichert sind.'
                }
                say(hints[task])
            else:
                crossing_tasks.append(task)
                messages = {
                    'tampen':'Du ziehst den losen Tampen fest und belegst ihn sicher an der Klampe. Eine Gefahr weniger!',
                    'segel':'Du holst das Sturmsegel ein und verzurrst es. Der Mast ächzt, hält aber stand!',
                    'steuerrad':'Du stemmst dich gegen das Steuerrad und hältst den Bug auf Nordwest. Der Sturm beginnt nachzulassen!'
                }
                if len(set(crossing_tasks)) == 3:
                    messages[task] += ' Professor Lidenbrock ruft: „Land in Sicht! Wir laufen Reykjavík an. Gehe nach rechts, um an Land zu gehen.“'
                say(messages[task])
            save_game(); return
        if state == 'hans' and name == 'Hans Bjelke':
            hans_spoken = True
            say('Hans Bjelke: „Morgen früh brechen wir auf. Ich bereite alles für die Reise vor. Ruht euch aus – vor uns liegt ein langer Weg.“')
            save_game(); return
        if state == 'island_weg' and name == 'Hans Bjelke am Weg':
            say('Hans Bjelke: „Von hier gehen wir zu Fuß westwärts entlang der Küste nach Stapi. Prüft mit der Seekarte und dem Kompass die Richtung, dann folgen wir dem Küstenweg.“')
            save_game(); return
        if state == 'island_weg' and name == 'Küstenweg nach Stapi':
            if island_route_solved:
                say('Hans führt euch auf dem Küstenweg westwärts. Nach der langen Tagesreise erreicht ihr Stapi am Fuß des Snæfellsjökull. Der Aufstieg zum Krater wartet als nächstes Kapitel.')
            elif item == 'Kompass' and 'Seekarte' in inventory:
                island_route_solved = True
                selected = None
                say('Du vergleichst den Kompass mit der Seekarte: Der Weg führt westwärts entlang der Küste nach Stapi. Hans nickt: „Genau. Wir bleiben auf dem Küstenweg nach Westen. In Stapi bereiten wir den Aufstieg zum Snæfellsjökull vor.“')
            elif item == 'Seekarte' and 'Kompass' in inventory:
                say('Die Karte zeigt das Ziel, aber du musst den Kompass auf den Küstenweg anwenden, um die Richtung zu bestimmen.')
            else:
                say('Hans wartet auf eine Richtungsbestimmung. Wähle den Kompass im Inventar und klicke dann auf den Küstenweg.')
            save_game(); return
        if state == 'island_weg' and name == 'Weiter entlang der Küste':
            change_scene('stapi')
            say('Nach dem Marsch entlang der Küste erreicht ihr Stapi. Vor euch erhebt sich der Snæfellsjökull.')
            return
        if state == 'stapi' and name == 'Meer beobachten':
            say('Du beobachtest die Brandung und die dunklen Lavaklippen. Weit draußen ziehen Seevögel über dem Wasser. Der Weg nach Westen führt weiter an der Küste entlang.')
            save_game(); return
        if state == 'stapi' and name == 'Küste betrachten':
            say('Der schmale Pfad folgt der Küste. Zwischen den Lavasteinen erkennst du alte Messmarken, doch sie geben keinen Hinweis auf den weiteren Weg.')
            save_game(); return
        if state == 'stapi' and name == 'Weg zum Snæfellsjökull':
            change_scene('stapi_aufstieg')
            say('Ihr verlasst Stapi und beginnt den steilen Aufstieg über den felsigen Pfad.')
            return
        if state == 'stapi' and name == 'Alte Vermessungskiste':
            if stapi_crate_open:
                say('Die Kiste ist bereits geöffnet. Zwischen den alten Messblättern liegt ein abgegriffenes Feldbuch. Klicke das Buch direkt an, um es mitzunehmen.')
            elif item == 'Schlüssel':
                stapi_crate_open = True
                selected = None
                say('Der alte Schlüssel dreht sich nur mit Mühe im rostigen Schloss. Der Deckel öffnet sich; zwischen den alten Messblättern liegt ein abgegriffenes Feldbuch. Klicke das Buch direkt an, um es mitzunehmen.')
            elif item:
                say(f'{item} hilft hier nicht weiter.')
                selected = None
            else:
                say('Das Schloss ist verrostet, aber noch geschlossen. Du brauchst einen passenden Schlüssel.')
            save_game(); return
        if state == 'stapi' and name == 'Feldbuch':
            if stapi_crate_open and 'Feldbuch' not in inventory:
                inventory.append('Feldbuch')
                stapi_fieldbook_found = True
                say('Du nimmst das alte Feldbuch an dich. Eine Skizze zeigt drei gespaltene Felsspitzen und eine schmale Passage dazwischen. Du weißt noch nicht, wozu sie dient.')
            elif 'Feldbuch' in inventory:
                stapi_fieldbook_found = True
                say('Das Feldbuch mit der Skizze der drei Felsspitzen steckt bereits in deinem Inventar.')
            else:
                say('Das Feldbuch liegt in der verschlossenen Vermessungskiste.')
            save_game(); return
        if state == 'stapi_aufstieg' and name == 'Hans Bjelke':
            say('Hans blickt zum Berg hinauf. „Der Snæfellsjökull liegt vor uns. Wir sollten den Weg sorgfältig erkunden.“')
            save_game(); return
        if state == 'stapi_aufstieg' and name == 'Steiler Bergpfad':
            if not ascent_rope_secured and item == 'Seil':
                if 'Seil' in inventory:
                    ascent_rope_secured = True
                    selected = None
                    say('Du befestigst das Seil am Felsvorsprung.')
                else:
                    say('Du hast diesen Gegenstand nicht dabei.')
            elif not ascent_rope_secured:
                say('Der steile Pfad ist im Moment nicht passierbar.')
            else:
                say('Der Pfad führt weiter zwischen den Felsen hinauf.')
            save_game(); return
        if state == 'stapi_aufstieg' and name == 'Dreifach gespaltene Felsnadel':
            if not ascent_rope_secured:
                say('Die drei Felsspitzen liegen hoch über dem Geröll. Von hier unten lässt sich ihre Form kaum genauer erkennen.')
            elif item == 'Feldbuch' or ('Feldbuch' in inventory and ascent_route_solved):
                ascent_route_solved = True
                selected = None
                say('Du vergleichst die Felsnadeln mit der Skizze im Feldbuch. Die mittlere Passage ist die richtige: Hinter dem Geröll führt ein schmaler, begehbarer Pfad weiter zum Gletscherrand. Hans nickt anerkennend.')
            elif not stapi_fieldbook_found:
                say('Die drei Felsspitzen ragen scharf gegen den Himmel. Zwischen den Felsen liegen Geröll und schmale Spalten.')
            else:
                say('Du betrachtest die Felsnadeln genauer, findest aber noch keine sichere Passage.')
            save_game(); return
        if state == 'stapi_aufstieg' and name == 'Weiter zum Kraterrand':
            change_scene('krater')
            say('Ihr erreicht den Kraterrand. Drei Öffnungen liegen vor euch; der Schatten des Gipfels wandert über das Gestein.')
            save_game(); return
        if state == 'krater' and name in ('Linke Öffnung','Mittlere Öffnung','Rechte Öffnung'):
            vent = {'Linke Öffnung':'links','Mittlere Öffnung':'mitte','Rechte Öffnung':'rechts'}[name]
            # Das Befestigen des Seils allein darf niemals den Szenenwechsel auslösen.
            # Nach der Befestigung wird die Öffnung als Laufziel dargestellt; erst
            # ein separater Klick auf dieses Laufziel startet den Abstieg.
            # Die richtige Öffnung muss zuerst untersucht werden. Danach wartet das
            # Spiel ausdrücklich auf die Anwendung des Seils: kein Laufen/Fußsymbol
            # und kein Szenenwechsel, bevor das Seil an der Öffnung befestigt wurde.
            if vent == 'mitte' and crater_route_solved and not crater_rope_used:
                if 'Seil' not in inventory or item != 'Seil':
                    # Kein Hinweis auf die konkrete Lösung beim bloßen Anklicken.
                    return
                else:
                    ascent_rope_secured = True
                    crater_rope_used = True
                    selected = None
                    say('Du befestigst das Seil sicher an der Felskante der Öffnung. Klicke die Öffnung erneut, wenn du bereit bist hinabzusteigen.')
                save_game(); return
            if item == 'Feldbuch' or 'Feldbuch' in inventory:
                if vent == 'mitte':
                    say('Du vergleichst den Schatten und die Skizze im Feldbuch. Die Zeichen passen zu dieser Öffnung.')
                    crater_route_solved = True
                else:
                    say('Du vergleichst die Öffnung mit der Skizze. Die Beobachtung passt nicht zur Skizze.')
            else:
                say('Du untersuchst den Rand der Öffnung. Dampf zieht aus der Tiefe herauf.')
            save_game(); return
        if state == 'krater' and name in ('Professor Lidenbrock','Hans Bjelke'):
            if name == 'Professor Lidenbrock':
                say('Lidenbrock: „Untersuche den Krater sorgfältig. Wir sollten nichts überstürzen.“')
            else:
                say('Hans: „Ich bin bereit, euch zu sichern. Achtet auf den losen Fels am Rand.“')
            save_game(); return
        if state == 'fridriksson' and name == 'Professor Fridriksson':
            fridriksson_spoken = True
            if not fridriksson_puzzle_solved:
                say('Fridriksson: „Bevor ich euch einen Führer vermittle, lösen wir eine praktische Frage: Reykjavík hat kein verfügbares Boot für die Überfahrt zur Halbinsel. Wie erreicht ihr den Snæfellsjökull?“ Wählt die passende Möglichkeit auf der Karte.')
            else:
                say('Fridriksson: „Richtig. Der Landweg entlang der Küste ist unsere einzige Möglichkeit. Hans Bjelke wird euch morgen früh führen.“')
            save_game(); return
        if state == 'fridriksson' and name == 'Mit dem Boot über die Bucht':
            say('Fridriksson schüttelt den Kopf: „Das wäre der kürzeste Weg, aber in Reykjavík steht kein verfügbares Boot bereit. Überlegt noch einmal.“')
            save_game(); return
        if state == 'fridriksson' and name == 'Zu Fuß entlang der Küste':
            if fridriksson_spoken:
                fridriksson_puzzle_solved = True
                say('Fridriksson nickt zufrieden: „Ganz richtig. Wir reisen zu Fuß entlang der Küste. Hans Bjelke ist ein zuverlässiger Führer; morgen früh kann es losgehen.“')
            else:
                say('Sprich zuerst mit Professor Fridriksson über die Reiseplanung.')
            save_game(); return
        if state in ('island_hafen', 'hans'):
            if state == 'island_hafen' and (name.startswith('Hafenarbeiter ') or name == 'Alter Fischer'):
                worker = {'Hafenarbeiter 1':'arbeiter1','Hafenarbeiter 2':'arbeiter2','Hafenarbeiter 3':'arbeiter3','Alter Fischer':'fischer'}.get(name)
                if worker not in island_workers_spoken:
                    island_workers_spoken.append(worker)
                    say({'arbeiter1':'Hafenarbeiter: „Fragt Professor Fridriksson. Er ist ein Gelehrter und kennt sich hier aus.“','arbeiter2':'Hafenarbeiter: „Fridrikssons Haus liegt bei der kleinen Kirche, oberhalb des Hafens.“','arbeiter3':'Hafenarbeiter: „Ihr findet den Professor in seinem Haus. Er kann euch weiterhelfen.“','fischer':'Fischer: „Geht zuerst zu Professor Fridriksson. Er wird wissen, wer euch durch das Land führen kann.“'}[worker])
                else: say('Ihr habt bereits miteinander gesprochen.')
                save_game(); return
            if name == 'Altes Seil':
                if not island_rope_found:
                    island_rope_found = True
                    if 'Seil' not in inventory: inventory.append('Seil')
                    say('Du nimmst das kräftige Seil mit. Es wird im Inventar verstaut und könnte bei späteren Rätseln helfen.')
                else: say('Das Seil hast du bereits eingesteckt.')
                save_game(); return
        if state == 'hafen':
            if name == 'Hafenarbeiter':
                if not harbor_key_found:
                    harbor_key_found = True
                    if 'Schlüssel' not in inventory: inventory.append('Schlüssel')
                    say('Hafenarbeiter: „Sie haben also die Seekarte gefunden. Ich habe etwas, das Ihnen vielleicht noch nützlich sein wird.“')
                else:
                    say('Hafenarbeiter: „Passen Sie gut auf Ihre Ausrüstung auf.“')
                save_game(); return
            if name == 'Holzkiste':
                if item == 'Schlüssel' and harbor_key_found and not crate_open:
                    crate_open = True
                    say('Mit dem Schlüssel öffnest du die Kiste. Zwischen Tuch und Werkzeug liegt ein Messingkompass. Klicke ihn an, um ihn aufzunehmen.')
                elif not crate_open:
                    say('Das Holz ist vom Wetter gezeichnet. Das Schloss sitzt fest.')
                else:
                    say('Die Kiste steht offen.')
                save_game(); return
            if name == 'Kompass':
                if not crate_open:
                    say('Der Kompass liegt noch in der verschlossenen Kiste.')
                elif 'Kompass' not in inventory:
                    inventory.append('Kompass'); compass_found=True
                    say('Du nimmst den Messingkompass auf. Er ist schwer und liegt gut in der Hand.')
                else: say('Den Kompass hast du bereits im Inventar.')
                save_game(); return
        h=next((v for v in hotspots if v['name']==name),None)
        if not h: return
        if h.get('route'):
            target = h['route']
            if target == 'hafen' and not harbor_unlocked:
                say('Der Weg zum Hafen ist noch verschlossen.')
                return
            change_scene(target)
            return
        if name == 'Pergament' and not professor_spoken:
            say('Sprich zuerst mit Professor Lidenbrock.')
            return
        if item:
            if item=='Lupe' and name=='Pergament':
                parchment_deciphered = True
                say('Unter den winzigen Zeichen erkennst du einen Namen: Snæfellsjökull. Daneben ist eine geheimnisvolle Wegbeschreibung nach Island eingetragen.')
            else: say(f'{item} passt hier nicht.')
            selected=None
        elif h.get('item'):
            if h['item'] not in inventory:
                inventory.append(h['item']); say('Du hebst die Messinglupe auf und legst sie ins Inventar.')
            else: say('Die Lupe hast du bereits gefunden.')
        elif name == 'Professor':
            if not professor_spoken:
                professor_spoken = True
                say('Professor Lidenbrock: „Dieses Pergament gibt mir Rätsel auf. Die fremdartigen Zeichen scheinen eine Botschaft zu verbergen. Finde heraus, was sie bedeuten, Axel. Wir sprechen danach noch einmal darüber.“')
            elif not parchment_deciphered or 'Lupe' not in inventory:
                say('Professor Lidenbrock: „Hast du etwas herausgefunden, Axel? Die Zeichen geben ihr Geheimnis noch nicht preis. Sieh dich im Arbeitszimmer um. Vielleicht entdeckst du etwas, das dir hilft, die rätselhafte Schrift zu verstehen.“')
            else:
                say('Professor Lidenbrock: „Snæfellsjökull! Ein Vulkan in Island! Jetzt kennen wir das Ziel. Bereite dich vor, Axel – unsere Reise beginnt dort!“')
                harbor_unlocked = True
                state = 'room'
        elif name == 'Bücherregal':
            bookshelf_examined = True
            say('Du durchsuchst das Bücherregal. Hinter einem dicken Folianten entdeckst du eine Messinglupe! Klicke auf die Lupe im Regal, um sie aufzunehmen.')
        elif name == 'Lupe':
            if not bookshelf_examined:
                say('Zwischen den Büchern könnte etwas verborgen sein. Untersuche das Regal genauer.')
            elif 'Lupe' not in inventory:
                inventory.append('Lupe'); say('Du nimmst die Messinglupe aus dem Regal und legst sie ins Inventar.')
            else: say('Die Lupe hast du bereits gefunden.')
        else: say(h['text'])
        save_game()
    def walk(x,y,action=None):
        nonlocal tx,ty,moving,facing_right,pending
        if y<400 or y>=SCENE_H-2: return False
        if state == 'fridriksson' and y < 485: return False
        tx=float(max(35,min(W-35,x))); ty=float(max(500,min(SCENE_H-4,y)))
        facing_right=tx>=px; moving=math.hypot(tx-px,ty-py)>2; pending=action
        if not moving and pending: finish_action()
        return True
    def interact(h):
        nonlocal state, message, message_until, ascent_rope_secured, selected, crater_rope_used, cave_enter_pending, tx, ty, moving, facing_right, pending
        # Am gelösten Krater-Hotspot wird zuerst das Seil angewendet. Nicht laufen,
        # also auch kein Fußsymbol, bis die Seilsicherung wirklich gesetzt ist.
        if state == 'krater' and h.get('name') == 'Mittlere Öffnung' and crater_route_solved and not crater_rope_used:
            if 'Seil' not in inventory or selected != 'Seil':
                # Der Spieler soll die Lösung selbst entdecken.
                return
            else:
                ascent_rope_secured = True
                crater_rope_used = True
                selected = None
                save_game()
                say('Du befestigst das Seil sicher an der Felskante. Der dunkle Schlund des Kraters liegt vor dir.')
            return
        if h.get('route'):
            if state == 'gaenge' and h['route'] == 'meer':
                change_scene('meer')
                save_game()
                return
            if state == 'meer' and h['route'] == 'gaenge':
                change_scene('gaenge')
                save_game()
                return
            if state == 'gaenge' and h['route'] == 'tiefe':
                change_scene('tiefe')
                save_game()
                return
            if state == 'meer' and h['route'] == 'floss' and meer_route_solved:
                change_scene('floss')
                save_game()
                return
            if state == 'floss' and h['route'] == 'meer':
                change_scene('meer')
                save_game()
                return
            if state == 'meerfahrt_ende' and h['route'] == 'punkt6':
                change_scene('punkt6')
                save_game()
                return
            if state == 'punkt6' and h['route'] == 'spielende':
                state = 'ending'
                message = ''
                message_until = 0
                return
            if state == 'tiefe' and h['route'] == 'gaenge':
                cave_enter_pending = True
                tx, ty = 900.0, 570.0
                facing_right = True
                moving = math.hypot(tx-px, ty-py) > 2
                pending = None
                if not moving:
                    cave_enter_pending = False
                    change_scene('gaenge')
                return
            if h['route'] == 'hafen' and state != 'ueberfahrt' and not harbor_unlocked:
                say('Der Weg zum Hafen ist noch verschlossen.')
                return
            if h['route'] == 'ueberfahrt' and not course_calculated:
                say('Lege zuerst Seekarte und Kompass aus und bestimme mit der Mannschaft den Kurs.')
                return
            if h['route'] == 'fridriksson' and len(set(island_workers_spoken)) < 3:
                say('Sprich zuerst mit mindestens drei Leuten am Hafen, um den Weg zu Professor Fridriksson zu erfahren.')
                return
            if h['route'] == 'hans' and not (fridriksson_spoken and fridriksson_puzzle_solved):
                say('Sprecht mit Fridriksson und löst zuerst seine Frage zur Reise nach Snæfellsjökull.')
                return
            if h['route'] == 'island_hafen' and state == 'ueberfahrt' and len(set(crossing_tasks)) < 3:
                say('Du kannst noch nicht an Land. Sichere zuerst Tampen und Sturmsegel und stabilisiere dann das Steuerrad.')
                return
            if state == 'floss' and h['route'] == 'meerfahrt' and not (floss_ready and floss_wood_aligned and floss_buoyancy_checked):
                say('Das Floß ist noch nicht seetüchtig. Prüfe zuerst Holz, Bindungen und Auftrieb.')
                return
            if h['route'] == 'tiefe':
                if 'Seil' not in inventory or not crater_rope_used:
                    # Beim bloßen Anklicken wird kein Lösungsweg verraten.
                    return
            change_scene(h['route'])
        else:
            walk(*h['approach'], action=(h['name'],selected))
    def draw_symbol(kind,pos):
        x,y=pos; c=(255,224,160)
        pygame.draw.circle(canvas,c,(x,y),17,2)
        if kind=='hand':
            pygame.draw.line(canvas,c,(x-4,y+8),(x-4,y-8),3); pygame.draw.line(canvas,c,(x-4,y-3),(x+3,y-12),3); pygame.draw.line(canvas,c,(x+3,y-6),(x+9,y-11),3)
        elif kind=='talk':
            pygame.draw.ellipse(canvas,c,(x-11,y-8,22,16),2); pygame.draw.line(canvas,c,(x-3,y+7),(x-8,y+13),2)
        else:
            pygame.draw.ellipse(canvas,c,(x-11,y-7,22,14),2); pygame.draw.circle(canvas,c,(x,y),3,2)
    def draw_item(item, rect):
        x,y=rect.center
        if item=='Seekarte':
            pygame.draw.rect(canvas,(213,190,133),(x-19,y-13,38,27),border_radius=2); pygame.draw.line(canvas,(114,82,42),(x-12,y-4),(x+12,y+6),2); pygame.draw.line(canvas,(114,82,42),(x-7,y+10),(x+8,y-8),2)
        elif item=='Kompass':
            pygame.draw.circle(canvas,(194,151,70),(x,y),15,4); pygame.draw.circle(canvas,(220,205,161),(x,y),10,1); pygame.draw.polygon(canvas,(150,35,25),[(x,y-8),(x+4,y+3),(x,y+1),(x-3,y+3)])
        elif item=='Schlüssel':
            pygame.draw.circle(canvas,(194,151,70),(x-5,y),7,3); pygame.draw.line(canvas,(194,151,70),(x+1,y),(x+18,y),4); pygame.draw.line(canvas,(194,151,70),(x+12,y),(x+12,y+6),3)
        elif item=='Seil':
            # Aufgewickeltes Hanfseil als sichtbares Inventarsymbol
            rope=(205,164,91); shadow=(112,75,35)
            pygame.draw.ellipse(canvas,shadow,(x-20,y-13,39,27),4)
            pygame.draw.ellipse(canvas,rope,(x-17,y-10,33,21),3)
            pygame.draw.ellipse(canvas,shadow,(x-13,y-7,25,15),3)
            pygame.draw.arc(canvas,rope,(x-17,y-10,33,21),0.2,5.8,3)
            pygame.draw.line(canvas,rope,(x+12,y+7),(x+20,y+12),3)
            pygame.draw.line(canvas,shadow,(x+18,y+10),(x+21,y+13),2)
        elif item=='Feldbuch':
            pygame.draw.rect(canvas,(106,56,32),(x-13,y-17,26,34),border_radius=2)
            pygame.draw.rect(canvas,(188,145,83),(x-10,y-14,20,28),1)
            pygame.draw.line(canvas,(220,190,130),(x-6,y-7),(x+6,y-7),1)
            pygame.draw.line(canvas,(220,190,130),(x-6,y-1),(x+6,y-1),1)
            pygame.draw.line(canvas,(220,190,130),(x-6,y+5),(x+3,y+5),1)
        elif item=='Lupe':
            pygame.draw.circle(canvas,(204,162,76),(x-5,y-4),11,4)
            pygame.draw.circle(canvas,(105,165,182),(x-5,y-4),7,1)
            pygame.draw.line(canvas,(184,131,49),(x+3,y+4),(x+16,y+17),5)
        elif item=='Holz':
            pygame.draw.line(canvas,(117,70,32),(x-20,y-9),(x+18,y-9),9)
            pygame.draw.line(canvas,(166,111,55),(x-20,y-9),(x+18,y-9),5)
            pygame.draw.ellipse(canvas,(205,157,91),(x+13,y-14,12,10),2)
            pygame.draw.line(canvas,(117,70,32),(x-17,y+7),(x+17,y+7),7)
            pygame.draw.line(canvas,(166,111,55),(x-17,y+7),(x+17,y+7),3)
        elif item=='Ranken':
            pygame.draw.arc(canvas,(96,135,62),(x-18,y-16,30,31),0.2,5.7,4)
            pygame.draw.arc(canvas,(126,158,72),(x-8,y-13,25,28),1.0,6.1,3)
            pygame.draw.ellipse(canvas,(126,158,72),(x-17,y-8,10,5))
            pygame.draw.ellipse(canvas,(126,158,72),(x+5,y+5,10,5))
    def wrap(text, f, width):
        lines=[]; line=''
        for word in text.split():
            test=(line+' '+word).strip()
            if f.size(test)[0]>width and line: lines.append(line); line=word
            else: line=test
        if line: lines.append(line)
        return lines

    def start_music(track):
        path = MUSIC_DIR / f'{track}.wav'
        if pygame.mixer.get_init() and path.is_file():
            try: pygame.mixer.music.load(str(path)); pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(-1)
            except pygame.error: pass
    def set_menu_state(target):
        nonlocal settings_from, state
        if target == 'settings': settings_from = 'menu'
        state = target
    def open_credits_from_menu():
        nonlocal state, credits_from
        credits_from = 'menu'
        state = 'credits'
    def stop_game():
        nonlocal running
        running = False

    while running:
        # Umgebungsgeräusche: Wind auf allen Außen-/Landschaftsszenen, Kamin drinnen, Möwen auf See.
        outdoor_states = ('island_weg', 'stapi', 'stapi_aufstieg', 'island_hafen', 'hans', 'hafen', 'krater')
        desired_effect = ('fireplace' if state in ('room','chapter2','fridriksson') else ('cave_drips' if state == 'tiefe' else ('wasser' if state in ('gaenge','meer','floss','meerfahrt','meerfahrt_ende', 'punkt6') else ('wind' if state in outdoor_states else ('seagulls' if state in ('schiff','ueberfahrt') else None)))))
        if desired_effect != active_effect:
            if effects_channel: effects_channel.stop()
            active_effect = desired_effect
            if effects_channel and desired_effect in effects_sounds:
                effects_channel.set_volume(effects_volume)
                effects_channel.play(effects_sounds[desired_effect], loops=-1)
        desired_music = ('menu' if state in ('intro','menu','settings','credits','ending') else ('ueberfahrt' if state == 'ueberfahrt' else ('chapter3' if state in ('chapter3','schiff') else ('chapter4' if state in ('island_hafen','fridriksson','hans','island_weg') else ('chapter2' if state in ('chapter2','hafen') else 'chapter1')))))
        if desired_music != music_state:
            start_music(desired_music); music_state = desired_music
        now = pygame.time.get_ticks()
        if state in ('room', 'chapter2') and now - last_autosave >= 5000:
            save_game()
        dt=min(clock.tick(FPS)/1000, .05)
        sw,sh=screen.get_size(); scale=min(sw/W,sh/H); vw,vh=int(W*scale),int(H*scale); ox,oy=(sw-vw)//2,(sh-vh)//2
        mouse=pygame.mouse.get_pos(); mpos=(int((mouse[0]-ox)/scale),int((mouse[1]-oy)/scale))
        if state in ('room','chapter2','zweites_zimmer','flur','hafen','schiff','ueberfahrt','island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6') and moving:
            dx,dy=tx-px,ty-py; dist=math.hypot(dx,dy); step=245*dt
            if dist<=step or dist<2:
                px,py=tx,ty; moving=False
                entering_cave = cave_enter_pending
                finish_action()
                # Erst nach Axels sichtbarer Gehbewegung in den zweiten Höhlenraum wechseln.
                if entering_cave and state == 'tiefe' and cave_enter_pending:
                    cave_enter_pending = False
                    change_scene('gaenge')
            else: px+=dx/dist*step; py+=dy/dist*step; facing_right=dx>=0
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN and e.key==pygame.K_F11:
                set_fullscreen(not fullscreen)
            elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                if state == 'settings': state=settings_from
                elif state == 'credits': state=credits_from
                elif state == 'ending': state='menu'
                elif state in ('room','chapter2','zweites_zimmer','flur','hafen','schiff','ueberfahrt','island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6'):
                    save_game(); state='menu'
                elif state=='menu': running=False
            elif e.type==pygame.MOUSEMOTION and state=='settings' and e.buttons[0] and (pygame.Rect(285,455,455,58).collidepoint((int((e.pos[0]-ox)/scale),int((e.pos[1]-oy)/scale))) or pygame.Rect(285,535,455,58).collidepoint((int((e.pos[0]-ox)/scale),int((e.pos[1]-oy)/scale)))):
                p=(int((e.pos[0]-ox)/scale),int((e.pos[1]-oy)/scale))
                if pygame.Rect(285,535,455,58).collidepoint(p):
                    effects_volume=max(0.0,min(1.0,(p[0]-300)/425))
                    if effects_channel: effects_channel.set_volume(effects_volume)
                else:
                    if pygame.mixer.get_init(): pygame.mixer.music.set_volume(volume)
                save_settings()
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                p=(int((e.pos[0]-ox)/scale),int((e.pos[1]-oy)/scale))
                # Text ausblenden, aber den Klick zugleich an das angeklickte Ziel weitergeben.
                # Sonst wirkt es, als würden Augen-/Gesprächs-Hotspots nicht reagieren.
                if message and state != 'intro':
                    message, message_until = '', 0
                if state=='intro':
                    intro_page += 1
                    if intro_page >= len(intro_pages): state='menu'
                    intro_start = pygame.time.get_ticks()
                elif state=='menu':
                    # Hitboxen passend zu den fünf sichtbaren Knöpfen im 1024x768-Menübild.
                    # Enge, getrennte Bereiche verhindern, dass ein Klick den Nachbarknopf trifft.
                    menu_buttons = [
                        (pygame.Rect(96, 286, 191, 58), begin_chapter),
                        (pygame.Rect(96, 363, 191, 59), load_game),
                        (pygame.Rect(96, 441, 191, 60), lambda: set_menu_state('settings')),
                        (pygame.Rect(96, 520, 191, 61), lambda: open_credits_from_menu()),
                        (pygame.Rect(96, 600, 191, 61), lambda: stop_game()),
                    ]
                    for hitbox, action in menu_buttons:
                        if hitbox.collidepoint(p):
                            action()
                            break
                elif state=='settings':
                    if pygame.Rect(285, 205, 455, 58).collidepoint(p): set_fullscreen(not fullscreen)
                    elif pygame.Rect(285, 285, 455, 58).collidepoint(p):
                        sound_driver = {'system':'pulseaudio','pulseaudio':'alsa','alsa':'system'}.get(sound_driver,'system'); save_settings()
                        say('Soundtreiber gespeichert. Die Treiberauswahl gilt nach einem Neustart.', 4500)
                    elif pygame.Rect(285, 365, 455, 58).collidepoint(p):
                        if sound_devices:
                            sound_device_index = (sound_device_index + 1) % len(sound_devices)
                            try:
                                pygame.mixer.quit(); pygame.mixer.init(devicename=sound_devices[sound_device_index]); pygame.mixer.music.set_volume(volume)
                                if effects_channel: effects_channel.set_volume(effects_volume)
                                say('Soundkarte gewechselt: ' + sound_devices[sound_device_index], 3500)
                            except TypeError:
                                try: pygame.mixer.init(); pygame.mixer.music.set_volume(volume)
                                except pygame.error: pass
                                say('Diese Pygame-Version kann das Audiogerät nicht direkt wechseln. Auswahl wird gespeichert.', 4000)
                            except pygame.error:
                                try: pygame.mixer.init(); pygame.mixer.music.set_volume(volume)
                                except pygame.error: pass
                                say('Audiogerät konnte nicht geöffnet werden; Standardgerät wird verwendet.', 4000)
                            save_settings()
                        else: say('Keine auswählbaren Audiogeräte gemeldet; Standardgerät wird verwendet.', 4000)
                    elif pygame.Rect(285, 455, 455, 58).collidepoint(p):
                        volume = max(0.0, min(1.0, (p[0]-300)/425))
                        if pygame.mixer.get_init(): pygame.mixer.music.set_volume(volume)
                        save_settings()
                    elif pygame.Rect(285, 535, 455, 58).collidepoint(p):
                        effects_volume=max(0.0,min(1.0,(p[0]-300)/425))
                        if effects_channel: effects_channel.set_volume(effects_volume)
                        save_settings()
                    elif pygame.Rect(285, 625, 455, 50).collidepoint(p): state=settings_from
                elif state=='ending':
                    if pygame.Rect(285, 455, 455, 54).collidepoint(p):
                        credits_from='ending'
                        state='credits'
                    elif pygame.Rect(285, 525, 455, 54).collidepoint(p):
                        begin_chapter()
                    elif pygame.Rect(285, 595, 455, 54).collidepoint(p):
                        state='menu'
                elif state=='credits':
                    state=credits_from
                elif state in ('room','chapter2','zweites_zimmer','flur','hafen','schiff','ueberfahrt','island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6'):
                    if p[1]>=SCENE_H:
                        slot=(p[0]-15)//92
                        if 0<=slot<len(inventory): selected=inventory[slot]; say(f'{selected} ausgewählt. Klicke auf ein Ziel.')
                    else:
                        h=hit(p)
                        if h: interact(h)
                        elif pygame.Rect(475, 320, 110, 70).collidepoint(p) and not professor_spoken: say('Sprich zuerst mit Professor Lidenbrock.')
                        elif walk(*p): selected=None
                        else: say('Klicke auf den freien Boden im Vordergrund.')
        if state=='intro':
            canvas.blit(intro_bg,(0,0))
            page=min(len(intro_pages)-1, intro_page); heading,body=intro_pages[page]
            shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((0,0,0,145)); canvas.blit(shade,(0,0))
            title=serif.render(TITLE,True,gold); canvas.blit(title,title.get_rect(center=(W//2,155)))
            sub=small.render('Ein Point-and-Click-Abenteuer nach Jules Verne',True,cream); canvas.blit(sub,sub.get_rect(center=(W//2,215)))
            pygame.draw.line(canvas,gold,(130,255),(894,255),2)
            head=serif.render(heading,True,gold); canvas.blit(head,head.get_rect(center=(W//2,355)))
            for i,line in enumerate(wrap(body,font,840)[:3]):
                surf=font.render(line,True,cream); canvas.blit(surf,surf.get_rect(center=(W//2,425+i*38)))
            hint=small.render('Linke Maustaste: weiter',True,cream); canvas.blit(hint,hint.get_rect(center=(W//2,720)))
        elif state=='menu':
            canvas.blit(menu,(0,0))
            if message:
                panel=pygame.Surface((650,38),pygame.SRCALPHA); panel.fill((10,7,4,220)); canvas.blit(panel,(25,710)); canvas.blit(small.render(message,True,cream),(36,721))
        elif state=='settings':
            canvas.blit(menu,(0,0)); shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((0,0,0,205)); canvas.blit(shade,(0,0))
            panel=pygame.Rect(190,85,645,630); pygame.draw.rect(canvas,(31,22,14),panel,border_radius=12); pygame.draw.rect(canvas,gold,panel,3,border_radius=12)
            head=serif.render('Einstellungen',True,gold); canvas.blit(head,head.get_rect(center=(W//2,155)))
            rows=[('Vollbildmodus', 'Ein' if fullscreen else 'Aus'),('Soundtreiber', {'system':'Systemstandard','pulseaudio':'PulseAudio','alsa':'ALSA'}.get(sound_driver,sound_driver)),('Soundkarte', sound_devices[sound_device_index] if 0<=sound_device_index<len(sound_devices) else 'Systemstandard / nicht erkannt')]
            for i,(label,value) in enumerate(rows):
                r=pygame.Rect(285,205+i*80,455,58); pygame.draw.rect(canvas,(48,37,25),r,border_radius=7); pygame.draw.rect(canvas,(148,111,58),r,1,border_radius=7)
                canvas.blit(small.render(label,True,cream),(r.x+14,r.y+6)); canvas.blit(tiny.render(value,True,gold),(r.x+14,r.y+32)); canvas.blit(tiny.render('Ändern  ›',True,cream),(r.right-100,r.y+20))
            r=pygame.Rect(285,455,455,58); pygame.draw.rect(canvas,(48,37,25),r,border_radius=7); pygame.draw.rect(canvas,(148,111,58),r,1,border_radius=7)
            canvas.blit(small.render(f'Lautstärke  {round(volume*100)} %',True,cream),(r.x+14,r.y+5)); pygame.draw.rect(canvas,(80,63,42),(r.x+14,r.y+35,425,8),border_radius=4); pygame.draw.rect(canvas,gold,(r.x+14,r.y+35,int(425*volume),8),border_radius=4); pygame.draw.circle(canvas,cream,(r.x+14+int(425*volume),r.y+39),7)
            r=pygame.Rect(285,535,455,58); pygame.draw.rect(canvas,(48,37,25),r,border_radius=7); pygame.draw.rect(canvas,(148,111,58),r,1,border_radius=7)
            canvas.blit(small.render(f'Umgebungsgeräusche  {round(effects_volume*100)} %',True,cream),(r.x+14,r.y+5)); pygame.draw.rect(canvas,(80,63,42),(r.x+14,r.y+35,425,8),border_radius=4); pygame.draw.rect(canvas,gold,(r.x+14,r.y+35,int(425*effects_volume),8),border_radius=4); pygame.draw.circle(canvas,cream,(r.x+14+int(425*effects_volume),r.y+39),7)
            back=pygame.Rect(285,625,455,50); pygame.draw.rect(canvas,(57,42,25),back,border_radius=7); pygame.draw.rect(canvas,gold,back,1,border_radius=7); canvas.blit(small.render('Zurück zum Hauptmenü',True,cream),small.render('Zurück zum Hauptmenü',True,cream).get_rect(center=back.center))
            canvas.blit(tiny.render('Hinweis: Treiberwechsel wird nach Neustart aktiv. F11 schaltet Vollbild um.',True,cream),(205,690))
            if message:
                canvas.blit(small.render(message,True,cream),(210,680))
        elif state=='ending':
            # Eigenständiger, klarer Abschluss statt einer Dialogbox über der Vulkanszene.
            canvas.blit(scene_images['punkt6'], (0,0))
            shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((0,0,0,145)); canvas.blit(shade,(0,0))
            panel=pygame.Rect(155,95,715,555)
            pygame.draw.rect(canvas,(20,14,10),panel,border_radius=14)
            pygame.draw.rect(canvas,gold,panel,3,border_radius=14)
            title=serif.render('DIE REISE IST BEENDET',True,gold)
            canvas.blit(title,title.get_rect(center=(W//2,150)))
            ending_lines=[
                'Ein gewaltiger Ausbruch trägt euch aus dem Vulkanschlot.',
                'Auf Stromboli erreicht ihr wieder das Tageslicht.',
                'Axel, Professor Lidenbrock und Hans haben überlebt.',
                'Das Geheimnis des Erdinneren wird euch für immer begleiten.'
            ]
            for i,line in enumerate(ending_lines):
                surf=small.render(line,True,cream)
                canvas.blit(surf,surf.get_rect(center=(W//2,225+i*32)))
            for rect,label in ((pygame.Rect(285,455,455,54),'Abspann und Mitwirkende'),(pygame.Rect(285,525,455,54),'Neues Spiel'),(pygame.Rect(285,595,455,54),'Hauptmenü')):
                pygame.draw.rect(canvas,(54,39,24),rect,border_radius=7)
                pygame.draw.rect(canvas,gold,rect,2,border_radius=7)
                text_surf=small.render(label,True,cream)
                canvas.blit(text_surf,text_surf.get_rect(center=rect.center))
        elif state=='credits':
            canvas.blit(menu,(0,0)); shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((0,0,0,185)); canvas.blit(shade,(0,0))
            panel=pygame.Rect(180,170,665,410); pygame.draw.rect(canvas,(31,22,14),panel,border_radius=12); pygame.draw.rect(canvas,gold,panel,3,border_radius=12)
            canvas.blit(serif.render('Mitwirkende',True,gold),serif.render('Mitwirkende',True,gold).get_rect(center=(W//2,230)))
            canvas.blit(font.render('Entwicklung und Gestaltung',True,cream),font.render('Entwicklung und Gestaltung',True,cream).get_rect(center=(W//2,320)))
            canvas.blit(serif.render('Goldisoft 2026',True,gold),serif.render('Goldisoft 2026',True,gold).get_rect(center=(W//2,385)))
            canvas.blit(small.render('Frei inspiriert vom Roman von Jules Verne',True,cream),small.render('Frei inspiriert vom Roman von Jules Verne',True,cream).get_rect(center=(W//2,445)))
            canvas.blit(tiny.render('Klicken zum Zurückkehren',True,cream),tiny.render('Klicken zum Zurückkehren',True,cream).get_rect(center=(W//2,535)))
        else:
            if state in ('zweites_zimmer','flur','hafen','schiff','ueberfahrt','island_hafen','fridriksson','hans','island_weg','stapi','stapi_aufstieg','krater','tiefe','gaenge','meer','floss','meerfahrt','meerfahrt_ende', 'punkt6'):
                canvas.blit(scene_images[{'hans':'island_hafen'}.get(state, state)], (0,0))
                scene_title = {'zweites_zimmer':'ZWEITES ZIMMER','flur':'FLUR','hafen':'HAFEN','schiff':'AN BORD · NAVIGATION','ueberfahrt':'STURMFAHRT NACH ISLAND','island_hafen':'REYKJAVÍK · ISLAND','fridriksson':'PROFESSOR FRIDRIKSSON','hans':'HANS BJELKE','island_weg':'AUFBRUCH ZUM SNÆFELLSJÖKULL','stapi':'STAPI · KÜSTENWEG','stapi_aufstieg':'AUFSTIEG ZUM SNÆFELLSJÖKULL','krater':'KRATERRAND · SNÆFELLSJÖKULL','tiefe':'IN DER HÖHLE','gaenge':'UNTERIRDISCHE GÄNGE','meer':'GROSSE HÖHLE UND UNTERIRDISCHES MEER','floss':'VORBEREITUNG DES FLOSSES','meerfahrt':'ÜBERFAHRT ÜBER DAS UNTERIRDISCHE MEER','meerfahrt_ende':'DIE SICHERE KÜSTE','punkt6':'DER VULKANSCHLOT'} [state]
                # Die Kursbestätigung erscheint nur kurz im Dialogfeld, nicht dauerhaft
                # mitten im Schiffsbild.
                title_surf = small.render(scene_title, True, gold)
                canvas.blit(title_surf, (18, 14))
            else:
                canvas.blit(room,(0,0))
            # Vermessungskiste: realistische, ausgewählte offene Kiste als separates Sprite.
            # Rätselzustand und Feldbuch-Hotspot bleiben unverändert.
            if state == 'stapi':
                if stapi_crate_open:
                    canvas.blit(stapi_chest_open_img, (405, 370))
                else:
                    # Geschlossene Gegenansicht derselben Vermessungskiste – kein Platzhalter.
                    canvas.blit(stapi_chest_closed_img, (405, 370))
            # Gut sichtbares, aufgewickeltes Seil auf freien Planken im Vordergrund.
            # Es liegt weit weg vom Szenenübergang und besitzt einen großzügigen Hotspot.
            if state in ('island_hafen', 'hans') and not island_rope_found:
                rope_centre = (235, 535)
                for rw, rh in ((112, 46), (94, 38), (76, 30), (58, 22)):
                    rect = pygame.Rect(rope_centre[0]-rw//2, rope_centre[1]-rh//2, rw, rh)
                    pygame.draw.ellipse(canvas, (83, 48, 24), rect.inflate(4, 4), 10)
                    pygame.draw.ellipse(canvas, (174, 126, 65), rect, 7)
                    pygame.draw.arc(canvas, (224, 181, 112), rect.inflate(-8, -6), 0.2, 5.8, 3)
                pygame.draw.line(canvas, (198, 151, 85), (270, 533), (307, 550), 8)
                pygame.draw.line(canvas, (91, 54, 28), (270, 533), (307, 550), 3)
            # Die Lupe ist kein Objekt auf dem Tisch: Sie wird erst nach der Regal-Untersuchung sichtbar.
            if bookshelf_examined and 'Lupe' not in inventory:
                draw_item('Lupe', pygame.Rect(390, 270, 36, 36))
            # Beide Figuren sind getrennte Sprites; nur Axel reagiert auf Boden-Klicks.
            if state in ('room','chapter2','fridriksson','island_hafen','hans','island_weg','stapi','stapi_aufstieg','krater','tiefe','gaenge','meer','floss','meerfahrt','meerfahrt_ende', 'punkt6'):
                outdoor = state not in ('room','chapter2','fridriksson')
                if state == 'fridriksson':
                    # Beide Professoren gehören in diese gemeinsame Gesprächsszene.
                    # Lidenbrock wird wie in allen Außenszenen um 20 % verkleinert.
                    lid = pygame.transform.smoothscale(professor, (max(1, round(professor.get_width()*0.8)), max(1, round(professor.get_height()*0.8))))
                    canvas.blit(lid, (570 - lid.get_width()//2, 610 - lid.get_height()))
                    canvas.blit(professor_fridriksson, (805 - professor_fridriksson.get_width()//2, 610 - professor_fridriksson.get_height()))
                elif state in ('meerfahrt','meerfahrt_ende', 'punkt6'):
                    professor_draw = pygame.transform.smoothscale(professor, (max(1, round(professor.get_width()*0.60)), max(1, round(professor.get_height()*0.60))))
                    canvas.blit(professor_draw, (755 - professor_draw.get_width()//2, 590 - professor_draw.get_height()))
                else:
                    professor_x = 340 if outdoor else 805
                    professor_draw = professor
                    if outdoor:
                        professor_draw = pygame.transform.smoothscale(professor, (max(1, round(professor.get_width()*0.8)), max(1, round(professor.get_height()*0.8))))
                    canvas.blit(professor_draw, (professor_x - professor_draw.get_width()//2, 610 - professor_draw.get_height()))
            # Hans erscheint im Hafen von Reykjavík erst, nachdem Fridriksson
            # gesprochen wurde und seine Reiseplanungsfrage gelöst ist.
            hans_visible = (
                state in ('hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6')
                or (state == 'island_hafen' and fridriksson_spoken and fridriksson_puzzle_solved)
            )
            if hans_visible:
                if state in ('meerfahrt','meerfahrt_ende', 'punkt6'):
                    hans_draw = pygame.transform.smoothscale(hans_sprite, (max(1, round(hans_sprite.get_width()*0.66)), max(1, round(hans_sprite.get_height()*0.66))))
                    canvas.blit(hans_draw, (885 - hans_draw.get_width()//2, 590 - hans_draw.get_height()))
                else:
                    hans_x = (910 if state == 'krater' else (820 if state != 'island_weg' else 790))
                    canvas.blit(hans_sprite, (hans_x - hans_sprite.get_width()//2, 610 - hans_sprite.get_height()))
            if state in ('hafen', 'schiff', 'ueberfahrt', 'island_hafen', 'fridriksson', 'hans', 'island_weg', 'stapi', 'stapi_aufstieg', 'krater', 'tiefe', 'gaenge', 'meer', 'floss', 'meerfahrt', 'meerfahrt_ende', 'punkt6'):
                player = axel_harbor_r if facing_right else axel_harbor_l
            else:
                player = axel_r if facing_right else axel_l
            if state in ('meerfahrt','meerfahrt_ende', 'punkt6'):
                player = pygame.transform.smoothscale(player, (max(1, round(player.get_width()*0.69)), max(1, round(player.get_height()*0.69))))
                # Größere, besser erkennbare Figuren; alle Füße stehen auf den Floßstämmen.
                canvas.blit(player, (int(610-player.get_width()/2), int(590-player.get_height())))
            else:
                canvas.blit(player, (int(px-player.get_width()/2), int(py-player.get_height())))
            pygame.draw.rect(canvas,(12,8,5),(0,SCENE_H,W,H-SCENE_H)); pygame.draw.line(canvas,gold,(0,SCENE_H),(W,SCENE_H),2)
            canvas.blit(small.render('INVENTAR',True,gold),(15,SCENE_H+8))
            for i,item in enumerate(inventory):
                r=pygame.Rect(15+i*92,SCENE_H+28,78,48); pygame.draw.rect(canvas,(35,25,16),r,border_radius=5); pygame.draw.rect(canvas,gold if selected==item else (115,82,44),r,2 if selected==item else 1,border_radius=5); draw_item(item,r)
                label=tiny.render(item,True,cream); canvas.blit(label,label.get_rect(center=(r.centerx,SCENE_H+88)))
            if message:
                box=pygame.Surface((790,78),pygame.SRCALPHA); box.fill((9,6,3,225)); canvas.blit(box,(117,12)); pygame.draw.rect(canvas,gold,(117,12,790,78),1)
                for i,line in enumerate(wrap(message,small,750)[:3]): canvas.blit(small.render(line,True,cream),(132,20+i*19))
            h=hit(mpos) if 0 <= mpos[1] < SCENE_H else None
            if h:
                if h.get('route'):
                    # Deutlich erkennbare Schuhsohlen von unten mit Profilrillen.
                    x,y=mpos; glow=(255,207,91); dark=(91,54,18)
                    left=pygame.Rect(x-21,y-20,17,34); right=pygame.Rect(x+4,y-12,17,34)
                    pygame.draw.ellipse(canvas,dark,left.inflate(8,8)); pygame.draw.ellipse(canvas,dark,right.inflate(8,8))
                    pygame.draw.ellipse(canvas,glow,left,3); pygame.draw.ellipse(canvas,glow,right,3)
                    for yy in (y-13,y-6,y+1,y+8):
                        pygame.draw.line(canvas,glow,(x-18,yy),(x-7,yy+2),2)
                    for yy in (y-5,y+2,y+9,y+16):
                        pygame.draw.line(canvas,glow,(x+7,yy),(x+18,yy+2),2)
                    pygame.draw.polygon(canvas,glow,[(x+23,y+3),(x+37,y+3),(x+37,y-3),(x+48,y+7),(x+37,y+17),(x+37,y+11),(x+23,y+11)])
                else: draw_symbol(h['kind'],mpos)
        screen.fill((0,0,0)); screen.blit(pygame.transform.smoothscale(canvas,(vw,vh)),(ox,oy)); pygame.display.flip()
    save_game()
    pygame.quit()

if __name__=='__main__':
    try: main()
    except Exception:
        import traceback; traceback.print_exc()
        try: input('Fehler im Spiel. Enter zum Schließen ...')
        except EOFError: pass
        raise
