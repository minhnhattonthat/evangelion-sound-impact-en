"""Generate the English replacement images into gfx/ from the original GIMs and the translations below.
usage: python tools/gen_gfx.py [section ...]      (sections: saveload, ...; default all)   run from the repo root
Each section reads its originals from work/gim (tools/unpack_all.py) and writes gfx/<cpk>/<arc>/<NNN>_<off>.png."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gim, typeset
from PIL import Image

def orig(id_):
    d = open(f'work/gim/{id_}.gim', 'rb').read(); im = gim.parse(d)[0]; w, h, rows = gim.to_rgba(d, im)
    return Image.frombytes('RGBA', (w, h), b''.join(rows))

def save(id_, img):
    p = f'gfx/{id_}.png'; os.makedirs(os.path.dirname(p), exist_ok=True); img.save(p)

def segments(img, y0, y1, gap=3, thr=40):
    """Horizontal runs of non-transparent pixels inside rows y0..y1 (gaps <= `gap` px are merged)."""
    w = img.width; px = img.load(); segs = []; s = None
    for x in range(w + 1):
        on = x < w and any(px[x, y][3] > thr for y in range(y0, y1 + 1))
        if on and s is None: s = x
        if not on and s is not None:
            if segs and s - segs[-1][1] <= gap: segs[-1] = (segs[-1][0], x - 1)
            else: segs.append((s, x - 1))
            s = None
    return segs

def bands(img, thr=40):
    px = img.load(); out = []; s = None
    for y in range(img.height + 1):
        on = y < img.height and any(px[x, y][3] > thr for x in range(img.width))
        if on and s is None: s = y
        if not on and s is not None: out.append((s, y - 1)); s = None
    return out

# ---------------------------------------------------------------- sys/menu_saveload: orange prompt panels, 256x128
SAVELOAD = {
    '000_110d0': ('This game supports auto-save. While auto-saving, the Memory Stick™ access indicator will blink. Do not remove the media or turn off the system while it blinks.', ['Next']),
    '000_195a0': ('Accessing the storage media.\nDo not turn off the system or remove the media.', []),
    '000_21a70': ('Retry saving?', ['Yes', 'No']),
    '000_29f40': ('Resume the game without saving?', ['Yes', 'No']),
    '000_32410': ('Create new save data?', ['Yes', 'No']),
    '000_3a8e0': ('Auto-save has been turned OFF.\nYou can change this in Options.', ['Next']),
    '000_42db0': ('The save data may have been modified.\nOverwrite it anyway?', ['Yes', 'No']),
    '000_730': ('Create new save data?', ['Yes', 'No']),
    '000_8c00': ('Continue without saving?', ['Yes', 'No']),
}

def prompt(id_, text, labels, font='segoe-b', size=12, xscale=0.92):
    """Orange prompt panel: text lines at the original line positions (centred in the sprite), button row where it was."""
    import funm
    o = orig(id_); bs = bands(o); col = typeset.dominant(o) + (255,)
    sw, sh, _ = funm.sprite(id_)
    tb = bs[:-1] if labels else bs
    canvas = Image.new('RGBA', o.size, (0, 0, 0, 0))
    while True:   # largest font whose wrapped text fits the original number of lines inside the sprite width
        lines = typeset.wrap(text, font, size, sw - 4, xscale).split('\n')
        if len(lines) <= len(tb) or size <= 8: break
        size -= 1
    for i, ln in enumerate(lines):
        y0 = tb[min(i, len(tb) - 1)][0] if i < len(tb) else tb[-1][0] + 16 * (i - len(tb) + 1)
        typeset.text_image(o.width, o.height, ln, font, size, col, xscale=xscale, align='c', valign='t', pad=0, canvas=canvas, box=(0, y0 - 2, sw, 16))
    if labels:
        y0, y1 = bs[-1]; segs = segments(o, y0, y1); icons = segs[0::2]; f = typeset.font(font, size)
        widths = [(ic[1] - ic[0] + 1) + 5 + int(f.getlength(lb) * xscale) for ic, lb in zip(icons, labels)]
        total = sum(widths) + 16 * (len(widths) - 1); x = (sw - total) // 2
        for ic, lb, wd in zip(icons, labels, widths):
            canvas.alpha_composite(o.crop((ic[0], y0, ic[1] + 1, y1 + 1)), (x, y0))
            typeset.text_image(o.width, o.height, lb, font, size, col, xscale=xscale, align='l', valign='t', pad=0, canvas=canvas,
                               box=(x + (ic[1] - ic[0] + 1) + 5, y0 - 3, 80, 16))
            x += wd + 16
    return canvas

def gen_saveload():
    for k, (t, l) in SAVELOAD.items(): save(f'sys/menu_saveload/{k}', prompt(f'sys/menu_saveload/{k}', t, l))

# ---------------------------------------------------------------- title logo (title/title/001_15d0, 512x512 atlas)
from PIL import ImageFilter, ImageChops
TITLE = 'title/title/001_15d0'
LOGO_WHITE = (0, 0, 360, 152)
LOGO_VARIANTS = [('glow1', (0, 152, 192, 240)), ('glow2', (192, 152, 400, 256)), ('orange', (288, 256, 472, 336))]

def new_white_logo(o):
    """White logo rect with the Japanese lines replaced (Latin '3nd Impact' kept)."""
    c = o.crop(LOGO_WHITE); cv = Image.new('RGBA', c.size, (0, 0, 0, 0)); cv.paste(c.crop((0, 0, 360, 76)), (0, 0))
    white = (255, 255, 255, 255)
    typeset.text_image(360, 152, 'REBUILD OF', 'serif-b', 17, white, xscale=0.85, align='c', valign='t', tracking=5, canvas=cv, box=(40, 80, 280, 22))
    typeset.text_image(360, 152, 'EVANGELION', 'serif-b', 40, white, xscale=0.82, align='c', valign='t', tracking=3, canvas=cv, box=(30, 98, 300, 36))
    typeset.text_image(360, 152, '— SOUND IMPACT —', 'serif-b', 13, white, xscale=0.9, align='c', valign='t', tracking=3, canvas=cv, box=(60, 134, 240, 16))
    return cv

def fit_variant(orig_white, orig_var, new_white):
    """Find scale/blur/gain turning the original white logo into the original variant, apply it to the new white logo."""
    bb = orig_var.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); tw = orig_var.width
    best = None
    ow_bb = orig_white.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox()
    base_w = ow_bb[2] - ow_bb[0]
    for sc_adj in (1.0,):
        sc = (bb[2] - bb[0]) / base_w
        def xform(img, r, gain):
            im = img.resize((max(1, round(img.width * sc)), max(1, round(img.height * sc))), Image.LANCZOS)
            a = im.getchannel('A'); a = a.filter(ImageFilter.GaussianBlur(r)) if r else a
            a = a.point(lambda v: min(255, int(v * gain)))
            return a
        ref = orig_var.getchannel('A')
        for r in (0, 1.5, 3, 4.5, 6):
            for gain in (1.4, 1.8, 2.4, 3.0):
                a = xform(orig_white, r, gain)
                canvas = Image.new('L', orig_var.size, 0); canvas.paste(a, (bb[0] - round(ow_bb[0] * sc), bb[1] - round(ow_bb[1] * sc)))
                err = sum(ImageChops.difference(canvas, ref).histogram()[i] * i for i in range(256))
                if best is None or err < best[0]: best = (err, r, gain, sc)
    _, r, gain, sc = best
    PAD = 12
    padded = Image.new('RGBA', (new_white.width + 2 * PAD, new_white.height + 2 * PAD), (0, 0, 0, 0)); padded.paste(new_white, (PAD, PAD))
    im = padded.resize((max(1, round(padded.width * sc)), max(1, round(padded.height * sc))), Image.LANCZOS)
    a = im.getchannel('A'); a = a.filter(ImageFilter.GaussianBlur(r)) if r else a; a = a.point(lambda v: min(255, int(v * gain)))
    out = Image.new('RGBA', orig_var.size, (0, 0, 0, 0))
    dx = bb[0] - round(ow_bb[0] * sc) - round(PAD * sc); dy = bb[1] - round(ow_bb[1] * sc) - round(PAD * sc)
    # colour of the variant: its brightest/most common opaque colour
    col = typeset.dominant(orig_var, 150) + (255,)
    layer = Image.new('RGBA', a.size, col); layer.putalpha(a)
    out.alpha_composite(layer.crop((max(-dx, 0), max(-dy, 0), layer.width, layer.height)), (max(dx, 0), max(dy, 0)))
    return out, (r, gain, round(sc, 2))

def gen_title():
    o = orig(TITLE); nw = new_white_logo(o); out = o.copy()
    out.paste(Image.new('RGBA', LOGO_WHITE[2:], (0, 0, 0, 0)), LOGO_WHITE[:2]); out.alpha_composite(nw, LOGO_WHITE[:2])
    for name, box in LOGO_VARIANTS:
        ov = o.crop(box); v, params = fit_variant(o.crop(LOGO_WHITE), ov, nw); print('  logo', name, params)
        out.paste(Image.new('RGBA', ov.size, (0, 0, 0, 0)), box[:2]); out.alpha_composite(v, box[:2])
    # copyright line: (c)khara (c)2011 NBGI
    cb = (0, 448, 104, 464); out.paste(Image.new('RGBA', (104, 16), (0, 0, 0, 0)), cb[:2])
    typeset.text_image(104, 16, '©khara  ©2011 NBGI', 'sans', 9, (255, 255, 255, 255), align='l', valign='m', pad=1, canvas=out, box=(0, 448, 104, 16))
    save(TITLE, out)

def rich(canvas, x, y, segs, font_name, size, xscale=1.0, tracking=0):
    """Draw [(text, rgba), ...] left to right starting at x,y (top of the em box); returns the end x."""
    f = typeset.font(font_name, size)
    for t, col in segs:
        im = typeset.text_image(0, 0, t, font_name, size, col, xscale=xscale, align='l', valign='t', pad=0, tracking=tracking,
                                canvas=canvas, box=(int(x), int(y), 600, size + 8))
        x += f.getlength(t) * xscale + tracking * len(t)
    return x

WHITE = (255, 255, 255, 255); ORANGE = (255, 104, 24, 255)

def gen_notice():
    gid = 'title/title/000_6e4'; o = orig(gid)
    out = Image.new('RGBA', o.size, (0, 0, 0, 255))
    fn, sz, xs = 'serif-b', 18, 0.78
    typeset.text_image(480, 272, 'NOTICE', fn, 30, ORANGE, xscale=0.8, align='c', valign='t', tracking=3, canvas=out, box=(0, 32, 480, 40))
    body = [
        [('Distributing game software over the Internet without the permission', WHITE)],
        [('of the rights holder is ', WHITE), ('a violation of Article 113, Paragraph 1', ORANGE)],
        [('of the Copyright Act', ORANGE), ('. Furthermore, since the January 2010 amendment', WHITE)],
        [('to the law, knowingly downloading illegally distributed content', WHITE)],
        [('is also illegal, even when it is only for private use.', WHITE)],
        [('Thank you for your understanding and cooperation.', WHITE)],
    ]
    for i, segs in enumerate(body): rich(out, 24, 96 + i * 26, segs, fn, sz, xs)
    save(gid, out)

def clear(img, box):
    img.paste(Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0)), box[:2])

def gen_pause():
    gid = 'static/pausemenu/000_b48'; o = orig(gid); out = o.copy()
    ORG = (240, 80, 0, 255); BLK = (0, 0, 0, 255)
    for box in [(144, 0, 230, 20), (144, 25, 230, 44), (0, 40, 140, 60), (0, 64, 140, 84), (86, 0, 140, 50)]: clear(out, box)   # last: the small English captions, now redundant
    for col, y in ((ORG, 0), (BLK, 24)):
        typeset.text_image(0, 0, 'CONTINUE', 'sans-cond-b', 17, col, align='c', valign='t', pad=0, canvas=out, box=(145, y, 84, 20))
    for col, y in ((ORG, 40), (BLK, 64)):
        typeset.text_image(0, 0, 'RETRY', 'sans-cond-b', None, col, align='l', valign='t', pad=0, max_size=17, canvas=out, box=(1, y, 44, 20))
        typeset.text_image(0, 0, 'SELECT TRACK', 'sans-cond-b', None, col, align='l', valign='t', pad=0, max_size=17, canvas=out, box=(50, y, 92, 20))
    save(gid, out)

def gen_loading():
    gid = 'static/loading/000_ba8'; o = orig(gid); out = o.copy()
    clear(out, (26, 45, 74, 60)); clear(out, (155, 45, 175, 60))   # small kanji captions under LOADING / COMPLETE
    save(gid, out)

SECTIONS = {'saveload': gen_saveload, 'title': gen_title, 'notice': gen_notice, 'pause': gen_pause, 'loading': gen_loading}


# ---------------------------------------------------------------- game_select song cards (002 = list, 006 = selected)
AS = 'Angel Session'
CARDS_002 = {   # id suffix -> (line1, line2); None keeps the original line
    'a8c0': (None, 'Shinji Ikari'), '12d90': (None, 'Rei Ayanami'), '1b260': (None, 'Shikinami Asuka Langley'),
    '23730': (None, 'Kaworu Nagisa'), '2bc00': (None, 'Makinami Mari Illustrious'),
    '340d0': (None, 'Unit-01'), '3c5a0': (None, 'Unit-00'), '44a70': (None, 'Unit-02'),
    '4cf40': (AS, '4th'), '55410': (AS, '5th'), '5d8e0': (AS, '6th'), '65db0': (AS, '3rd'), '6e280': (AS, '7th'),
    '76750': (AS, '8th'), '7ec20': (AS, '9th'), '870f0': (AS, '10th'),
    '8f5c0': (None, '4th Angel'), '97a90': (None, '5th Angel'), '9ff60': (None, '6th Angel'), 'a8430': (None, '3rd Angel'),
    'b0900': (None, '7th Angel'), 'b8dd0': (None, '8th Angel'), 'c12a0': (None, '9th Angel'), 'c9770': (None, '10th Angel'),
    'd1c40': (None, 'Unit-01 Awakens'), 'e25e0': (None, 'Rei Ayanami'), 'eaab0': (None, 'Makinami Mari Illustrious'),
    'f2f80': (None, 'Shikinami Asuka Langley'), 'fb450': (None, 'Provisional Unit-05'), '103920': (None, 'The Beast'),
    '10bdf0': ("Rei's Pokapoka Bento", None),
}
CARDS_006 = {
    '2020': (None, 'Shinji Ikari'), 'a4f0': (None, 'Rei Ayanami'), '129c0': (None, 'Shikinami Asuka Langley'),
    '1ae90': (None, 'Kaworu Nagisa'), '23360': (None, 'Makinami Mari Illustrious'),
    '2b830': (None, 'Unit-01'), '33d00': (None, 'Unit-00'), '3c1d0': (None, 'Unit-02'),
    '446a0': (AS, '4th'), '4cb70': (AS, '5th'), '55040': (AS, '6th'), '5d510': (AS, '3rd'), '659e0': (AS, '7th'),
    '6deb0': (AS, '8th'), '76380': (AS, '9th'), '7e850': (AS, '10th'),
    '86d20': (None, '4th Angel'), '8f1f0': (None, '5th Angel'), '976c0': (None, '6th Angel'), '9fb90': (None, '3rd Angel'),
    'a8060': (None, '7th Angel'), 'b0530': (None, '8th Angel'), 'b8a00': (None, '9th Angel'), 'c0ed0': (None, '10th Angel'),
    'c93a0': (None, 'Unit-01 Awakens'), 'd1870': (None, 'Unit-01 Awakens'), 'd9d40': (None, 'Rei Ayanami'),
    'e2210': (None, 'Makinami Mari Illustrious'), 'ea6e0': (None, 'Shikinami Asuka Langley'),
    'f2bb0': (None, 'Provisional Unit-05'), 'fb080': (None, 'The Beast'),
}

def serif_line(canvas, text, box, col, xs, size, align, maxw, shrink=True):
    """Draw `text` in the condensed-serif house style inside box=(x,y,w,h); shrinks horizontally, then in size, to fit maxw."""
    f = typeset.font('serif-b', size)
    while f.getlength(text) * xs > maxw and xs > 0.40: xs -= 0.01
    while f.getlength(text) * xs > maxw and size > 8: size -= 1; f = typeset.font('serif-b', size)
    typeset.text_image(0, 0, text, 'serif-b', size, col, xscale=xs, align=align, valign='m', pad=0, canvas=canvas, box=box)

def gen_cards():
    for suffix, (l1, l2) in CARDS_002.items():
        gid = f'game_select/game_select/002_{suffix}'; out = orig(gid); col = typeset.dominant(out) + (255,)
        if l1: clear(out, (0, 11, 160, 46)); serif_line(out, l1, (1, 11, 160, 34), col, 0.49, 46, 'l', 158)
        if l2: clear(out, (0, 46, 160, 73)); serif_line(out, l2, (1, 46, 160, 26), col, 0.5, 30, 'l', 158)
        clear(out, (0, 72, 256, 84))   # small English gloss line: repeats the title now
        save(gid, out)
    for suffix, (l1, l2) in CARDS_006.items():
        gid = f'game_select/game_select/006_{suffix}'; out = orig(gid); col = typeset.dominant(out) + (255,)
        if l1: clear(out, (0, 19, 256, 64)); serif_line(out, l1, (0, 19, 256, 42), col, 0.49, 53, 'c', 236)
        if l2: clear(out, (0, 64, 256, 93)); serif_line(out, l2, (0, 64, 256, 28), col, 0.5, 30, 'c', 236)
        clear(out, (0, 93, 256, 110))
        save(gid, out)

SECTIONS['cards'] = gen_cards


def gen_menu():
    gid = 'game_select/game_select/006_103550'; out = orig(gid)
    for k, word in enumerate(['BACK', 'BACK', 'START', 'START', 'HELP', 'HELP']):
        y = 40 * k; slot = out.crop((0, y, 48, y + 24)); col = typeset.dominant(slot, 150) + (255,)
        clear(out, (0, y, 48, y + 26))
        serif_line(out, word, (0, y, 48, 24), col, 0.55, 22, 'c', 36 if word == 'START' else 44)
    save(gid, out)

SECTIONS['menu'] = gen_menu


def gen_option():
    gid = 'game_select/game_select/009_1e58'; out = orig(gid)
    ORG = (240, 80, 0, 255); BLK = (0, 0, 0, 255)
    for (y0, y1, word, col, w) in [(65, 83, 'BGM', BLK, 46), (89, 107, 'BGM', ORG, 45), (113, 131, 'SE', BLK, 45), (137, 155, 'SE', ORG, 45),
                                   (161, 179, 'AUTO SAVE', BLK, 70), (185, 203, 'AUTO SAVE', ORG, 70)]:
        clear(out, (0, y0 - 1, w if word != 'AUTO SAVE' else 72, y1 + 2))
        typeset.text_image(0, 0, word, 'sans-cond-b', None, col, align='l', valign='m', pad=0, max_size=24, canvas=out, box=(1, y0, 70 if word == 'AUTO SAVE' else 44, y1 - y0 + 1))
    for box in [(88, 0, 104, 8), (88, 8, 104, 16), (88, 16, 128, 24)]: clear(out, box)   # tx_BGM / tx_SE / tx_AUTOSAVE sub-captions: repeat the labels
    clear(out, (64, 40, 216, 88))
    for y, text in [(40, 'Adjust the BGM volume.'), (56, 'Change the auto-save setting.'), (72, 'Adjust the SE volume.')]:   # tx_info1/3/2 sprite rects
        typeset.text_image(0, 0, text, 'segoe-b', None, ORG, xscale=0.92, align='c', valign='m', pad=0, max_size=12, canvas=out, box=(64, y, 152, 16))
    save(gid, out)

SECTIONS['option'] = gen_option


# ---------------------------------------------------------------- game_select unlock notices (010_*): orange lines + "Next" button
T = 'track'; F = 'free'
UNLOCK = {
    '11194': [(T, 'Angel Session 3rd'), (T, 'Number 5  Provisional Unit-05'), (T, 'AT/A3  3rd Angel'), (T, 'HEX  Makinami Mari Illustrious'), (F, 'have been added')],
    '19664': [(T, 'Angel Session 7th'), (T, 'AT/A7  7th Angel'), (T, 'HEX  Shikinami Asuka Langley'), (F, 'have been added')],
    '21b34': [(T, 'Angel Session 8th'), (T, 'Teardrop  Unit-01'), (T, 'Teardrop  Unit-02'), (T, 'Teardrop  Unit-00'), (T, 'Call of Fourteen  2nd'), (T, 'AT/A8  8th Angel'), (F, 'have been added')],
    '2a004': [(T, 'Call of Fourteen  k'), (T, 'Angel Session 9th'), (T, 'AT/A9  9th Angel'), (F, 'have been added')],
    '324d4': [(T, 'Call of Fourteen  m'), (T, 'Angel Session 10th'), (T, 'AT/A10  10th Angel'), (T, 'Beastie Girl  The Beast'), (F, 'have been added')],
    '3a9a4': [(T, 'AT  Unit-01 Awakens'), (F, 'has been added')],
    '42e74': [(F, 'Ending has been added to the Gallery'), (F, 'HARD mode has been added'), (F, 'Press Left or Right on the Select Track'), (F, 'screen to switch between modes')],
    '4b344': [(F, 'Content has been added to the Gallery')],
    '7f4': [(T, 'HEX  Rei Ayanami'), (T, 'Angel Session 5th'), (T, 'AT/A5  5th Angel'), (F, 'The Gallery has been added'), (F, 'Press the {0} button on the Select Track'), (F, 'screen to go to the Gallery')],
    '8cc4': [(T, 'Angel Session 6th'), (T, 'Call of Fourteen  1st'), (T, 'AT/A6  6th Angel'), (F, 'have been added')],
}

def gen_unlock():
    ORG = (240, 80, 0, 255)
    for suffix, lines in UNLOCK.items():
        gid = f'game_select/game_select/010_{suffix}'; o = orig(gid); out = o.copy(); bs = bands(o)
        btn = bs[-1]; tb = bs[:-1]; assert len(tb) == len(lines), (gid, len(tb), len(lines), bs)
        icons = []   # inline icons (triangle button) found in text rows
        import iconscan
        ic_all = [b for b in iconscan.find_icons(o) if b[1] < btn[0] - 2]
        for (a, b), (kind, text) in zip(tb, lines):
            segs = segments(o, a, b, gap=6)
            if kind == T:
                x0 = 62; clear(out, (x0 - 1, a - 1, 256, b + 2)); x = x0
            else:
                clear(out, (0, a - 1, 256, b + 2)); x = 1
            if '{0}' in text:
                pre, post = text.split('{0}'); f = typeset.font('segoe', 12)
                ic = [i for i in ic_all if a - 4 <= i[1] <= b + 4][0]; icw = ic[2] - ic[0] + 1
                px = x; typeset.text_image(0, 0, pre, 'segoe', 12, ORG, xscale=0.95, align='l', valign='m', pad=0, canvas=out, box=(x, a - 2, 256, b - a + 5)); px += f.getlength(pre) * 0.95 + 2
                out.alpha_composite(o.crop((ic[0], ic[1], ic[2] + 1, ic[3] + 1)), (int(px), ic[1])); px += icw + 3
                typeset.text_image(0, 0, post, 'segoe', 12, ORG, xscale=0.95, align='l', valign='m', pad=0, canvas=out, box=(int(px), a - 2, 256, b - a + 5))
            else:
                typeset.text_image(0, 0, text, 'segoe', 12, ORG, xscale=0.95, align='l', valign='m', pad=0, canvas=out, box=(x, a - 2, 256, b - a + 5))
        # button row: keep the circle icon, replace the label
        segs = segments(o, btn[0], btn[1], gap=4); ic = segs[0]; label = segs[-1]
        clear(out, (label[0] - 1, btn[0] - 1, label[1] + 2, btn[1] + 2))
        typeset.text_image(0, 0, 'Next', 'segoe-b', 12, ORG, xscale=0.95, align='l', valign='m', pad=0, canvas=out, box=(label[0], btn[0] - 2, 60, btn[1] - btn[0] + 5))
        save(gid, out)

SECTIONS['unlock'] = gen_unlock


# ---------------------------------------------------------------- result screens (identical copies in every song's result*.arc)
import glob, hashlib

def copies(gid):
    """All gids under work/gim whose bytes equal gid's (the same texture is stored once per result arc)."""
    d = open(f'work/gim/{gid}.gim', 'rb').read(); h = hashlib.md5(d).hexdigest(); name = gid.split('/')[-1]; out = []
    for fn in glob.glob(f'work/gim/*/result*/{name}.gim'):
        if hashlib.md5(open(fn, 'rb').read()).hexdigest() == h: out.append(os.path.relpath(fn, 'work/gim').replace(chr(92), '/')[:-4])
    return out

