const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ICONS = {
  hp: `<path d="M20 55 L50 28 L80 55" />
       <path d="M28 48 L28 78 L72 78 L72 48" />
       <path d="M42 78 L42 60 L58 60 L58 78" />
       <path d="M50 50 L66 62 L61 64 L64 71 L58 74 L55 67 L50 71 Z" fill="currentColor" stroke="none"/>`,

  oshirase: `<path d="M22 46 L45 46 L68 30 L68 68 L45 52 L22 52 Z" />
             <path d="M45 46 L45 52" />
             <path d="M30 52 L30 66 Q30 72 36 72 L36 58" />
             <path d="M74 32 L74 48" />
             <path d="M66 40 L82 40" />`,

  jigane: `<ellipse cx="50" cy="70" rx="27" ry="9" />
           <path d="M23 70 L23 58" />
           <path d="M77 70 L77 58" />
           <ellipse cx="50" cy="58" rx="27" ry="9" />
           <path d="M23 58 L23 46" />
           <path d="M77 58 L77 46" />
           <ellipse cx="50" cy="46" rx="27" ry="9" />`,

  satei: `<path d="M32 20 L60 20 L70 30 L70 82 L32 82 Z" />
          <path d="M60 20 L60 30 L70 30" />
          <path d="M40 40 L58 40" />
          <path d="M40 50 L58 50" />
          <path d="M40 60 L50 60" />
          <circle cx="68" cy="72" r="15" fill="#e4e0d3" />
          <path d="M61 72 L66 78 L76 65" />`,

  hasso: `<path d="M22 42 L50 30 L78 42 L50 54 Z" />
          <path d="M22 42 L22 74 L50 86 L50 54" />
          <path d="M78 42 L78 74 L50 86" />
          <path d="M50 30 L50 54" />
          <path d="M36 36 L64 48" />
          <path d="M62 26 L82 18 L88 30 Z" />
          <path d="M74 22 L88 12" />
          <path d="M80 12 L88 12 L88 20" />`,

  gazo: `<path d="M24 40 L36 40 L42 32 L60 32 L66 40 L78 40 L78 68 L24 68 Z" />
         <circle cx="48" cy="54" r="11" />
         <circle cx="70" cy="70" r="12" />
         <path d="M79 79 L88 88" stroke-linecap="round"/>`,
};

const ITEMS = [
  { key: '01_hp', label: 'HP', subtitle: '公式サイトはこちら', icon: ICONS.hp, highlight: false },
  { key: '02_oshirase', label: 'お知らせ', subtitle: '最新情報をチェック', icon: ICONS.oshirase, highlight: false },
  { key: '03_jigane-souba', label: '地金相場', subtitle: '本日の買取価格', icon: ICONS.jigane, highlight: false },
  { key: '04_satei-irai-sho', label: '査定依頼書', subtitle: '宅配買取のお申込み', icon: ICONS.satei, highlight: false },
  { key: '05_hasso-houhou', label: '発送方法', subtitle: '梱包・送り方ガイド', icon: ICONS.hasso, highlight: false },
  { key: '06_gazo-satei', label: '画像査定', subtitle: 'メッセージ作成機能搭載', icon: ICONS.gazo, highlight: true },
];

const LAYOUTS = {
  large: {
    sizes: [[2500, 1686], [1200, 810], [800, 540]],
  },
  small: {
    sizes: [[2500, 843], [1200, 405], [800, 270]],
  },
};

function buildHtml(item, layout) {
  const isSmall = layout === 'small';
  const bg = item.highlight ? '#3c6b62' : '#e4e0d3';
  const borderCss = item.highlight
    ? 'box-shadow: inset 0 0 0 3.2vmin #dcb84c, inset 0 0 0 5.2vmin rgba(255,255,255,0.9);'
    : 'box-shadow: inset 0 0 0 0.35vmin #d3cdbc;';
  const arcColor = item.highlight ? 'rgba(255,255,255,0.85)' : '#a9a094';
  const iconColor = item.highlight ? '#ffffff' : '#948b7c';
  const labelColor = item.highlight ? '#ffffff' : '#6f6759';
  const subColor = item.highlight ? '#cfe3dc' : '#a49c8d';

  const iconSizeVmin = isSmall ? 22 : 16;
  const labelSizeVmin = isSmall ? 11 : 8.5;
  const subSizeVmin = isSmall ? 6.2 : 4.6;
  const arcWidthVmin = isSmall ? 26 : 20;

  const arcSvg = `
    <svg class="arc" viewBox="0 0 100 30" style="width:${arcWidthVmin}vmin;">
      <path d="M6 26 Q50 -4 94 26" fill="none" stroke="${arcColor}" stroke-width="2.6" stroke-linecap="round"/>
    </svg>`;

  const iconSvg = `
    <svg class="icon" viewBox="0 0 100 100" style="width:${iconSizeVmin}vmin;height:${iconSizeVmin}vmin;">
      <g fill="none" stroke="${iconColor}" stroke-width="4.2" stroke-linejoin="round" stroke-linecap="round">
        ${item.icon}
      </g>
    </svg>`;

  const bodyClass = isSmall ? 'row' : 'col';

  return `<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @font-face {
    font-family: 'NotoJP';
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:100%; overflow:hidden; }
  body {
    font-family: "IPAGothic", "IPAゴシック", "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif;
    background:${bg};
    ${borderCss}
    display:flex;
    align-items:center;
    justify-content:center;
  }
  .wrap { display:flex; align-items:center; justify-content:center; width:100%; height:100%; }
  .wrap.col { flex-direction:column; gap: 2.4vmin; }
  .wrap.row { flex-direction:row; gap: 6vmin; padding: 0 8vmin; }
  .arc { display:block; }
  .row .textblock { display:flex; flex-direction:column; align-items:flex-start; gap:1.6vmin; }
  .col .textblock { display:flex; flex-direction:column; align-items:center; gap:1.6vmin; }
  .label { font-weight:700; font-size:${labelSizeVmin}vmin; color:${labelColor}; letter-spacing:0.02em; line-height:1; white-space:nowrap; }
  .sub { font-weight:400; font-size:${subSizeVmin}vmin; color:${subColor}; letter-spacing:0.03em; line-height:1; white-space:nowrap; }
  .row .iconblock { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1vmin; }
</style>
</head>
<body>
  <div class="wrap ${bodyClass}">
    ${isSmall ? `
      <div class="iconblock">
        ${arcSvg}
        ${iconSvg}
      </div>
      <div class="textblock">
        <div class="label">${item.label}</div>
        <div class="sub">${item.subtitle}</div>
      </div>
    ` : `
      ${arcSvg}
      ${iconSvg}
      <div class="textblock">
        <div class="label">${item.label}</div>
        <div class="sub">${item.subtitle}</div>
      </div>
    `}
  </div>
</body></html>`;
}

async function main() {
  const outRoot = path.resolve(__dirname, 'out');
  fs.mkdirSync(path.join(outRoot, 'large'), { recursive: true });
  fs.mkdirSync(path.join(outRoot, 'small'), { recursive: true });

  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();

  for (const layoutName of Object.keys(LAYOUTS)) {
    for (const item of ITEMS) {
      const html = buildHtml(item, layoutName);
      for (const [w, h] of LAYOUTS[layoutName].sizes) {
        await page.setViewportSize({ width: w, height: h });
        await page.setContent(html, { waitUntil: 'networkidle' });
        const outPath = path.join(outRoot, layoutName, `${item.key}_${w}x${h}.png`);
        await page.screenshot({ path: outPath });
        console.log('wrote', outPath);
      }
    }
  }

  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
