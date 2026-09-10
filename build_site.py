"""Baut aus app.html die fertige Website fuer GitHub Pages.

Eine Quelle, zwei Apps. Sie unterscheiden sich in vier Zeichenketten: Seitentitel,
Untertitel in der Kopfleiste, Beschriftung des Symbols auf dem Home-Bildschirm und
dem Namensraum im Browserspeicher. Der Namensraum ist der wichtigste davon — beide
Apps liegen auf derselben Domain, und der Browserspeicher gilt pro Domain.

Aufruf:  python build_site.py
Ergebnis: site/  (fertig zum Hochladen)
"""

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "app.html"
# Die Ausgabe liegt im Wurzelverzeichnis des Repositorys, damit GitHub Pages sie
# ohne Umweg ausliefert: .../panthera/ und .../addy/
SITE = HERE
ICONS = SITE / "icons"

GRUND = "#07090F"

# ordner, <title>, Untertitel, Home-Bildschirm, Speicher-Namensraum
VARIANTEN = [
    ("panthera", "Panthera Fitness", "Krafttraining", "Panthera", "panthera"),
    ("addy", "Panthera Fitness für Addy", "Krafttraining für Addy", "Addy", "addy"),
]

KOPF = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titel}</title>
<meta name="description" content="Trainingsplan und Satzaufzeichnung fürs Krafttraining.">
<meta name="theme-color" content="{grund}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="{home}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" sizes="180x180" href="../icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="../icons/icon-192.png">
<style>
:root {{ color-scheme: dark; }}
html {{ background: {grund}; }}
body {{ margin: 0; font: 14px system-ui, -apple-system, sans-serif; background: {grund}; }}
img {{ max-width: 100%; }}
[hidden] {{ display: none !important; }}
</style>
</head>
<body>
{inhalt}
<script>
// Service Worker anmelden. Schlaegt es fehl, laeuft die App trotzdem — nur ohne
// Offline-Betrieb. Deshalb ohne Fehlermeldung an den Nutzer.
if ("serviceWorker" in navigator) {{
  window.addEventListener("load", function () {{
    navigator.serviceWorker.register("sw.js").catch(function () {{}});
  }});
}}
</script>
</body>
</html>
"""

SW = """/* Service Worker fuer {titel}.
   Fassung {version} — aendert sich bei jedem Bau, dadurch raeumt der Browser
   den alten Zwischenspeicher auf.

   Seitenaufrufe zuerst aus dem Netz, mit kurzem Zeitlimit und Rueckfall auf den
   Zwischenspeicher: online bekommt man immer den neuesten Stand, im Studio ohne
   Empfang oeffnet die App trotzdem. Alles andere zuerst aus dem Zwischenspeicher. */
const CACHE = "panthera-{ns}-{version}";
const SCHALE = ["./", "./index.html", "./manifest.webmanifest",
  "../icons/apple-touch-icon.png", "../icons/icon-192.png", "../icons/icon-512.png"];
const NETZ_ZEITLIMIT = 2500;

self.addEventListener("install", (e) => {{
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SCHALE)).then(() => self.skipWaiting()));
}});

self.addEventListener("activate", (e) => {{
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});

function mitZeitlimit(req) {{
  return new Promise((loesen, ablehnen) => {{
    const uhr = setTimeout(() => ablehnen(new Error("zeit")), NETZ_ZEITLIMIT);
    fetch(req).then((r) => {{ clearTimeout(uhr); loesen(r); }}, (f) => {{ clearTimeout(uhr); ablehnen(f); }});
  }});
}}

self.addEventListener("fetch", (e) => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const schriften = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";

  if (req.mode === "navigate") {{
    e.respondWith(
      mitZeitlimit(req)
        .then((r) => {{
          const kopie = r.clone();
          caches.open(CACHE).then((c) => c.put("./index.html", kopie));
          return r;
        }})
        .catch(() => caches.match("./index.html").then((r) => r || caches.match("./")))
    );
    return;
  }}

  if (url.origin === self.location.origin || schriften) {{
    e.respondWith(
      caches.match(req).then((treffer) =>
        treffer ||
        fetch(req).then((r) => {{
          // Schriften kommen undurchsichtig zurueck; sie lassen sich trotzdem ablegen.
          if (r && (r.ok || r.type === "opaque")) {{
            const kopie = r.clone();
            caches.open(CACHE).then((c) => c.put(req, kopie));
          }}
          return r;
        }})
      )
    );
  }}
}});
"""

WEICHE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panthera Fitness</title>
<meta http-equiv="refresh" content="0; url=./panthera/">
<link rel="canonical" href="./panthera/">
<style>
:root{{color-scheme:dark}}
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
background:{grund};color:#E9F1FA;font:16px/1.5 system-ui,-apple-system,sans-serif}}
a{{color:#00C2FF}}
</style>
</head>
<body><p>Weiter zu <a href="./panthera/">Panthera Fitness</a>.</p></body>
</html>
"""


def ersetze(text: str, muster: str, neu: str, wo: str) -> str:
    """Genau ein Vorkommen ersetzen. Kein oder mehrere Treffer heisst: app.html
    hat sich geaendert und der Bau wuerde still etwas Falsches ausliefern."""
    neuer, n = re.subn(muster, lambda _: neu, text)
    if n != 1:
        sys.exit(f"{wo}: {n} Treffer statt genau einem — app.html hat sich geaendert")
    return neuer


def main() -> None:
    quelle = SRC.read_text(encoding="utf-8")
    version = hashlib.sha256(quelle.encode("utf-8")).hexdigest()[:10]

    if not ICONS.exists():
        sys.exit("site/icons fehlt — zuerst 'python make_icons.py' ausfuehren")

    for ordner, titel, untertitel, home, ns in VARIANTEN:
        t = quelle
        t = ersetze(t, r"<title>.*?</title>", "", "Seitentitel")  # Titel steht jetzt im Kopf
        t = ersetze(t, r'var UNTERTITEL="[^"]*";', f'var UNTERTITEL="{untertitel}";', "Untertitel")
        t = ersetze(t, r'var HOMETITEL="[^"]*";', f'var HOMETITEL="{home}";', "Home-Bildschirm")
        t = ersetze(t, r'var SPEICHER="[^"]*";', f'var SPEICHER="{ns}";', "Speicher-Namensraum")

        ziel = SITE / ordner
        ziel.mkdir(parents=True, exist_ok=True)
        (ziel / "index.html").write_text(
            KOPF.format(titel=titel, home=home, grund=GRUND, inhalt=t.strip()), encoding="utf-8"
        )
        (ziel / "sw.js").write_text(SW.format(titel=titel, ns=ns, version=version), encoding="utf-8")
        (ziel / "manifest.webmanifest").write_text(json.dumps({
            "name": titel,
            "short_name": home,
            "start_url": "./",
            "scope": "./",
            "display": "standalone",
            "orientation": "portrait",
            "background_color": GRUND,
            "theme_color": GRUND,
            "lang": "de",
            "icons": [
                {"src": "../icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "../icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                {"src": "../icons/icon-512.png", "sizes": "512x512", "type": "image/png",
                 "purpose": "maskable"},
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        groesse = (ziel / "index.html").stat().st_size
        print(f"{ordner+'/':12} {groesse:>7} Bytes  {titel}")

    (SITE / "index.html").write_text(WEICHE.format(grund=GRUND), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")  # sonst ignoriert Pages Dateien mit _
    print(f"Fassung {version} · {SITE}")


if __name__ == "__main__":
    main()
