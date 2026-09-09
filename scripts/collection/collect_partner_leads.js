/* ============================================================================
   Silverleaf lead collector — TATO directory + OpenStreetMap employer layer
   ----------------------------------------------------------------------------
   HOW TO RUN
     1. Open https://tatotz.org in a browser tab.
     2. Open DevTools (F12) -> Console.
     3. Paste this whole file, press Enter.
     4. Run:  await runAll()            // ~2-3 minutes
     5. Run:  download()                // saves tato_leads.tsv + osm_employers.tsv

   WHY IT RUNS IN THE BROWSER
     tatotz.org is same-origin only; fetching from the page avoids CORS.
     Overpass (OSM) allows cross-origin requests, so it works from here too.

   RE-RUN CADENCE
     TATO membership changes slowly. Quarterly is enough.
   ========================================================================== */

/* ---------- 1. Campus anchors -------------------------------------------- */
/* APPROXIMATE — neighbourhood centroids, not surveyed GPS pins.
   Replace with real coordinates from Silverleaf before using distances
   for anything that matters (transport banding, fee quotes).            */
const CAMPUS = {
  'Usa River':            [-3.3714, 36.8582],
  'Arusha City (Sakina)': [-3.3579, 36.6642],
  'Kijenge':              [-3.3701, 36.7123],
  'Ilboru':               [-3.3487, 36.6878],
  'Boma Ngombe':          [-3.3342, 37.1383],
};

/* ---------- 2. Locality gazetteer ---------------------------------------- */
/* TATO publishes free-text locations ("Sakina Kwa Idd", "Njiro Block D").
   This maps those strings to coordinates. Coordinates came from an
   Overpass query for place/boundary nodes in the Arusha-Kilimanjaro bbox.  */
const GAZ = {
  'usa river':[-3.3714,36.8582],'usariver':[-3.3714,36.8582],'leganga':[-3.3690,36.8480],
  'maji ya chai':[-3.3716,36.8972],'tengeru':[-3.3733,36.7860],'duluti':[-3.3790,36.8080],
  'kikatiti':[-3.3888,36.9452],'kingori':[-3.3792,37.0214],'momela':[-3.2500,36.8700],
  'ambureni':[-3.3690,36.8100],'kiserian':[-3.3900,36.7600],'kiseriani':[-3.3900,36.7600],
  'sakina':[-3.3579,36.6642],'kwa idd':[-3.3579,36.6642],'kwa iddi':[-3.3579,36.6642],
  'namnaga':[-3.3560,36.6600],'unga limited':[-3.3796,36.6741],'unga ltd':[-3.3796,36.6741],
  'ilboru':[-3.3487,36.6878],'sekei':[-3.3679,36.6986],'sanawari':[-3.3606,36.6950],
  'sokon':[-3.3583,36.7248],'oldadai':[-3.3563,36.7349],'kimandolu':[-3.3679,36.7161],
  'kijenge':[-3.3701,36.7123],'njiro':[-3.4250,36.7040],'themi':[-3.3864,36.7031],
  'lemara':[-3.4015,36.6974],'moshono':[-3.4135,36.7369],'baraa':[-3.3793,36.7377],
  'engutoto':[-3.4268,36.7095],'kaloleni':[-3.3658,36.6881],'levolosi':[-3.3718,36.6813],
  'ngarenaro':[-3.3690,36.6764],'sombetini':[-3.3851,36.6652],'osunyai':[-3.3900,36.6668],
  'mianzini':[-3.3623,36.6844],'muriet':[-3.4100,36.7300],'olasiti':[-3.4092,36.6527],
  'daraja mbili':[-3.3858,36.6910],'kilombero':[-3.4209,36.7207],'soweto':[-3.3780,36.6800],
  'philips':[-3.3640,36.6900],'burka':[-3.3800,36.6600],'ngulelo':[-3.3668,36.7270],
  'kisongo':[-3.3719,36.5720],'ngaramtoni':[-3.3140,36.6398],'oljoro':[-3.5890,36.6879],
  'terrat':[-3.4844,36.6852],'nduruma':[-3.4945,36.7997],'shangarai':[-3.3900,36.6500],
  'kiranyi':[-3.3950,36.6400],'mringa':[-3.3700,36.6900],'sokoine':[-3.3690,36.6830],
  'goliondoi':[-3.3690,36.6830],'boma road':[-3.3690,36.6860],'clock tower':[-3.3690,36.6830],
  'aicc':[-3.3660,36.6890],'pangani':[-3.3730,36.6810],'kanisa road':[-3.3700,36.6850],
  'station road':[-3.3670,36.6870],'india street':[-3.3700,36.6830],'nyerere':[-3.3720,36.6870],
  'arusha cbd':[-3.3696,36.6881],'arusha city':[-3.3696,36.6881],'arusha':[-3.3696,36.6881],
  'arumeru':[-3.3800,36.7800],'meru':[-3.3714,36.8582],
  "boma ng'ombe":[-3.3342,37.1383],'boma ngombe':[-3.3342,37.1383],'hai':[-3.3342,37.1383],
  'kia':[-3.4200,37.0700],'moshi':[-3.3487,37.3435],'himo':[-3.3800,37.5300],
  'shanty town':[-3.3400,37.3300],'kilimanjaro':[-3.3487,37.3435],
  'karatu':[-3.3400,35.6700],'mto wa mbu':[-3.3700,35.8500],'monduli':[-3.3000,36.4500],
  'dar es salaam':[-6.7924,39.2083],'dar':[-6.7924,39.2083],'zanzibar':[-6.1659,39.2026],
  'mwanza':[-2.5164,32.9175],'iringa':[-7.7700,35.6900],'dodoma':[-6.1630,35.7516],
  'nairobi':[-1.2864,36.8172],
};

