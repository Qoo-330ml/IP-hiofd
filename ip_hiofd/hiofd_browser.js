const { chromium } = require('playwright');

async function run(ip) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://tool.hiofd.com/ip/', { waitUntil: 'domcontentloaded', timeout: 45000 });

  const get = async (sel) => ((await page.textContent(sel)) || '').trim();

  const myIp = await get('#myIp');

  // 用页面原生事件链路设置输入值并触发查询
  await page.click('#queryIp');
  await page.fill('#queryIp', ip);
  await page.dispatchEvent('#queryIp', 'input');
  await page.dispatchEvent('#queryIp', 'change');

  // 按钮点击 + 回车双保险
  await page.click('#queryBtn');
  await page.press('#queryIp', 'Enter');

  // 等待结果IP不再是“正在查询...”
  await page.waitForFunction(() => {
    const v = (document.querySelector('#resultIpAddress')?.textContent || '').trim();
    return v && v !== '正在查询...' && v !== '-';
  }, { timeout: 45000 });

  await page.waitForTimeout(1500);

  const result = {
    queryIp: ip,
    myIp,
    resultIp: await get('#resultIpAddress'),
    isp: await get('#resultIsp'),
    location: await get('#resultLocation'),
    district: await get('#resultDistrict'),
    street: await get('#resultStreet'),
  };

  console.log(JSON.stringify(result, null, 2));
  await browser.close();
}

const ip = process.argv[2] || '61.175.188.57';
run(ip).catch(err => {
  console.error('ERROR:', err.message);
  process.exit(1);
});
