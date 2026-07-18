/* Service worker — Mes Recettes (PWA)
   Stratégie :
   - Shell même origine + CDN connus : stale-while-revalidate (ouverture instantanée + offline).
   - Navigation : network-first → fallback sur index.html en cache (app utilisable hors-ligne).
   - Firestore / Auth / Google : BYPASS total (réseau direct) — le SDK gère son propre offline.
   Mise à jour : skipWaiting AUTO (le nouveau SW s'active seul) + clients.claim + reload
   de la page sur controllerchange -> aucun appareil ne reste figé sur l'ancien code.
   Le bandeau « Recharger » reste comme filet (envoie {type:'SKIP_WAITING'}).
   ⚠️ Bumper CACHE_VERSION à chaque déploiement de contenu pour éviter un cache figé. */

const CACHE_VERSION = 'v67';
const PRECACHE = 'precache-' + CACHE_VERSION;
const RUNTIME = 'runtime-' + CACHE_VERSION;

// Même origine uniquement (un cross-origin qui échoue ferait planter tout addAll).
const PRECACHE_URLS = [
  './',
  './index.html',
  './styles.css',
  './icons.js',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon.svg',
  './icons/apple-touch-icon.png',
  './assets/forest-bg.jpg',
];

// CDN à mettre en cache pour le boot hors-ligne (polices, xlsx, SDK Firebase).
const CDN_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net', 'www.gstatic.com'];

// Endpoints dynamiques à NE JAMAIS intercepter (auth, firestore, app check…).
const BYPASS_HOSTS = [
  'firestore.googleapis.com',
  'firebaseinstallations.googleapis.com',
  'identitytoolkit.googleapis.com',
  'securetoken.googleapis.com',
  'oauth2.googleapis.com',
  'accounts.google.com',
  'apis.google.com',
  'content-firebaseappcheck.googleapis.com',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(PRECACHE).then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()) // activation auto : aucun client ne reste bloqué sur l'ancien code
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== PRECACHE && k !== RUNTIME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

function staleWhileRevalidate(request) {
  return caches.open(RUNTIME).then((cache) =>
    cache.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && (response.ok || response.type === 'opaque')) {
            cache.put(request, response.clone());
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
}

function networkFirst(request) {
  return fetch(request)
    .then((response) => {
      const copy = response.clone();
      caches.open(RUNTIME).then((cache) => cache.put(request, copy));
      return response;
    })
    .catch(() => caches.match(request).then((c) => c || caches.match('./index.html')));
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return; // jamais de cache sur les écritures

  const url = new URL(req.url);
  if (BYPASS_HOSTS.some((h) => url.hostname.endsWith(h))) return; // réseau direct

  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req));
    return;
  }

  const sameOrigin = url.origin === self.location.origin;
  if (sameOrigin || CDN_HOSTS.some((h) => url.hostname.endsWith(h))) {
    event.respondWith(staleWhileRevalidate(req));
  }
  // sinon : passthrough navigateur par défaut
});
