(function(){
'use strict';
const $app = document.getElementById('app');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const store = {
  get(k, d){ try{ const v = localStorage.getItem('gemguide:'+k); return v == null ? d : JSON.parse(v); }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem('gemguide:'+k, JSON.stringify(v)); }catch(e){} }
};
const byId = Object.fromEntries(GEMS.map(g => [g.id, g]));
const GROUP_ORDER = ['コランダム','ベリル','クリソベリル','トパーズ','トルマリン','ガーネット','スピネル','オリビン','ゾイサイト','スフェーン','ヒスイ','オパール','有機質','ダイヤモンド'];
const COLOR_CHIPS = [['赤','#C0213A'],['ピンク','#E57AA4'],['オレンジ','#E8792B'],['黄','#D8B636'],['緑','#2E8B57'],['青','#2B57B5'],['紫','#7B4FB0'],['茶','#8A5A33'],['無色','#E8EEF2'],['遊色','linear-gradient(90deg,#e5484d,#f0b429,#30a46c,#3e63dd)']];

/* ---------- theme ---------- */
(function(){
  const t = store.get('theme', null);
  if (t) document.documentElement.setAttribute('data-theme', t);
  document.getElementById('themeBtn').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme')
      || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    store.set('theme', next);
  });
})();

/* ---------- gem icon ---------- */
let gid = 0;
function gemIcon(g){
  const id = 'g' + (++gid);
  const c = g.sw, c2 = g.sw2 || g.sw;
  if (g.cut === 'opal'){
    return `<svg class="gemicon" viewBox="0 0 48 48" aria-hidden="true"><defs><clipPath id="${id}"><ellipse cx="24" cy="24" rx="20" ry="16"/></clipPath>
    <radialGradient id="${id}h" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
    <g clip-path="url(#${id})"><rect width="48" height="48" fill="${c}"/>
    <circle cx="14" cy="20" r="7" fill="#e5484d" opacity=".8"/><circle cx="27" cy="15" r="6" fill="#30a46c" opacity=".8"/><circle cx="33" cy="28" r="7" fill="#3e63dd" opacity=".8"/><circle cx="20" cy="32" r="6" fill="#f0b429" opacity=".75"/><circle cx="38" cy="18" r="4" fill="#12a594" opacity=".8"/>
    <rect width="48" height="48" fill="url(#${id}h)"/></g><ellipse cx="24" cy="24" rx="20" ry="16" fill="none" stroke="#000" stroke-opacity=".2"/></svg>`;
  }
  if (g.cut === 'cab'){
    return `<svg class="gemicon" viewBox="0 0 48 48" aria-hidden="true"><defs>
    <radialGradient id="${id}" cx=".38" cy=".32" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".25" stop-color="${c}" stop-opacity="1"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient></defs>
    <ellipse cx="24" cy="24" rx="20" ry="16" fill="${c}"/><ellipse cx="24" cy="24" rx="20" ry="16" fill="url(#${id})"/>
    ${g.id==='cateye'?'<path d="M24 8.5c1.2 5 1.2 26 0 31" stroke="#fff" stroke-opacity=".85" stroke-width="1.6" fill="none"/>':''}
    ${g.id==='sapphirecab'||g.id==='rubycab'?'<g stroke="#fff" stroke-opacity=".55" stroke-width=".9"><path d="M24 12v24M14 18l20 12M14 30l20-12"/></g>':''}
    <ellipse cx="24" cy="24" rx="20" ry="16" fill="none" stroke="#000" stroke-opacity=".2"/></svg>`;
  }
  // facet: round brilliant, top view
  const P = (r, n, off) => Array.from({length:n}, (_, i) => { const a = (i/n)*Math.PI*2 + off; return [24 + r*Math.cos(a), 24 + r*Math.sin(a)]; });
  const o = P(21, 8, Math.PI/8), t = P(10.5, 8, 0);
  let facets = '';
  for (let i = 0; i < 8; i++){
    const a = o[i], b = o[(i+1)%8], ti = t[(i+1)%8];
    const op = [0.28,0.08,0.18,0.02,0.24,0.12,0.30,0.05][i];
    const tone = i%2 ? '#000' : '#fff';
    facets += `<polygon points="${a} ${b} ${ti}" fill="${tone}" fill-opacity="${op}"/>`;
    const t1 = t[i], t2 = t[(i+1)%8];
    facets += `<polygon points="${a} ${t1} ${t2}" fill="${i%2?'#fff':'#000'}" fill-opacity="${[0.1,0.22,0.06,0.3,0.12,0.2,0.04,0.26][i]}"/>`;
  }
  const fill = g.sw2 ? `url(#${id})` : c;
  const grad = g.sw2 ? `<defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset=".45" stop-color="${c}"/><stop offset=".55" stop-color="${c2}"/></linearGradient></defs>` : '';
  return `<svg class="gemicon" viewBox="0 0 48 48" aria-hidden="true">${grad}<polygon points="${o.join(' ')}" fill="${fill}"/>${facets}
    <polygon points="${t.join(' ')}" fill="#fff" fill-opacity=".14" stroke="#fff" stroke-opacity=".35" stroke-width=".6"/>
    <polygon points="${o.join(' ')}" fill="none" stroke="#000" stroke-opacity=".25" stroke-width=".8"/></svg>`;
}