/* ---------- 3. Helpers ---------------------------------------------------- */
const hav = (a,b) => { const R=6371,t=Math.PI/180;
  const dLa=(b[0]-a[0])*t, dLo=(b[1]-a[1])*t;
  const x=Math.sin(dLa/2)**2+Math.cos(a[0]*t)*Math.cos(b[0]*t)*Math.sin(dLo/2)**2;
  return 2*R*Math.asin(Math.sqrt(x)); };

/* Bands mirror Silverleaf's published school-transport pricing tiers,
   so a lead's band maps directly to what the bus would cost that family. */
const band = d => d==null?'unknown':d<=5?'0-5 km':d<=10?'6-10 km':d<=15?'11-15 km'
                 :d<=20?'16-20 km':d<=25?'21-25 km':d<=40?'26-40 km':'>40 km';

function locate(hay){ hay=(hay||'').toLowerCase(); let best=null,len=0;
  for(const k in GAZ) if(hay.includes(k) && k.length>len){best=k;len=k.length;}
  return best; }

function nearestCampus(pt){ let c=null,d=null;
  for(const k in CAMPUS){ const x=hav(pt,CAMPUS[k]); if(d===null||x<d){d=x;c=k;} }
  return {campus:c, km:d}; }

/* ---------- 4. TATO parsers ---------------------------------------------- */
/* TATO runs TWO record templates. Newer members use labelled prose
   ("NAME: ... ADDRESS: ... CONTACT: ..."); long-standing members use a
   structured field block ("Street Address / City/Town / Phone / Email").
   The second group is the one that matters most — it is where the large,
   established operators live — so both parsers are required.            */

const LABELS = ['NAME','ADDRESS','P.O.BOX','P.O. BOX','LOCATION','CONTACT','CONCTACT',
                'CONTACTS','EMAIL','E-MAIL','WEBSITE','WEB','PROFILE','PORTFOLIO',
                'Company Slogan','SLOGAN'];