def save_all(gid, img):
    for c in copies(gid): save(c, img)

def tiny(img, text, x, top, size=7, font='sans-cond-b', col=(240, 80, 0, 255), maxw=None, align='l', tracking=0):
    """Small lettering matched to the original pixel text: cap tops on row `top`, starting at x (or centred on x for align='c');
    squeezed horizontally to stay within maxw."""
    f = typeset.font(font, size); w = f.getlength(text) + tracking * len(text); xs = min(1.0, maxw / w) if maxw else 1.0
    if align == 'c': x -= int(w * xs) // 2
    typeset.text_image(0, 0, text, font, size, col, xscale=xs, align='l', valign='t', pad=0, tracking=tracking, canvas=img,
                       box=(x - 2, top - f.getbbox('I')[1] - 2, 300, size + 8))

def flavour(img, y):
    """'Transmission Recorded / Recording Saved To MAGI01 Databanks' (original art: typo 'Saced'), cap tops at y and y + 6, inside x 0..111
    (the result screen shows only a 112 px wide strip of it)."""
    clear(img, (0, y - 1, 120, y + 13))
    tiny(img, 'Transmission Recorded', 56, y, align='c', maxw=110); tiny(img, 'Recording Saved To MAGI01 Databanks', 56, y + 6, align='c', maxw=110)

