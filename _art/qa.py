"""Headless QA: drive the built game with installed Chrome, screenshot every screen."""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

GAME = Path(sys.argv[1] if len(sys.argv) > 1 else '../江湖未晚.html').resolve()
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else 'qa')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

async def main():
    OUT.mkdir(exist_ok=True)
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, headless=True,
                                           args=['--allow-file-access-from-files'])
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 1000},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        page.on('console', lambda m: errors.append(f'console.{m.type}: {m.text}')
                if m.type in ('error', 'warning') else None)

        await page.goto(GAME.as_uri())
        await page.wait_for_timeout(1200)
        # close tutorial / any overlay
        for _ in range(3):
            ov = await page.locator('#overlay').inner_text()
            if ov.strip():
                btns = page.locator('#overlay button')
                if await btns.count():
                    await btns.first.click()
                    await page.wait_for_timeout(400)
            else:
                break

        async def shot(name):
            await page.screenshot(path=OUT / f'{name}.png')
            print('shot', name)

        async def ev(fn, *args):
            return await page.evaluate(f'() => JIANGHU_TEST.{fn}({",".join(repr(a) for a in args)})')

        await shot('01_encounter_day1')

        # finish the day-1 encounter
        await ev('choose', 0)
        await page.wait_for_timeout(600)
        await shot('02_event_result')

        # journey + battle vs wolf
        await page.click('[data-tab="journey"]')
        await page.wait_for_timeout(500)
        await shot('03_journey')
        await ev('startBattle', 'wolf')
        await page.wait_for_timeout(800)
        await shot('04_battle_open')
        await ev('battleAction', 'guard')
        await page.wait_for_timeout(700)
        await shot('05_battle_guard')
        await ev('battleAction', 'attack')
        await page.wait_for_timeout(700)
        await shot('06_battle_attack')

        # bag: items / gear / martial (seed some gear, end the battle first)
        s = await page.evaluate('() => JIANGHU_TEST.getState()')
        s['battle'] = None
        s['inventory'] = list(dict.fromkeys(
            s['inventory'] + ['dragonring', 'windboot', 'jadecrown', 'cloudboot', 'iron', 'silk', 'fang', 'tally']))
        s['energy'] = 3
        await page.evaluate('st => JIANGHU_TEST.setState(st)', s)
        await page.click('[data-tab="bag"]')
        await page.wait_for_timeout(600)
        await page.locator('.bag-tabs button').nth(0).click()
        await page.wait_for_timeout(400)
        await shot('07_bag_items')
        await page.locator('.bag-tabs button').nth(1).click()
        await page.wait_for_timeout(600)
        await shot('08_bag_gear')
        await page.locator('.bag-tabs button').nth(2).click()
        await page.wait_for_timeout(600)
        await shot('09_bag_martial')

        # shop + quests
        await page.click('[data-tab="shop"]')
        await page.wait_for_timeout(600)
        await shot('10_shop')
        await page.click('[data-tab="quests"]')
        await page.wait_for_timeout(600)
        await shot('11_quests')

        # ending
        s = await page.evaluate('() => JIANGHU_TEST.getState()')
        s['day'] = 30; s['ended'] = False; s['eventDone'] = True; s['energy'] = 3
        s['kills'] = 20; s['gold'] = 500; s['karma'] = 25; s['fame'] = 25; s['insight'] = 25
        await page.evaluate('st => JIANGHU_TEST.setState(st)', s)
        await page.evaluate('() => JIANGHU_TEST.sleep()')
        await page.wait_for_timeout(1200)
        await shot('12_ending')

        # encounter art on a later day (day 32 → loops through all events)
        try:
            await page.locator('#overlay button').first.click(timeout=3000)
        except Exception:
            await page.evaluate('() => closeModal()')
        await page.wait_for_timeout(400)
        await page.evaluate('() => { const st = JIANGHU_TEST.getState(); st.day = 32; st.eventDone = false; JIANGHU_TEST.setState(st); }')
        await page.click('[data-tab="encounter"]')
        await page.wait_for_timeout(900)
        await shot('13_encounter_later')

        # win a battle: loot, banner, titles
        s = await page.evaluate('() => JIANGHU_TEST.getState()')
        s['battle'] = None; s['energy'] = 3; s['kills'] = 19
        await page.evaluate('st => JIANGHU_TEST.setState(st)', s)
        await ev('startBattle', 'wolf')
        await page.wait_for_timeout(700)
        await page.evaluate('() => { S.battle.hp = 3; JIANGHU_TEST.battleAction("attack"); }')
        await page.wait_for_timeout(1400)
        await shot('14_battle_win')
        try:
            await page.locator('#overlay button').first.click(timeout=3000)
        except Exception:
            await page.evaluate('() => closeModal()')
        await page.wait_for_timeout(500)

        # keyboard shortcuts 1-5 in battle
        s = await page.evaluate('() => JIANGHU_TEST.getState()')
        s['battle'] = None; s['energy'] = 3
        await page.evaluate('st => JIANGHU_TEST.setState(st)', s)
        await ev('startBattle', 'elite')
        await page.wait_for_timeout(600)
        turns = await page.evaluate('() => S.battle.turn')
        await page.keyboard.press('2')
        await page.wait_for_timeout(900)
        turns2 = await page.evaluate('() => S.battle.turn')
        await page.keyboard.press('1')
        await page.wait_for_timeout(900)
        turns3 = await page.evaluate('() => S.battle.turn')
        print('keyboard turns:', turns, turns2, turns3)

        # save roundtrip
        rt = await page.evaluate('''() => {
            const j = JSON.stringify(S);
            const v = validate(JSON.parse(j));
            const s = JIANGHU_TEST.getState();
            return {ok: !!v, gold: v.gold === s.gold, gear: JSON.stringify(v.gear) === JSON.stringify(s.gear),
                    battle: v.battle && s.battle && v.battle.hp === s.battle.hp && v.battle.turn === s.battle.turn,
                    titles: v.titles.length};
        }''')
        print('save roundtrip:', rt)
        await page.evaluate('() => { const st = JIANGHU_TEST.getState(); st.battle = null; JIANGHU_TEST.setState(st); }')

        # mobile pass
        mctx = await browser.new_context(viewport={'width': 390, 'height': 844},
                                         device_scale_factor=2)
        mpage = await mctx.new_page()
        mpage.on('pageerror', lambda e: errors.append(f'mobile pageerror: {e}'))
        await mpage.goto(GAME.as_uri())
        await mpage.wait_for_timeout(1200)
        for _ in range(3):
            ov = await mpage.locator('#overlay').inner_text()
            if ov.strip():
                btns = mpage.locator('#overlay button')
                if await btns.count():
                    await btns.first.click()
                    await mpage.wait_for_timeout(400)
            else:
                break
        await mpage.screenshot(path=OUT / '15_m_encounter.png')
        await mpage.evaluate('() => { const st = JIANGHU_TEST.getState(); st.day = 25; JIANGHU_TEST.setState(st); JIANGHU_TEST.startBattle("boss"); }')
        await mpage.wait_for_timeout(700)
        await mpage.screenshot(path=OUT / '16_m_battle.png')
        await mpage.evaluate('() => { const st = JIANGHU_TEST.getState(); st.day = 25; st.battle = null; st.inventory = st.inventory.concat(["dragonring","windboot","jadecrown","cloudboot","iron","silk"]); JIANGHU_TEST.setState(st); }')
        await mpage.click('[data-tab="bag"]')
        await mpage.wait_for_timeout(600)
        await mpage.locator('.bag-tabs button').nth(1).click()
        await mpage.wait_for_timeout(600)
        await mpage.screenshot(path=OUT / '17_m_gear.png')
        await mpage.locator('.bag-tabs button').nth(2).click()
        await mpage.wait_for_timeout(600)
        await mpage.screenshot(path=OUT / '18_m_martial.png')
        await mctx.close()

        await browser.close()
    print('ERRORS:' if errors else 'no console errors')
    for e in errors[:30]:
        print(' ', e)

asyncio.run(main())
