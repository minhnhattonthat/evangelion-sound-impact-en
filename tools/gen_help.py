"""Help / explanation pages of the select-track screen (game_select/008_*): white text on a flat panel + orange button icons.
usage: python tools/gen_help.py      (also registered as gen_gfx section 'help')"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset
from PIL import Image
from gen_gfx import orig, save, bands, segments, clear, inpaint


def is_white(p):
    """white lettering incl. its faint anti-aliasing: any low-alpha pixel or a light grey/white one (icons are orange/brown, rules brown)."""
    return p[3] > 0 and (p[3] < 110 or (min(p[:3]) > 140 and abs(p[0] - p[2]) < 60))


def erase_white(img, box):
    """Make white lettering transparent inside box; coloured icons and rules survive."""
    px = img.load(); x0, y0, x1, y1 = box
    for y in range(max(y0, 0), min(y1, img.height)):
        for x in range(max(x0, 0), min(x1, img.width)):
            if is_white(px[x, y]): px[x, y] = (0, 0, 0, 0)


def rules(img, x1=178):
    """y of the thin brown separator rules across the left column."""
    px = img.load(); out = []
    for y in range(img.height):
        n = sum(1 for x in range(0, x1) if px[x, y][3] > 150 and px[x, y][0] > 60 and min(px[x, y][:3]) < 70)
        if n > 0.7 * x1: out.append(y)
    return [y for i, y in enumerate(out) if i == 0 or y != out[i - 1] + 1]


def paragraph(img, text, box, size=12, xs=0.88, color=(255, 255, 255, 255), font='segoe', min_size=8):
    x, y, w, h = box
    while True:
        lines = typeset.wrap(text, font, size, w - 2, xs).split('\n'); pitch = size + 4
        if len(lines) * pitch <= h + 2 or size <= min_size: break
        size -= 1
    for i, ln in enumerate(lines):
        typeset.text_image(0, 0, ln, font, size, color, xscale=xs, align='l', valign='t', pad=0, canvas=img, box=(x, y + i * pitch, w, pitch))
    return len(lines)


def label(img, text, x, y0, y1, size=12, xs=0.94, color=(255, 255, 255, 255), font='segoe'):
    lines = text.split('\n'); pitch = size + 3; total = len(lines) * pitch; top = y0 + (y1 - y0 + 1 - total) // 2
    xs = min(xs, (177 - x) / max(typeset.font(font, size).getlength(ln) for ln in lines))   # the panel shows x < 179 only
    for i, ln in enumerate(lines):
        typeset.text_image(0, 0, ln, font, size, color, xscale=xs, align='l', valign='t', pad=0, canvas=img, box=(x, top + i * pitch, 200, pitch))


def bottom_bar(img, o, labels, y0=238, y1=256, size=12, xs=0.94, font='segoe-b'):
    """Re-lay the footer: keep the icons (non-white blobs), replace each white text run with the next label, centred on the original span."""
    px = o.load(); w = o.width; cols = [any(px[x, y][3] > 60 for y in range(y0, y1)) for x in range(w)]
    segs = []; s = None
    for x in range(w + 1):
        if x < w and cols[x]:
            if s is None: s = x
        elif s is not None:
            if segs and s - segs[-1][1] <= 4: segs[-1] = (segs[-1][0], x - 1)
            else: segs.append((s, x - 1))
            s = None
    items = []
    for a, b in segs:
        white = sum(1 for x in range(a, b + 1) for y in range(y0, y1) if is_white(px[x, y]))
        tot = sum(1 for x in range(a, b + 1) for y in range(y0, y1) if px[x, y][3] > 60)
        items.append(('text' if white > 0.5 * tot else 'icon', a, b))
    merged = []
    for it in items:   # a label is one text run: join pieces closer than 12 px
        if merged and it[0] == 'text' and merged[-1][0] == 'text' and it[1] - merged[-1][2] <= 12: merged[-1] = ('text', merged[-1][1], it[2])
        else: merged.append(it)
    f = typeset.font(font, size); lab = iter(labels); parts = []
    for kind, a, b in merged:
        if kind == 'icon': parts.append(('icon', o.crop((a, y0, b + 1, y1)), b - a + 1))
        else:
            t = next(lab); parts.append(('text', t, int(f.getlength(t) * xs)))
    gap = lambda i: 4 if (parts[i][0] == 'icon' and i + 1 < len(parts) and parts[i + 1][0] == 'text') else 12
    total = sum(p[2] for p in parts) + sum(gap(i) for i in range(len(parts) - 1))
    cx = (merged[0][1] + merged[-1][2]) // 2; x = max(0, cx - total // 2)
    img.paste(Image.new('RGBA', (w, y1 + 2 - (y0 - 2)), (0, 0, 0, 0)), (0, y0 - 2))
    for i, p in enumerate(parts):
        if p[0] == 'icon': img.alpha_composite(p[1], (x, y0))
        else: typeset.text_image(0, 0, p[1], font, size, (255, 255, 255, 255), xscale=xs, align='l', valign='m', pad=0, canvas=img, box=(x, y0 - 1, p[2] + 6, y1 - y0 + 3))
        if i + 1 < len(parts): x += p[2] + gap(i)


BACK = 'Back'   # returns to the song's BACK/START/HELP menu, not the title
HELP = {   # id suffix -> para / head / rows (y0, y1, x, text) / footer labels
    '93904': dict(para="Match the waveform's height and strike the beat the moment it overlaps the centre of the target.",
                  rows=[(76, 85, 36, 'Beat'), (106, 123, 37, 'Move the waveform\nup and down')], bar=[BACK, 'Start']),
    'a3dd4': dict(para='Dodge obstacles by jumping as you run toward the target landing point.',
                  rows=[(60, 69, 35, 'High Jump'), (91, 100, 37, 'Long Jump')], bar=[BACK, 'Start']),
    'b42a4': dict(head='Session Mode', para="Press the indicated button as an Angel's attack comes full circle around the ring and the UN Forces will attack. Keep dealing damage for a set time to move on to Free Play Mode.",
                  rows=[(118, 138, 106, 'In-game\nicon'), (148, 166, 106, 'Attack')], bar=['Next Page', BACK, 'Start']),
    'c4774': dict(head='Free Play Mode', para='Press buttons freely to attack.\nWatch your ammo.', rows=[(70, 90, 109, 'Attack')], bar=['Next Page', BACK, 'Start']),
    'd4c44': dict(para='An A.T. Field spreading out from the centre is destroyed when it lines up with the frame. Destroy the last A.T. Field to move on to Core Destruction Mode.',
                  rows=[(84, 109, 30, 'A.T. Field on the left\nof the screen (purple)'), (115, 140, 30, 'A.T. Field on the right\nof the screen (yellow)'),
                        (146, 171, 80, 'Large A.T. Field\n(rainbow)')], bar=['Next Page', BACK, 'Start']),
    'e5114': dict(head='Core Destruction Mode', para='Mash the buttons to destroy it.', rows=[(58, 73, 80, 'Strike')], bar=['Next Page', BACK, 'Start']),
    '105ab4': dict(para='Press the button when the targets overlap to flip the panels.', rows=[(58, 73, 31, 'Flip the panel')], bar=[BACK, 'Start']),
    '115f84': dict(para='Press the button when the bar flowing in from the sides lines up with the guide in the centre.',
                   rows=[(74, 89, 40, 'Bar flowing in from the left'), (105, 120, 40, 'Bar flowing in from the right')], bar=[BACK, 'Start']),
}


def gen_help():
    for suffix, d in HELP.items():
        gid = f'game_select/game_select/008_{suffix}'; o = orig(gid); out = o.copy(); rs = rules(o)
        top = rs[0] - 3 if rs else 100
        clear(out, (0, 11 if not d.get('head') else 24, 179, top)); y = 13   # whole paragraph area: grey anti-aliasing escapes erase_white
        if d.get('head'):
            erase_white(out, (12, 11, 179, 24))
            typeset.text_image(0, 0, d['head'], 'segoe-b', 13, (255, 255, 255, 255), xscale=0.94, align='l', valign='t', pad=0, canvas=out, box=(12, 11, 165, 16)); y = 28
        paragraph(out, d['para'], (1, y, 176, top - y))
        for (y0, y1, x, text) in d['rows']:
            erase_white(out, (x - 2, y0 - 3, 180, y1 + 3)); label(out, text, x, y0, y1)
        bottom_bar(out, o, d['bar']); save(gid, out)


def txt(img, text, x, y, w=240, size=11, xs=0.9, align='l', font='segoe', color=(255, 255, 255, 255), h=None):
    typeset.text_image(0, 0, text, font, size, color, xscale=xs, align=align, valign='t', pad=0, canvas=img, box=(x, y, w, h or size + 5))


def icon_caption(img, o, x, y0, y1, pre, post, icon_box, size=12, xs=0.9):
    """Caption with an inline button icon: `pre`, the icon cut from the original, `post`."""
    f = typeset.font('segoe', size); ic = o.crop(icon_box); icw = ic.width; img.paste(Image.new('RGBA', ic.size, (0, 0, 0, 0)), icon_box[:2])
    txt(img, pre, x, y0, 300, size, xs); px = x + int(f.getlength(pre) * xs) + 3
    img.alpha_composite(ic, (px, icon_box[1])); txt(img, post, px + icw + 3, y0, 300, size, xs)


EXPL = {}


def gen_expl():
    g = 'game_select/game_select/008_'
    # waveform page
    o = orig(g + 'db4'); out = o.copy()
    erase_white(out, (160, 18, 242, 68)); paragraph(out, 'The waveform can move freely up and down.', (164, 20, 76, 50), size=12, xs=0.9)
    out = inpaint(out, (28, 26, 83, 44), white_min=100); txt(out, 'Target', 30, 28, 51, 11, 0.9, 'r')
    out = inpaint(out, (125, 90, 153, 105), white_min=100); txt(out, 'Waveform', 126, 90, 60, 10, 0.9)
    erase_white(out, (1, 112, 84, 180)); paragraph(out, "On success, the character's line appears and a hole is punched in the background.", (3, 114, 82, 90), size=11, xs=0.88)
    out = inpaint(out, (88, 122, 238, 156), white_min=120)
    typeset.text_image(0, 0, "I'm Shinji Ikari!!", 'sans-cond-b', 26, (215, 215, 215, 255), xscale=0.95, align='c', valign='m', pad=0, canvas=out, box=(90, 122, 148, 34))
    save(g + 'db4', out)
    # jump page
    o = orig(g + '11284'); out = o.copy()
    erase_white(out, (20, 91, 210, 109)); icon_caption(out, o, 24, 93, 107, 'Tall structures: ', 'High Jump', (104, 93, 119, 108))
    erase_white(out, (20, 185, 210, 203)); icon_caption(out, o, 24, 187, 201, 'Wide structures: ', 'Long Jump', (104, 187, 119, 202))
    save(g + '11284', out)
    # turns page
    o = orig(g + '21754'); out = o.copy()
    erase_white(out, (142, 26, 246, 92)); erase_white(out, (142, 121, 246, 190))
    txt(out, "Angel's Turn", 153, 27, 90, 12, 0.92, font='segoe-b')
    paragraph(out, "An Angel's attack appears clockwise from the centre reticle.", (142, 43, 98, 50), size=11, xs=0.88)
    txt(out, "UN Forces' Turn", 153, 122, 90, 12, 0.92, font='segoe-b')
    paragraph(out, "Press the button matching the Angel's attack as it lines up with the reticle.", (142, 137, 98, 56), size=11, xs=0.88)
    save(g + '21754', out)
    # ammo page
    o = orig(g + '31c24'); out = o.copy(); erase_white(out, (0, 154, 244, 192))
    txt(out, 'Shows the ammo assigned to each button.', 4, 158, 240, 12, 0.92); txt(out, 'It reloads automatically when it runs out.', 4, 175, 240, 12, 0.92)
    save(g + '31c24', out)
    # A.T. field labels (two pages share the layout)
    for suffix in ('420f4', '62a94'):
        o = orig(g + suffix); out = o.copy(); erase_white(out, (0, 130, 256, 162))
        for cx, a in ((36, 'Left'), (121, 'Large'), (207, 'Right')):
            txt(out, a, cx - 50, 133, 100, 11, 0.92, 'c'); txt(out, 'A.T. Field', cx - 50, 146, 100, 11, 0.92, 'c')
        save(g + suffix, out)
    # panel page
    o = orig(g + '72f64'); out = o.copy()
    erase_white(out, (78, 36, 137, 51)); txt(out, 'Single', 79, 38, 60, 12, 0.92)
    erase_white(out, (150, 34, 246, 68)); paragraph(out, 'Press the button the moment the panels overlap.', (152, 38, 92, 64), size=11, xs=0.88)
    erase_white(out, (68, 112, 128, 128)); txt(out, 'Multiple', 70, 114, 60, 12, 0.92)
    erase_white(out, (150, 110, 246, 178)); paragraph(out, 'Hold the button from the moment the lead panel overlaps, and release at the last one.', (152, 114, 92, 66), size=11, xs=0.88)
    save(g + '72f64', out)
    # bar page
    o = orig(g + '83434'); out = o.copy()
    erase_white(out, (40, 96, 116, 110)); erase_white(out, (128, 96, 206, 110)); erase_white(out, (16, 186, 185, 203))
    txt(out, 'Press L', 28, 97, 100, 12, 0.92, 'c'); txt(out, 'Press R', 116, 97, 100, 12, 0.92, 'c')
    txt(out, 'Hold when a band-shaped bar flows in', 19, 188, 200, 12, 0.92)
    save(g + '83434', out)


SECTIONS_HELP = {'help': gen_help, 'expl': gen_expl}

if __name__ == '__main__':
    for k in (sys.argv[1:] or SECTIONS_HELP): SECTIONS_HELP[k]()
