# Gameplay "fun" layer, exec'd by build.py after the art patches (shares `s` and `sub`).
# Adds: daily almanac (黄历), battle reads / crits, loot drops + rare charms,
# 江湖称号 achievements, synthesized sound effects, and toast banners.

# ---------- CSS ----------
sub('</style></head>', r"""
/* Fun layer: almanac, titles, banners, battle reads. */
.omen-chip{display:inline-block;margin-left:8px;padding:2px 8px;border:1px solid #c79a5b;border-radius:3px;color:#9a4f32;font:13px "Songti SC","SimSun",serif;letter-spacing:1px;vertical-align:3px}
.omen-card{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:0 0 12px;padding:10px 12px;border:1px dashed #c9a46c;border-radius:8px;background:#f7ecd5}
.omen-card span{font-size:11px;letter-spacing:2px;color:#8a6a43}.omen-card b{font:600 17px "Songti SC","SimSun",serif;color:#9a4f32}.omen-card small{color:#6b5a40;font-size:12px}
.omen-line{margin:0 0 10px;padding:8px 12px;border-left:3px solid #c79a5b;background:#f7ecd5;font-size:13px;color:#6b4a2c}
.title-chip{display:inline-block;margin-right:6px;padding:1px 7px;border-radius:3px;background:#9a4f32;color:#fff3dc;font-size:12px;letter-spacing:1px;vertical-align:4px}
.title-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:12px 0 4px}
.title-card{border:1px solid var(--line);border-radius:8px;padding:10px 11px;background:#f5f1e3;text-align:left;min-height:0;display:block;width:100%}
.title-card strong{display:block;font:600 15px "Songti SC","SimSun",serif;color:#243f36}.title-card small{display:block;margin-top:4px;font-size:12px;color:#6a7566;line-height:1.5}
.title-card.locked{opacity:.5;filter:grayscale(1)}.title-card.worn{border-color:#9a4f32;box-shadow:inset 0 0 0 1px #9a4f32;background:#fbefe0}
#bannerRoot{position:fixed;left:50%;top:18px;transform:translateX(-50%);z-index:70;pointer-events:none}
.banner{min-width:240px;max-width:88vw;padding:12px 22px;border-radius:10px;background:linear-gradient(120deg,#173b39,#2c5446);color:#fff4d8;border:1px solid #c9a46c;box-shadow:0 12px 40px #0d2a2655;text-align:center;animation:banner-in 2.3s ease both}
.banner b{display:block;font:600 18px "Songti SC","SimSun",serif;letter-spacing:2px;color:#f1d491}.banner small{display:block;margin-top:4px;font-size:13px;color:#d9dcc4}
@keyframes banner-in{0%{opacity:0;transform:translateY(-14px)}12%{opacity:1;transform:none}85%{opacity:1}100%{opacity:0;transform:translateY(-8px)}}
.battle-number.crit{font-size:34px;color:#d0461f;text-shadow:0 2px #fff2d0,0 0 14px #f5c35a}.battle-number small{display:block;font:bold 14px "Songti SC","SimSun",serif;text-align:center}
.read-badge{position:absolute;left:50%;top:12%;transform:translateX(-50%);padding:4px 14px;border-radius:4px;background:#173b39e6;color:#f1d491;font:600 18px "Songti SC","SimSun",serif;letter-spacing:4px;animation:rise 1s ease-out both;pointer-events:none}
.battle-field.crit-hit{animation:crit-shake .38s ease-out}
@keyframes crit-shake{20%{transform:translate(-5px,2px)}40%{transform:translate(5px,-2px)}60%{transform:translate(-3px,1px)}80%{transform:translate(2px,0)}}
.loot{display:inline-block;margin-top:8px;color:#9a4f32;font-weight:600}
.focus-tag{color:#a5512f;font-weight:600}
@media(max-width:760px){#bannerRoot{top:calc(150px + env(safe-area-inset-top))}.omen-chip{font-size:12px}}
@media(prefers-reduced-motion:reduce){.banner{animation:none}}
</style></head>""")

