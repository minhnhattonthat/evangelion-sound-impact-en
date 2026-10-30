# Rebuild of Evangelion -Sound Impact- English translation

Unofficial English fan translation of **Evangelion Shin Gekijouban -3nd Impact-** (*Rebuild of Evangelion -Sound
Impact-*, PSP, Bandai Namco, 2010, NPJH-50457): the source text and tools that build the patch.

**No game data is included.** Download the xdelta patch from the [latest release](../../releases/latest) and apply it to
your own dump of the Japanese UMD (1,142,915,072 bytes, CRC32 D8515C17). The release README lists the hashes,
patching steps and known issues.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status
| Part | Status |
|---|---|
| Menus, options, help and explanation pages, save/load prompts, pause menu, loading screens | Translated |
| Song cards, unlock notices, results screens, gallery captions | Translated (tiny 5 px detail lines on the result personnel cards left in Japanese) |
| "Call of Fourteen" song subtitles | Translated (150 lines) |
| Title logo, piracy notice, XMB icon/background/title, built-in text strings | Translated |
| Text inside the videos (song title cards, credits roll) | Left in Japanese (baked into the .pmf videos) |
| Stage art | Not checked in play (not re-surveyed after the last pass) |

Names follow the Rebuild of Evangelion English wording ("Angel Session", "Call of Fourteen", "Provisional Unit-05",
"The Beast").

Known issues: two result title bars keep a stray middle-dot; the "Object Unlock Report" footer on dialogs and the
title-menu colours are the original game's design.

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
