"""Lokaler Testserver fuer die gebaute Website, ohne Zwischenspeicher.

python -m http.server schickt keine Cache-Control-Kopfzeilen, dadurch kann der
Browser nach einem Neubau noch die alte Seite anzeigen. Dieser Server verbietet
das Zwischenspeichern ausdruecklich, damit ein Neuladen immer den frischen
Stand zeigt.

Aufruf:  python serve.py [Port]
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIST = Path(__file__).parent


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = partial(NoCacheHandler, directory=str(DIST))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"http://localhost:{port}  ->  {DIST}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