# ---------- new state ----------
sub("tutorial:true};}",
    "tutorial:true,omenSeed:Math.floor(Math.random()*1e9)+1,titles:[],title:null,feats:{reads:0,crits:0,flawless:0,drops:0}};}")

# ---------- rare drop charms (not sold in the market) ----------
sub("{id:'potion',name:'回春散'",
    "{id:'fang',name:'狼牙坠',type:'charm',atk:3,price:70,drop:true,icon:'✧',desc:'攻击 +3。清风林灰狼的獠牙，战利品。'},"
    "{id:'scarf',name:'赤巾',type:'charm',def:2,hp:12,price:80,drop:true,icon:'✧',desc:'防御 +2，最大气血 +12。山道匪徒的头巾，战利品。'},"
    "{id:'tally',name:'哨卫铁令',type:'charm',atk:2,def:3,price:120,drop:true,icon:'✧',desc:'攻击 +2，防御 +3。黑风岭的通行令，战利品。'},"
    "{id:'fur',name:'寨主狼裘',type:'charm',atk:4,def:4,hp:20,price:200,drop:true,icon:'✧',desc:'攻击 +4，防御 +4，最大气血 +20。寨主的狼裘，战利品。'},"
    "{id:'potion',name:'回春散'")

# ---------- core fun module ----------
sub("function currentEvent(){", r"""const OMENS=[{id:'train',name:'宜习武',desc:'习武阅历 +50%'},{id:'work',name:'宜帮工',desc:'帮工铜钱 +50%'},{id:'rest',name:'宜静养',desc:'调息恢复翻倍'},{id:'hunt',name:'宜出行',desc:'胜战铜钱 +50%，战利品更易得'},{id:'fierce',name:'忌刀兵',desc:'敌人攻击 +15%，胜战阅历 +50%'},{id:'star',name:'吉星高照',desc:'会心一击几率 +15%'},{id:'market',name:'集市逢五',desc:'集市货品八折'},{id:'calm',name:'诸事平顺',desc:'无事便是好日子'}];
function omen(s=S){let h=(s.omenSeed^Math.imul(s.day,2654435761))>>>0;h=Math.imul(h^(h>>>15),2246822507)>>>0;h=(h^(h>>>13))>>>0;return OMENS[h%OMENS.length]}
function omenHTML(){const o=omen();return `<div class="omen-card"><span>今日黄历</span><b>${o.name}</b><small>${o.desc}</small></div>`}
function omenLine(ids){const o=omen();return ids.includes(o.id)?`<p class="omen-line">今日黄历「${o.name}」：${o.desc}</p>`:''}
function omenBattleNote(){const o=omen();return o.id==='fierce'?'<br><span class="focus-tag">忌刀兵：敌方攻击 +15%，胜战阅历 +50%</span>':o.id==='star'?'<br><span class="focus-tag">吉星高照：会心一击几率 +15%</span>':''}
const DROPS={wolf:{item:'fang',rate:.15},bandit:{item:'scarf',rate:.14},elite:{item:'tally',rate:.18},boss:{item:'fur',rate:1}},DROP_IDS=Object.values(DROPS).map(d=>d.item);
function winLoot(b,e){const o=omen().id,luck=o==='hunt'?1.5:1;let xp=e.xp,gold=e.gold;if(o==='fierce')xp=Math.round(xp*1.5);if(o==='hunt')gold=Math.round(gold*1.5);gainXP(xp);S.gold+=gold;const got=[];if(!b.hurt){S.feats.flawless++;got.push('毫发无伤')}if(rand()<.3*luck){S.potions++;got.push('回春散 ×1')}if(rand()<.2*luck){const g=Math.round(e.gold*.6);S.gold+=g;gold+=g;got.push('碎银 '+g+' 文')}const d=DROPS[b.id];if(d&&!S.inventory.includes(d.item)&&rand()<d.rate*luck){S.inventory.push(d.item);S.feats.drops++;got.push('稀有佩饰「'+findItem(d.item).name+'」，可在行囊佩戴')}log('击败'+e.name+'，获得 '+xp+' 阅历与 '+gold+' 文，武学点 +1'+(got.length?'；'+got.join('、'):'')+'。');return{xp,gold,html:got.length?'<br><span class="loot">战利品 · '+got.join(' · ')+'</span>':''}}
const FEAT_KEYS=['reads','crits','flawless','drops'];
const TITLES=[{id:'first',name:'初出茅庐',desc:'赢得第一场战斗',check:s=>s.kills>=1},{id:'reader',name:'料敌先机',desc:'看破或乘隙 10 次',check:s=>s.feats.reads>=10},{id:'crit',name:'会心一剑',desc:'打出 8 次会心一击',check:s=>s.feats.crits>=8},{id:'flawless',name:'片叶不沾',desc:'毫发无伤赢下 3 场',check:s=>s.feats.flawless>=3},{id:'veteran',name:'百战归来',desc:'赢得 20 场战斗',check:s=>s.kills>=20},{id:'rich',name:'腰缠万贯',desc:'身上铜钱达到 400 文',check:s=>s.gold>=400},{id:'kind',name:'菩萨心肠',desc:'仁心达到 25',check:s=>s.karma>=25},{id:'famous',name:'名动一方',desc:'声望达到 25',check:s=>s.fame>=25},{id:'sage',name:'灵台清明',desc:'心悟达到 25',check:s=>s.insight>=25},{id:'friends',name:'知交满天下',desc:'三位朋友好感都达到 30',check:s=>Object.values(s.bond).every(v=>v>=30)},{id:'collector',name:'珍宝猎人',desc:'集齐 4 件战利品佩饰',check:s=>DROP_IDS.every(id=>s.inventory.includes(id))},{id:'master',name:'武学奇才',desc:'任一功法修至三重',check:s=>Object.values(s.martial.ranks).some(r=>r>=3)},{id:'boss',name:'黑风克星',desc:'击败黑风寨主',check:s=>!!s.flags.bossDefeated}];
function titleName(id){return TITLES.find(t=>t.id===id)?.name||''}
function titleChip(){return S.title?`<span class="title-chip">${titleName(S.title)}</span>`:''}
function checkTitles(){for(const t of TITLES){if(S.titles.includes(t.id)||!t.check(S))continue;S.titles.push(t.id);S.gold+=15;if(!S.title)S.title=t.id;log('获得江湖称号「'+t.name+'」：'+t.desc+'，赏 15 文。');sfx('title');banner('江湖称号 ·「'+t.name+'」',t.desc+' · 赏 15 文')}}
function setTitle(id){if(!S.titles.includes(id))return;S.title=S.title===id?null:id;render()}
function titlesHTML(){return `<h3 style="margin-top:22px">江湖称号 <span class="tag">${S.titles.length} / ${TITLES.length}</span></h3><p class="note">达成即得，每个称号赏 15 文。点选已得称号，可显示在名号之前。</p><div class="title-grid">${TITLES.map(t=>{const has=S.titles.includes(t.id);return `<button class="title-card ${has?'':'locked'} ${S.title===t.id?'worn':''}" onclick="setTitle('${t.id}')" ${has?'':'disabled'}><strong>${has?t.name:'？？？'}</strong><small>${t.desc}${S.title===t.id?' · 佩戴中':''}</small></button>`}).join('')}</div>`}
function normalizeFun(s){if(!Number.isSafeInteger(s.omenSeed)||s.omenSeed<1)s.omenSeed=(s.seed%999983)+1;const f=s.feats&&typeof s.feats==='object'&&!Array.isArray(s.feats)?s.feats:{};s.feats={};for(const k of FEAT_KEYS){const v=f[k];s.feats[k]=Number.isSafeInteger(v)&&v>=0?v:0}s.titles=Array.isArray(s.titles)?[...new Set(s.titles.filter(id=>TITLES.some(t=>t.id===id)))]:[];if(!s.titles.includes(s.title))s.title=null;if(s.battle){s.battle.focus=s.battle.focus===true;s.battle.hurt=s.battle.hurt===true}}
const bannerQ=[];let bannerOn=false;function banner(t,sub){bannerQ.push([t,sub]);if(!bannerOn)nextBanner()}function nextBanner(){const n=bannerQ.shift();if(!n){bannerOn=false;$('bannerRoot').innerHTML='';return}bannerOn=true;$('bannerRoot').innerHTML=`<div class="banner"><b>${escapeHTML(n[0])}</b><small>${escapeHTML(n[1])}</small></div>`;setTimeout(nextBanner,2300)}
const SFX_KEY='jianghu-weiwan-sfx';let sfxOn=true,actx=null;try{sfxOn=localStorage.getItem(SFX_KEY)!=='off'}catch(e){}
function toggleSfx(){sfxOn=!sfxOn;try{localStorage.setItem(SFX_KEY,sfxOn?'on':'off')}catch(e){}syncSfx();if(sfxOn)sfx('coin')}
function syncSfx(){const b=$('sfxToggle');if(b){b.textContent=sfxOn?'♪ 音效':'♪ 静音';b.setAttribute('aria-pressed',String(sfxOn))}}
function sfx(type){if(!sfxOn)return;try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;actx=actx||new AC();if(actx.state==='suspended')actx.resume();const t0=actx.currentTime,out=actx.createGain();out.gain.value=.55;out.connect(actx.destination);
const tone=(f,f2,dur,wave='sine',vol=.2,at=0)=>{const o=actx.createOscillator(),g=actx.createGain(),t=t0+at;o.type=wave;o.frequency.setValueAtTime(f,t);if(f2!==f)o.frequency.exponentialRampToValueAtTime(f2,t+dur);g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(vol,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g).connect(out);o.start(t);o.stop(t+dur+.02)};
const noise=(dur,freq=1800,vol=.25,at=0)=>{const n=Math.floor(actx.sampleRate*dur),buf=actx.createBuffer(1,n,actx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*(1-i/n);const src=actx.createBufferSource(),f=actx.createBiquadFilter(),g=actx.createGain();src.buffer=buf;f.type='lowpass';f.frequency.value=freq;g.gain.value=vol;src.connect(f).connect(g).connect(out);src.start(t0+at)};
({hit:()=>{noise(.09,2400,.35);tone(190,80,.12,'triangle',.25)},crit:()=>{noise(.14,4200,.4);tone(520,1040,.12,'square',.08);tone(1320,1320,.28,'sine',.18,.06)},guard:()=>{tone(1250,1180,.32,'triangle',.16);tone(1870,1800,.2,'sine',.08);noise(.05,6000,.15)},hurt:()=>{noise(.12,900,.35);tone(150,60,.18,'sawtooth',.1)},heal:()=>{[523,659,784].forEach((f,i)=>tone(f,f,.22,'sine',.12,i*.07))},coin:()=>{tone(1318,1318,.07,'square',.05);tone(1760,1760,.16,'square',.05,.06)},level:()=>{[523,659,784,1046].forEach((f,i)=>tone(f,f,.3,'triangle',.14,i*.09))},title:()=>{[784,988,1175,1568].forEach((f,i)=>tone(f,f,.45,'sine',.12,i*.1))},win:()=>{[392,523,659,784].forEach((f,i)=>tone(f,f,.35,'triangle',.14,i*.1))},lose:()=>{[392,330,262].forEach((f,i)=>tone(f,f*.98,.4,'triangle',.13,i*.16))},read:()=>{tone(880,1480,.14,'sine',.14);noise(.06,7000,.12)},page:()=>{noise(.12,3000,.08);tone(660,700,.08,'sine',.05,.04)},bell:()=>{tone(440,440,1.4,'sine',.16);tone(880,880,.9,'sine',.06);tone(1320,1320,.5,'sine',.03)}})[type]?.()}catch(e){}}
function playFx(fx){if(fx.read==='看破')sfx('read');if(fx.crit)sfx('crit');else if(fx.dealt)sfx('hit');if(fx.type==='guard'&&fx.read!=='看破')sfx('guard');if(fx.healed)sfx('heal');if(fx.taken)setTimeout(()=>sfx('hurt'),reducedMotion()?0:420)}
function currentEvent(){""")

