const CACHE_NAME = 'proxima8-v21';
const LEVEL_CACHE = 'proxima8-levels-v1';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './level_manifest.json',
  './assets/icon-192.png',
  './assets/icon-512.png',
  'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js'
];

// Force immediate activation
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Clear out old caches and trigger warm-up
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      caches.keys().then((keys) => {
        return Promise.all(
          keys.map((key) => {
            if (key !== CACHE_NAME && key !== LEVEL_CACHE) {
              return caches.delete(key);
            }
          })
        );
      }),
      self.clients.claim(),
      triggerWarmUp()
    ])
  );
});

async function triggerWarmUp() {
  try {
    const cache = await caches.open(LEVEL_CACHE);
    const manifestReq = new Request('level_manifest.json');
    
    // Fetch manifest for warmup
    const response = await fetch(manifestReq);
    if (!response.ok) return;
    
    const levels = await response.json();
    const total = levels.length;
    let current = 0;

    // Initial report
    reportProgress(0, total);

    for (const level of levels) {
       const req = new Request(`levels/${level.id}.json`);
       const cached = await cache.match(req);
       
       if (!cached) {
           try {
               await cache.add(req);
           } catch(e) { 
               console.warn('Failed to cache level', level.id, e); 
           }
       }
       current++;
       if (current % 5 === 0 || current === total) {
           reportProgress(current, total);
       }
    }
  } catch (e) {
    console.error('Warmup failed', e);
  }
}

async function reportProgress(current, total) {
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
        client.postMessage({
            type: 'CACHE_PROGRESS',
            current,
            total
        });
    });
}

self.addEventListener('fetch', (event) => {
    // Stale-While-Revalidate Strategy for levels and assets
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }

                let targetCache = CACHE_NAME;
                const url = event.request.url;
                if (url.includes('/levels/') || url.includes('level_manifest.json')) {
                    targetCache = LEVEL_CACHE;
                }
                
                const responseToCache = networkResponse.clone();
                caches.open(targetCache).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return networkResponse;
            }).catch(() => {
                // Return cached if network fails
            });

            return cachedResponse || fetchPromise;
        })
    );
});
