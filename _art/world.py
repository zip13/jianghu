# 大富翁行路（合并奇遇+寻宝）、药圃种植、武功晋升（参考天龙八部）、同境历练、难度优化
# exec'd by build.py AFTER fun.py and bag.py (shares `s`, `sub`, `sys`).

def cut(start, end):
    global s
    a = s.find(start); b = s.find(end, a)
    if a < 0 or b < 0 or s.find(start, a + 1) >= 0:
        sys.exit(f'world cut anchor problem: {start!r}')
    s = s[:a] + s[b:]

# ---------- CSS ----------
sub('</style></head>', r"""
/* 大富翁行路、药圃、境界。 */
.board{border:1px solid var(--line);border-radius:12px;padding:14px;margin:0 0 16px;background:#f3eeda}
.board-head{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:10px}
.board-head b{color:var(--red);font-size:16px}
.track{display:flex;gap:6px;overflow-x:auto;padding:6px 2px 10px;scrollbar-width:thin}
.tile{flex:0 0 64px;height:78px;border:1px solid #d3ceb6;border-radius:9px;background:#faf6e6;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;position:relative;font-size:11px;color:#5d6d5f}
.tile.here{border:2px solid var(--red);background:#fff3dc;box-shadow:0 0 0 3px #af4e3533}
.tile-icon{font:22px "Songti SC","SimSun",serif;color:#9a4f32}
.tile-name{font-size:10px;letter-spacing:1px}
.tile.type-encounter .tile-icon{color:#4f6585}.tile.type-treasure .tile-icon{color:#b68d43}.tile.type-garden .tile-icon{color:#2f6b45}.tile.type-rest .tile-icon{color:#5d8a6a}.tile.type-chance .tile-icon{color:#7a5a8a}.tile.type-market .tile-icon{color:#a5512f}.tile.type-battle .tile-icon{color:#a2412a}.tile.type-start .tile-icon{color:#173b39}
.token{position:absolute;top:-11px;left:50%;transform:translateX(-50%);background:var(--red);color:#fff;font-size:10px;padding:1px 7px;border-radius:9px;white-space:nowrap}
.board-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.hint-card{border:1px dashed #c9a46c;border-radius:9px;padding:14px;background:#f7ecd5;color:#6b5a40;line-height:1.7;margin-top:4px}
.garden-grid{display:grid;gap:10px}
.plot{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--line);border-radius:10px;background:#f6f2e2}
.plot.ready{border-color:#2f6b45;background:#eaf2e2}
.plot-glyph{flex:none;width:46px;height:46px;border-radius:8px;background:#e7e2cc;display:grid;place-items:center;font:22px "Songti SC","SimSun",serif;color:#9a4f32}
.plot-copy{flex:1;min-width:0}.plot-copy strong{display:block;font-size:15px}.plot-copy small{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.plot-actions{display:grid;gap:5px;flex:none}.plot-actions button{font-size:12px;padding:7px 10px}
.treasure-box{text-align:center;padding:8px 0}.treasure-glyph{font:40px "Songti SC","SimSun",serif;color:#b68d43}.treasure-box .loot{color:#9a4f32}
.realm-panel{border:1px solid #c9a46c;border-radius:10px;padding:14px;margin:0 0 16px;background:linear-gradient(120deg,#f7ecd5,#f3eeda)}
.realm-head{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px}
.realm-name{font:600 20px "Songti SC","SimSun",serif;color:#9a4f32}
.realm-next{font-size:12px;color:var(--muted)}
.realm-panel .bar{margin:10px 0 8px}
@media(max-width:760px){.tile{flex:0 0 52px;height:66px}.tile-icon{font-size:19px}.tile-name{font-size:9px}.plot{flex-wrap:wrap}.plot-actions{width:100%;grid-auto-flow:column;grid-auto-columns:1fr}}
</style></head>""")

# ---------- new state fields ----------
sub("feats:{reads:0,crits:0,flawless:0,drops:0}};}",
    "feats:{reads:0,crits:0,flawless:0,drops:0},rolls:3,rollsMax:3,pos:0,realm:0,xiuwei:0,encTriggered:false,garden:[{seed:null,days:0},{seed:null,days:0},{seed:null,days:0}]};}")