def fix_search(img):
    """'Seach Results: Personal Data' (original 4 px art, x 59..143, rows 163..166): insert an 'r' before the 'c' at x 70 and
    start the line 2 px further left so it still keeps a 1 px gap to both frame bars (x 55, x 146)."""
    a = np.array(img); strip = a[162:168, 59:144].copy(); cols = [strip[:, i] for i in range(strip.shape[1])]
    r1 = np.zeros_like(cols[0]); r1[2:5] = (240, 80, 0, 255); r2 = np.zeros_like(cols[0]); r2[2] = (240, 80, 0, 170)
    cols[11:11] = [r1, r2, np.zeros_like(r1)]
    a[162:168, 57:145] = np.stack(cols, 1); return Image.fromarray(a)

CARD_NAMES = {   # result*/000_5988 personnel cards, keyed by the first arc that holds each variant
    'at00/result17': 'Ritsuko Akagi', 'at01/result18': 'Kozo Fuyutsuki', 'at02/result19': 'Misato Katsuragi', 'at03/result20': 'Ryoji Kaji',
    'at04/result21': 'Maya Ibuki', 'at05/result22': 'Gendo Ikari', 'at08/result25': 'Kaworu Nagisa',
}

def gen_results():
    ORG = (240, 80, 0, 255); BLK = (0, 0, 0, 255)
    # 000_14b8: result panel header (Song Complete / Mission Failed captions)
    gid = 'at00/result17/000_14b8'; o = orig(gid); out = o.copy()
    clear(out, (1, 1, 78, 27)); clear(out, (142, 25, 226, 51))
    typeset.text_image(0, 0, 'Song Complete', 'serif-b', None, ORG, xscale=0.62, align='l', valign='m', pad=0, max_size=26, canvas=out, box=(3, 1, 76, 26))
    typeset.text_image(0, 0, 'Mission Failed', 'serif-b', None, ORG, xscale=0.62, align='l', valign='m', pad=0, max_size=26, canvas=out, box=(144, 25, 80, 25))
    save_all(gid, out)
    for gid, word, col, box in [('at00/result17/003_608', 'Song Complete', ORG, (66, 52, 131, 23)), ('at00/result17/003_8ad8', 'Mission Failed', BLK, (92, 53, 68, 24))]:
        o = orig(gid); out = o.copy(); clear(out, (box[0] - 8, box[1] - 2, box[0] + box[2] + 10, box[1] + box[3] + 2))
        cx = box[0] + box[2] // 2
        typeset.text_image(0, 0, word, 'serif-b', 24, col, xscale=0.58, align='c', valign='m', pad=0, canvas=out, box=(cx - 70, box[1] - 1, 140, box[3] + 2))
        save_all(gid, out)
    # 004_f20: katakana glosses under SELECT TRACK / RETRY
    gid = 'at00/result17/004_f20'; o = orig(gid); out = o.copy()
    for b in [(53, 27, 112, 40), (53, 63, 112, 80), (24, 106, 51, 120), (103, 106, 130, 120)]: clear(out, b)
    # flavour text (original art, garbled 'N ERV HQt' and too wide for the 64 px obj1 / 112 px obj2 sprites)
    clear(out, (174, 35, 240, 48)); tiny(out, 'NERV HQ', 175, 36); tiny(out, '1st Command Center', 175, 42, maxw=56)
    flavour(out, 120)
    save_all(gid, out)
    # personnel cards
    for arc_id, name in CARD_NAMES.items():
        gid = f'{arc_id}/000_5988'; o = orig(gid); out = o.copy()
        clear(out, (106, 11, 182, 33)); clear(out, (58, 150, 148, 163))
        typeset.text_image(0, 0, name, 'serif-b', None, ORG, xscale=0.62, align='l', valign='m', pad=0, max_size=20, canvas=out, box=(107, 11, 74, 20))
        typeset.text_image(0, 0, 'PERSONAL DATA', 'sans-cond-b', None, ORG, align='c', valign='m', pad=0, max_size=13, canvas=out, box=(60, 150, 86, 13))
        given, family = name.split(); roman = f'{family.upper()}, {given}'   # original 'IKARI, gendou': match the heading's spelling
        clear(out, (106, 33, 194, 46)); tiny(out, roman, 110, 34, size=11, maxw=82)
        clear(out, (36, 202, 120, 211)); tiny(out, roman, 38, 203, size=7, font='sans-b', tracking=0.6)
        out = fix_search(out)
        save_all(gid, out)

