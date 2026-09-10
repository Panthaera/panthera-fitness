"""Setzt die Pfadangabe aus PantheraLOGO.svg in app.html ein.

Einmalig auszufuehren. Das Abtippen der Pfadangabe waere fehleranfaellig, und
die Datei liegt ausserhalb des Projekts. Der Platzhalter __LOGO_PATH__ in
app.html wird durch den echten Pfad ersetzt.

Aufruf:  python embed_logo.py [pfad-zur-svg]
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
APP = HERE / "app.html"
DEFAULT_SVG = Path(r"C:\Users\Panthera\Desktop\PantheraTV\PantheraLOGO.svg")
PLACEHOLDER = "__LOGO_PATH__"


def biggest_path(svg_text: str) -> str:
    """Nimmt die laengste Pfadangabe. Die Inkscape-Datei enthaelt neben dem
    Logo nur winzige Reste, der eigentliche Umriss ist mit Abstand der laengste."""
    paths = re.findall(r'\sd="([^"]+)"', svg_text)
    if not paths:
        raise SystemExit("keine Pfadangabe in der SVG gefunden")
    return max(paths, key=len)


def main() -> None:
    svg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SVG
    if not svg_path.exists():
        raise SystemExit(f"SVG nicht gefunden: {svg_path}")

    d = biggest_path(svg_path.read_text(encoding="utf-8"))
    html = APP.read_text(encoding="utf-8")

    if PLACEHOLDER not in html:
        raise SystemExit(f"Platzhalter {PLACEHOLDER} steht nicht mehr in app.html — schon eingesetzt?")

    APP.write_text(html.replace(PLACEHOLDER, d), encoding="utf-8")
    print(f"Pfad aus {svg_path.name} eingesetzt ({len(d)} Zeichen)")


if __name__ == "__main__":
    main()
