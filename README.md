# Die Reise zum Mittelpunkt der Erde

**Version 2.3.1**

Ein grafisches Point-and-Click-Adventure, frei inspiriert vom Roman *Voyage au centre de la Terre* (1864) von Jules Verne. Erkunde Orte, sprich mit Figuren, sammle Gegenstände und löse Rätsel auf der Reise von Hamburg nach Island und durch die unterirdische Welt.

## Inhalt

- Vorspann und illustriertes Hauptmenü
- Point-and-Click-Steuerung mit untersuchbaren Bereichen, Gesprächen und Inventar
- Sechs Abenteuerabschnitte: Höhle, unterirdische Gänge, große Höhle und Meer, Floßlager, Überfahrt und sichere Küste sowie Vulkanschlot
- Eigenständige Hintergründe und separat dargestellte Figuren
- Rätsel-Fortschritt und Spielstand
- Kapitelmusik und Umgebungsgeräusche
- Einstellungsmenü für Vollbild, Lautstärke, Umgebungsgeräusche und unterstützte Soundtreiber
- Abschlusssequenz mit Mitwirkenden, Neustart und Rückkehr ins Hauptmenü

## Voraussetzungen

- Python 3.10 oder neuer empfohlen
- Pygame 2.5 oder neuer
- Für die Audiowiedergabe eine vom Betriebssystem unterstützte Audioausgabe

Die Anwendung verwendet nur die in `requirements.txt` aufgeführten Python-Abhängigkeiten.

## Start unter Linux

1. ZIP entpacken.
2. In das entpackte Verzeichnis wechseln.
3. Abhängigkeit installieren und das Spiel starten:

```bash
python3 -m pip install -r requirements.txt
python3 src/game.py
```

Alternativ kann das mitgelieferte Startskript verwendet werden:

```bash
chmod +x start.sh
./start.sh
```

Auf Debian-basierten Systemen kann Pygame auch über die Paketverwaltung installiert werden, sofern das Paket `python3-pygame` verfügbar ist.

## Start unter Windows

Python 3 installieren, Pygame in der verwendeten Python-Umgebung installieren und `Start-Windows.bat` doppelklicken. Alternativ in einer Eingabeaufforderung:

```bat
py -m pip install -r requirements.txt
py -3 src\game.py
```

## Steuerung

- **Linke Maustaste:** Gegenstände, Figuren, Untersuchungsstellen und Übergänge anklicken; Dialoge fortsetzen
- **Inventar:** Gegenstand auswählen und anschließend ein passendes Objekt oder eine passende Stelle anklicken
- **F11:** Vollbildmodus umschalten (sofern vom aktuellen System unterstützt)
- Die sichtbaren Maus-Symbole zeigen an, welche Art von Interaktion an einer Stelle möglich ist.

Einige Übergänge werden erst freigeschaltet, nachdem die erforderlichen Hinweise untersucht oder Rätsel gelöst wurden.

## Spielstände und Einstellungen

Unter Linux werden Einstellungen und Spielstand im Benutzerprofil gespeichert:

- `~/.config/reise-mittelpunkt-erde/settings.json`
- `~/.config/reise-mittelpunkt-erde/savegame.json`

Ein neues Spiel setzt den Rätsel- und Szenenfortschritt zurück. Wenn du einen Spielstand behalten möchtest, sichere die genannten Dateien vor einem Neustart.

## Projektstruktur

```text
Die-Reise-zum-Mittelpunkt-der-Erde-2.3.1-GitHub/
├── assets/             # Hintergründe, Figuren, Icons, Musik und Soundeffekte
├── src/
│   ├── game.py         # Spielcode
│   └── VERSION         # Versionsnummer
├── CHANGELOG.md        # Versionshistorie
├── RELEASE_NOTES_2.3.1.md
├── VERSION             # Versionsnummer
├── requirements.txt    # Python-Abhängigkeiten
├── start.sh            # Linux-Startskript
├── Start-Windows.bat   # Windows-Startskript
└── debian-control      # Debian-Paketmetadaten
```



Unter Linux lässt sich das Spiel aus dem Terminal starten, damit Python-Tracebacks sichtbar bleiben:

```bash
python3 src/game.py
```

## Projektstatus und Testhinweis

Die Veröffentlichung enthält den vollständigen Quellcode sowie die benötigten lokalen Grafik- und Audiodateien. Für diese Paketierung wurden Versionsangaben, Python-Syntax und Dateiinhalte geprüft. Ein vollständiger interaktiver Spieldurchlauf unter Linux und Windows wurde für diese ZIP-Erstellung nicht durchgeführt.

## Lizenz und Rechte

Diese ZIP enthält keine Open-Source-Lizenz. Die Veröffentlichung auf GitHub allein gewährt keine zusätzlichen Rechte zur Weiterverwendung, Änderung oder Weiterverbreitung. *Die Reise zum Mittelpunkt der Erde* ist ein eigenständiges Fan-/Abenteuerprojekt, frei inspiriert von Jules Vernes gemeinfreiem Roman; einzelne enthaltene Bibliotheken und Medien unterliegen ihren jeweiligen Lizenz- und Rechtebedingungen.