const kindTag = k => `<span class="kind ${k}">${esc(KIND[k].label)}</span>`;
const impTag = l => `<span class="imp" data-l="${l}" title="価値への影響"><i></i><i></i><i></i>${esc(IMPACT[l])}</span>`;

/* ---------- list ---------- */
let listState = store.get('list', {q:'', color:''});
function viewList(){
  const q = listState.q.trim().toLowerCase();
  const hits = GEMS.filter(g => {
    if (listState.color && !g.colors.includes(listState.color)) return false;
    if (!q) return true;
    const hay = [g.ja, g.en, g.group, g.similar, g.key, g.incl, ...(g.origin||[]).flat(), ...(g.treat||[]).map(t=>t.n)].join(' ').toLowerCase();
    return hay.includes(q);
  });
  const groups = GROUP_ORDER.map(gr => [gr, hits.filter(g => g.group === gr)]).filter(x => x[1].length);
  $app.innerHTML = `<section class="view">
    <label class="search" for="q"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg>
      <input id="q" type="search" placeholder="名前・産地・処理・類似石で検索" value="${esc(listState.q)}" autocomplete="off"></label>
    <div class="chips" role="group" aria-label="色で絞り込み">
      <button class="chip" type="button" data-color="" aria-pressed="${!listState.color}">すべて</button>
      ${COLOR_CHIPS.map(([c,v]) => `<button class="chip" type="button" data-color="${c}" aria-pressed="${listState.color===c}"><span class="dot" style="background:${v}"></span>${c}</button>`).join('')}
    </div>
    <div class="count">${hits.length} 種</div>
    ${hits.length ? `<div class="list">${groups.map(([gr, gs]) => `<div class="groupHead">${esc(gr)}</div>` + gs.map(g => `
      <a class="row" href="#g-${g.id}">${gemIcon(g)}
        <div><div class="name">${esc(g.ja)}</div><div class="sub">${esc(g.key)}</div></div>
        <div class="meta">硬度<b>${esc(g.h)}</b>RI<b>${esc(fmtRi(g))}</b></div>
      </a>`).join('')).join('')}</div>` : `<div class="empty">該当する宝石がありません。検索語を短くするか、色の絞り込みを外してください。</div>`}
    <p class="foot">出典：社内シート「★熊★」（宝石について①〜③、案件トーク、査定手順、値段まとめ）。不足分はGIA・AGL・CGLなど鑑別機関の公開情報で補足。</p>
  </section>`;
  const qi = document.getElementById('q');
  qi.addEventListener('input', () => { listState.q = qi.value; store.set('list', listState); rerenderListKeepFocus(); });
  $app.querySelectorAll('[data-color]').forEach(b => b.addEventListener('click', () => { listState.color = b.dataset.color; store.set('list', listState); viewList(); }));
}
function rerenderListKeepFocus(){
  const pos = document.getElementById('q').selectionStart;
  viewList();
  const qi = document.getElementById('q'); qi.focus(); try{ qi.setSelectionRange(pos, pos); }catch(e){}
}
const fmtRi = g => g.ri[0] === g.ri[1] ? String(g.ri[0]) : `${g.ri[0].toFixed(3)}–${g.ri[1].toFixed(3)}`;