# ---------- save validation ----------
sub("if(legacy){s.martial=martialFresh();s.v=2}", "normalizeFun(s);if(legacy){s.martial=martialFresh();s.v=2}")

# ---------- render hooks ----------
sub("function render(){frameEpoch++;", "function render(){frameEpoch++;checkTitles();")
sub("+'</b> 日'+(S.ended?'':' / 三十日');",
    "+'</b> 日'+(S.ended?'':' / 三十日')+' <span class=\"omen-chip\" title=\"'+omen().desc+'\">'+omen().name+'</span>';syncSfx();")
sub('<div class="serif name">无名少侠</div>', '<div class="serif name">${titleChip()}无名少侠</div>')
sub('<h3>无名少侠 · Lv.${S.level}</h3>', '<h3>${titleChip()}无名少侠 · Lv.${S.level}</h3>')
sub('<strong>第 ${S.day} 日 <small>Lv.${S.level} · 详情 ›</small></strong>',
    '<strong>第 ${S.day} 日 <small>${omen().name} · Lv.${S.level} ›</small></strong>')
sub('<button onclick="openHelp()" aria-label="玩法说明">玩法</button>',
    '<button id="sfxToggle" onclick="toggleSfx()" aria-pressed="true" aria-label="音效开关">♪ 音效</button><button onclick="openHelp()" aria-label="玩法说明">玩法</button>')
