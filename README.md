# Panthera Fitness

Trainings-App fürs Krafttraining. Läuft im Browser, lässt sich auf dem iPhone
über „Zum Home-Bildschirm" ablegen und arbeitet danach ohne Netz.

Zwei Ausgaben aus einer Quelle:

| Adresse      | für   | Speicher-Namensraum |
|--------------|-------|---------------------|
| `/panthera/` | Chris | `kraft.panthera.*`  |
| `/addy/`     | Addy  | `kraft.addy.*`      |

Beide liegen auf derselben Domain. Weil der Browserspeicher pro Domain gilt und
nicht pro Pfad, trennt der Namensraum die Daten — sonst würden sich die Apps
gegenseitig überschreiben, sobald jemand beide Adressen im selben Browser öffnet.

## Was die App kann

Trainingstage mit Übungen, Sätzen, Wiederholungszielen und RIR. Beim Training
führt sie Übung für Übung durch und nimmt Wiederholungen und Gewicht auf, mit
den Werten der letzten Einheit als Vorbelegung.

Je Übung eine Ausrüstungsart: Langhantel, Kurzhantel, Gerät oder Körpergewicht.
Bei der Langhantel wird nur das Scheibengewicht eingetragen, das Stangengewicht
steht einmal an der Übung; die App rechnet die Gesamtlast und die Belegung je
Seite aus. Bei der Kurzhantel gilt die Zahl, die auf der Hantel steht.

Zu jeder Übung bis zu zwei Bilder zur Ausführung. Sie liegen verkleinert in
einer IndexedDB und bleiben auf dem Gerät, auf dem sie aufgenommen wurden.

Mehrere Personen je Ausgabe, jede mit eigenem Plan, Verlauf und eigenen Bildern.

## Daten

Alles bleibt im Browser des jeweiligen Geräts. Kein Server, kein Konto, keine
Übertragung. Über „Übergeben" lässt sich der Plan als Text weitergeben — der
Verlauf des Empfängers bleibt dabei erhalten, Bilder wandern nicht mit.

## Bauen

```
python make_icons.py     # Symbole aus dem Logo, nur nötig wenn sich das Logo ändert
python build_site.py     # erzeugt index.html, panthera/, addy/
python serve.py          # lokaler Testserver auf http://localhost:8765
```

Geändert wird ausschließlich `app.html`. `build_site.py` erzeugt daraus beide
Ausgaben und ersetzt dabei genau vier Zeichenketten: Seitentitel, Untertitel in
der Kopfleiste, Beschriftung des Symbols auf dem Home-Bildschirm und den
Speicher-Namensraum. Findet es eine dieser Stellen nicht genau einmal, bricht es
ab, statt still etwas Falsches auszuliefern.

`app.html` beginnt ohne `<!doctype>` und ohne `<head>` — beides setzt
`build_site.py`. Der Grund ist die Vorgeschichte: dieselbe Datei ließ sich so
auch als Claude-Artifact veröffentlichen.

Nach jedem `build_site.py` ändert sich die Fassungsnummer im Service Worker.
Dadurch räumt der Browser beim nächsten Besuch den alten Zwischenspeicher auf.

## Herkunft

Der Ausgangsplan stammt aus `Ganzkoerpertraining_Evidenzbasiert.pptx`: zwei
Ganzkörpereinheiten im Wechsel, zehn Übungen mit Sätzen, Wiederholungsbereichen,
Zielmuskulatur und je vier Ausführungshinweisen.

Das Logo kommt aus `PantheraLOGO.svg`, eingesetzt von `embed_logo.py`. Die
Symbole erzeugt `make_icons.py` aus der Rasterfassung des Logos.
