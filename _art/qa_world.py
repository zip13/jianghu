"""Focused QA for the world.py features: board, dice, treasure, garden, realm, rival, peerless arts."""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

GAME = Path(sys.argv[1] if len(sys.argv) > 1 else '../江湖未晚.html').resolve()
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else 'qa_world')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

async def main():
    OUT.mkdir(exist_ok=True)
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, headless=True,
                                           args=['--allow-file-access-from-files'])
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 1000}, device_scale_factor=2)
        page = await ctx.new_page()
        page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        page.on('console', lambda m: errors.append(f'console.{m.type}: {m.text}')
                if m.type in ('error', 'warning') else None)
        await page.goto(GAME.as_uri())
        await page.wait_for_timeout(1200)
        for _ in range(3):
            ov = await page.locator('#overlay').inner_text()
            if ov.strip():
                btns = page.locator('#overlay button')
                if await btns.count():
                    await btns.first.click()
                    await page.wait_for_timeout(400)
            else:
                break

        async def ev(fn, *args):
            return await page.evaluate(f'() => JIANGHU_TEST.{fn}({",".join(repr(a) for a in args)})')
        async def setst(**kw):
            await page.evaluate('k => { const st = JIANGHU_TEST.getState(); Object.assign(st, k); JIANGHU_TEST.setState(st); }', kw)

        # 1. board renders
        await page.screenshot(path=OUT / 'w01_board.png')
        st = await page.evaluate('() => ({pos: S.pos, rolls: S.rolls, realm: S.realm, xiuwei: S.xiuwei, garden: JSON.stringify(S.garden)})')
        print('initial', st)

        # 2. roll dice several times
        rolls_log = []
        for _ in range(5):
            before = await page.evaluate('() => ({pos: S.pos, rolls: S.rolls})')
            await page.evaluate('() => rollDice()')
            after = await page.evaluate('() => ({pos: S.pos, rolls: S.rolls, enc: S.encTriggered})')
            rolls_log.append((before, after))
        print('rolls:', rolls_log)

        # 3. reveal encounter, screenshot story
        await page.evaluate('() => revealEncounter()')
        await page.wait_for_timeout(400)
        await page.screenshot(path=OUT / 'w02_encounter_revealed.png')
        await ev('choose', 0)
        await page.wait_for_timeout(400)

        # 4. garden: plant all three, grow, harvest
        await setst(gold=300)
        await page.evaluate('() => { plantSeed(0, "grass"); }')
        await page.evaluate('() => { plantSeed(1, "honey"); }')
        await page.evaluate('() => { plantSeed(2, "spirit"); }')
        print('after plant:', await page.evaluate('() => JSON.stringify(S.garden)'))
        for _ in range(5):
            await page.evaluate('() => growGarden()')
        print('after grow5:', await page.evaluate('() => JSON.stringify(S.garden)'))
        await page.evaluate('() => harvestPlot(0)')
        await page.evaluate('() => harvestPlot(1)')
        await page.evaluate('() => harvestPlot(2)')
        st = await page.evaluate('() => ({gold: S.gold, potions: S.potions, xiuwei: S.xiuwei, garden: JSON.stringify(S.garden)})')
        print('after harvest:', st)

        # 5. realm: pump xiuwei, checkRealm
        await setst(xiuwei=600)
        await page.evaluate('() => { checkRealm(); render(); }')
        await page.evaluate('() => switchTab("bag")')
        await page.evaluate('() => renderMartial()')
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / 'w03_realm_martial.png')
        print('realm after pump:', await page.evaluate('() => ({realm: S.realm, name: REALMS[S.realm].name, atk: stats().atk, def: stats().def, hp: stats().hp})'))

        # 6. peerless arts unlock + study
        await setst(gold=1000)
        unlock = await page.evaluate('() => MARTIAL.filter(m => ["liumai","xianglong","beiming","yijin","lingbo","douzhuan"].includes(m.id)).map(m => ({id: m.id, name: m.name, unlock: m.unlock(S)}))')
        print('peerless unlock:', unlock)
        await page.evaluate('() => { studyMartial("liumai"); studyMartial("lingbo"); equipMartial("lingbo"); }')
        await page.evaluate('() => { S.martial.slots.move = "liumai"; render(); }')
        print('martial ranks:', await page.evaluate('() => JSON.stringify(S.martial.ranks)'))

        # 7. rival battle
        await setst(energy=3, hp=200)
        await page.evaluate('() => startRival()')
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / 'w04_rival_battle.png')
        print('rival battle:', await page.evaluate('() => ({id: S.battle.id, hp: S.battle.hp, e: S.battle.e && JSON.stringify(S.battle.e)})'))

        # 8. board battle
        await page.evaluate('() => { S.battle = null; S.tab = "encounter"; S.rolls = 3; render(); }')
        await page.evaluate('() => startBoardBattle()')
        await page.wait_for_timeout(500)
        print('board battle:', await page.evaluate('() => ({id: S.battle && S.battle.id, origin: S.battle && S.battle.origin})'))
        await page.evaluate('() => { S.battle = null; render(); }')

        # 9. treasure reveal (direct)
        await page.evaluate('() => revealTreasure()')
        await page.wait_for_timeout(400)
        await page.screenshot(path=OUT / 'w05_treasure.png')
        await page.evaluate('() => closeModal()')

        # 10. save roundtrip with new fields
        rt = await page.evaluate('''() => { const v = validate(JSON.parse(JSON.stringify(S))); return {ok: !!v, rolls: v.rolls, pos: v.pos, realm: v.realm, xiuwei: v.xiuwei, garden: JSON.stringify(v.garden)}; }''')
        print('save roundtrip:', rt)

        await browser.close()
    print('ERRORS:' if errors else 'no console errors')
    for e in errors[:40]:
        print(' ', e)

asyncio.run(main())