sub('<div id="toastRoot" aria-live="polite"></div>', '<div id="toastRoot" aria-live="polite"></div><div id="bannerRoot" aria-live="polite"></div>')

# daily actions use the almanac
sub("$('actions').innerHTML=`<div class=\"quick\">", "$('actions').innerHTML=`${omenHTML()}<div class=\"quick\">")
sub("<small>1 行动 · 经验 +22 · 武学点 +1<br>", "<small>1 行动 · 经验 +${omen().id==='train'?33:22} · 武学点 +1<br>")
sub("<small>1 行动 · 气血 +35<br>", "<small>1 行动 · 气血 +${omen().id==='rest'?70:35}<br>")
sub("<small>1 行动 · 铜钱 +22<br>", "<small>1 行动 · 铜钱 +${omen().id==='work'?33:22}<br>")
sub("S.energy--;S.trained++;gainXP(22);", "const tx=omen().id==='train'?33:22;S.energy--;S.trained++;gainXP(tx);")
sub("log('习武一时，获得 22 阅历。');render();toast('习武完成 · 阅历 +22 · 武学点 +1')",
    "log('习武一时，获得 '+tx+' 阅历。');render();sfx('read');toast('习武完成 · 阅历 +'+tx+' · 武学点 +1')")
sub("S.energy--;S.gold+=22;log('在渡口搬货，挣得 22 文。');render();toast('帮工完成 · 铜钱 +22')",
    "S.energy--;const g=omen().id==='work'?33:22;S.gold+=g;log('在渡口搬货，挣得 '+g+' 文。');render();sfx('coin');toast('帮工完成 · 铜钱 +'+g)")
