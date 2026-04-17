/* sw.js — PYL0N Suite Service Worker
   Strategy:
   - HTML navigations → Network-first (always fresh from server; cache as
     offline fallback only). This prevents Safari WebKitInternal:0 errors and
     avoids serving stale content after deployments.
   - Static assets (scripts, libs, fonts, images) → Cache-first (fast repeat
     loads; only hits the network on a miss).
   All fetches use redirect:'follow' so the SW never hands a redirect
   response to the browser (Safari refuses those with WebKitInternal:0).
*/

const CACHE_NAME = 'pyl0n-v3';

const PRECACHE_ASSETS = [
  /* ── Brand assets ───────────────────────────────────────────────── */
  './favicon.svg',
  './logo.svg',

  /* ── Vendor scripts ─────────────────────────────────────────────── */
  './vendor/pyl0n-native.js',
  './vendor/pyl0n-suite.js',
  './vendor/pyl0n-state.js',
  './vendor/pyl0n-validate.js',

  /* ── Local libraries ────────────────────────────────────────────── */
  './libs/chart.js',
  './libs/xlsx.full.min.js',
  './libs/html2pdf.bundle.min.js',
  './libs/html2canvas.min.js',
];

/* HTML pages — fetched network-first at runtime, cached as offline fallback */
const HTML_PAGES = [
  './index.html',
  './timecast.html',
  './resourcecast.html',
  './orgcast.html',
  './rfqcast.html',
  './dorcast.html',
  './riskcast.html',
  './calccast.html',
  './lettercast.html',
  './cashflow.html',
  './w2w-report.html',
  './cvcast.html',
];

/* ── Install: pre-cache stable assets + seed HTML pages ─────────────── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      const all = [...PRECACHE_ASSETS, ...HTML_PAGES];
      return Promise.allSettled(
        all.map(url =>
          // redirect:'follow' prevents storing a redirect response in cache
          fetch(url, { redirect: 'follow' })
            .then(res => {
              if (res.ok) return cache.put(url, res);
              console.warn('PYL0N SW: non-ok response for', url, res.status);
            })
            .catch(err => console.warn('PYL0N SW: could not pre-cache', url, err.message))
        )
      );
    }).then(() => self.skipWaiting())
  );
});

/* ── Activate: delete stale caches from previous versions ───────────── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys =>
        Promise.all(
          keys
            .filter(k => k !== CACHE_NAME)
            .map(k => {
              console.log('PYL0N SW: deleting old cache', k);
              return caches.delete(k);
            })
        )
      )
      .then(() => self.clients.claim())
  );
});

/* ── Fetch ───────────────────────────────────────────────────────────── */
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isNavigation = event.request.mode === 'navigate';

  // ── HTML navigations: Network-first ──────────────────────────────────
  // Always try the server so users get the latest version of the app.
  // Fall back to the cached .html file only when offline.
  if (isNavigation) {
    event.respondWith(
      fetch(event.request, { redirect: 'follow' })
        .then(response => {
          if (!response.ok) return response; // pass through 4xx/5xx
          // Cache the fresh response for offline use
          const clone = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
          return response;
        })
        .catch(async () => {
          // Offline: try the exact URL, then the .html variant, then index
          const exact = await caches.match(event.request);
          if (exact) return exact;

          // Cloudflare / Azure may serve /timecast (no extension).
          // Try the .html variant we pre-cached.
          if (!url.pathname.includes('.')) {
            const htmlUrl = url.origin + url.pathname + '.html';
            const htmlCached = await caches.match(htmlUrl);
            if (htmlCached) return htmlCached;
          }

          return caches.match('./index.html');
        })
    );
    return;
  }

  // ── Static assets: Cache-first ───────────────────────────────────────
  // Scripts, libs, fonts, images — stable and large; serve from cache.
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;

      return fetch(event.request, { redirect: 'follow' }).then(response => {
        if (
          !response ||
          response.status !== 200 ||
          response.type === 'opaque' ||
          response.type === 'opaqueredirect'
        ) {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
        return response;
      });
    })
  );
});
