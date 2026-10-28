# Recovered custom tunes

The owner requested Twiggy, Air65 Savage, Tordle 2S and Tordl3 3S, including filters. The earlier instruction to omit PID/filter presets is superseded for these named builds. Full backups and raw Blackbox files are not published; this repository contains selected tune/filter values only.

## Selected sources

| Entry | Source PID slot (CLI index) | Roll P/I/D/F | Pitch P/I/D/F |
| --- | --- | --- | --- |
| Twiggy Savage, 4.5 | `SB405-AIO/tuning/SAVAGE_TUNE.txt`, 0 | 63 / 95 / 54 / 125 | 65 / 99 / 62 / 131 |
| Air65 Savage, 4.5 | `A65/SavageTune.txt`, 2 | 76 / 108 / 50 / 153 | 79 / 114 / 57 / 159 |
| AIR65 C Savage, 2026.6 alpha | latest `A652C/SAVAGE…` backup, 2 | 76 / 108 / 50 / 153 | 79 / 114 / 57 / 159 |
| Tordle 2S, vendor 4.6 | `Lazarus/tuning/SAVAGE TUNE.txt`, 0 | 45 / 60 / 28 / 60 | 47 / 63 / 32 / 62 |
| Tordl3 3S, 4.5 | `crazy-f405/SavageTune.txt`, 0 | 45 / 80 / 40 / 120 | 56 / 100 / 55 / 149 |

The owner explicitly confirmed the Tordle battery/build mapping. The displayed D columns are the native firmware's CLI values and should not be compared as if 4.5 D-min and 4.6 D-max used the same convention. PIDs omitted in a diff are filled from reference defaults: notably Tordle 2S roll/yaw P=45 and pitch P=47, and Tordl3 roll 45/80/40/120. The complete restored values are in `tunes.json`.

Twiggy's final SAVAGE file supersedes `D-Set.txt`, `P-D+Master Set.txt`, and `Twiggy_PreTune.txt`. Its first two PID slots have the same numeric tune; slot 2 has more D and a different simplified D-max slider. The named SAVAGE profile 0 is the recovered final tune, not all sweep variants.

Air65's named Savage profile is index 2 in `A65/SavageTune.txt`. The newer July `Air65` rebuild has the HQ31mm and 1219S profiles but no named Savage profile; it does not replace the explicitly named Savage tune. The September AIR65 C backup copies the Savage main gains into profile 2, providing corroborating later evidence. It uses different gyro/notch filters and native D-max settings, so its own firmware-specific entry is included.

Lazarus's latest working SAVAGE profile supersedes the July Tordle/M8 backups and initial RC setup. Files such as `MasterSweep.TXT`, `D 0_*.TXT`, `FilterTweak.TXT` and `FilterTweak2.TXT` contain Blackbox data despite their text extensions. Their headers show zero-I/zero-feedforward tuning sweeps, not a second finished battery tune. They were inspected locally to distinguish test states from the final CLI tune. The actual 3S build was found under `crazy-f405` with craft name Tordl3.

## Filters and compatibility

Each entry restores explicit gyro low-pass types/cutoffs, gyro notch state, dynamic notch parameters, RPM harmonics/weights/cutoffs, D-term low-pass types/dynamic limits/static notch, yaw low-pass, and simplified filter metadata. Values omitted by the diff are filled from upstream default references; matching source overrides win. No full-FC or parameter-group reset is used.

Important source differences include:

- Twiggy: gyro LPF2 400 Hz, two dynamic notches spanning 70–850 Hz, RPM minimum 70 Hz, D-term LPF1 dynamic 71–142 Hz and LPF2 142 Hz.
- Original Air65: gyro LPF1 disabled with a 500 Hz LPF2 baseline; one dynamic notch, Q500, 200–450 Hz; RPM minimum 200 Hz.
- AIR65 C: LPF2 550 Hz, one dynamic notch, Q400, 120–400 Hz; native D-max disabled on roll/pitch.
- Tordle 2S: BIQUAD gyro LPF2 450 Hz, one Q500 dynamic notch, a 300/200 Hz D-term static notch, thrust linearization 30 and battery sag compensation 100.
- Tordl3 3S: two dynamic notches spanning 125–850 Hz, two RPM harmonics, accelerometer LPF 10 Hz, pitch D-min 40 / upper D55, thrust linearization 20 and battery sag compensation 100.

Global gyro/dynamic-notch/RPM settings affect every PID profile. D-term and other profile tune values affect only the currently selected PID profile. PID/rate selection, rates, throttle curves, auto battery-profile selection, motor output limit, physical idle percentage, loop divisor, bidirectional DShot enablement, motor poles, board alignment, motor mapping, modes and OSD remain unchanged. Saved RC smoothing is optional and off by default.

Do not combine Tordle 2S and 3S in one battery checkbox without a separately validated firmware conversion. Their saves are from different firmware generations and use changed D semantics. Native version labels are intentionally narrow. The 4.6 vendor firmware has no recoverable source revision; the 2025.12 reference supplies omitted defaults, and its exact firmware acceptance/factory defaults remain unverified. The AIR65 C source is an alpha build. All entries remain EXPERIMENTAL, and no hardware was connected.

Default references: upstream `firmware-presets` tune files for 4.5, 2025.12 and 2026.6; common filter defaults from 4.5 (also included by newer upstream filter presets); firmware `pg/dyn_notch.c`, `pg/rpm_filter.c` and `flight/pid.c`. Firmware source corrects the 4.5 preset-default file's EZ landing limit from 5 to 15 and supplies omitted feedforward defaults. The builder never runs `simplified_tuning apply`; restoring slider metadata must not recalculate recorded gains.

## Other possible custom tunes

These are worth reviewing, but were not added as new tune presets without a request. Non-default values prove a saved configuration, not who authored it.

| Candidate | Evidence | Confidence / distinction |
| --- | --- | --- |
| Halo / AOS7 | `HD0Halo/AOS7_SAVAGE.txt`, profile 0: roll 53/95/35/187, pitch 53/95/40/185; 1000 Hz gyro LPF2, simplified gyro filtering OFF, RPM weights 100/0/80 | Strong candidate: explicitly saved as SAVAGE and distinct from the requested builds |
| AOS4 | latest `AOS4/BetaFlight` backup: roll 67/119/50/195, pitch 70/125/57/203; simplified master 125 | Non-default tune; authorship unclear |
| AOS 5 | latest `AOS 5/Backups` file: roll 56/100/35/187, pitch 56/100/40/185 | Non-default tune; related to Halo settings but different gains |
| Air65 prop-specific profiles | `F1219S` and `FHQ 31mm` in A65, and `HQ 31mm` / `1219S` in the later Air65 rebuild | Distinct saved prop profiles, possibly factory/borrowed rather than additional Savage tunes |
| M8 / Lion4 / early Lazarus | Same roll 46/82/27/113 and pitch 48/86/30/118 in their latest relevant saves | One repeated older tune, not three separate custom tunes; superseded for Lazarus by final SAVAGE |

AIR65 C's named Savage profile is the same main PID set as the requested Air65 tune, not an additional forgotten PID tune. AIR65 Race2's setup retains the stock GF1207 PIDs, so it is not a strong candidate for a separate custom Savage tune. Zero-I D sweeps, MasterTesting and pre-tune files are intermediate experiments and were not promoted to final presets.