sub("const n=Math.min(35,stats().hp-S.hp);", "const n=Math.min(omen().id==='rest'?70:35,stats().hp-S.hp);")
sub("render();toast('调息完成 · 气血 +'+n)", "render();sfx('heal');toast('调息完成 · 气血 +'+n)")
sub("render();toast('使用回春散 · 气血 +'+healed)", "render();sfx('heal');toast('使用回春散 · 气血 +'+healed)")
sub("log('晨光入山，新的一日开始了。');render();toast('第 '+S.day+' 日 · 山河又一程')",
    "log('晨光入山，新的一日开始了。今日黄历：'+omen().name+'。');render();sfx('bell');banner('第 '+S.day+' 日 · 黄历「'+omen().name+'」',omen().desc);for(const d of [S.day,S.day+1]){const ev=EVENTS[d<=30?d-1:(d-31)%EVENTS.length],ea=ENCOUNTER_ART[ev.id];if(ea){const im=new Image();im.src=artURL(ea.src);im.decode?.().catch(()=>{})}}")
sub("render();toast('这一笔，江湖记下了。')", "render();sfx('page');toast('这一笔，江湖记下了。')")

# market: almanac discount, drop-only items hidden
sub("function price(i){return i.price}", "function price(i){return Math.round(i.price*(omen().id==='market'?.8:1))}")
sub("ITEMS.filter(i=>i.price>0)", "ITEMS.filter(i=>i.price>0&&!i.drop)")
sub("if(!i||i.price<=0||S.gold<i.price||", "if(!i||i.price<=0||i.drop||S.gold<price(i)||")
sub("S.gold-=i.price;", "const paid=price(i);S.gold-=paid;")
sub("'，花费 '+i.price+' 文。');render();toast(i.name+'已入行囊'", "'，花费 '+paid+' 文。');render();sfx('coin');toast(i.name+'已入行囊'")
sub('<p class="note">明码实价，不耗行动。', "${omenLine(['market'])}<p class=\"note\">明码实价，不耗行动。")
sub("render();toast('已出售'", "render();sfx('coin');toast('已出售'")
sub("render();toast('委托完成 · '", "render();sfx('coin');toast('委托完成 · '")

