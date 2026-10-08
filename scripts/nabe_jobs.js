// Read every job on NABE's EconJobs board (https://econjobs.nabe.com/jobs/) in the built-in browser.
// NABE's site blocks scripts, so econ-industry-scan runs this with the browser's javascript tool
// on that page, saves the result as nabe_jobs.json, and passes it to industry_scan.py --board-file.
// Read-only: it only reads the listing and turns its pages (the site's own searchJobs()).
async function nabeJobs(maxPages = 10) {
  const grab = () => [...document.querySelectorAll('.job-tile')].map(t => {
    const id = (t.className.match(/job-tile-(\d+)/) || [])[1];
    const a = t.querySelector('.job-title a');
    if (!id || !a) return null;
    const box = t.querySelector('.job-main-data, .job-details') || t;
    const lines = box.innerText.split('\n').map(s => s.trim()).filter(s => s && s !== 'Preferred' && s.length > 1);
    return {id: 'NABE-' + id, url: a.href, title: a.innerText.trim(), employer: lines[1] || '',
            location: lines.slice(2).filter(s => !/ago$/.test(s)).join(' '),
            posted: lines.find(s => /ago$/.test(s)) || '', source: 'NABE'};
  }).filter(Boolean);
  let out = grab();
  for (let p = 2; p <= maxPages && typeof searchJobs === 'function'; p++) {
    const before = out.length;
    searchJobs(p, true);
    await new Promise(r => setTimeout(r, 4000));
    const seen = new Set(out.map(x => x.id));
    out = out.concat(grab().filter(x => !seen.has(x.id)));
    if (out.length === before) break;
  }
  return out;
}
await nabeJobs();
