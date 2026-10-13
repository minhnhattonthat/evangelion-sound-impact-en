# Rebuild of Evangelion -Sound Impact- (PSP, NPJH50457) English patch

Rhythm game: almost all text is GIM images inside CRI CPK/ARC archives. Skill: `.agents/skills/translate-retro-game` (read `references/platform-psp.md` first).
Python: `python -X utf8`. Run everything from this folder. Pillow + numpy needed for image work.

## Commands
- Unpack disc: `python tools/unpack_all.py` (-> `work/iso`, `work/cpk`, `work/arc`, `work/gim`; ~1.5 GB, gitignored)
- Redraw all English images: `python tools/gen_gfx.py [section..]` (writes `gfx/`). Sections: saveload title notice pause loading cards menu option unlock results gallery subs pic1 icon hints help expl (help pages: tools/gen_help.py)
- Look at images: `python tools/showgim.py OUT.png <cpk>/<arc>/<NNN>_<hexoff> --new` (original | replacement); `tools/uniq_sheets.py REGEX PREFIX` = contact sheets of untranslated unique GIMs (set ALL=1 to include translated)
- Build ISO: `python tools/build.py build/test.iso` (~45 s; EBOOT strings from `text/eboot.tsv`, subtitles from `notes/subs.tsv`)
- QA: `python <skill>/scripts/emu.py build/test.iso --out work/qaN --route routes/to_song.txt --smoke --sheet`; states: `--save-state/--state-in`; PPSSPP is in `tools/PPSSPPWindows64.exe`, memstick `tools/memstick` (saves persist: `--clean-saves`)
- Decrypted EBOOT: `work/EBOOT.dec.elf`, dumped by PPSSPP with `DumpFileTypes = 7` in `tools/memstick/PSP/SYSTEM/ppsspp.ini`

## Rulings (confirm with user, not yet asked)
- Names: Rebuild of Evangelion title wording, "Angel Session", "Call of Fourteen", "HEX", "Teardrop", "Number 5", "AT", Unit-01/00/02, Provisional Unit-05, The Beast. Full names, no abbreviations.
- Japanese button layout: circle = OK, cross = cancel. Button icons in text pictures are kept from the originals.

## Status
Done and checked in-game: help + explanation pages (game_select 008_*; the old tiny dummy page f55e4 left), save/load prompts, title logo + copyright + piracy notice, pause menu, loading, song cards (list + selected), menu/option/unlock notices, results (header, FINISHED/GAME OVER, personnel cards), gallery captions, 150 cof* subtitle lines, XMB icon/background/title, EBOOT strings, select-track hint bar.
Open: tiny personnel-card detail lines (5 px Japanese text on each card: needs a 5 px font pass), `・` dots in 2 result title bars (hex01/hex02), video text (PMF: song-name title cards "予告" "使徒セッション", credits roll) not touched, td*/ss*/yu* stage art not re-surveyed after the last pass, no release patch built (ISO is 1.1 GB; xdelta3), no git identity set here (nothing committed yet).