# journey: almanac + loot info
sub('<p class="note">敌人会提前显露下一招。', "${omenLine(['hunt','fierce','star'])}<p class=\"note\">敌人会提前显露下一招。招架重击可「看破」，趁喘息出手可「乘隙」，偶有会心一击；胜后可能掉落战利品。")
sub("获胜：${e.xp} 阅历 / ${e.gold} 文", "获胜：${e.xp} 阅历 / ${e.gold} 文<br>稀有掉落：${findItem(DROPS[id].item).name}${S.inventory.includes(DROPS[id].item)?' ✓ 已得':''}")

# ---------- battle: reads, crits, flawless, loot ----------
sub("heavy:'蓄势 · 下一招重击，伤害约 1.7 倍！招架可减伤 75%。'",
    "heavy:'蓄势 · 下一招重击，伤害约 1.7 倍！招架可减伤 75%，并「看破」：真气 +1，下一击 +30%。'")
sub("rest:'喘息 · 本回合敌人不会攻击。'", "rest:'喘息 · 本回合敌人不会攻击。此时出手为「乘隙」，伤害 +25%。'")
sub("真气 ${b.qi}/4</div>", "真气 ${b.qi}/4${b.focus?' · <span class=\"focus-tag\">蓄锋待发 +30%</span>':''}</div>")
sub("<p class=\"note\">${martialSummary()}<br>${martialDesc(martialActive().id,martialRank(martialActive().id))}",
    "<p class=\"note\">${martialSummary()}${omenBattleNote()}<br>${martialDesc(martialActive().id,martialRank(martialActive().id))}")
sub("const actual=Math.min(b.hp,damage);",
    "{let mult=1;if(b.focus){mult+=.3;b.focus=false;fx.read='蓄锋'}if(it==='rest'){mult+=.25;fx.read='乘隙';S.feats.reads++}if(rand()<.1+(omen().id==='star'?.15:0)){mult*=1.6;fx.crit=true;S.feats.crits++}damage=Math.max(1,Math.round(damage*mult))}const actual=Math.min(b.hp,damage);")