/* ---------- detail ---------- */
function viewGem(g){
  let n = 0; const sec = (title, body) => `<div class="card"><h2><span class="n">${String(++n).padStart(2,'0')}</span>${title}</h2>${body}</div>`;
  const grade = g.grade && GRADES[g.grade];
  $app.innerHTML = `<section class="view">
    <a class="back" href="#gems">← 図鑑に戻る</a>
    <div class="hero">${gemIcon(g)}<div>
      <h1>${esc(g.ja)}</h1><div class="en">${esc(g.en)}</div>
      <span class="tag">${esc(g.group)}</span> ${g.added?'<span class="tag add">鑑別機関情報で追加</span>':''}
    </div></div>
    <div class="keyline"><span class="eyebrow">まず覚える</span>${esc(g.key)}</div>
    <dl class="spec">
      <div><dt>モース硬度</dt><dd class="mono">${esc(g.h)}</dd></div>
      <div><dt>比重</dt><dd class="mono">${esc(g.sg)}</dd></div>
      <div><dt>複屈折量</dt><dd class="mono">${esc(g.bi)}</dd></div>
      <div class="wide"><dt>屈折率（RI）</dt><dd><span class="mono">${esc(g.riText)}</span>　<span class="muted">${esc(g.optic)}</span></dd></div>
      <div class="wide"><dt>UVライト反応</dt><dd>${esc(g.uv)}</dd></div>
      <div class="wide"><dt>チェルシーフィルター</dt><dd>${esc(g.cf)}</dd></div>
      <div class="wide"><dt>白熱灯カラーチェンジ</dt><dd>${esc(g.cc)}</dd></div>
    </dl>
    ${sec('価値を決めるポイント', `<ul>${g.value.map(v=>`<li>${esc(v)}</li>`).join('')}</ul>`)}
    ${sec('判別の注意点（天然・合成・類似石）', `<ul>${g.check.map(v=>`<li>${esc(v)}</li>`).join('')}</ul>
      <dl class="kv"><dt>天然の内包物</dt><dd>${esc(g.incl)}</dd><dt>類似石</dt><dd>${esc(g.similar)}</dd></dl>
      ${g.fluo ? `<div class="eyebrow" style="margin-top:4px">色別の蛍光（シート②）</div><div class="tbl"><table><thead><tr><th>色</th><th>蛍光</th><th>蛍光色</th><th>備考</th></tr></thead><tbody>${g.fluo.map(r=>`<tr>${r.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:''}`)}
    ${sec('処理の種類と価値への影響', g.treat.map(t => `<div class="tr"><div class="h"><span class="nm">${esc(t.n)}</span>${kindTag(t.k)}${t.k!=='N'?impTag(t.imp):''}</div>${t.note?`<div class="note">${esc(t.note)}</div>`:''}</div>`).join('')
      + (g.treatNote ? `<p class="note-s">${esc(g.treatNote)}</p>` : '') + `<p class="note-s"><a href="#treat">処理の種類をまとめて見る →</a></p>`)}
    ${sec('産地と特徴', `<div class="origin">${g.origin.map(([a,b])=>`<div><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join('')}</div>`)}
    ${(g.price.length || g.idx) ? sec('相場感（1ctあたり）', `
      ${g.price.length ? `<div class="tbl"><table><tbody>${g.price.map(([a,b])=>`<tr><td>${esc(a)}</td><td class="num">${esc(b)}</td></tr>`).join('')}</tbody></table></div>`:''}
      ${g.idx ? `<div class="eyebrow">社内指標（値段まとめ）</div><div class="idx">${['高品質','高グレード','中グレード','低グレード'].map((l,i)=>`<div><span>${l}</span><b>${esc(g.idx[i]||'―')}</b></div>`).join('')}</div>`:''}
      <p class="note-s">相場はシート記載の目安。社内指標の単位はシート「宝石の値段まとめ」の表記のまま。</p>`) : ''}
    ${grade ? sec('社内グレード基準（A / B / C）', `<div class="grade"><div class="gh"></div><div class="gh">A</div><div class="gh">B</div><div class="gh">C</div>
      ${[['色','color'],['キズ','kizu'],['テリ','teri']].map(([l,k])=>`<div class="gl">${l}</div>${grade[k].map(x=>`<div>${esc(x)}</div>`).join('')}`).join('')}</div>
      <p class="note-s">シート「SREのデータまとめ」より。記録項目：色・キズ・テリ・1ct単価・産地・カット・枠の良し悪し・インクルージョン・鑑別書。</p>`) : ''}
    ${sec('鑑別書・鑑別機関でのチェック', `<ul class="lab">${g.lab.map(v=>`<li>${esc(v)}</li>`).join('')}</ul>`)}
    ${g.warn ? g.warn.map(w=>`<div class="warn"><b>シートとの相違</b>　${esc(w)}</div>`).join('') : ''}
    <p class="foot">内容は査定の目安です。高額品・判断に迷う石は必ず鑑別機関の鑑別書・分析報告書で確認してください。</p>
  </section>`;
}

/* ---------- treatments ---------- */
function viewTreat(){
  $app.innerHTML = `<section class="view">
    <div><div class="eyebrow">Treatments</div><h1 style="font-family:var(--f-display);font-size:26px">処理の種類</h1></div>
    <div class="legend">
      ${['E','T','A'].map(k=>`<div class="card"><div>${kindTag(k)}</div><p style="font-size:14px">${esc(KIND[k].desc)}</p></div>`).join('')}
    </div>
    <div class="warn"><b>価格への影響</b>　同じ大きさ・色でも、トリートメント品は加熱品の1/2〜1/10以下になることがある（案件トーク ポイントより）。</div>
    <div class="card">
      ${TREATMENTS.map(t=>`<div class="tr tcard"><div class="row2"><h3>${esc(t.n)}</h3>${kindTag(t.k)}${impTag(t.imp)}</div>
        <div style="font-size:14px">${esc(t.what)}</div>
        <dl class="kv"><dt>主な宝石</dt><dd>${esc(t.stones)}</dd><dt>見分け方</dt><dd>${esc(t.detect)}</dd></dl></div>`).join('')}
    </div>
    <p class="foot">区分は国内の鑑別団体（AGL）とGIAの考え方に沿った一般的な扱い。宝石ごとに扱いが変わる処理（樹脂含浸など）は各宝石のページを確認。</p>
  </section>`;
}

/* ---------- identification ---------- */
const FLOW = [
  ['基本情報の確認','宝石の種類の特定／サイズと重量（カラット）の測定／カット形状の確認'],
  ['鑑別','屈折率の測定（屈折計）／比重の測定（比重計）'],
  ['品質評価','色味（色相・彩度・明度）／透明度／インクルージョン／表面の傷やエッジの状態'],
  ['真贋判定','処理石か（加熱・照射・充填など）／合成石か（インクルージョンのパターン・蛍光反応）／模造石か'],
  ['最終評価','4C（カット・カラー・クラリティ・カラット）／マーケット価値の算定（希少性も考慮）']
];
const QUALITY = [
  ['色','色味／色の均一性と濃淡／色変化・多色性の有無'],
  ['表面','ファセットの接合部の鋭さ／すり減りやチップの有無'],
  ['内部','内包物の確認'],
  ['UV','長波・短波での反応／蛍光の色と強度を記録／蛍光分布の均一性'],
  ['屈折率','屈折計で測定／複屈折の有無と程度'],
  ['処理・合成','顕微鏡で特徴的な構造を観察／紫外線反応のパターン'],
  ['総合','色味・透明度・キズ・照り（輝き）の総合評価、希少性']
];
const TOOLS = [
  ['ルーペ（10倍）・顕微鏡','内包物の種類で天然・合成・産地を判断。ファセットエッジの鋭さ、裏面の二重像、張り合わせの接合面'],
  ['屈折計','屈折率と複屈折量。測れる上限は約1.81（それ以上は「範囲外」＝デマントイド、スフェーン、ジルコン、ダイヤモンド等）'],
  ['偏光器','単屈折／複屈折／集合体の判別。合成スピネルの異常複屈折'],
  ['二色鏡（ダイクロスコープ）','多色性の確認（タンザナイト、アレキサンドライト、トルマリンで強い）'],
  ['UVライト','長波365nm・短波254nm。ルビーの赤蛍光、合成エメラルドの蛍光、ヒスイB貨の青白い蛍光'],
  ['チェルシーフィルター','クロム発色（ルビー、エメラルド）やコバルト発色（合成ブルースピネル）が赤く見える'],
  ['分光器','吸収線：ルビーのクロム、サファイアの鉄、パライバの銅、染料'],
  ['比重','重さで類似石を分ける（アクアマリン2.72／ブルートパーズ3.53、CZ 5.6 など）'],
  ['熱伝導テスター','ダイヤモンドとモアサナイトに反応。CZ・ガラスは反応しない']
];
let riVal = store.get('ri', 1.762);
function viewCheck(){
  $app.innerHTML = `<section class="view">
    <div><div class="eyebrow">Identification</div><h1 style="font-family:var(--f-display);font-size:26px">鑑別と査定の手順</h1></div>
    <div class="card"><h2>屈折率から探す</h2>
      <div class="ri-input"><label for="riNum" class="muted" style="font-size:13px">測定値</label>
        <input id="riNum" type="number" step="0.001" min="1.35" max="2.45" value="${riVal}">
        <input id="riRange" type="range" min="1.35" max="2.45" step="0.001" value="${riVal}" aria-label="屈折率スライダー"></div>
      <div id="riOut"></div>
      <p class="note-s">±0.005の誤差を含めて一致する宝石を強調表示。1.81を超える値は通常の屈折計では測れない（範囲外）。</p>
    </div>
    <div class="card"><h2>査定の基本フロー</h2><div class="flow">${FLOW.map(([a,b])=>`<div class="step"><div><b>${a}</b><span>${b}</span></div></div>`).join('')}</div></div>
    <div class="card"><h2>総合品質評価のチェック項目</h2><dl class="kv">${QUALITY.map(([a,b])=>`<dt>${a}</dt><dd>${b}</dd>`).join('')}</dl></div>
    <div class="card"><h2>器具と使いどころ</h2><dl class="kv">${TOOLS.map(([a,b])=>`<dt>${a}</dt><dd>${b}</dd>`).join('')}</dl></div>
  </section>`;
  const num = document.getElementById('riNum'), rng = document.getElementById('riRange');
  const upd = v => { riVal = Math.round(v*1000)/1000; store.set('ri', riVal); drawRi(); };
  num.addEventListener('input', () => { const v = parseFloat(num.value); if (!isNaN(v)){ rng.value = v; upd(v); } });
  rng.addEventListener('input', () => { num.value = rng.value; upd(parseFloat(rng.value)); });
  drawRi();
}
function drawRi(){
  const lo = 1.35, hi = 2.45, pct = v => ((v - lo) / (hi - lo) * 100);
  const seen = new Set();
  const rows = GEMS.filter(g => { const k = g.ri.join('-') + g.group; if (/cab$/.test(g.id) || seen.has(k)) return false; seen.add(k); return true; })
    .sort((a,b) => a.ri[0] - b.ri[0]);
  const tol = 0.005;
  const hits = rows.filter(g => riVal >= g.ri[0] - tol && riVal <= g.ri[1] + tol);
  const out = document.getElementById('riOut');
  out.innerHTML = `<p style="margin:4px 0 8px"><span class="mono">${riVal.toFixed(3)}</span> に該当：${hits.length ? hits.map(g=>`<a href="#g-${g.id}"><b>${esc(g.ja)}</b></a>`).join('、') : '<span class="muted">なし</span>'}${riVal>1.81?'　<span class="kind A">範囲外（OTL）</span>':''}</p>
    <div class="tbl" style="border:0"><div style="min-width:420px" class="riRows">
    <div class="riAxis"><div></div><div>${[1.4,1.6,1.8,2.0,2.2,2.4].map(v=>`<span style="left:${pct(v)}%">${v.toFixed(1)}</span>`).join('')}</div></div>
    ${rows.map(g => { const hit = hits.includes(g);
      return `<a class="riRow ${hit?'hit':(hits.length?'dim':'')}" href="#g-${g.id}"><span>${esc(g.ja.replace(/（.*）/,''))}</span><span class="bar"><i style="left:${pct(g.ri[0])}%;width:${Math.max(pct(g.ri[1])-pct(g.ri[0]),0.4)}%;background:${g.sw}"></i><span class="cur" style="left:${pct(riVal)}%"></span></span></a>`; }).join('')}
    </div></div>`;
}

/* ---------- reference ---------- */
function viewRef(){
  const withIdx = GEMS.filter(g => g.idx);
  $app.innerHTML = `<section class="view">
    <div><div class="eyebrow">Reference</div><h1 style="font-family:var(--f-display);font-size:26px">鑑別書の読み方と資料</h1></div>
    <div class="card"><h2>書類の種類</h2><dl class="kv">
      <dt>鑑別書</dt><dd>宝石の種類、天然・合成・模造の別、処理の有無を記載。色石・ダイヤ共通。品質（グレード）や価格は書かれない</dd>
      <dt>鑑定書</dt><dd>ダイヤモンドの品質評価書（グレーディングレポート）。4C（カラー・クラリティ・カット・カラット）を評価</dd>
      <dt>分析報告書</dt><dd>産地、非加熱、ピジョンブラッド・ロイヤルブルーなど色の評価、ベリリウム拡散の有無など、通常の鑑別書では分からない項目を機器分析で報告</dd>
    </dl></div>
    <div class="card"><h2>主な鑑別機関</h2><dl class="kv">
      <dt>CGL</dt><dd>中央宝石研究所。国内最大手。鑑別書・ダイヤの鑑定書・分析報告書（産地・処理）</dd>
      <dt>AGL</dt><dd>宝石鑑別団体協議会。国内の鑑別機関が加盟し、鑑別書の記載ルール（処理の表記など）を定めている</dd>
      <dt>GIA</dt><dd>米国宝石学会。ダイヤの4Cを作った機関。色石レポートで加熱の有無・産地・エメラルドの含浸の程度を記載</dd>
      <dt>海外ラボ</dt><dd>GRS・Gübelin・SSEFなど。ルビー・サファイアの産地や「ピジョンブラッド」「ロイヤルブルー」の記載で知られる</dd>
    </dl></div>
    <div class="card"><h2>GIAレポートの主な表記</h2><div class="tbl"><table><thead><tr><th>表記</th><th>意味</th></tr></thead><tbody>
      <tr><td>No indications of heating</td><td>加熱の痕跡なし（非加熱）</td></tr>
      <tr><td>Indications of heating</td><td>加熱の痕跡あり</td></tr>
      <tr><td>…with minor / moderate / significant residues</td><td>加熱時の残留物（フラックス等）の量</td></tr>
      <tr><td>Clarity enhancement: None / Minor / Moderate / Significant</td><td>エメラルド等の含浸の程度</td></tr>
      <tr><td>Origin</td><td>産地の見解</td></tr>
      <tr><td>Composite / Manufactured product</td><td>鉛ガラス充填など、複合石・人工的な製品</td></tr>
      <tr><td>Laboratory-grown</td><td>合成（ラボグロウン）</td></tr>
    </tbody></table></div></div>
    <div class="card"><h2>鑑別書を受け取ったら確認すること</h2><ul>
      <li>発行機関と発行日（古い鑑別書は当時の技術で判定されている）</li>
      <li>写真・形状・重量・寸法が現物と一致するか</li>
      <li>宝石名の後ろやコメント欄にある処理の記載（含浸・染色・拡散・充填など）</li>
      <li>非加熱・産地をうたう場合は、分析報告書や海外ラボのレポートがあるか</li>
      <li>枠の刻印（Pt900・Pt850・K18など）。高額石が良い枠に留められているか</li>
    </ul></div>
    <div class="card"><h2>社内価格指標（1ctあたり）</h2>
      <div class="tbl"><table><thead><tr><th>宝石</th><th class="num">高品質</th><th class="num">高</th><th class="num">中</th><th class="num">低</th></tr></thead><tbody>
      ${withIdx.map(g=>`<tr><td><a href="#g-${g.id}">${esc(g.ja.replace(/（.*）/,''))}</a></td>${g.idx.map(v=>`<td class="num">${esc(v||'―')}</td>`).join('')}</tr>`).join('')}
      </tbody></table></div>
      <p class="note-s">シート「宝石の値段まとめ（案件レベルの早見表）」より。単位はシートの表記のまま。実査定では石名・重量・評価・自分の査定額・実際の査定額を記録して差を確認する。</p>
    </div>
    <div class="card"><h2>おすすめ書籍</h2><dl class="kv">
      <dt>宝石学の基礎</dt><dd>中央宝石研究所。宝石の種類・特徴・鑑定方法を体系的に学べる</dd>
      <dt>ジュエリー&amp;ジェム</dt><dd>実際の査定に役立つ知識が豊富</dd>
      <dt>カラーストーンのすべて</dt><dd>リチャード・W・ヒューズ。カラーストーンの鑑定に強くなる</dd>
      <dt>ダイヤモンドの科学</dt><dd>ダイヤモンドの評価基準を理解する</dd>
    </dl></div>
  </section>`;
}

/* ---------- quiz ---------- */
const shuffle = a => { a = a.slice(); for (let i = a.length-1; i > 0; i--){ const j = Math.floor(Math.random()*(i+1)); [a[i],a[j]] = [a[j],a[i]]; } return a; };
const pick = a => a[Math.floor(Math.random()*a.length)];
const base = GEMS.filter(g => !/cab$/.test(g.id));
const QTYPES = {
  ri:{label:'屈折率', make(){
    const g = pick(base);
    const d = shuffle(base.filter(x => Math.abs(x.ri[0]-g.ri[0]) > 0.02)).slice(0,3);
    return {q:`屈折率 <span class="mono">${esc(g.riText.replace(/（.*）/,''))}</span> を示す宝石は？`, ans:g, opts:[g,...d], why:`${g.ja}：${g.riText}（${g.optic}）`};
  }},
  h:{label:'硬度', make(){
    const g = pick(base);
    const d = shuffle(base.filter(x => x.h !== g.h && x.group !== g.group)).filter((x,i,a)=>a.findIndex(y=>y.h===x.h)===i).slice(0,3);
    return {q:`モース硬度 <span class="mono">${esc(g.h)}</span> の宝石は？`, ans:g, opts:[g,...d], why:`${g.ja}の硬度は${g.h}。`};
  }},
  sig:{label:'特徴', make(){
    const g = pick(base);
    const d = shuffle(base.filter(x => x.id !== g.id && x.group !== g.group)).slice(0,3);
    return {q:`「${esc(pick(g.sig))}」が特徴の宝石は？`, ans:g, opts:[g,...d], why:g.key};
  }},
  origin:{label:'産地', make(){
    const g = pick(base.filter(x => x.origin.length));
    const [o, f] = pick(g.origin);
    const d = shuffle(base.filter(x => x.id !== g.id && x.group !== g.group)).slice(0,3);
    return {q:`産地「${esc(o)}」${f?`：${esc(f)}`:''}。この宝石は？`, ans:g, opts:[g,...d], why:`${g.ja}の産地の特徴。`};
  }},
  treat:{label:'処理', make(){
    const t = pick(TREATMENTS);
    const opts = ['E','T','A'].map(k => ({id:k, ja:KIND[k].label}));
    return {q:`「${esc(t.n)}」の区分は？<div class="muted" style="font-size:13px;font-weight:500">主な宝石：${esc(t.stones)}</div>`, ans:opts.find(o=>o.id===t.k), opts, fixed:true, why:`${t.what}。${KIND[t.k].desc}`, noLink:true};
  }}
};
let quiz = {types: store.get('qtypes', Object.keys(QTYPES)), cur:null, answered:false, right:0, total:0, streak:0, best: store.get('best', 0)};
function newQ(){
  const types = quiz.types.length ? quiz.types : Object.keys(QTYPES);
  const q = QTYPES[pick(types)].make();
  q.opts = q.fixed ? q.opts : shuffle(q.opts);
  quiz.cur = q; quiz.answered = false;
}
function viewQuiz(){
  if (!quiz.cur) newQ();
  const q = quiz.cur;
  $app.innerHTML = `<section class="view">
    <div><div class="eyebrow">Quiz</div><h1 style="font-family:var(--f-display);font-size:26px">覚えるクイズ</h1></div>
    <div class="chips" role="group" aria-label="出題範囲">${Object.entries(QTYPES).map(([k,v])=>`<button class="chip" type="button" data-qt="${k}" aria-pressed="${quiz.types.includes(k)}">${v.label}</button>`).join('')}</div>
    <div class="qcard">
      <div class="qhead"><span>${quiz.total+ (quiz.answered?0:1)}問目</span><div class="score"><span>正解 <b>${quiz.right}/${quiz.total}</b></span><span>連続 <b>${quiz.streak}</b></span><span>最高 <b>${quiz.best}</b></span></div></div>
      <div class="qtext">${q.q}</div>
      <div class="opts">${q.opts.map((o,i)=>`<button class="opt" type="button" data-i="${i}">${esc(o.ja)}</button>`).join('')}</div>
      <div id="qexp"></div>
    </div>
  </section>`;
  $app.querySelectorAll('[data-qt]').forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.qt; const s = new Set(quiz.types); s.has(k) ? s.delete(k) : s.add(k);
    quiz.types = [...s]; store.set('qtypes', quiz.types); newQ(); viewQuiz();
  }));
  $app.querySelectorAll('.opt').forEach(b => b.addEventListener('click', () => answer(+b.dataset.i)));
}
function answer(i){
  if (quiz.answered) return;
  const q = quiz.cur; quiz.answered = true; quiz.total++;
  const ok = q.opts[i].id === q.ans.id;
  if (ok){ quiz.right++; quiz.streak++; if (quiz.streak > quiz.best){ quiz.best = quiz.streak; store.set('best', quiz.best); } } else quiz.streak = 0;
  $app.querySelectorAll('.opt').forEach((b, j) => { b.disabled = true; if (q.opts[j].id === q.ans.id) b.classList.add('ok'); else if (j === i) b.classList.add('ng'); });
  document.getElementById('qexp').innerHTML = `<div class="explain"><b>${ok?'正解':'不正解'}</b>　正解は「${esc(q.ans.ja)}」。${esc(q.why)}${q.noLink?'':` <a href="#g-${q.ans.id}">詳しく見る</a>`}</div>
    <div class="btnrow" style="margin-top:10px"><button class="btn" type="button" id="nextQ">次の問題</button></div>`;
  $app.querySelector('.qhead').querySelector('.score').innerHTML = `<span>正解 <b>${quiz.right}/${quiz.total}</b></span><span>連続 <b>${quiz.streak}</b></span><span>最高 <b>${quiz.best}</b></span>`;
  document.getElementById('nextQ').addEventListener('click', () => { newQ(); viewQuiz(); window.scrollTo(0,0); });
}

/* ---------- router ---------- */
function route(){
  const h = (location.hash || '#gems').slice(1);
  let tab = 'gems';
  if (h.startsWith('g-') && byId[h.slice(2)]) viewGem(byId[h.slice(2)]);
  else if (h === 'treat'){ tab = 'treat'; viewTreat(); }
  else if (h === 'check'){ tab = 'check'; viewCheck(); }
  else if (h === 'quiz'){ tab = 'quiz'; viewQuiz(); }
  else if (h === 'cert'){ tab = 'cert'; viewRef(); }
  else viewList();
  document.querySelectorAll('.tabs a').forEach(a => { if (a.dataset.tab === tab) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
}
window.addEventListener('hashchange', () => { route(); window.scrollTo(0,0); });
route();
})();
