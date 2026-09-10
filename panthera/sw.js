/* Service Worker fuer Panthera Fitness.
   Fassung 5e5046f072 — aendert sich bei jedem Bau, dadurch raeumt der Browser
   den alten Zwischenspeicher auf.

   Seitenaufrufe zuerst aus dem Netz, mit kurzem Zeitlimit und Rueckfall auf den
   Zwischenspeicher: online bekommt man immer den neuesten Stand, im Studio ohne
   Empfang oeffnet die App trotzdem. Alles andere zuerst aus dem Zwischenspeicher. */
const CACHE = "panthera-panthera-5e5046f072";
const SCHALE = ["./", "./index.html", "./manifest.webmanifest",
  "../icons/apple-touch-icon.png", "../icons/icon-192.png", "../icons/icon-512.png"];
const NETZ_ZEITLIMIT = 2500;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SCHALE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function mitZeitlimit(req) {
  return new Promise((loesen, ablehnen) => {
    const uhr = setTimeout(() => ablehnen(new Error("zeit")), NETZ_ZEITLIMIT);
    fetch(req).then((r) => { clearTimeout(uhr); loesen(r); }, (f) => { clearTimeout(uhr); ablehnen(f); });
  });
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const schriften = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";

  if (req.mode === "navigate") {
    e.respondWith(
      mitZeitlimit(req)
        .then((r) => {
          const kopie = r.clone();
          caches.open(CACHE).then((c) => c.put("./index.html", kopie));
          return r;
        })
        .catch(() => caches.match("./index.html").then((r) => r || caches.match("./")))
    );
    return;
  }

  if (url.origin === self.location.origin || schriften) {
    e.respondWith(
      caches.match(req).then((treffer) =>
        treffer ||
        fetch(req).then((r) => {
          // Schriften kommen undurchsichtig zurueck; sie lassen sich trotzdem ablegen.
          if (r && (r.ok || r.type === "opaque")) {
            const kopie = r.clone();
            caches.open(CACHE).then((c) => c.put(req, kopie));
          }
          return r;
        })
      )
    );
  }
});