SECTIONS['results'] = gen_results


# ---------------------------------------------------------------- gallery
import numpy as np

def inpaint(img, box, white_min=170, iters=60):
    """Remove near-white lettering inside box by diffusing the surrounding colours into it (for text drawn over art)."""
    a = np.array(img.convert('RGBA')).astype(float); x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    mask = (reg[..., :3].min(axis=2) > white_min) & (reg[..., 3] > 60)
    for _ in range(2):   # grow over the anti-aliased halo
        m = mask.copy(); m[1:] |= mask[:-1]; m[:-1] |= mask[1:]; m[:, 1:] |= mask[:, :-1]; m[:, :-1] |= mask[:, 1:]; mask = m
    known = ~mask; cur = reg.copy(); cur[mask] = 0
    for _ in range(iters):
        wsum = np.zeros(mask.shape); acc = np.zeros(reg.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1)); v = np.roll(cur, (dy, dx), (0, 1))
            if dy: k[0 if dy > 0 else -1, :] = False   # no wraparound from the opposite edge
            if dx: k[:, 0 if dx > 0 else -1] = False
            wsum += k; acc += v * k[..., None]
        fill = mask & ~known & (wsum > 0)
        cur[fill] = acc[fill] / wsum[fill][:, None]; known = known | fill
    a[y0:y1, x0:x1] = cur
    return Image.fromarray(a.clip(0, 255).astype('uint8'), 'RGBA')

