# 行囊 rework, exec'd by build.py after fun.py (shares `s`, `sub`, `webp`, `crop_alpha`, `ART`).
# Splits the bag into 背包 / 装备 / 武学; 装备 and 武学 use a figure-with-slots layout.

# ---------- item icons ----------
icons = {}
for p in sorted((ART / 'out' / 'icons').glob('*.png')):
    icons[p.stem] = webp(crop_alpha(Image.open(p).convert('RGBA'), pad=24), (128, 128), 74)
sub("const LANDSCAPE='", 'const ICONS={' + ','.join(f"{k}:'{v}'" for k, v in icons.items()) + "};\nconst LANDSCAPE='")

# ---------- extra gear slots: 头饰 / 手环 / 靴子 ----------
sub("const findItem=id=>ITEMS.find(x=>x.id===id);",
    "const findItem=id=>ITEMS.find(x=>x.id===id);\nconst GEAR_TYPES=['weapon','armor','head','wrist','boots','charm'],OPTIONAL_GEAR=['head','wrist','boots','charm'];")
sub("{id:'potion',name:'回春散'",
    "{id:'headband',name:'青布头巾',type:'head',def:1,hp:6,price:35,icon:'◎',desc:'防御 +1，最大气血 +6。挡得住山风，也挡得住汗水。'},"
    "{id:'jadecrown',name:'束发玉冠',type:'head',def:2,hp:15,price:110,icon:'◎',desc:'防御 +2，最大气血 +15。玉冠端正，心神也端正。'},"
    "{id:'ironbrow',name:'玄铁护额',type:'head',def:3,hp:25,price:220,icon:'◎',desc:'防御 +3，最大气血 +25。护住要害，敢迎刀锋。'},"
    "{id:'redcord',name:'红绳手环',type:'wrist',atk:1,hp:5,price:30,icon:'○',desc:'攻击 +1，最大气血 +5。渡口阿婆编的平安绳。'},"
    "{id:'bracer',name:'铜护腕',type:'wrist',atk:3,def:1,price:100,icon:'○',desc:'攻击 +3，防御 +1。腕力更稳，出剑更沉。'},"
    "{id:'dragonring',name:'龙纹臂环',type:'wrist',atk:5,def:1,price:230,icon:'○',desc:'攻击 +5，防御 +1。龙纹盘绕，一臂千钧。'},"
    "{id:'clothshoe',name:'千层布靴',type:'boots',def:1,hp:8,price:40,icon:'▱',desc:'防御 +1，最大气血 +8。千针万线，走得了远路。'},"
    "{id:'cloudboot',name:'踏云靴',type:'boots',def:2,hp:15,price:120,icon:'▱',desc:'防御 +2，最大气血 +15。步履轻盈，如踏云端。'},"
    "{id:'windboot',name:'追风靴',type:'boots',atk:2,def:3,hp:20,price:240,icon:'▱',desc:'攻击 +2，防御 +3，最大气血 +20。快人一步，便胜一招。'},"
    "{id:'potion',name:'回春散'")
sub("[s.gear.weapon,s.gear.armor,s.gear.charm]", "GEAR_TYPES.map(t=>s.gear[t])")
sub("gear:{weapon:'bamboo',armor:'cloth',charm:null}", "gear:{weapon:'bamboo',armor:'cloth',head:null,wrist:null,boots:null,charm:null}")
sub("Object.keys(s.gear).some(k=>!['weapon','armor','charm'].includes(k))", "Object.keys(s.gear).some(k=>!GEAR_TYPES.includes(k))")
sub("for(const type of ['weapon','armor','charm']){const id=s.gear[type];if(type==='charm'&&!id)continue;",
    "for(const type of GEAR_TYPES){const id=s.gear[type]??null;s.gear[type]=id;if(OPTIONAL_GEAR.includes(type)&&!id)continue;")
sub("i.type==='weapon'?'兵刃':i.type==='armor'?'衣甲':i.type==='charm'?'佩饰':'药品'", "GEAR_SLOTS[i.type]||'药品'")
sub("<br>佩饰 <span class=\"tag\">${S.gear.charm?findItem(S.gear.charm).name:'尚未佩戴'}</span>",
    "${['head','wrist','boots','charm'].map(t=>`<br>${GEAR_SLOTS[t]} <span class=\"tag\">${S.gear[t]?findItem(S.gear[t]).name:'尚未佩戴'}</span>`).join('')}")