# ---------- stats: realm bonus + peerless effects + drain ----------
sub("let reduction=0,guard=0,opening=0,regenEvery=0;", "let reduction=0,guard=0,opening=0,regenEvery=0,drain=0;")
sub("if(inner==='zhouliu')regenEvery=4-r;if(light==='qingfeng')reduction=l;if(light==='yanshui')guard=2*l;if(light==='liuying')opening=3*l;return{atk:a,def:d,hp:h,reduction,guard,opening,regenEvery}}",
    "if(inner==='zhouliu')regenEvery=4-r;if(inner==='beiming'){h+=10*r;drain=2*r}if(inner==='yijin'){a+=r;d+=2*r;h+=8*r}if(light==='qingfeng')reduction=l;if(light==='yanshui')guard=2*l;if(light==='liuying')opening=3*l;if(light==='lingbo')reduction=2*l+1;if(light==='douzhuan'){guard=3*l;reduction=l}const rl=REALMS[clamp(s.realm||0,0,REALMS.length-1)];a+=rl.atk;d+=rl.def;h+=rl.hp;return{atk:a,def:d,hp:h,reduction,guard,opening,regenEvery,drain}}")

# ---------- martialDesc for peerless arts ----------
sub("先手普攻与招式均生效。`};return desc[id]}",
    "先手普攻与招式均生效。`,liumai:`消耗 4 真气：${210+20*(r-1)}% 攻击，无视敌方防御。六脉剑气，无坚不摧。`,xianglong:`消耗 3 真气：${150+15*(r-1)}% 攻击，敌防御仅计 50%。降龙十八掌，至刚至猛。`,beiming:`气血上限 +${10*r}；普攻或招式命中时恢复 ${2*r} 气血。北冥神功，吸化内息。`,yijin:`攻击 +${r}，防御 +${2*r}，气血上限 +${8*r}。易筋洗髓，内外兼修。`,lingbo:`每次受击额外减伤 ${2*r+1}（至少承受 1）。凌波微步，飘忽难测。`,douzhuan:`招架额外减伤 ${3*r}，且每次受击减伤 ${r}。斗转星移，借力打力。`};return desc[id]}")

# ---------- peerless arts (天龙八部) ----------
sub("{id:'liuying',name:'掠影步',type:'light',source:'游侠步谱 · 等级 4 · 另需 45 文',unlock:s=>s.level>=4,cost:45}\n];",
    "{id:'liuying',name:'掠影步',type:'light',source:'游侠步谱 · 等级 4 · 另需 45 文',unlock:s=>s.level>=4,cost:45},\n{id:'liumai',name:'六脉神剑',type:'move',source:'大理段氏绝学 · 融会贯通可修',unlock:s=>realmLevel(s)>=2,cost:120,qi:4},\n{id:'xianglong',name:'降龙十八掌',type:'move',source:'丐帮镇帮绝学 · 出神入化可修',unlock:s=>realmLevel(s)>=3,cost:180,qi:3},\n{id:'beiming',name:'北冥神功',type:'inner',source:'逍遥派绝学 · 出神入化可修',unlock:s=>realmLevel(s)>=3,cost:150},\n{id:'yijin',name:'易筋经',type:'inner',source:'少林镇寺之宝 · 返璞归真可修',unlock:s=>realmLevel(s)>=4,cost:220},\n{id:'lingbo',name:'凌波微步',type:'light',source:'逍遥派步法 · 融会贯通可修',unlock:s=>realmLevel(s)>=2,cost:100},\n{id:'douzhuan',name:'斗转星移',type:'light',source:'姑苏慕容绝学 · 出神入化可修',unlock:s=>realmLevel(s)>=3,cost:160}\n];")