TRAILER_ICONS = {'051_0': 1, '052_0': 2, '053_0': 3, '054_0': 4, '055_0': 5, '056_0': 6, '057_0': 7, '058_0': 8, '059_0': 9}
GAL_TEXT = {   # 256x128 white caption images
    **{f'{n:03d}_0': f'Total rank {r}\nto unlock' for n, r in zip(range(64, 73), (150, 160, 180, 200, 220, 240, 260, 280, 300))},
    **{f'{n:03d}_0': f'Total rank {r} to unlock' for n, r in zip(range(74, 81), (20, 40, 60, 80, 100, 120, 140))},
    '081_0': 'Illustration 01', '092_0': 'Illustration 02', '102_0': 'Illustration 03', '103_0': 'Illustration 04', '104_0': 'Illustration 05', '105_0': 'Illustration 06',
    '106_0': 'Character Bento 01', '107_0': 'Character Bento 02', '108_0': 'Character Bento 03', '082_0': 'Character Bento 04', '083_0': 'Character Bento 05',
    '084_0': 'Composition 01', '085_0': 'Composition 02', '086_0': 'Composition 03', '087_0': 'Composition 04', '088_0': 'Composition 05', '089_0': 'Composition 06', '090_0': 'Composition 07',
    '091_0': 'Trailer 01', '093_0': 'Trailer 02', '094_0': 'Trailer 03', '095_0': 'Trailer 04', '096_0': 'Trailer 05', '097_0': 'Trailer 06', '098_0': 'Trailer 07', '099_0': 'Trailer 08', '100_0': 'Trailer 09',
    '101_0': 'Analog Pad: Move',
}
GAL_TITLES = {'022_0': 'ENDING', '024_0': 'ILLUSTRATIONS', '061_0': 'TRAILERS'}

