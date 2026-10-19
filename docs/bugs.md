# Bugs

Tick `- [x] (fixed in <build>)` once re-checked from the cited state.

## 2026-10-20 playtest - test.iso sha1 ed5432fe791a
Evidence: `work/playtest/2026-10-20/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] (fixed in 8f45475848ea) step 0012 - text - auto-save notice - mojibake for ™ (UTF-8 bytes shown as cp1252) - "the Memory Stickâ„¢ access indicator will blink"
- [x] (fixed in 8f45475848ea) step 0040 - text - HELP, Call of Fourteen - left-panel line cut off at the panel edge - "Move the waveform up and d"
- [x] (fixed in 8f45475848ea) step 0040 - text - HELP, Call of Fourteen - stray garbage glyphs above the "Waveform" label in the screenshot, and a stray tick after "Target" - "' ' ▯ '"
- [x] (fixed in 8f45475848ea) step 0030 - text - RETRY/SELECT TRACK screen after results - flavour text clipped and garbled. The same block on the SAVE/LOAD screen (step 0021) is whole: "1st Command Center", "MAGI01 Databanks". Here: "N ERV HQt", "1st Command Cente", "Recording Saced To MAGI 01 Databan"
- [x] (fixed in 8f45475848ea) step 0021 - wording - SAVE/LOAD screen - typo "Saced" and missing space - "Recording Saced ToMAGI01 Databanks"
- [x] (fixed in 8f45475848ea) step 0029 - wording - result card (all characters, also step 0042) - typo "Seach" - "Seach Results: Personal Data"
- [x] (fixed in 8f45475848ea) step 0029 - text - result card - stray mark or tail hanging off the "d" in "Mission Failed" (same at step 0042) - "Mission Failed"
- [x] (fixed in 8f45475848ea) step 0025 - text - HELP p1, Angel Session - small stray marks between "button" and "as" (leftover pixels) - "Press the indicated button as an Angel's"
- [x] (fixed in 8f45475848ea) step 0016-0018 - text - OPTION menu - a small fixed tick right of "OPTION" overlaps every description line - "Change the auto-save setting."
- [x] (fixed in 8f45475848ea) step 0025-0027 - wording - HELP footer - "Back to Title" returns to the song's BACK/START/HELP menu, not the title - "Back to Title"
- [x] (fixed in 8f45475848ea) step 0029 - wording - result card - romanized names in lowercase with a long vowel ("gendou") don't match the card heading or the glossary - "IKARI, gendou" / "KATSURAGI, misato"
- [x] (fixed in 8f45475848ea) step 0013 - wording - song card Track 01 (also step 0024) - the big title wraps as "Angel Session" / "4th", then repeats as "Angel Session 4th". Track 02 puts the character name on line 2 instead - "Angel Session / 4th / Angel Session 4th"
- [x] (fixed in 8f45475848ea) step 0016 - wording - OPTION menu - each small sub-label repeats the big label (leftover from Japanese subtitles?) - "BGM / BGM", "SE / SE", "AUTO SAVE / AUTO SAVE"
- [ ] step 0008 - wording - every save/notice/option/pause dialog frame - the frame footer says "Unlock Report" even on save prompts and options (maybe original decoration) - "Object Unlock Report" -- wontfix: original NERV frame decoration (kazari2 sprite, same English in the Japanese release)
- [ ] step 0002 - wording - title (also step 0006) - the unselected item is dark red on red and almost unreadable, and the cursor defaults to CONTINUE when a save exists (maybe original) - "NEW GAME" -- wontfix: original title art colours and cursor behaviour, untouched by the patch