# ---------- battle: peerless move multipliers + drain ----------
sub("const mult=move.id==='polang'?1.65+.15*(rank-1):move.id==='huifeng'?1.2+.1*(rank-1):1.05+.1*(rank-1);damage=Math.max(3,Math.round(attack*mult-e.def*(move.id==='polang'?.35:1)));",
    "const mult=move.id==='polang'?1.65+.15*(rank-1):move.id==='huifeng'?1.2+.1*(rank-1):move.id==='liumai'?2.1+.2*(rank-1):move.id==='xianglong'?1.5+.15*(rank-1):1.05+.1*(rank-1);const defMul=move.id==='polang'?.35:move.id==='liumai'?0:move.id==='xianglong'?.5:1;damage=Math.max(3,Math.round(attack*mult-e.def*defMul));")
sub("if(it==='guard'&&(action==='attack'||move.id!=='polang'))damage=Math.max(1,Math.floor(damage*.5));",
    "if(it==='guard'&&(action==='attack'||(move.id!=='polang'&&move.id!=='liumai')))damage=Math.max(1,Math.floor(damage*.5));")
sub("if(action==='skill'&&move.id==='huifeng'){fx.healed=Math.min(3*rank,actual,st.hp-S.hp);S.hp+=fx.healed}",
    "if(action==='skill'&&move.id==='huifeng'){fx.healed=Math.min(3*rank,actual,st.hp-S.hp);S.hp+=fx.healed}if(st.drain&&(action==='attack'||action==='skill')){const dr=Math.min(st.drain,st.hp-S.hp);if(dr>0){fx.healed=(fx.healed||0)+dr;S.hp+=dr}}")

# ---------- enemyOf (supports dynamically scaled rivals) ----------
sub("function intent(b=S.battle){return ENEMIES[b.id].pattern[b.turn%ENEMIES[b.id].pattern.length]}",
    "function enemyOf(b){return b.e||ENEMIES[b.id]}\nfunction intent(b=S.battle){const e=enemyOf(b);return e.pattern[b.turn%e.pattern.length]}")
sub("const b=S.battle,e=ENEMIES[b.id],it=fx?.intent||intent()", "const b=S.battle,e=enemyOf(b),it=fx?.intent||intent()")
sub("const e=ENEMIES[b.id],it=intent(),st=stats()", "const e=enemyOf(b),it=intent(),st=stats()")
sub("function stageURL(id){return artURL(ART[STAGE[id]])}", "function stageURL(id){return artURL(ART[STAGE[id]]||ART.bg_road)}")

# ---------- battle origin (board vs journey) ----------
sub("S.battle={id,hp:e.hp,maxHp:e.hp,turn:0,qi:2,logs:", "S.battle={id,origin:'journey',hp:e.hp,maxHp:e.hp,turn:0,qi:2,logs:")
sub("S.battle=null;S.tab='journey';", "S.battle=null;S.tab=b.origin==='board'?'encounter':'journey';", count=3)

# ---------- 修为 gain from training / wins ----------
sub("S.energy--;S.trained++;gainXP(tx);", "S.energy--;S.trained++;gainXP(tx);S.xiuwei+=2;checkRealm();")
sub("gainXP(xp);S.gold+=gold;const got=[];", "gainXP(xp);S.gold+=gold;S.xiuwei+=3+(b.id==='elite'?3:0)+(b.id==='boss'?9:0);checkRealm();const got=[];")

# ---------- sleep: reset dice, grow garden ----------
sub("S.eventResult=null;S.energy=3;S.hp=Math.min(stats().hp,S.hp+30);S.tab='encounter';render();showEnding();return}",
    "S.eventResult=null;S.energy=3;S.rolls=3;S.encTriggered=false;growGarden();S.hp=Math.min(stats().hp,S.hp+30);S.tab='encounter';render();showEnding();return}")
sub("S.day++;S.energy=3;S.hp=Math.min(stats().hp,S.hp+30);S.eventDone=false;",
    "S.day++;S.energy=3;S.rolls=3;S.encTriggered=false;growGarden();S.hp=Math.min(stats().hp,S.hp+30);S.eventDone=false;")

