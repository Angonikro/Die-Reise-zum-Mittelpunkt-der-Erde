# Changelog

## 2.3.1 — 2026-10-19
- Entfernt ausschließlich die sichtbaren Kapitelpräfixe „Punkt X von 6“ aus den Szenentiteln.
- Die eigentlichen Szenentitel bleiben erhalten.
- Rätsel, Klickbereiche, Dialoge, Grafiken, Musik und Übergänge wurden nicht absichtlich verändert.

# Änderungsprotokoll

## 2.3.0 — GitHub-Veröffentlichung
- Einheitliche Versionierung in Spiel, Projektdateien und Debian-Metadaten.
- README und Release-Notizen für eine eigenständige GitHub-Veröffentlichung vervollständigt.
- Hinweise zu Installation, Steuerung, Speicherständen, Fehlerberichten und Projektstruktur ergänzt.
- Cache-Dateien aus dem Quellarchiv entfernt; lokale Grafiken, Musik und Soundeffekte bleiben enthalten.
- Spielinhalt aus 2.2.113 übernommen; keine absichtlichen Änderungen an Rätseln, Klickbereichen oder Übergängen.

## Version 2.2.112
- Behoben: Untersuchungspunkte an der sicheren Küste verwenden beim Dialog den internen Rätselschlüssel; Klick auf die riesenhafte Gestalt verursacht keinen KeyError mehr.
- Keine Änderung an Rätseln, Klickbereichen oder Szenenübergängen.

## 2.2.110
- Paket-Fix: GitHub-ZIP und Debian-Paket werden aus demselben Quellstand gebaut.
- Fix: `meerfahrt_ende` ist beim Zeichnen der sicheren Küste als Szenenbild registriert; der KeyError beim Szenenwechsel wird verhindert.
- Übernimmt die Änderungen aus 2.2.109: größerer Klickbereich für den Übergang zu Punkt 6 und Kaminfeuer statt Wind in Fridrikssons Zimmer.

## 2.2.109
- Fix: Übergang von Punkt 5 zu Punkt 6 hat jetzt einen deutlich größeren, leichter anklickbaren Bereich (nach allen drei Beobachtungen).
- Ton in Fridrikssons Zimmer: Kaminfeuer statt Wind.

## 2.2.108
- Fix: verhindert Absturz beim Übergang von Punkt 5 zur sicheren Küste (fehlendes Szenenbild `meerfahrt_ende`).
- Die sichere Küste verwendet vorerst das vorhandene Bild der Untermeerfahrt; Rätsel und Übergang zu Punkt 6 bleiben erhalten.

## 2.2.105
- Axel in Punkt 5 um weitere 15 % vergrößert.
- Hans in Punkt 5 um weitere 10 % vergrößert.
- Professor Lidenbrock, Hintergrund und übrige Kapitel unverändert.

## 2.2.104
- Punkt 5: Axel, Professor Lidenbrock und Hans um rund 43 % gegenüber Version 2.2.103 vergrößert.
- Figuren auf dem Floß weiter auseinander positioniert und die Standlinie an die sichtbaren Floßstämme angepasst.

## 2.2.103
- Fehler behoben, durch den Punkt 5 nach dem Ablegen das Arbeitszimmer statt des Unterirdischen Meeres zeigte.
- Punkt-5-Hintergrund, Kapitelüberschrift und alle drei separaten Figuren werden korrekt gezeichnet.

## 2.2.102
- Punkt 4: Floßbau mit Holz-Ausrichtung, Rankenbindung und Auftriebsprüfung abgeschlossen.
- Punkt 5: Unterirdische Überfahrt mit Algenfeld, Kampf der Meerestiere und Strömungsrätsel integriert.
- Drei Spielfiguren werden auf dem Floß separat und verkleinert dargestellt.

## 2.2.101
- „Neues Spiel“ setzt jetzt sämtliche Rätsel- und Szenenfortschritte zurück, einschließlich der geöffneten Vermessungskiste in Stapi.
- Veralteter Fortschritt wird beim Start eines neuen Spiels durch einen frischen Spielstand ersetzt.

## 2.2.100
- Überflüssigen Hinweis „Dafür brauchst du keine Lupe“ beim Aufnehmen von Holz und Ranken entfernt.

## 2.2.99
- Holz und Ranken werden beim direkten Aufnehmen jeweils als eigene Gegenstände im Inventar angezeigt.
- Bereits gespeicherte Fundstände werden beim Laden ins Inventar übernommen.

## 2.2.98
- Holz und Ranken in Punkt 3 direkt mit der Hand aufnehmen; keine Lupe erforderlich.
- Fundstatus für Holz und Ranken wird im Spielstand gespeichert.
- Fuß-Hotspot für den freigeschalteten Abstieg in Punkt 1 an den rechten Szenenrand verschoben.

## 2.2.97
- Eigenständiges, figurenfreies Hintergrundbild für Punkt 4 (Floßlager) eingebaut.
- Der Übergang von Punkt 3 zum Floßlager wird erst nach Lösung des Ufer-Rätsels freigeschaltet.
- Rätsel in Punkt 4 bleiben für die nächste Ausbaustufe offen.

