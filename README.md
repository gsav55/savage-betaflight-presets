# Savage Betaflight presets

Personal preset source for quickly setting up new drones, reviewed from 93 CLI backups in Drone logs. Repository: **public**, [gsav55/savage-betaflight-presets](https://github.com/gsav55/savage-betaflight-presets), branch `main`.

## Add this source in Betaflight

In **Presets → Preset Sources → Add new source**, enter:

- Name: **Savage presets**
- URL: **`https://github.com/gsav55/savage-betaflight-presets`**
- GitHub branch: **`main`**

Enable the source, refresh, filter to your connected firmware version, and search **Savage**. Apply a modes preset, an OSD preset, and a rates preset, reviewing options each time. The repository is public, so no login or local launcher is required.

## Optional offline local source

The included local launcher remains useful offline or for previewing unpushed edits:

1. Double-click **Start Preset Source.command** in this folder. Keep the Terminal window open. Requires Python 3, already available on this Mac. You can also run `python3 scripts/serve.py` from this folder.
2. In Betaflight, open **Presets → Preset Sources → Add new source**.
3. Name: **Savage local**. URL: **`http://127.0.0.1:18765/`**. Leave GitHub branch blank; this is a website source. Enable it and refresh the preset list.
4. If the browser requests local-network access, allow it for Betaflight. The launcher permits the official Betaflight app origins and desktop app (`null`) origin. If your older Configurator/browser blocks a local source, use the matching desktop Configurator or the manual procedure below.
5. Filter to the connected firmware version; search **Savage**. Apply a modes preset, an OSD preset, and a rates preset. Review options each time.

The server binds only to this computer's loopback address. It serves `index.json`, `index_hash.txt`, and preset text files only; backup files, repository metadata, and documentation are not served. Stop it with Control-C. No GitHub token is embedded in the presets or source URL. The local source continues working offline and uses whichever branch/files are checked out locally. It does not automatically pull from GitHub.

**Manual fallback:** back up the FC, open the matching `.txt` file, copy its unconditional CLI lines plus only the desired option blocks into the CLI, then `save`. Metadata comments do not implement checkboxes in CLI: pasting the entire preset file would apply every alternative. Keep props off for mode/failsafe verification. Make a fresh `diff all` after applying and compare it with the backup.

## Included presets

There are **31 presets**: 10 modes/failsafe presets, 15 OSD presets, one preset that installs three rate profiles, and five native-firmware tune/filter entries. Modes, OSD and rates presets preserve PID/filter settings. The tune entries intentionally restore PID and filter settings; motor protocol, board alignment, resources, UARTs, receiver protocol and VTX power remain untouched.

| Type | Choices |
| --- | --- |
| Modes + failsafe | GPS rescue or non-GPS DROP, separately for each firmware generation |
| Switch layout | Newest six-position layout selected by default; legacy analog whoop, HDZero whoop, and Twiggy alternatives |
| OSD | Analog NTSC 30×13, HDZero 53×20, DJI O4 53×20 |
| Battery checkbox | **Single-cell battery reporting**, checked by default (`report_cell_voltage` affects telemetry reporting; an average-cell OSD element remains an average-cell element) |
| GPS checkbox | **More GPS details**, checked by default: home arrow/distance, speed, coordinates, altitude; PDOP where supported |
| GPS display selection | Non-GPS selected by default; choose GPS-equipped drone to show satellites and checked details |
| Other OSD options | Imperial units; current and mAh display for a calibrated current sensor |
| Other mode options | Rate-profile selection on AUX4; UBLOX WAAS/Galileo; allow arming without GPS fix |
| Custom tunes + filters | Twiggy, Air65 Savage (original and AIR65 C filters), Tordle 2S, Tordl3 3S |

GPS display and flight GPS are separate presets. Choosing GPS in OSD changes only overlays. Apply the GPS modes/failsafe preset separately when appropriate. For a non-GPS drone, GPS fields remain hidden even though the More GPS details checkbox starts checked. Choosing GPS and unchecking More GPS details shows satellites only. OSD presets replace the shared layout fields and normalize visibility across all three OSD profiles; active profile becomes 1. They preserve alarm thresholds and units unless you select Imperial units.

HDZero layout: newest `HD0Halo/AOS7_SAVAGE.txt`. DJI O4 layout: latest `AOS 5/Backups` backup, explicitly selected by the owner. Analog layout: newest `A65Race2/Setup.txt`. GPS overlays on analog are adapted to fit NTSC. Digital presets require OSD/MSP DisplayPort support in the firmware, a correctly configured VTX UART, and a compatible goggles canvas. Check the layout in the actual goggles; firmware/OSD fonts and canvas negotiation can affect its appearance.

## Default switches

These are **one-based AUX numbers**, unlike the CLI's zero-based channel indices. Ranges are the values reported by the backup, with the upper boundary treated as exclusive by Betaflight.

| AUX | Function | Range |
| --- | --- | --- |
| AUX1 | Arm | 1500–2100 |
| AUX2 | Horizon | 1125–1275 |
| AUX2 | Angle | 1325–1450 |
| AUX2 | Prearm | 1300–1625 |
| AUX2 | Altitude hold, GPS preset on 2025.12 / 2026.6 | 1550–1675 |
| AUX2 | Position hold, GPS preset on 2025.12 / 2026.6 | 1750–1875 |
| AUX2 | GPS rescue, GPS preset only | 1950–2100 |
| AUX3 | Turtle | 1400–1600 |
| AUX3 | Beeper | 1900–2100 |
| AUX4 | Optional rate-profile selection | 900–2100 |

The modes preset **replaces all 20 mode slots and clears all 30 adjustment ranges**, preventing old ARM, FAILSAFE, rescue or in-flight tuning assignments from remaining active. It does not copy PID-profile switching from the backup. Optional AUX4 selection is the newest layout's rate-profile selector. For legacy layouts with GPS, rescue is deliberately assigned to AUX7 high so it cannot overlap their AUX2 Horizon range. Review every selected layout against the radio before flight. The newest prearm range overlaps Angle and part of the altitude-hold selection; this is preserved from the owner's backup.

Modes 3 and 11 are omitted from 4.4, 4.5 and vendor 4.6 presets because they were unavailable or cannot be confirmed on those builds. Newer hold modes require the matching firmware features and sensors. Non-GPS presets disable GPS and select DROP. GPS presets enable GPS, select GPS-RESCUE, enable rescue sanity checks and require a fix before arming by default. Both explicitly set the Stage 1 delay to 1.5 seconds.

**Intentional change from the GPS backups:** `gps_rescue_allow_arming_without_fix` starts OFF. There is an unchecked option to restore the backups' ON behavior. GPS rescue cannot return home until fix/home requirements are met. GPS rescue trajectory, throttle, minimum satellites, altitude, receiver channel failsafe values and other airframe-specific parameters are preserved; this preset is not a complete GPS commissioning procedure. Verify receiver-loss behavior on the bench, then test switch-activated rescue in a suitable area before relying on it. A preset cannot verify those hardware behaviors.

## Rates

The **Three rate profiles - Standard, Race, Tuning** preset installs these Actual rates in order. Betaflight displays profiles 1–3; CLI indices are 0–2. Each tuple below is **roll / pitch / yaw**. Center sensitivity and maximum rate are degrees/second; expo 0.20 is stored as CLI `20`.

| Profile | Name | Center sensitivity | Maximum rate | Expo |
| --- | --- | --- | --- | --- |
| 1 | 60\|54\|20 | 60 / 60 / 60 | 540 / 540 / 540 | 0.20 / 0.20 / 0.20 |
| 2 | Race | 60 / 60 / 120 | 540 / 540 / 730 | 0.20 / 0.20 / 0.20 |
| 3 | Tuning | 150 / 150 / 150 | 150 / 150 / 150 | 0 / 0 / 0 |

Tuning was recovered from `SB405-AIO/tuning/SAVAGE_TUNE.txt`. The preset writes Actual rate type, profile name and all nine axis values in each of the first three slots. Profile 4, throttle curves, rate limits, PID profiles and filters are preserved.

Choose the active profile using the mutually exclusive **Active rate profile after applying** checkboxes. Profile 1 is checked by default. If you clear every checkbox, the preset still finishes on profile 1. This choice changes only the final active profile; all three rate sets are always installed. Transmitter adjustments can subsequently change the active profile if rate-profile switching is configured.

## Custom tunes and filters

Select the intended **PID profile** in Betaflight before applying a tune. These presets change that profile's PIDs, D-term filtering and tune controls, plus the **global gyro/dynamic-notch/RPM filters** shared by every profile. They do not switch PID or rate profiles, or alter the three saved rate sets. Each tune requires working bidirectional DShot RPM telemetry, correct motor-pole configuration, and the original build/loop setup. They preserve motor protocol, idle percentage, motor pole count and PID loop divisor. Saved RC smoothing is an optional unchecked checkbox when present in the source.

| Preset | Native firmware | Source |
| --- | --- | --- |
| Twiggy Savage | 4.5 (saved on 4.5.5) | `SB405-AIO/tuning/SAVAGE_TUNE.txt`, profile 1 |
| Air65 Savage | 4.5 (saved on 4.5.0) | `A65/SavageTune.txt`, profile 3 named Savage |
| Air65 Savage - AIR65 C filters | 2026.6 alpha | `A652C/SAVAGE_BTFL_cli_backup_AIR65_C_20260928_202051_BETAFPVG473_V2.txt`, profile 3 |
| Tordle 2S Savage | Vendor 4.6.0 | `Lazarus/tuning/SAVAGE TUNE.txt`, profile 1 |
| Tordl3 3S Savage | 4.5.0 | `crazy-f405/SavageTune.txt`, profile 1 |

The owner confirmed **Lazarus = 2S** and **Tordl3 = 3S**. Those saves use different D-term semantics: 4.5 stores upper D in `d_roll`/`d_pitch` and lower D in `d_min_*`; the vendor 4.6 save stores base D plus `d_max_*`. They are separate native-version presets, rather than an unverified 2S/3S conversion checkbox. Other firmware generations are deliberately not claimed as tune-compatible merely because a setting name exists.

The AIR65 C entry preserves the later backup's own global filters and native D-max settings; its main Savage P/I/D/F values match the original Air65. All entries fill omitted diff values from documented reference defaults, then preserve the source overrides. This explicitly restores such things as zero yaw D, D-min/D-max, feedforward, TPA and filter types instead of inheriting an unrelated tune. No `simplified_tuning apply` is issued, so recorded gains are not recalculated from slider settings. The vendor 4.6 source revision and exact factory defaults are unavailable: its omitted values use the documented 2025.12 reference and remain experimental, requiring verification on the original build.

See [tune recovery notes and other candidates](docs/tunes.md) and [portable tune data](tunes.json). Back up the FC, verify RPM telemetry and settings with props removed, then perform a short cautious test and check motor temperatures. No tune was applied to hardware during recovery.

## Compatibility and provenance

See [review notes](docs/review.md), [complete backup inventory](docs/backup-inventory.json), and [portable source catalog](catalog.json). The catalog contains only selected setting excerpts and command-name compatibility snapshots, not complete FC dumps, receiver identifiers, radio models, or flight logs. Original backups remain untouched outside this repository.

| Preset firmware label | Backup evidence | Validation basis |
| --- | --- | --- |
| 4.4 | 4.4.3 | Official 4.4.3 CLI and modes |
| 4.5 | 4.5.0 / .1 / .2 / .3 / .5 | Official 4.5.0 common commands; checked 4.5.5 changes |
| 4.6 | Vendor 4.6.0, May 12 2025, `norevision`, MSP 1.47 | Conservative 4.5 / 2025.12 shared command set; requires vendor-build verification |
| 2025.12 | 2025.12.2 / .4 | Official 2025.12.4 CLI and modes |
| 2026.6 | 2026.6.0-alpha / 2026.6.2 | Official 2026.6.2 CLI and modes; alpha builds require verification |

Version labels match Betaflight's preset filters by firmware generation, rather than patch version. Source-level checks are not proof that every optional feature was compiled into every board. All presets are marked EXPERIMENTAL pending application and bench/flight checks. Custom/vendor-only settings such as the backup's `gps_set_home_point_once` are not transferred to official releases. PDOP is omitted in 4.4. No hardware has been connected or configured during repository creation.

## Maintain

Edit `catalog.json` for modes/OSD/rates, `tunes.json` for the recovered tune/filter values, or `scripts/build.py` for structure, then run:

```sh
npm run build
npm run check
git add .
git commit -m "Update personal presets"
git push
```

Node.js and Python 3 are required; no package installation is needed. Commit the regenerated `presets/`, `index.json`, and `index_hash.txt` together. The local launcher serves the current local files immediately; use `git pull` on another computer before launching there.

The upstream [Betaflight preset specification](https://github.com/betaflight/firmware-presets#preset-specifications) and indexer are used. Indexer and license copied from `betaflight/firmware-presets` commit `a6784247b98020f2b38061ac743b96f7da8d8d1b`. Loader behavior was checked against [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator) commit `5ac1dd37f0d256e494e41ad826dba75f90d30252`, including its actual option parser. Firmware command schemas come from [Betaflight](https://github.com/betaflight/betaflight) release tags listed above.