def gen_gallery():
    white = (255, 255, 255, 255)
    for k, n in TRAILER_ICONS.items():
        gid = f'gallery/gallery/{k}'; o = orig(gid); out = inpaint(o, (6, 16, 60, 52))
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):   # dark 1px outline so the lettering reads on any art
            typeset.text_image(0, 0, 'TRAILER', 'sans-cond-b', 12, (0, 0, 0, 255), align='c', valign='t', pad=0, canvas=out, box=(2 + ox, 16 + oy, 60, 14))
        typeset.text_image(0, 0, 'TRAILER', 'sans-cond-b', 12, white, align='c', valign='t', pad=0, canvas=out, box=(2, 16, 60, 14))
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            typeset.text_image(0, 0, str(n), 'serif-b', 30, (0, 0, 0, 255), xscale=0.8, align='c', valign='t', pad=0, canvas=out, box=(2 + ox, 26 + oy, 60, 34))
        typeset.text_image(0, 0, str(n), 'serif-b', 30, white, xscale=0.8, align='c', valign='t', pad=0, canvas=out, box=(2, 26, 60, 34))
        save(gid, out)
    for k, text in GAL_TEXT.items():
        gid = f'gallery/gallery/{k}'; o = orig(gid); out = Image.new('RGBA', o.size, (0, 0, 0, 0))
        lines = text.split('\n')
        for i, ln in enumerate(lines):
            typeset.text_image(0, 0, ln, 'segoe', 16, white, xscale=0.95, align='l', valign='t', pad=0, canvas=out, box=(1, i * 20, 255, 20))
        save(gid, out)
    for k, text in GAL_TITLES.items():
        gid = f'gallery/gallery/{k}'; o = orig(gid); out = Image.new('RGBA', o.size, (0, 0, 0, 0))
        typeset.text_image(0, 0, text, 'serif-b', None, (225, 225, 240, 255), xscale=0.62, align='l', valign='m', pad=1, max_size=28, canvas=out, box=(0, 0, o.width, o.height))
        save(gid, out)