sub("<br>佩饰：${S.gear.charm?findItem(S.gear.charm).name:'尚未佩戴'}",
    "${['head','wrist','boots','charm'].map(t=>`<br>${GEAR_SLOTS[t]}：${S.gear[t]?findItem(S.gear[t]).name:'尚未佩戴'}`).join('')}")

# ---------- drop the old bag / martial renderers ----------
def cut(start, end):
    global s
    a = s.find(start)
    b = s.find(end, a)
    if a < 0 or b < 0 or s.find(start, a + 1) >= 0:
        sys.exit(f'cut anchor problem: {start!r}')
    s = s[:a] + s[b:]

cut("function setBagView(view){", "function studyMartial(id){")
cut("function renderBag(){", "function equip(id){")

# ---------- new bag module ----------
sub("function studyMartial(id){", r"""let gearSlot='weapon',martialSlot='move';
const GEAR_SLOTS={weapon:'兵刃',armor:'衣甲',head:'头饰',wrist:'手环',boots:'靴子',charm:'佩饰'},MARTIAL_GLYPH={move:'招',inner:'功',light:'身'};
function itemIcon(id){const src=ICONS[id];return src?`<img src="${artURL(src)}" alt="" decoding="async">`:`<span>${findItem(id)?.icon||'◇'}</span>`}
function itemStats(i){return [i.atk?'攻击 +'+i.atk:'',i.def?'防御 +'+i.def:'',i.hp?'气血 +'+i.hp:''].filter(Boolean).join(' · ')||'—'}
function setBagView(view){if(battleBusy||S.battle)return;bagView=['items','gear','martial'].includes(view)?view:'gear';render()}
function openMartial(){if(battleBusy||S.battle){toast('交锋期间不能修习或更换功法。');return}closeModal();bagView='martial';switchTab('bag')}
function openGear(slot){if(battleBusy||S.battle)return;if(GEAR_SLOTS[slot])gearSlot=slot;bagView='gear';render()}
function pickGearSlot(t){if(GEAR_SLOTS[t]){gearSlot=t;render()}}
function pickMartialSlot(t){if(MARTIAL_TYPES[t]){martialSlot=t;render()}}
function unequipGear(t){if(battleBusy||S.battle||!OPTIONAL_GEAR.includes(t)||!S.gear[t])return;const n=findItem(S.gear[t]).name;S.gear[t]=null;S.hp=Math.min(S.hp,stats().hp);render();toast('已卸下'+n)}
function bagTabs(){return `<div class="bag-tabs" role="tablist">${[['items','背包',S.inventory.length+(S.potions?1:0)+' 件'],['gear','装备',''],['martial','武学',martialPoints()+' 点']].map(([id,label,n])=>`<button role="tab" aria-selected="${bagView===id}" class="${bagView===id?'on':''}" onclick="setBagView('${id}')">${label}${n?`<small>${n}</small>`:''}</button>`).join('')}</div>`}
function slotBtn(on,fn,icon,label,name,sub){return `<button class="slot ${on?'on':''}" onclick="${fn}" aria-pressed="${on}"><span class="slot-icon">${icon}</span><span class="slot-copy"><small>${label}</small><strong>${name}</strong><em>${sub}</em></span></button>`}
function dollHTML(left,right,foot=''){return `<div class="doll"><div class="doll-col">${left}</div><div class="doll-figure">${heroSVG()}</div><div class="doll-col">${right}</div>${foot?`<div class="doll-foot">${foot}</div>`:''}</div>`}
function gearSlotBtn(t){const id=S.gear[t],i=id&&findItem(id);return slotBtn(gearSlot===t,`pickGearSlot('${t}')`,i?itemIcon(id):'<span class="slot-empty">＋</span>',GEAR_SLOTS[t],i?i.name:'未佩戴',i?itemStats(i):'点击挑选')}
function diffChips(id){const i=findItem(id),cur=stats(),n=stats({...S,gear:{...S.gear,[i.type]:id}});return [['攻击',n.atk-cur.atk],['防御',n.def-cur.def],['气血上限',n.hp-cur.hp]].filter(x=>x[1]).map(([k,v])=>`<span class="diff ${v>0?'up':'down'}">${k} ${v>0?'+':''}${v} ${v>0?'▲':'▼'}</span>`).join('')||'<span class="diff">属性不变</span>'}
function renderGear(){const st=stats(),cur=S.gear[gearSlot],list=S.inventory.filter(id=>findItem(id).type===gearSlot).sort((a,b)=>(b===cur)-(a===cur)||findItem(b).price-findItem(a).price);
return `${dollHTML(gearSlotBtn('head')+gearSlotBtn('armor')+gearSlotBtn('boots'),gearSlotBtn('weapon')+gearSlotBtn('wrist')+gearSlotBtn('charm'),`<div class="doll-stats"><span>攻击<b>${st.atk}</b></span><span>防御<b>${st.def}</b></span><span>气血<b>${S.hp}/${st.hp}</b></span></div>`)}<h3 class="pick-title">更换${GEAR_SLOTS[gearSlot]} <span class="tag">${list.length} 件可选</span></h3><div class="pick-list">${list.map(id=>{const i=findItem(id),on=cur===id;return `<div class="pick ${on?'on':''}"><span class="pick-icon">${itemIcon(id)}</span><div class="pick-copy"><strong>${i.name}${i.drop?' <span class="tag">战利品</span>':''}</strong><small>${itemStats(i)}</small><div>${on?'<span class="diff">当前佩戴</span>':diffChips(id)}</div></div>${on?(OPTIONAL_GEAR.includes(gearSlot)?`<button class="ghost" onclick="unequipGear('${gearSlot}')">卸下</button>`:'<button disabled>佩戴中</button>'):`<button class="primary" onclick="equip('${id}')">换上</button>`}</div>`}).join('')||`<p class="empty">行囊里还没有${GEAR_SLOTS[gearSlot]}。</p>`}</div><div class="chiprow"><button class="ghost" onclick="switchTab('shop')">去青石集市添置 →</button></div>`}
function martialSeal(m){return `<span class="seal-icon type-${m.type}">${m.name[0]}</span>`}
function martialSlotBtn(t){const id=S.martial.slots[t],m=id&&martialFind(id);return slotBtn(martialSlot===t,`pickMartialSlot('${t}')`,m?martialSeal(m):`<span class="slot-empty">${MARTIAL_GLYPH[t]}</span>`,MARTIAL_TYPES[t],m?m.name:'未运用',m?martialRank(id)+' 重':'点击挑选')}
function renderMartialView(){const t=martialSlot,cur=S.martial.slots[t];
return `${dollHTML(martialSlotBtn('move')+martialSlotBtn('inner'),martialSlotBtn('light')+`<div class="doll-stats"><span>可用<b>${martialPoints()}</b></span><span>累计<b>${martialBudget()}</b></span><span>已用<b>${martialSpent()}</b></span></div>`)}<p class="note">武学点：习武、胜战各 +1，升级 +2。学习 2 点、二重 3 点、三重 5 点，购谱铜钱只在首次学习时支付。每类只运用一门，交锋中锁定。</p><h3 class="pick-title">${MARTIAL_TYPES[t]} · ${t==='move'?'主动出招':t==='inner'?'根基取舍':'进退之道'}</h3><div class="pick-list">${MARTIAL.filter(m=>m.type===t).map(m=>{const r=martialRank(m.id),on=cur===m.id,cost=r===0?2:r===1?3:5,can=m.unlock(S),canStudy=r<3&&martialPoints()>=cost&&(r||(can&&S.gold>=m.cost));
return `<div class="pick ${on?'on':''} ${!r&&!can?'locked':''}"><span class="pick-icon">${martialSeal(m)}</span><div class="pick-copy"><strong>${m.name} <span class="tag">${r?r+' / 3 重':can?'可学习':'未解锁'}</span>${on?' <span class="tag">运用中</span>':''}</strong><small>${martialDesc(m.id,r||1)}</small>${r&&r<3?`<small class="next">下一重：${martialDesc(m.id,r+1)}</small>`:''}${r?'':`<small class="next">${m.source}${can?'':' · 条件未达'}</small>`}</div><div class="pick-actions">${r<3?`<button onclick="studyMartial('${m.id}')" ${canStudy?'':'disabled'}>${r?'升至 '+(r+1)+' 重':'学习'} · ${cost} 点${!r&&m.cost?' + '+m.cost+' 文':''}</button>`:'<span class="tag">三重圆满</span>'}${r&&!on?`<button class="primary" onclick="equipMartial('${m.id}')">运用</button>`:''}${on&&t!=='move'?`<button class="ghost" onclick="unequipMartial('${t}')">暂停运用</button>`:''}</div></div>`}).join('')}</div>`}
function renderItems(){const order=GEAR_TYPES,inv=[...S.inventory].sort((a,b)=>order.indexOf(findItem(a).type)-order.indexOf(findItem(b).type)),full=S.hp>=stats().hp;
return `<p class="note">行囊里的全部家当。佩戴中的装备不可出售；想换装请点「去装备」。</p><div class="shop-grid"><div class="item"><div class="item-top"><span class="item-icon">${itemIcon('potion')}</span><span class="tag">×${S.potions}</span></div><h3>回春散</h3><p>${findItem('potion').desc}</p><button class="primary" onclick="usePotion()" ${S.potions<1||full?'disabled':''}>${S.potions<1?'已用完':full?'气血已满':'服用 · 气血 +40'}</button></div>${inv.map(id=>{const i=findItem(id),on=S.gear[i.type]===id;return `<div class="item ${on?'worn':''}"><div class="item-top"><span class="item-icon">${itemIcon(id)}</span><span class="tag">${on?'已佩戴':GEAR_SLOTS[i.type]}</span></div><h3>${i.name}</h3><p>${i.desc}</p><button onclick="openGear('${i.type}')">${on?'查看装备栏':'去装备'}</button>${!on&&i.price>0?`<button class="ghost" style="margin-top:7px" onclick="sell('${id}')">出售 · +${Math.floor(i.price/2)} 文</button>`:''}</div>`}).join('')}</div>`}
function renderBag(){if(!['items','gear','martial'].includes(bagView))bagView='gear';$('content').innerHTML=`<div class="content-head"><div><div class="section-label">${bagView==='martial'?'THE WAY WITHIN':'WHAT YOU CARRY'}</div><h2>${bagView==='items'?'行囊与旧物':bagView==='gear'?'披挂上阵':'一招一式，自成江湖'}</h2></div><span class="tag">铜钱 ${S.gold} 文</span></div>${bagTabs()}${bagView==='items'?renderItems():bagView==='gear'?renderGear():renderMartialView()}`}
function renderMartial(){bagView='martial';renderBag()}
function studyMartial(id){""")

