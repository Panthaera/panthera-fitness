"""Erzeugt die App-Symbole aus dem Logo.

Als Vorlage dient die 1024er-Rasterfassung, in der die Logoflaeche gruen und der
Hintergrund schwarz ist. Daraus wird eine Maske gewonnen, mit dem Cyan-Magenta-
Verlauf eingefaerbt und auf den Nachtgrund gesetzt.

Aufruf:  python make_icons.py [zielordner]
"""

import sys
from pathlib import Path

from PIL import Image

VORLAGE = Path(r"C:\Users\Panthera\Desktop\PantheraTV\Panther Silhouette im Neonrahmen.png")
GRUND = (7, 9, 15)
CYAN = (0, 194, 255)
MAGENTA = (255, 43, 176)

# Groessen: 180 fuer apple-touch-icon, 192 und 512 fuer das Manifest.
GROESSEN = {"apple-touch-icon.png": 180, "icon-192.png": 192, "icon-512.png": 512}
RAND = 0.11  # Anteil der Kantenlaenge, den das Symbol frei laesst


def maske(im: Image.Image) -> Image.Image:
    """Alpha aus der Gruenflaeche. In der Vorlage ist die Logoflaeche gruen,
    alles andere nahezu schwarz — die Differenz Gruen minus Rot trennt beides
    sauber, ohne dass ein Schwellwert von Hand gesetzt werden muss."""
    r, g, b = im.convert("RGB").split()
    return Image.eval(Image.merge("L", (g,)).point(lambda v: v), lambda v: v).point(
        lambda v: 255 if v > 90 else 0
    )


def verlauf(size: int) -> Image.Image:
    """Diagonaler Verlauf von Cyan nach Magenta, wie im Kopf der App."""
    g = Image.new("RGB", (size, size))
    px = g.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1)) if size > 1 else 0
            px[x, y] = tuple(round(CYAN[i] + (MAGENTA[i] - CYAN[i]) * t) for i in range(3))
    return g


def main() -> None:
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "icons"
    if not VORLAGE.exists():
        raise SystemExit(f"Vorlage nicht gefunden: {VORLAGE}")
    ziel.mkdir(parents=True, exist_ok=True)

    quelle = Image.open(VORLAGE)
    m = maske(quelle)
    # Auf den tatsaechlichen Umriss zuschneiden, damit der Rand unten stimmt.
    kasten = m.getbbox()
    m = m.crop(kasten)

    for name, size in GROESSEN.items():
        innen = round(size * (1 - 2 * RAND))
        mm = m.copy()
        mm.thumbnail((innen, innen), Image.LANCZOS)
        bild = Image.new("RGB", (size, size), GRUND)
        farbe = verlauf(size).crop((0, 0, mm.width, mm.height))
        bild.paste(farbe, ((size - mm.width) // 2, (size - mm.height) // 2), mm)
        bild.save(ziel / name)
        print(f"{name:22} {size}x{size}  {(ziel / name).stat().st_size:>6} Bytes")


if __name__ == "__main__":
    main()