SECTIONS['gallery'] = gen_gallery


# ---------------------------------------------------------------- cof* subtitle lines (256x32 white glow text); text in notes/subs.tsv
def glow_line(text, size=(256, 32)):
    w, h = size; out = Image.new('RGBA', size, (0, 0, 0, 0))
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    typeset.text_image(w, h, text, 'sans-cond-b', None, (255, 255, 255, 255), xscale=1.0, align='l', valign='m', pad=4, max_size=26, min_size=9, canvas=layer, box=(0, 0, w, h))
    a = layer.getchannel('A'); halo = a.filter(ImageFilter.GaussianBlur(2.2)).point(lambda v: min(255, int(v * 1.3)))
    out.putalpha(halo); out = Image.merge('RGBA', (*Image.new('RGB', size, (255, 255, 255)).split(), halo))
    solid = Image.new('RGBA', size, (255, 255, 255, 0)); solid.putalpha(a); out.alpha_composite(solid)
    return out

def gen_subs():
    for ln in open('notes/subs.tsv', encoding='utf-8'):
        if not ln.strip() or ln.startswith('#'): continue
        gid, text = ln.rstrip('\n').split('\t'); o = orig(gid); save(gid, glow_line(text, o.size))

SECTIONS['subs'] = gen_subs


# ---------------------------------------------------------------- XMB background (PSP_GAME/PIC1.PNG, 480x272 RGB) -> gfx/PSP_GAME/PIC1.png
def gen_pic1():
    o = Image.open('work/iso/PSP_GAME/PIC1.PNG').convert('RGBA')
    out = inpaint(o, (284, 214, 428, 269), white_min=140)
    out = inpaint(out, (0, 255, 100, 272), white_min=95)
    W = (255, 255, 255, 255)
    typeset.text_image(0, 0, 'REBUILD OF', 'serif-b', 11, W, xscale=0.85, align='c', valign='t', tracking=3, canvas=out, box=(286, 214, 140, 13))
    typeset.text_image(0, 0, 'EVANGELION', 'serif-b', 30, W, xscale=0.74, align='c', valign='t', tracking=2, canvas=out, box=(286, 226, 140, 30))
    typeset.text_image(0, 0, '— SOUND IMPACT —', 'serif-b', 10, W, xscale=0.9, align='c', valign='t', tracking=2, canvas=out, box=(286, 256, 140, 12))
    typeset.text_image(0, 0, '©khara  ©2011 NBGI', 'sans', 9, W, align='l', valign='t', pad=0, canvas=out, box=(3, 259, 100, 10))
    os.makedirs('gfx/PSP_GAME', exist_ok=True); out.convert('RGB').save('gfx/PSP_GAME/PIC1.png')