# market shows the same icons
sub('<span class="item-icon">${i.icon}</span>', '<span class="item-icon">${itemIcon(i.id)}</span>')

# ---------- CSS ----------
sub('</style></head>', r"""
/* 行囊: tabs, figure-with-slots, pick lists. */
.bag-tabs{display:flex;gap:4px;padding:4px;margin:0 0 16px;background:#e9e6d4;border-radius:10px}
.bag-tabs button{flex:1;border:0;background:transparent;min-height:42px;padding:8px;font-size:14px;border-radius:7px;color:#476352}
.bag-tabs button:hover:not(:disabled){transform:none;box-shadow:none;background:#f5f2e4}
.bag-tabs button.on,.bag-tabs button.on:hover{background:var(--deep);color:#fff8e9;box-shadow:0 2px 8px #173b3933}
.bag-tabs small{margin-left:6px;font-size:11px;opacity:.75}
.doll{display:grid;grid-template-columns:1fr 190px 1fr;gap:12px;align-items:center;padding:14px;border-radius:12px;background:radial-gradient(ellipse at 50% 45%,#fff4d4,#dfe5cf 72%);border:1px solid #d3d4bf}
.doll-col{display:grid;gap:10px;align-content:center}
.doll-foot{grid-column:1/-1}.doll-foot .doll-stats{max-width:420px;margin:0 auto}
.doll-figure{height:300px}.doll-figure svg{width:100%;height:100%;filter:drop-shadow(0 8px 6px #183e332b)}
.slot{display:flex;align-items:center;gap:10px;text-align:left;padding:8px 10px;background:#fbf8eccc;border:1px solid #c9cdb8;border-radius:10px;min-height:66px;width:100%}
.slot.on{border-color:var(--red);box-shadow:0 0 0 2px #af4e3533;background:#fff8ea}
.slot-icon{flex:none;width:50px;height:50px;border-radius:8px;background:#e7e2cc;display:grid;place-items:center;overflow:hidden;border:1px solid #d3cdb2}
.slot-icon img,.pick-icon img{width:100%;height:100%;object-fit:contain;display:block}
.slot-copy{min-width:0}.slot-copy small{display:block;font-size:11px;color:var(--muted);letter-spacing:1px}
.slot-copy strong{display:block;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.slot-copy em{display:block;font-style:normal;font-size:12px;color:#8a6a43}
.slot-empty{font:22px "Songti SC","SimSun",serif;color:#a99f80}
.doll-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.doll-stats span{background:#f3efdf;border-radius:8px;padding:8px 4px;text-align:center;font-size:11px;color:var(--muted)}
.doll-stats b{display:block;font-size:16px;color:var(--ink);margin-top:2px}
.pick-title{margin:20px 0 10px}
.pick-list{display:grid;gap:8px}
.pick{display:flex;align-items:center;gap:12px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#f8f4e6}
.pick.on{border-color:#9a4f32;background:#fbefe0}.pick.locked{opacity:.62}
.pick-icon{flex:none;width:58px;height:58px;border-radius:8px;background:#ece7d2;display:grid;place-items:center;overflow:hidden}
.pick-copy{flex:1;min-width:0}.pick-copy strong{display:block;font-size:15px;font-weight:600}
.pick-copy small{display:block;font-size:12px;color:#5d6d5f;line-height:1.6;margin-top:3px}.pick-copy small.next{color:#8a7a5c}
.pick>button,.pick-actions button{flex:none;padding:8px 14px}
.pick-actions{display:grid;gap:6px;flex:none}
.diff{display:inline-block;margin:4px 6px 0 0;font-size:12px;padding:1px 6px;border-radius:4px;background:#ebe8d8;color:#5d6d5f}
.diff.up{background:#e1eedd;color:#2f6b45}.diff.down{background:#f6e0d8;color:#a2412a}
.seal-icon{width:100%;height:100%;display:grid;place-items:center;font:600 24px "Songti SC","STSong","SimSun",serif;color:#fff2d6;background:#af4e35;border:3px double #dba78a;border-radius:6px}
.seal-icon.type-inner{background:#2f5d52;border-color:#8fb3a2}.seal-icon.type-light{background:#4f6585;border-color:#a3b4cc}
.item-icon:has(img){filter:none}.item-icon img{width:46px;height:46px;object-fit:contain;display:block}
.item.worn{border-color:#9a4f32}
@media(max-width:760px){.doll-foot .doll-stats{grid-template-columns:repeat(3,1fr)}.doll-foot .doll-stats span{display:block;text-align:center}.doll{grid-template-columns:1fr 88px 1fr;gap:6px;padding:10px 7px}.doll-figure{height:190px}.slot{flex-direction:column;align-items:flex-start;gap:5px;padding:7px;min-height:0}.slot-icon{width:40px;height:40px}.slot-copy strong{font-size:13px;white-space:normal}.slot-copy em{font-size:11px}.doll-stats{grid-template-columns:1fr;gap:4px}.doll-stats span{display:flex;justify-content:space-between;align-items:center;padding:5px 7px}.doll-stats b{font-size:13px;margin:0}.pick{flex-wrap:wrap}.pick>button,.pick-actions{width:100%}.pick-actions{grid-auto-flow:column;grid-auto-columns:1fr}.pick-actions button{width:100%}}
</style></head>""")
