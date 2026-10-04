// Render thumbnail HTML pages to PNG at 800x450 (then converted to WebP).
// Usage: node render.js <dir with jobs.json>
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

(async () => {
  const dir = process.argv[2];
  const jobs = JSON.parse(fs.readFileSync(path.join(dir, 'jobs.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 800, height: 450 } });
  for (const j of jobs) {
    await page.goto('file://' + path.resolve(j.html));
    await page.waitForTimeout(50);
    await page.screenshot({ path: path.join(dir, j.name + '.png') });
  }
  await browser.close();
  console.log('rendered', jobs.length);
})();