# ---------- validate: normalize new fields + allow rival battles ----------
sub("normalizeFun(s);if(legacy){", "normalizeFun(s);normalizeWorld(s);if(legacy){")
sub("if(s.battle){const b=s.battle;if(!Object.prototype.hasOwnProperty.call(ENEMIES,b.id)||!Number.isInteger(b.hp)||b.hp<=0||b.hp>ENEMIES[b.id].hp||b.maxHp!==ENEMIES[b.id].hp||!Number.isInteger(b.turn)||b.turn<0||!Number.isInteger(b.qi)||b.qi<0||b.qi>4||!Array.isArray(b.logs))throw Error('战斗数据损坏');",
    "if(s.battle){const b=s.battle;if(b.id!=='rival'&&!Object.prototype.hasOwnProperty.call(ENEMIES,b.id))throw Error('战斗数据损坏');const bmax=b.e&&Number.isInteger(b.e.hp)?b.e.hp:ENEMIES[b.id]?ENEMIES[b.id].hp:0;if(!bmax||!Number.isInteger(b.hp)||b.hp<=0||b.hp>bmax||b.maxHp!==bmax||!Number.isInteger(b.turn)||b.turn<0||!Number.isInteger(b.qi)||b.qi<0||b.qi>4||!Array.isArray(b.logs))throw Error('战斗数据损坏');")

