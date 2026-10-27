"""Rebuild 江湖未晚.html from the original backup + generated art + code patches.
Always starts from 江湖未晚.orig.html, so it is safe to re-run."""
import base64, io, re, sys
from pathlib import Path
from PIL import Image

ART = Path(__file__).parent
SRC = ART / '江湖未晚.orig.html'
DST = ART.parent / '江湖未晚.html'

def webp(im, size, q):
    im = im.copy()
    im.thumbnail(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

def crop_alpha(im, pad=8):
    box = im.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))

def load(name):
    return Image.open(ART / 'out' / f'{name}.png')

art = {}
for k in ['wolf', 'elite', 'boss']:
    art[k] = webp(crop_alpha(load(k).convert('RGBA')), (560, 640), 78)
for k in ['lin', 'shen', 'gu']:
    art[k] = webp(crop_alpha(load(k).convert('RGBA')), (288, 288), 78)
for k in ['bg_forest', 'bg_road', 'bg_ridge', 'bg_hall']:
    art[k] = webp(load(k).convert('RGB'), (1024, 683), 66)
art['ending'] = webp(load('ending').convert('RGB'), (1024, 683), 72)

s = SRC.read_text(encoding='utf-8')

def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'patch anchor found {n}x (want {count}): {old[:80]!r}')
    s = s.replace(old, new)

# --- shrink oversized hero / bandit art (shown at ~220px, stored at 1100-1500px) ---
for name in ['HERO_ART', 'ENEMY_ART']:
    m = re.search(name + r"='(data:image/webp;base64,[A-Za-z0-9+/=]+)'", s)
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1).split(',', 1)[1]))).convert('RGBA')
    s = s.replace(m.group(1), webp(im, (640, 760), 84))

# --- slim embedded encounter art (30 × 960px, shown at ≤360×240) and LANDSCAPE ---
enc_i = s.find('const ENCOUNTER_ART')
enc_j = s.find('};', enc_i) + 2
def slim_enc(m):
    im = Image.open(io.BytesIO(base64.b64decode(m.group(2)))).convert('RGB')
    return m.group(1) + webp(im, (720, 480), 64) + m.group(3)
s = s[:enc_i] + re.sub(r'("src":")data:image/webp;base64,([A-Za-z0-9+/=]+)(")', slim_enc, s[enc_i:enc_j]) + s[enc_j:]
m = re.search(r"const LANDSCAPE='(data:image/webp;base64,[^']*)'", s)
im = Image.open(io.BytesIO(base64.b64decode(m.group(1).split(',', 1)[1]))).convert('RGB')
s = s.replace(m.group(1), webp(im, (1280, 853), 60))

# --- art table ---
art_js = 'const ART=' + '{' + ','.join(f"{k}:'{v}'" for k, v in art.items()) + '};\n'
sub("const LANDSCAPE='", art_js + "const LANDSCAPE='")

# --- CSS ---
css = r"""
/* Painted battle stages, enemy and companion portraits. */
.battle-field.staged{background-size:cover;background-position:center 62%}
.battle-field.staged:before{opacity:0}
.battle-field.staged:after{content:'';position:absolute;inset:auto 0 0 0;height:38%;z-index:-1;background:linear-gradient(transparent,#1d2c2266);pointer-events:none}
.npc-avatar img{width:100%;height:100%;object-fit:cover;object-position:50% 0;display:block;transform:scale(1.75);transform-origin:50% 12%}
.map-card.staged{background-size:cover;background-position:center;position:relative}
.map-card.staged>*{position:relative}
.ending-art{display:block;width:calc(100% + 50px);margin:-25px -25px 18px;aspect-ratio:3/2;object-fit:cover;border-radius:10px 10px 0 0}
.key-hint{display:inline-block;min-width:18px;margin-right:6px;padding:0 4px;border:1px solid currentColor;border-radius:4px;font:11px/16px Georgia,serif;opacity:.55;text-align:center}
@media(max-width:760px),(hover:none){.key-hint{display:none}}
"""
sub('</style></head>', css + '</style></head>')

# --- heroSVG: real portraits for wolf / elite / boss / companions ---
sub("function heroSVG(enemy=false,type='hero'){",
    "const ART_LABEL={wolf:'山林灰狼，银灰毛皮与琥珀色眼睛',elite:'黑风寨哨卫，玄铁鳞甲与红缨长枪',boss:'黑风寨主，赤铜重甲、狼裘与偃月大刀',lin:'林知夏，青衣素裙与渡口灯',shen:'沈砚，深蓝长衫与密信',gu:'顾铁衣，皮围裙与锻锤'};\n"
    "function heroSVG(enemy=false,type='hero'){if(ART[type]&&(enemy?['wolf','elite','boss']:['lin','shen','gu']).includes(type))return `<svg viewBox=\"0 0 240 280\" role=\"img\" aria-label=\"${ART_LABEL[type]}\"><image href=\"${artURL(ART[type])}\" x=\"0\" y=\"${type==='wolf'?60:0}\" width=\"240\" height=\"${type==='wolf'?220:280}\" preserveAspectRatio=\"xMidYMax meet\"/></svg>`;")