SECTIONS['pic1'] = gen_pic1


# ---------------------------------------------------------------- select-track hint bar and save/load captions
def gen_hints():
    gid = 'game_select/game_select/001_2e14'; o = orig(gid); out = o.copy(); W = (255, 255, 255, 255)
    clear(out, (43, 0, 138, 16)); clear(out, (182, 0, 256, 16))
    typeset.text_image(0, 0, 'Options Menu', 'sans-cond-b', None, W, align='l', valign='m', pad=0, max_size=12, canvas=out, box=(43, 0, 94, 16))
    typeset.text_image(0, 0, 'Save / Load', 'sans-cond-b', None, W, align='l', valign='m', pad=0, max_size=12, canvas=out, box=(182, 0, 72, 16))
    save(gid, out)
    gid = 'game_select/save_load__bin/000_f74'; o = orig(gid); out = o.copy()
    for box in [(112 + 18, 26, 112 + 43, 39), (112 + 84, 26, 112 + 106, 39), (112 + 18, 66, 112 + 43, 79), (112 + 84, 66, 112 + 106, 79)]: clear(out, box)
    flavour(out, 73)
    save(gid, out)

SECTIONS['hints'] = gen_hints


# ---------------------------------------------------------------- save-data icon (saveload.cpk/icon0.png, 144x80) -> gfx/raw/saveload/icon0.png
def gen_icon():
    o = Image.open('work/cpk/saveload/icon0.png').convert('RGBA')
    out = inpaint(o, (30, 42, 114, 64), white_min=130)
    W = (255, 255, 255, 255)
    typeset.text_image(0, 0, 'REBUILD OF', 'serif-b', 6, W, xscale=0.9, align='c', valign='t', tracking=2, canvas=out, box=(30, 43, 84, 7))
    typeset.text_image(0, 0, 'EVANGELION', 'serif-b', 15, W, xscale=0.8, align='c', valign='t', tracking=1, canvas=out, box=(30, 50, 84, 14))
    os.makedirs('gfx/raw/saveload', exist_ok=True); out.convert('RGB').save('gfx/raw/saveload/icon0.png')

SECTIONS['icon'] = gen_icon

SECTIONS['help'] = lambda: __import__('gen_help').gen_help()
SECTIONS['expl'] = lambda: __import__('gen_help').gen_expl()

if __name__ == '__main__':
    for s in (sys.argv[1:] or SECTIONS): SECTIONS[s]()