# ---------- replace the encounter tab with the 大富翁 board ----------
cut("function renderEvent(){", "function choose(i){")
sub("function choose(i){", r"""
const REALMS=[
 {name:'初窥门径',need:0,atk:0,def:0,hp:0,desc:'武学之门初开，一招一式尚无章法。'},
 {name:'登堂入室',need:40,atk:2,def:1,hp:12,desc:'招法已有章法，可堪一用。'},
 {name:'融会贯通',need:120,atk:4,def:2,hp:26,desc:'诸般武学互为印证，见招拆招。'},
 {name:'出神入化',need:280,atk:7,def:4,hp:44,desc:'收发由心，出手已不拘成法。'},
 {name:'返璞归真',need:520,atk:11,def:6,hp:66,desc:'重剑无锋，大巧不工。'}
];
function realmLevel(s=S){let lv=0;for(let i=0;i<REALMS.length;i++)if((s.xiuwei||0)>=REALMS[i].need)lv=i;return lv}
function checkRealm(){const lv=realmLevel(S);if(lv>S.realm){S.realm=lv;const r=REALMS[lv];sfx('title');banner('武功晋升 · '+r.name,r.desc+' · 气血、攻击、防御提升');log('武功晋升至「'+r.name+'」：'+r.desc)}}
const BOARD=[
 {name:'栖霞渡口',type:'start',icon:'渡'},
 {name:'江湖奇遇',type:'encounter',icon:'遇'},
 {name:'寻宝',type:'treasure',icon:'宝'},
 {name:'药圃',type:'garden',icon:'圃'},
 {name:'驿站',type:'rest',icon:'驿'},
 {name:'江湖奇遇',type:'encounter',icon:'遇'},
 {name:'寻宝',type:'treasure',icon:'宝'},
 {name:'机缘',type:'chance',icon:'缘'},
 {name:'集市',type:'market',icon:'市'},
 {name:'江湖奇遇',type:'encounter',icon:'遇'},
 {name:'寻宝',type:'treasure',icon:'宝'},
 {name:'山道',type:'battle',icon:'战'},
 {name:'江湖奇遇',type:'encounter',icon:'遇'},
 {name:'药圃',type:'garden',icon:'圃'},
 {name:'机缘',type:'chance',icon:'缘'},
 {name:'驿站',type:'rest',icon:'驿'}
];
const PLANTS=[
 {id:'grass',name:'回春草',icon:'草',cost:12,grow:2,yield:'回春散 ×2',desc:'种下两日，收获回春散。'},
 {id:'honey',name:'金银花',icon:'花',cost:18,grow:3,yield:'铜钱 +50',desc:'花开三日，可换五十文。'},
 {id:'spirit',name:'灵芝',icon:'芝',cost:45,grow:5,yield:'修为 +15',desc:'五日落成，服之助长修为。'}
];
function plantFind(id){return PLANTS.find(p=>p.id===id)}
const TREASURE=[
 {t:'gold',w:20,min:30,max:80,name:'一袋碎银',desc:'沉甸甸的，够买几件趁手家伙。'},
 {t:'potion',w:18,n:2,name:'回春散',desc:'两包伤药，行走江湖的底气。'},
 {t:'xiuwei',w:15,n:6,name:'前人武学手札',desc:'字迹潦草，却记着半套吐纳心得。'},
 {t:'gear',w:12,name:'一件旧兵器',desc:'尘封的兵刃，尚可一用。'},
 {t:'charm',w:8,name:'稀有佩饰',desc:'不知哪位前辈遗落的佩饰。'},
 {t:'hp',w:10,n:20,name:'山泉',desc:'清冽甘甜，解渴也解乏。'}
];
function rollDice(){if(battleBusy||S.battle)return;if(S.rolls<1){toast('今日摇骰次数已用完，歇息后刷新。');return}S.rolls--;const n=1+Math.floor(rand()*6);S.pos=(S.pos+n)%BOARD.length;const t=BOARD[S.pos];log('掷出 '+n+' 点，行至「'+t.name+'」。');if(!landTile(t))render()}
function landTile(t){let rendered=true;switch(t.type){
 case 'start':{S.gold+=5;S.hp=Math.min(stats().hp,S.hp+5);sfx('coin');banner('回到渡口','铜钱 +5 · 气血 +5');rendered=false;break}
 case 'encounter':{S.encTriggered=true;rendered=false;break}
 case 'treasure':{treasureHunt();rendered=false;break}
 case 'garden':{openGarden();rendered=false;break}
 case 'rest':{const h=Math.min(20,stats().hp-S.hp);S.hp+=h;sfx('heal');banner('驿站歇脚','气血 +'+h);rendered=false;break}
 case 'chance':{chanceEvent();rendered=false;break}
 case 'market':{switchTab('shop');break}
 case 'battle':{startBoardBattle();break}
}return rendered}
function revealEncounter(){if(battleBusy||S.battle)return;S.encTriggered=true;render()}
function chanceEvent(){const roll=Math.floor(rand()*6);let t,d;if(roll===0){S.xiuwei+=5;checkRealm();t='静坐悟道';d='修为 +5'}else if(roll===1){S.insight++;t='灵台一清';d='心悟 +1'}else if(roll===2){S.gold+=20;t='捡到钱袋';d='铜钱 +20'}else if(roll===3){S.potions++;t='采得草药';d='回春散 +1'}else if(roll===4){S.hp=Math.min(stats().hp,S.hp+15);t='掬饮山泉';d='气血 +15'}else{S.atk++;t='偶得心法';d='攻击 +1'}log('机缘「'+t+'」：'+d+'。');sfx('read');banner('机缘 · '+t,d)}
function treasureHunt(){modal('寻宝',`<div class="treasure-box"><div class="treasure-glyph">✦</div><p class="note">你在荒野中发现一处藏宝。要不要翻开看看？</p></div>`,[{text:'再等等',fn:'closeModal()'},{text:'翻开宝箱',fn:'revealTreasure()',primary:true}])}
function revealTreasure(){const pool=[];for(const tr of TREASURE)for(let i=0;i<tr.w;i++)pool.push(tr);const tr=pool[Math.floor(rand()*pool.length)];let got='';if(tr.t==='gold'){const g=tr.min+Math.floor(rand()*(tr.max-tr.min+1));S.gold+=g;got='铜钱 +'+g+' 文'}else if(tr.t==='potion'){S.potions+=tr.n;got='回春散 ×'+tr.n}else if(tr.t==='xiuwei'){S.xiuwei+=tr.n;checkRealm();got='修为 +'+tr.n}else if(tr.t==='hp'){const h=Math.min(tr.n,stats().hp-S.hp);S.hp+=h;got='气血 +'+h}else if(tr.t==='gear'){const ids=['iron','silk','vest','moon','bracer','cloudboot','jadecrown','windboot','dragonring'].filter(id=>!S.inventory.includes(id));if(ids.length){const id=ids[Math.floor(rand()*ids.length)];S.inventory.push(id);got='获得 '+findItem(id).name}else{S.gold+=40;got='铜钱 +40 文（已得装备换成现钱）'}}else if(tr.t==='charm'){const ids=DROP_IDS.filter(id=>!S.inventory.includes(id));if(ids.length){const id=ids[Math.floor(rand()*ids.length)];S.inventory.push(id);S.feats.drops++;got='获得稀有佩饰「'+findItem(id).name+'」'}else{S.gold+=50;got='铜钱 +50 文'}}log('寻宝所得：'+got+'。');sfx('coin');banner('寻宝 · '+tr.name,got);modal('寻得宝物',`<div class="treasure-box"><div class="treasure-glyph">${tr.name[0]}</div><h3 style="margin:10px 0 4px">${tr.name}</h3><p>${tr.desc}</p><p class="loot">收获 · ${got}</p></div>`,[{text:'收入行囊',fn:'closeModal()',primary:true}])}
function growGarden(){for(const p of S.garden)if(p.seed)p.days++}
function gardenPlotHTML(i){const p=S.garden[i],pl=plantFind(p.seed);if(!pl)return `<div class="plot"><div class="plot-glyph">＋</div><div class="plot-copy"><strong>空地</strong><small>可播种</small></div><div class="plot-actions">${PLANTS.map(x=>`<button class="ghost" onclick="plantSeed(${i},'${x.id}')" ${S.gold<x.cost?'disabled':''}>${x.icon} ${x.name} · ${x.cost}文</button>`).join('')}</div></div>`;const ready=p.days>=pl.grow;return `<div class="plot ${ready?'ready':''}"><div class="plot-glyph">${pl.icon}</div><div class="plot-copy"><strong>${pl.name}</strong><small>${ready?'已成熟，可收获':'生长 '+p.days+' / '+pl.grow+' 日'}</small></div><div class="plot-actions">${ready?`<button class="primary" onclick="harvestPlot(${i})">收获 · ${pl.yield}</button>`:`<button disabled>${pl.grow-p.days} 日后成熟</button>`}</div></div>`}
function openGarden(){if(battleBusy||S.battle)return;modal('药圃 · 一方田园',`<p class="note">择一方地，种几株草木。歇息一夜，草木生长一日；成熟后可收获。</p><div class="garden-grid">${S.garden.map((_,i)=>gardenPlotHTML(i)).join('')}</div>`,[{text:'收好锄头',fn:'closeModal()',primary:true}])}
function plantSeed(i,id){if(battleBusy||S.battle)return;const pl=plantFind(id);if(!pl||S.garden[i].seed||S.gold<pl.cost)return;S.gold-=pl.cost;S.garden[i]={seed:id,days:0};log('在药圃种下'+pl.name+'。');sfx('coin');openGarden()}
function harvestPlot(i){if(battleBusy||S.battle)return;const p=S.garden[i],pl=plantFind(p.seed);if(!pl||p.days<pl.grow)return;S.garden[i]={seed:null,days:0};let got;if(pl.id==='grass'){S.potions+=2;got='回春散 ×2'}else if(pl.id==='honey'){S.gold+=50;got='铜钱 +50'}else{S.xiuwei+=15;checkRealm();got='修为 +15'}log('收获'+pl.name+'，获得'+got+'。');sfx('heal');banner('丰收 · '+pl.name,got);openGarden()}
function rivalSpec(s=S){const lv=s.level;return{name:'同境散修',hp:40+lv*13,atk:10+lv*2,def:2+lv,xp:18+lv*4,gold:20+lv*3,desc:'与你同境，势均力敌的对手。',pattern:['quick','heavy','guard','rest']}}
function startRival(){if(battleBusy)return;importEpoch++;window.pendingImport=null;if(S.battle||S.energy<1)return;const e=rivalSpec();S.energy--;S.battle={id:'rival',origin:'journey',e,hp:e.hp,maxHp:e.hp,turn:0,qi:2,logs:['你与'+e.name+'拉开架势。'+martialActive().name+'消耗 '+martialActive().qi+' 真气，普攻与招架各回复 1 真气。']};render()}
function rivalCard(){const r=rivalSpec();return `<div class="map-card staged" style="background-image:linear-gradient(100deg,#f8f4e6 48%,#f8f4e6d9 64%,#f8f4e633),url(${stageURL('rival')})"><div><h3>同境试炼 <span class="tag">${r.name}</span></h3><p>${r.desc} 随你的等级成长。<br>气血 ${r.hp} · 攻击 ${r.atk} · 防御 ${r.def}<br>获胜：${r.xp} 阅历 / ${r.gold} 文</p></div><button class="primary" onclick="startRival()" ${S.energy<1?'disabled':''}>前往 · 1 行动</button></div>`}
function startBoardBattle(){if(battleBusy||S.battle)return;importEpoch++;window.pendingImport=null;let id;if(S.level<3)id='wolf';else if(S.level<5)id=rand()<.6?'wolf':'bandit';else id=rand()<.4?'wolf':rand()<.75?'bandit':'elite';const e=ENEMIES[id];S.battle={id,origin:'board',hp:e.hp,maxHp:e.hp,turn:0,qi:2,logs:['山道相逢，你与'+e.name+'动起手来。']};render()}
function realmPanel(){const r=REALMS[clamp(S.realm||0,0,REALMS.length-1)],n=REALMS[S.realm+1];const prog=n?Math.min(100,Math.round((S.xiuwei-r.need)/(n.need-r.need)*100)):100;return `<div class="realm-panel"><div class="realm-head"><span class="realm-name">${r.name}</span>${n?`<span class="realm-next">距「${n.name}」还需 ${n.need-S.xiuwei} 修为</span>`:'<span class="realm-next">已臻化境</span>'}</div><div class="bar xp"><i style="width:${prog}%"></i></div><p class="note">修为 ${S.xiuwei} · 习武、胜战、机缘、种植灵草皆可增长。境界提升气血、攻击、防御，并解锁天龙八部绝世武功。</p></div>`}
function normalizeWorld(s){if(!Number.isSafeInteger(s.rolls)||s.rolls<0||s.rolls>3)s.rolls=3;if(!Number.isSafeInteger(s.rollsMax)||s.rollsMax<1||s.rollsMax>9)s.rollsMax=3;if(!Number.isSafeInteger(s.pos)||s.pos<0)s.pos=0;if(!Number.isSafeInteger(s.xiuwei)||s.xiuwei<0)s.xiuwei=0;s.realm=realmLevel(s);s.encTriggered=s.encTriggered===true;if(!Array.isArray(s.garden)||s.garden.length!==3)s.garden=[{seed:null,days:0},{seed:null,days:0},{seed:null,days:0}];s.garden=s.garden.map(p=>{const seed=plantFind(p&&p.seed)?p.seed:null;const days=Number.isSafeInteger(p&&p.days)&&p.days>=0?p.days:0;return{seed,days}});if(s.battle&&s.battle.id==='rival'&&(!s.battle.e||!Number.isInteger(s.battle.e.hp)||s.battle.e.hp<1))s.battle.e=rivalSpec(s)}
function boardHTML(){return `<div class="board"><div class="board-head"><span>行至第 ${S.pos+1} / ${BOARD.length} 格</span><span>今日摇骰 <b>${S.rolls}</b> / ${S.rollsMax}</span></div><div class="track">${BOARD.map((t,i)=>`<div class="tile ${i===S.pos?'here':''} type-${t.type}" title="${t.name}"><span class="tile-icon">${t.icon}</span><span class="tile-name">${t.name}</span>${i===S.pos?'<span class="token">你</span>':''}</div>`).join('')}</div><div class="board-actions"><button class="primary" onclick="rollDice()" ${S.rolls<1||S.battle?'disabled':''}>⚄ 摇骰前进（剩 ${S.rolls} 次）</button>${!S.eventDone?`<button onclick="revealEncounter()" ${S.battle?'disabled':''}>◈ 今日奇遇</button>`:''}<button class="ghost" onclick="openGarden()" ${S.battle?'disabled':''}>❧ 药圃</button></div></div>`}
function renderEvent(){const e=currentEvent();let tail;if(S.eventDone){tail=`<div class="result"><h3>${S.eventResult?.label||'今日的选择已落定'}</h3>${S.eventResult?.text||'今天的故事已经写入手记。'}</div><p class="note">今日奇遇已完成。余下时光可继续摇骰寻宝、种植、修行，或去历练。</p><div class="chiprow"><button onclick="switchTab('journey')">去历练 →</button><button onclick="switchTab('shop')">逛集市 →</button>${S.ended?'<button onclick="showEnding()">重读本卷结局</button>':''}</div>`}else if(S.encTriggered){tail=`<p class="event-text">${e.text}</p><div class="choices">${e.choices.map((c,i)=>`<button class="choice" onclick="choose(${i})" ${c.req&&!c.req(S)?'disabled':''}><span><strong><span class="key-hint">${i+1}</span>${c.label}</strong><small>${c.cost}${c.req&&!c.req(S)?' · 条件不足':''}</small></span><span class="arrow">↗</span></button>`).join('')}</div>${martialEventNote(e)}`}else{tail=`<div class="hint-card"><p>今日奇遇尚未遇见。掷出骰子行走江湖，落在「遇」字格便能触发今日故事；也可直接前往。</p></div>`}$('content').innerHTML=`<div class="content-head"><div><div class="section-label">THE ROAD OF JIANGHU · 大富翁行路</div><h2>掷骰行江湖</h2></div><div class="event-number">${String(S.day).padStart(2,'0')}</div></div>${boardHTML()}${tail}`}
function choose(i){""")