function parseProse(txt, title){
  let t = txt.replace(/\u200b/g,'').replace(/\s+/g,' ').trim().replace(/\s*View Details\s*$/i,'');
  const rx = new RegExp('\\b('+LABELS.map(l=>l.replace(/[.]/g,'\\.')).join('|')+')\\s*:','gi');
  const hits=[...t.matchAll(rx)], f={};
  hits.forEach((h,i)=>{ const key=h[1].toUpperCase().replace(/[.\s]/g,'');
    const val=t.slice(h.index+h[0].length,(i+1<hits.length?hits[i+1].index:t.length)).trim();
    if(!f[key]) f[key]=val; });
  const pick=(...k)=>{for(const x of k) if(f[x]) return f[x]; return '';};
  return { name:(title||pick('NAME')||'').replace(/\u200b/g,'').trim(),
           pobox:pick('ADDRESS','POBOX'), loc:pick('LOCATION'),
           phone:pick('CONTACT','CONCTACT','CONTACTS'), email:pick('EMAIL'),
           website:pick('WEBSITE','WEB'), profile:pick('PROFILE','PORTFOLIO').slice(0,300) };
}

function parseFields(txt){
  const t=txt.replace(/\u200b/g,'').replace(/\s+/g,' ').trim();
  const L=['Street Address','City/Town','State/Region','Postal Code','Phone','Mobile',
           'Fax','Email','Website','Overview','Category','Tags'];
  const rx=new RegExp('('+L.join('|').replace(/\//g,'\\/')+')','g');
  const hits=[...t.matchAll(rx)], f={};
  hits.forEach((h,i)=>{ const v=t.slice(h.index+h[0].length,
      (i+1<hits.length?hits[i+1].index:t.length)).trim();
    if(f[h[1]]===undefined) f[h[1]]=v; });
  const em=(f['Email']||'').match(/[\w.+-]+@[\w.-]+\.\w+/g)||[];
  return { addr:[f['Street Address'],f['City/Town']].filter(x=>x&&x.length>1).join(', '),
           phone:((f['Phone']||'')+' '+(f['Mobile']||'')).trim().slice(0,60),
           email:em.join(' | '), website:(f['Website']||'').split(' ')[0],
           overview:(f['Overview']||'').slice(0,250) };
}

/* ---------- 5. TATO scrape ------------------------------------------------ */
const CATS = ['tour-operators','dmc-tour-operators','mountain-trekking-operators',
              'mainland-tour-operators','affiliate-members','ngo','financial-services',
              'automotives','airlines'];

async function scrapeCat(cat){
  const out=[];
  for(let p=1;p<=25;p++){
    const url = p===1 ? `https://tatotz.org/portfolio-cats/${cat}/`
                      : `https://tatotz.org/portfolio-cats/${cat}/page/${p}/`;
    const r = await fetch(url); if(!r.ok) break;
    const d = new DOMParser().parseFromString(await r.text(),'text/html');
    const arts=[...d.querySelectorAll('article')]; if(!arts.length) break;
    for(const a of arts){
      const link=a.querySelector('a[href*="/portfolio/"]');
      const h=a.querySelector('h1,h2,h3,h4,.post-title,.entry-title');
      const rec=parseProse(a.textContent, h?h.textContent:'');
      rec.url=link?link.href:''; rec.cat=cat;
      if(rec.name) out.push(rec);
    }
    if(arts.length<50) break;              // last page
  }
  return out;
}

/* Members whose archive card is thin get their detail page fetched.
   This is what rescues the big operators from the bottom of the list. */
async function enrich(records){
  const need = records.filter(r=>r.url && (!r.loc || !r.email));
  const CHUNK = 20;                        // politeness + avoids console timeouts
  for(let i=0;i<need.length;i+=CHUNK){
    await Promise.all(need.slice(i,i+CHUNK).map(async r=>{
      try{
        const q=await fetch(r.url); if(!q.ok) return;
        const d=new DOMParser().parseFromString(await q.text(),'text/html');
        const m=d.querySelector('.portfolio-content,.entry-content,article,main,#content')||d.body;
        const prose=parseProse(m.textContent, r.name);
        const flds=parseFields(m.textContent);
        r.legacy = (flds.addr||flds.email||flds.phone||flds.overview) ? 'Y' : '';
        if(!r.loc)     r.loc     = prose.loc || prose.pobox || flds.addr;
        if(!r.email)   r.email   = prose.email   || flds.email;
        if(!r.phone)   r.phone   = prose.phone   || flds.phone;
        if(!r.website) r.website = prose.website || flds.website;
        if(!r.profile) r.profile = prose.profile || flds.overview;
      }catch(e){}
    }));
  }
}

/* ---------- 6. Scoring ---------------------------------------------------- */
/* READ THIS BEFORE TRUSTING THE SCORE.
   It measures how ready a record is to be contacted, NOT how valuable the
   employer is. The variable that actually matters — how many payrolled local
   staff the company has — is not in any of these sources. Treat the score as
   a call-ordering hint; fill `size_check` from a phone call or LinkedIn
   before deciding who to prioritise.                                       */
function score(r){
  const key = locate((r.loc||'')+' | '+(r.pobox||''));
  const pt  = key ? GAZ[key] : null;
  const near = pt ? nearestCampus(pt) : {campus:null, km:null};
  const ph   = r.phone||'';
  const em   = (r.email||'').split(/[|,;\s]+/).filter(x=>/@/.test(x))[0]||'';
  const free = /@(gmail|yahoo|hotmail|outlook|live|icloud)\./i.test(em);
  const site = (r.website||'').replace(/^https?:\/\//i,'').split(/\s/)[0];
  const ncat = [...new Set((r.cat||'').split(','))].length;
  const p    = (r.profile||'').toLowerCase();

  let size = (ncat>=3?12:ncat===2?8:3)
           + (/\b(ltd|limited|company)\b/i.test(r.name)?8:0)
           + (/\bfleet|land ?cruiser|4x4|vehicles|team of|our team|our guides|our staff|employs\b/.test(p)?10:0)
           + ((p.match(/\b(19[7-9]\d|20[0-2]\d)\b/)||[])[0]?5:0);
  const d   = near.km;
  const geo = d===null?5:d<=5?25:d<=10?21:d<=15?17:d<=20?12:d<=25?8:d<=40?3:0;
  const loc = /\+?255/.test(ph)?20:0;      // local number => local payroll
  const con = (em?(free?7:12):0) + (site?8:0);
  const total = size+geo+loc+con;
  const outOfRange = d!==null && d>25;

  return { name:r.name.replace(/\s+/g,' ').trim(),
           tier: outOfRange?'X (out of range)':total>=70?'A':total>=58?'B':total>=45?'C':'D',
           score: total, campus: near.campus||'', km: d===null?'':+d.toFixed(1),
           band: band(d), locality: key||'', email: em, website: site,
           phone: ph.replace(/\s+/g,' ').slice(0,45),
           tato_cats: [...new Set((r.cat||'').split(','))].join(','),
           established: r.legacy||'', size_check:'',
           notes: d===null?'location not published by TATO - verify':'' };
}

/* ---------- 7. OSM employer layer ---------------------------------------- */
/* Complements TATO exactly: OSM has coordinates but almost no contacts;
   TATO has contacts but almost no coordinates.                            */
async function scrapeOSM(){
  const bbox='(-3.60,36.45,-3.25,37.30)';
  const q=`[out:json][timeout:60];
   (nwr["office"]["name"]${bbox};
    nwr["tourism"~"hotel|lodge|guest_house|resort|hostel"]["name"]${bbox};
    nwr["amenity"~"hospital|clinic|bank|university|college"]["name"]${bbox};);
   out center tags;`;
  const r=await fetch('https://overpass-api.de/api/interpreter',
    {method:'POST', body:'data='+encodeURIComponent(q),
     headers:{'Content-Type':'application/x-www-form-urlencoded'}});
  const j=await r.json();
  const KEEP=/hospital|university|college|bank|office:(company|government|ngo|it|telecommunication|financial|research|educational_institution)|tourism:hotel/;
  const NOISE=/^(staff room|canteen|main cafe|class hall|classes|new classes|stionaries|papa|nyangumi|hotel|indian restaurant|dispensery|hospital|cyber computer room|lecture hall)$/i;

  const rows=j.elements.map(e=>{ const t=e.tags||{};
    return { name:t.name,
      kind: t.office?('office:'+t.office) : t.tourism?('tourism:'+t.tourism) : ('amenity:'+t.amenity),
      lat:+((e.lat??e.center?.lat)||0).toFixed(5), lon:+((e.lon??e.center?.lon)||0).toFixed(5),
      phone:t.phone||t['contact:phone']||'', email:t.email||t['contact:email']||'',
      web:t.website||t['contact:website']||'' }; })
    .filter(x=>x.lat && x.name && KEEP.test(x.kind) && !NOISE.test(x.name.trim()));

  const seen=new Map();
  for(const p of rows){
    const near=nearestCampus([p.lat,p.lon]);
    if(near.km>25) continue;
    const k=p.name.toLowerCase().replace(/[^a-z0-9]/g,'')+'|'+p.kind;
    const rec={...p, campus:near.campus, km:+near.km.toFixed(1), band:band(near.km)};
    if(seen.has(k)){ const e=seen.get(k);
      e.phone=e.phone||rec.phone; e.email=e.email||rec.email; e.web=e.web||rec.web; }
    else seen.set(k,rec);
  }
  return [...seen.values()].sort((a,b)=>a.km-b.km);
}

/* ---------- 8. Orchestration --------------------------------------------- */
async function runAll(){
  const all=[];
  for(const c of CATS){ console.log('scraping',c); all.push(...await scrapeCat(c)); }

  const m=new Map();                       // dedupe, union the categories
  for(const r of all){
    const k=r.name.toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,40); if(!k) continue;
    if(m.has(k)){ const e=m.get(k); e.cat+=','+r.cat;
      e.loc=e.loc||r.loc; e.email=e.email||r.email; e.phone=e.phone||r.phone; }
    else m.set(k,{...r});
  }
  window.TATO=[...m.values()];
  console.log('unique TATO members:', window.TATO.length);

  console.log('enriching thin records from detail pages...');
  await enrich(window.TATO);

  window.LEADS = window.TATO.map(score).sort((a,b)=>b.score-a.score||a.name.localeCompare(b.name));
  console.log('scoring done. tiers:',
    window.LEADS.reduce((a,r)=>(a[r.tier]=(a[r.tier]||0)+1,a),{}));

  console.log('fetching OSM employer layer...');
  window.OSM = await scrapeOSM();
  console.log('OSM employers within 25 km:', window.OSM.length);
  return {tato: window.LEADS.length, osm: window.OSM.length};
}

/* ---------- 9. Export ----------------------------------------------------- */
function toTSV(rows, cols){
  return [cols.join('\t')].concat(rows.map(r =>
    cols.map(c => String(r[c] ?? '').replace(/[\t\n\r]/g,' ')).join('\t'))).join('\n');
}
function save(name, text){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([text],{type:'text/tab-separated-values'}));
  a.download=name; a.click();
}
function download(){
  save('tato_leads.tsv', toTSV(window.LEADS,
    ['name','tier','score','campus','km','band','locality','email','website','phone',
     'tato_cats','established','size_check','notes']));
  save('osm_employers.tsv', toTSV(window.OSM,
    ['name','kind','campus','km','band','phone','email','web']));
}

console.log('Loaded. Run:  await runAll()   then:  download()');