sub("b.logs.push((action==='skill'?move.name+' · '+rank+' 重':'你挥剑出击')+'，造成 '",
    "b.logs.push((fx.crit?'【会心】':'')+(fx.read?'【'+fx.read+'】':'')+(action==='skill'?move.name+' · '+rank+' 重':'你挥剑出击')+'，造成 '")
sub("else if(action==='guard'){guarded=true;b.qi=Math.min(4,b.qi+1);b.logs.push('你收剑招架，回复 1 真气。')}",
    "else if(action==='guard'){guarded=true;b.qi=Math.min(4,b.qi+1);if(it==='heavy'){b.qi=Math.min(4,b.qi+1);b.focus=true;fx.read='看破';S.feats.reads++;b.logs.push('【看破】你看准重击收剑招架，回复 2 真气，下一击 +30%。')}else b.logs.push('你收剑招架，回复 1 真气。')}")
sub("S.hp=Math.max(0,S.hp-dmg);fx.taken=dmg;", "S.hp=Math.max(0,S.hp-dmg);fx.taken=dmg;b.hurt=true;")
sub("battleFX=fx;renderBattle();", "battleFX=fx;playFx(fx);renderBattle();", count=2)
sub("b.turn++;b.logs=b.logs.slice(-20);battleFX=fx;lockBattle();render()", "b.turn++;b.logs=b.logs.slice(-20);battleFX=fx;playFx(fx);lockBattle();render()")
sub("gainXP(e.xp);S.gold+=e.gold;log('击败'+e.name+'，获得 '+e.xp+' 阅历与 '+e.gold+' 文，武学点 +1。');S.battle=null;S.tab='journey';battleResult('一战告捷',`<p>你击败了${e.name}。<br>获得 ${e.xp} 阅历 · ${e.gold} 文 · 武学点 +1",
    "const loot=winLoot(b,e);S.battle=null;S.tab='journey';battleResult('一战告捷',`<p>你击败了${e.name}。<br>获得 ${loot.xp} 阅历 · ${loot.gold} 文 · 武学点 +1${loot.html}")
sub("function battleResult(title,body,buttons){battleBusy=true;",
    "function battleResult(title,body,buttons){battleBusy=true;setTimeout(()=>sfx(title==='一战告捷'?'win':'lose'),380);")
sub("${fx?'fx-'+fx.type:''}", "${fx?'fx-'+fx.type:''}${fx?.crit?' crit-hit':''}")
sub('<span class="battle-number enemy-num">${fx.dealt?\'−\'+fx.dealt:\'\'}</span>',
    '<span class="battle-number enemy-num${fx.crit?\' crit\':\'\'}">${fx.dealt?\'−\'+fx.dealt:\'\'}${fx.crit?\'<small>会心</small>\':\'\'}</span>${fx.read?`<span class="read-badge">${fx.read}</span>`:\'\'}')

# level-up banner
sub("log('突破至 '+S.level+' 级：", "sfx('level');banner('突破 · Lv.'+S.level,'气血、攻击、防御提升，武学点 +2');log('突破至 '+S.level+' 级：")

# ---------- titles page, ending, help ----------
sub('${causalLedger()}<h3 style="margin-top:22px">沿途委托</h3>', '${causalLedger()}${titlesHTML()}<h3 style="margin-top:22px">沿途委托</h3>')
sub('<span class="tag">胜战 ${e.kills}</span>', '<span class="tag">胜战 ${e.kills}</span><span class="tag">称号 ${S.titles.length} / ${TITLES.length}</span>')
sub('<div><b>五</b>', '<div><b>✦</b>每日黄历带来不同加成。战斗中招架重击可「看破」、趁喘息出手可「乘隙」，还有会心一击；胜战可能掉落稀有佩饰；达成目标获得江湖称号。右上角可开关音效。</div><div><b>五</b>')