# ---------- 历练 tab: add 同境试炼 card ----------
sub("${Object.entries(ENEMIES).map(([id,e],i)=>", "${rivalCard()}${Object.entries(ENEMIES).map(([id,e],i)=>")

# ---------- header / sheet: surface realm ----------
sub("<div class=\"rank\">${S.level<3?'初入江湖':S.level<6?'小有所成':S.level<9?'锋芒初现':'一方侠客'} · Lv.${S.level}</div>",
    "<div class=\"rank\">${S.level<3?'初入江湖':S.level<6?'小有所成':S.level<9?'锋芒初现':'一方侠客'} · Lv.${S.level} · ${REALMS[clamp(S.realm||0,0,REALMS.length-1)].name}</div>")
sub("<div class=\"gear\">${martialSummary()}<br>",
    "<div class=\"gear\"><div style=\"margin-bottom:6px\"><span class=\"tag\">境界 · ${REALMS[clamp(S.realm||0,0,REALMS.length-1)].name}</span> <span class=\"tag\">修为 ${S.xiuwei}</span></div>${martialSummary()}<br>")
sub("<h3>${titleChip()}无名少侠 · Lv.${S.level}</h3>",
    "<h3>${titleChip()}无名少侠 · Lv.${S.level} · ${REALMS[clamp(S.realm||0,0,REALMS.length-1)].name}</h3>")