sub("heroSVG(true,b.id==='wolf'?'wolf':b.id==='boss'?'boss':'bandit')", "heroSVG(true,b.id)")

# NPC avatars as cropped portraits
sub('<div class="npc-avatar">${heroSVG(false,k)}</div>',
    '<div class="npc-avatar"><img src="${artURL(ART[k])}" alt="" decoding="async"></div>')

# --- battle stage backgrounds ---
sub("const ENEMIES={",
    "const STAGE={wolf:'bg_forest',bandit:'bg_road',elite:'bg_ridge',boss:'bg_hall'};function stageURL(id){return artURL(ART[STAGE[id]])}\nconst ENEMIES={")
sub('<div class="battle-field enemy-${b.id} intent-${it}',
    '<div style="background-image:url(${stageURL(b.id)})" class="battle-field staged enemy-${b.id} intent-${it}')

# top scene uses the matching stage during battle
sub("function scenery(theme='dawn'){return `<img class=\"painted-landscape ${theme}\" src=\"${artURL(LANDSCAPE)}\"",
    "function scenery(theme='dawn',src=null){return `<img class=\"painted-landscape ${src?'':theme}\" src=\"${src||artURL(LANDSCAPE)}\"")
sub("const sig=[theme,title,place].join('|');if(sig===sceneSignature)return;sceneSignature=sig;$('scene').innerHTML=scenery(theme)+",
    "const sig=[theme,title,place,S.battle?.id].join('|');if(sig===sceneSignature)return;sceneSignature=sig;$('scene').innerHTML=scenery(theme,S.battle?stageURL(S.battle.id):null)+")

# journey cards show their stage
sub('`<div class="map-card"><div><h3>',
    '`<div class="map-card staged" style="background-image:linear-gradient(100deg,#f8f4e6 48%,#f8f4e6d9 64%,#f8f4e633),url(${stageURL(id)})"><div><h3>')

# warm up enemy + stage images when the journey page opens, so battles don't flash empty
sub("function renderJourney(){", "function warmBattleArt(){if(warmBattleArt.done)return;warmBattleArt.done=true;for(const k of ['wolf','elite','boss','bg_forest','bg_road','bg_ridge','bg_hall']){const im=new Image();im.src=artURL(ART[k]);im.decode?.().catch(()=>{})}}\nfunction renderJourney(){warmBattleArt();")

# --- ending illustration ---
sub('<div class="ending"><div class="tiny" style="color:#aabda6">YOUR STORY, YOUR WAY</div>',
    '<div class="ending"><img class="ending-art" src="${artURL(ART.ending)}" alt="夕照下的栖霞渡，少侠立于古桥，河灯初上"><div class="tiny" style="color:#aabda6">YOUR STORY, YOUR WAY</div>')

# --- keyboard shortcuts: 1-5 in battle, 1-3 for encounter choices ---
sub("onclick=\"battleAction('attack')\">", "onclick=\"battleAction('attack')\"><span class=\"key-hint\">1</span>")
sub("onclick=\"battleAction('guard')\">", "onclick=\"battleAction('guard')\"><span class=\"key-hint\">2</span>")
sub("onclick=\"battleAction('skill')\" ${b.qi<martialActive().qi?'disabled':''}>",
    "onclick=\"battleAction('skill')\" ${b.qi<martialActive().qi?'disabled':''}><span class=\"key-hint\">3</span>")
sub("onclick=\"battleAction('potion')\" ${S.potions<1||S.hp>=stats().hp?'disabled':''}>",
    "onclick=\"battleAction('potion')\" ${S.potions<1||S.hp>=stats().hp?'disabled':''}><span class=\"key-hint\">4</span>")
sub("onclick=\"battleAction('flee')\">", "onclick=\"battleAction('flee')\"><span class=\"key-hint\">5</span>")
sub('<span><strong>${c.label}</strong>', '<span><strong><span class="key-hint">${i+1}</span>${c.label}</strong>')
sub("if(document.addEventListener)document.addEventListener('keydown',e=>{if(!$('overlay').innerHTML)return;",
    "if(document.addEventListener)document.addEventListener('keydown',e=>{if(!$('overlay').innerHTML){if(e.ctrlKey||e.metaKey||e.altKey||/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||''))return;const n='12345'.indexOf(e.key);if(n<0)return;if(S.battle){const a=['attack','guard','skill','potion','flee'][n],btn=document.querySelector(`.battle-actions button[onclick=\"battleAction('${a}')\"]`);if(btn&&!btn.disabled){e.preventDefault();battleAction(a)}}else if(S.tab==='encounter'&&!S.eventDone&&n<3){const btn=document.querySelectorAll('.choices .choice')[n];if(btn&&!btn.disabled){e.preventDefault();choose(n)}}return}")

# gameplay fun layer
exec((ART / 'fun.py').read_text(encoding='utf-8'))
exec((ART / 'bag.py').read_text(encoding='utf-8'))
exec((ART / 'world.py').read_text(encoding='utf-8'))

DST.write_text(s, encoding='utf-8')
print('written', DST, f'{len(s.encode()) / 1e6:.2f} MB', {k: len(v) // 1024 for k, v in art.items()})
