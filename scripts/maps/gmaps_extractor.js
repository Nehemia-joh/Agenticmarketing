// Google Maps lookup extractor for the coordinator's browser rounds (scripts/maps/build_gmaps_round.py).
//
// Saved from the browser's localStorage on 13 October 2026 so the source lives in the repository. The functions run in the
// coordinator's own browser pane on google.com/maps; no other agent looks up on Google Maps.
//
// Install once (on a google.com tab), storing each function's source as a string:
//   localStorage.setItem('slfn', <source of slfn below>);  localStorage.setItem('slsync', <source of slsync below>);
//
// Use, one lookup per lead (the key is the lead's organisation ID):
//   navigate to https://www.google.com/maps/search/<query>/@-3.37,36.69,11z?hl=en   (Boma Ng'ombe leads: @-3.33,37.20,11z)
//   pane visible:  eval(localStorage.slfn)("<id>")    waits for the result itself (it uses timers)
//   pane hidden:   wait 6-10 s, then eval(localStorage.slsync)("<id>")   reads the page once; returns NOT READY when the page
//                  has not loaded (retry with a longer wait) and NO RESULTS (saved as []) when Maps finds nothing.
// Timers are throttled in a hidden pane, so slfn can time out there; keep the pane visible when possible.
//
// Results accumulate in localStorage.slres as {id: [listing, ...]}, up to 5 listings from a results list or one place page.
// Export them with:
//   JSON.stringify(Object.fromEntries(Object.entries(JSON.parse(localStorage.slres)).map(([k, v]) => [k, v.map(r =>
//     ({n: r.name, la: r.lat, lo: r.lon, c: r.cat || '', a: r.addr || '', i: r.info || '', w: r.web || '', p: r.phone || '',
//       u: r.url}))])))
// which is the --results input of build_gmaps_round.py. Clear between rounds with localStorage.removeItem('slres').

// slfn (asynchronous: waits up to 12 s for a results list or a place page)
(async (q) => {
  for (let i = 0; i < 24 && !/!3d-?[\d.]+!4d/.test(location.href) && !document.querySelector('[role=feed] a[href*="/maps/place/"]'); i++) await new Promise(r => setTimeout(r, 500));
  await new Promise(r => setTimeout(r, 900));
  const f = document.querySelector('[role=feed]');
  let res;
  if (f) {
    res = [...f.querySelectorAll('a[href*="/maps/place/"]')].slice(0, 5).map(a => { const m = a.href.match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/); let c = a.parentElement; for (let k = 0; k < 4 && c && c.innerText.split('\n').length < 3; k++) c = c.parentElement; return { name: a.getAttribute('aria-label'), lat: m && +m[1], lon: m && +m[2], info: (c ? c.innerText : '').split('\n').map(s => s.trim()).filter(Boolean).slice(1, 5).join(' | '), url: a.href.split('?')[0] }; });
  } else {
    const m = location.href.match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/); const M = document.querySelector('[role=main]');
    const g = s => (M && [...M.querySelectorAll(s)].map(b => (b.innerText || '').trim())[0] || '').replace(/^\W+/, '');
    res = [{ name: (document.querySelector('h1') || {}).innerText || '', lat: m && +m[1], lon: m && +m[2], cat: g('button[jsaction*="category"]'), addr: g('[data-item-id="address"]'), phone: g('[data-item-id^="phone"]'), web: (M && [...M.querySelectorAll('a[data-item-id="authority"]')].map(b => b.href)[0]) || '', url: location.href.split('?')[0].replace(/\/@[^/]+/, '') }];
  }
  const all = JSON.parse(localStorage.getItem('slres') || '{}'); all[q] = res; localStorage.setItem('slres', JSON.stringify(all));
  return q + ' => ' + res.map(r => (r.name || '?') + ' @' + r.lat + ',' + r.lon + ' ' + (r.cat || r.info || '') + (r.addr ? ' | ' + r.addr : '')).join(' || ');
})

// slsync (synchronous: reads the page once, for a hidden pane after an explicit wait)
((q) => {
  const f = document.querySelector('[role=feed]');
  let res;
  if (f && f.querySelector('a[href*="/maps/place/"]')) {
    res = [...f.querySelectorAll('a[href*="/maps/place/"]')].slice(0, 5).map(a => { const m = a.href.match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/); let c = a.parentElement; for (let k = 0; k < 4 && c && c.innerText.split('\n').length < 3; k++) c = c.parentElement; return { name: a.getAttribute('aria-label'), lat: m && +m[1], lon: m && +m[2], info: (c ? c.innerText : '').split('\n').map(s => s.trim()).filter(Boolean).slice(1, 5).join(' | '), url: a.href.split('?')[0] }; });
  } else {
    const m = location.href.match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/); const M = document.querySelector('[role=main]');
    if (!m) { if ((document.body.innerText || '').includes("Google Maps can't find")) { const all0 = JSON.parse(localStorage.getItem('slres') || '{}'); all0[q] = []; localStorage.setItem('slres', JSON.stringify(all0)); return q + ' => NO RESULTS'; } return q + ' => NOT READY'; }
    const g = s => (M && [...M.querySelectorAll(s)].map(b => (b.innerText || '').trim())[0] || '').replace(/^\W+/, '');
    res = [{ name: (document.querySelector('h1') || {}).innerText || '', lat: +m[1], lon: +m[2], cat: g('button[jsaction*="category"]'), addr: g('[data-item-id="address"]'), phone: g('[data-item-id^="phone"]'), web: (M && [...M.querySelectorAll('a[data-item-id="authority"]')].map(b => b.href)[0]) || '', url: location.href.split('?')[0].replace(/\/@[^/]+/, '') }];
  }
  const all = JSON.parse(localStorage.getItem('slres') || '{}'); all[q] = res; localStorage.setItem('slres', JSON.stringify(all));
  return q + ' => ' + res.map(r => (r.name || '?') + ' @' + r.lat + ',' + r.lon + ' ' + (r.cat || r.info || '') + (r.addr ? ' | ' + r.addr : '')).join(' || ');
})
