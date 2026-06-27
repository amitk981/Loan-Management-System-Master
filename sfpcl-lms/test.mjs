import puppeteer from 'puppeteer';
const browser = await puppeteer.launch();
const page = await browser.newPage();
page.on('console', msg => console.log('PAGE LOG:', msg.text()));
page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
await page.goto('http://localhost:5173');
await new Promise(r => setTimeout(r, 2000));
await page.click('button'); // click the first button (which should be DM Finance login)
await new Promise(r => setTimeout(r, 2000));
await page.evaluate(() => {
  const links = Array.from(document.querySelectorAll('a'));
  const appraisalLink = links.find(a => a.textContent.includes('Appraisal'));
  if (appraisalLink) appraisalLink.click();
});
await new Promise(r => setTimeout(r, 2000));
await browser.close();