## 2.2.96
- Punkt 3: Wasserlinie, Küstenverlauf und Floßmaterial werden als echte Rätselhinweise gespeichert.
- Erst nach allen drei Untersuchungen wird die sichere Anlegestelle und der Übergang zu Punkt 4 freigeschaltet.
- Punkt 4: eigenes Floßlager auf figurenfreiem Hintergrund; Holz ordnen und Ranken festziehen, bis das Floß vorbereitet ist.
- Der Übergang von Punkt 1 zu Punkt 2 bleibt unverändert.

## 2.2.95
- Neuer figurenfreier Hintergrund für Punkt 3: Große Höhle und unterirdisches Meer.
- Übergang von Punkt 2 zum Meer wird nach Lösung des Gangrätsels freigeschaltet; der Übergang von Punkt 1 zu Punkt 2 bleibt unverändert.
- Gesprächs-Hotspots in Punkt 2 und 3 ergänzt/verkleinert.
- Punkt 3 erhält Ufer-Erkundungen und das vom Nutzer bereitgestellte Wassergeräusch wasser.mp3.

## 2.2.93
- Fix: Hans wird auch in Punkt 2 als separates Sprite angezeigt.
- Fix: Der Rückweg von Punkt 2 nach Punkt 1 wechselt beim Anklicken zuverlässig zurück.

## 2.2.92
- Neues figurenfreies Hintergrundbild für Punkt 2: Unterirdische Gänge.
- Axel, Lidenbrock und Hans bleiben separate Spielfiguren und werden nicht in den Hintergrund eingebrannt.

## 2.2.91
- Fix: Fußspuren/Weitergehen nach Punkt 2 erscheinen erst nach Gesprächen mit Lidenbrock und Hans sowie Untersuchung des dunklen Abstiegs.
- Fix: Klick auf den Fußspuren-Ausgang lässt Axel sichtbar zum rechten Übergang laufen, bevor die Szene wechselt.

## 2.2.90
- Fix: Bewegung läuft auch im Raum „Unterirdische Gänge“ weiter.
- Fix: Nach Gesprächen mit Lidenbrock und Hans sowie Untersuchung des Abstiegs läuft Axel sichtbar zum Übergang; erst bei Ankunft wechselt die Szene zu Punkt 2.
- Fußspuren-/Gehcursor bleibt der Hinweis für begehbare Übergänge.

## 2.2.89
- Klickbereich für Professor Lidenbrock weiter nach oben verschoben.
- Versionsangaben in Spiel, ZIP, README und DEB aktualisiert.
- Übergang und Fußspuren-Hotspot für Punkt 2 zur erneuten Prüfung vorbereitet.

## 2.2.88
- Eigenständiges, neu generiertes Hintergrundbild für Punkt 2 eingebunden (ohne UI).
- Klickbereich von Professor Lidenbrock weiter nach oben erweitert.
- Übergang von Punkt 1 zu Punkt 2 erfolgt nach einer Gehbewegung mit Fußschritten.
- Versionsnummern in Projektdateien, README und Changelog vereinheitlicht.

## 2.2.87
- Höhlenraum „Unterirdische Gänge“ wird als eigener Raum geladen und im Spielstand unterstützt.
- Klickflächen für Professor Lidenbrock und Hans in Punkt 1 nach oben erweitert.
- Beim bloßen Anklicken des Höhlenabstiegs wird die Seil-Lösung nicht mehr verraten.
- Punkt 2 enthält Untersuchungen zu Wasserlauf, Luftzug und Echo sowie drei Gangoptionen.

## 2.2.87
- Anklickbereich von Professor Lidenbrock und Hans in der Höhle nach oben erweitert.
- Kein ausdrücklicher Seil-Lösungshinweis beim bloßen Anklicken des Höhleneingangs.
- Punkt 2 „Unterirdische Gänge“ mit eigener Szene und Orientierungsrätsel ergänzt.

# Changelog

## Version 2.2.85
- Höhlenszene in Punkt 1 erweitert: Professor Lidenbrock und Hans können angesprochen werden.
- Neue Dialoge behandeln die vulkanischen Gesteinsschichten, das Echo und den Luftzug.
- Die Untersuchung des dunklen Abstiegs reagiert auf den Gesprächsfortschritt; die neuen Gesprächsflags werden im Spielstand gespeichert.
- Versionsnummer im Fenstertitel und in den Projekt-/Paketmetadaten auf 2.2.85 vereinheitlicht.
- Vorhandene Seil-, Krater- und frühere Rätselmechaniken bleiben unverändert.

## Version 2.2.84
- Grundlage: ursprünglicher Stand 2.2.81 mit korrigierter Sichtbarkeit von Hans nach dem Gespräch mit Fridriksson und dem Lösen seiner Frage.


## 2.2.106
- Punkt 6 ergänzt: fossile Küste, Mastodonten-Beobachtung, Saknussemms Zeichen und Vulkanschlot.
- Übergang von der sicheren Küste zu Punkt 6 und Abschluss am Stromboli ergänzt.

## 2.2.111
- Eigenständiger, figuren- und UI-freier Hintergrund für „Die sichere Küste“ (Punkt 5).
- Rätsel, Klickbereiche, Übergänge und sonstige Spiellogik unverändert.


### Version 2.2.113 – Spielabschluss

- Nach dem Vulkanausbruch erscheint ein eigener Abschlussbildschirm.
- Die Schlusssequenz nennt die Rückkehr nach Stromboli und das Überleben der drei Reisenden.
- Schaltflächen: Abspann und Mitwirkende, Neues Spiel und Hauptmenü.
- Bestehende Rätsel, Szenen und Klickbereiche bleiben unverändert.