sub("return `${dollHTML(martialSlotBtn('move')", "return `${realmPanel()}${dollHTML(martialSlotBtn('move')")

# ---------- ending: include realm ----------
sub("insight:s.insight,kills:s.kills}", "insight:s.insight,kills:s.kills,realm:s.realm||0}")
sub("<span class=\"tag\">胜战 ${e.kills}</span>", "<span class=\"tag\">胜战 ${e.kills}</span><span class=\"tag\">境界 ${REALMS[e.realm||0].name}</span>")

# ---------- nav label + help ----------
sub("<span class=\"nav-icon\" aria-hidden=\"true\">◈</span>", "<span class=\"nav-icon\" aria-hidden=\"true\">⚄</span>")
sub("<span class=\"nav-long\">◈ 今日奇遇</span><span class=\"nav-short\">奇遇</span>", "<span class=\"nav-long\">⚄ 江湖行路</span><span class=\"nav-short\">行路</span>")
sub("<div><b>五</b>第 30 日歇息写下结局", "<div><b>✦</b>掷骰行走大富翁江湖：每日 3 次摇骰，落在奇遇、寻宝、药圃、机缘等格子各有际遇；武学可修至「境界」晋升，解锁天龙八部绝世武功。</div><div><b>五</b>第 30 日歇息写下结局")
