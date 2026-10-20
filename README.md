# Rebuild of Evangelion -Sound Impact- English translation

Unofficial English fan translation of **Evangelion Shin Gekijouban -3nd Impact-** (*Rebuild of Evangelion -Sound
Impact-*, PSP, Bandai Namco, 2010, NPJH-50457): the source text and tools that build the patch.

**No game data is included.** Download the xdelta patch from the [latest release](../../releases/latest) and apply it to
your own dump of the Japanese UMD (1,142,915,072 bytes, CRC32 D8515C17). The release README lists the hashes,
patching steps and known issues.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What is translated
- All menus, the option screen, help and explanation pages, save/load prompts, the pause menu and loading screens.
- Song cards, unlock notices, results screens and gallery captions.
- 150 subtitle lines in the "Call of Fourteen" songs, the title logo and the piracy notice.
- The XMB icon, background and title, and the game's built-in text strings.
- Names follow the Rebuild of Evangelion English wording ("Angel Session", "Call of Fourteen", "Provisional Unit-05",
  "The Beast").
- Text inside the videos (song title cards, credits roll) stays Japanese.

## Building from source
You need your own ISO and Python with Pillow and numpy. See `CLAUDE.md` for the commands (`python tools/unpack_all.py`,
`tools/gen_gfx.py`, `tools/build.py`).

- `text/eboot.tsv`: EBOOT strings (Japanese + English)
- `notes/subs.tsv`: song subtitles; `notes/`: research notes
- `tools/`: disc/archive unpacking, GIM image redraw, build and QA tools
- `routes/`: emulator routes for QA

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project
owner. Evangelion is (c) khara; the game is (c) Bandai Namco Games. This project is not affiliated with them. Do not
share patched images.
