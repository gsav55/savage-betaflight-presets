# Backup review

Reviewed 93 CLI dumps/diffs across 19 folders containing CLI backups. The inventory records the exact header, content SHA-256, and filename date for every examined backup. File modification timestamps were reviewed locally and omitted from the public inventory. Stock files were retained as evidence of firmware/build history, not used as the personal layout authority.

## Selection method

Within each folder, prefer the newest explicit backup timestamp in the filename; use file modification time for undated working/tuning files. Compare related initial, tuning and backup folders before extracting a setting. A newer file that contains no personal modes or rates is not evidence that an older layout is still current. The chosen default layout comes from the newest Halo working configuration, as confirmed by the owner; older families remain available as alternatives.

| Folder | Preferred personal backup | Firmware |
| --- | --- | --- |
| A65 | `SavageTune.txt` | 4.5.0 |
| A65/Betaflight | `BTFL_cli_backup_AIR65_FS_20260608_104201_BETAFPVG473.txt` | 4.5.0 |
| A65/tuning | `MasterTesting.txt` | 4.5.0 |
| A652C | `SAVAGE_BTFL_cli_backup_AIR65_C_20260928_202051_BETAFPVG473_V2.txt` | 2026.6.0 |
| A65Race2 | `Setup.txt` | 2026.6.0 |
| AIO5 | Stock evidence only; no personal preset extracted | 4.5.1 |
| AOS 5/Backups | `BTFL_cli_backup_AOS_5_20260623_234912_SPEEDYBEEF405V5.txt` | 2025.12.4 |
| AOS4/BetaFlight | `BTFL_cli_backup_AOS_4_20260608_234018_SPEEDYBEEF405MINI.txt` | 2025.12.4 |
| Air65 | `BTFL_cli_backup_AIR65_FS_20260728_224917_BETAFPVG473.txt` | 4.5.0 |
| C35 | `BTFL_cli_backup_20260628_125648_BETAFLIGHTF4.txt` | 4.4.3 |
| HD0Halo | `AOS7_SAVAGE.txt` | 2026.6.2 |
| HD0Halo/Logs | `AOS7_SAVAGE.txt` | 2026.6.2 |
| Lazarus | `BTFL_cli_backup_TORDLE_20260730_210750_HDZERO_AIO15.txt` | 4.6.0 |
| Lazarus/tuning | `SAVAGE TUNE.txt` | 4.6.0 |
| Lion4 | `BTFL_cli_backup_M8_FS_20260613_235545_HDZERO_AIO15.txt` | 4.6.0 |
| M8 | `BTFL_cli_backup_M8_FS_20260614_194226_HDZERO_AIO15.txt` | 4.6.0 |
| SB405-AIO/initial | `BTFL_cli_backup_TWIGGY_20260730_231307_SPEEDYBEEF405AIO.txt` | 4.5.1 |
| SB405-AIO/tuning | `SAVAGE_TUNE.txt` | 4.5.5 |
| crazy-f405 | `SavageTune.txt` | 4.5.0 |

## Decisions and differences

- Newest common modes: `HD0Halo/AOS7_SAVAGE.txt`. The same six-position layout occurs in AOS4 and AOS 5. Halo uses AUX1 1500–2100 for ARM; AOS 5 used 1600–2100. The common preset uses the newer Halo range.
- `HD0Halo/Logs/AOS7_SAVAGE.txt` additionally contains an always-enabled USER1 mode. It is omitted because USER1 depends on board-specific PINIO wiring. The root working file was used for common modes. Both versions show the same 60 / 550 / 20 rates. The Logs copy also explicitly enables cell reporting and PDOP; both are offered as checked OSD options.
- Newest legacy analog switch layout: `A65Race2/Setup.txt`. AIR65 C uses a different Angle/Horizon ordering and lacks the AIR MODE switch. The default is the newer shared layout, with the A65Race2 family exposed as the analog alternative; this is not a byte-for-byte restore of every drone.
- Legacy HDZero whoop layout: `Lazarus/tuning/SAVAGE TUNE.txt`, newer tuning working file than the July Lazarus CLI backups. It uses AUX1 ARM 1775–2100 and AUX8 PREARM 1700–2100.
- Legacy Twiggy: `SB405-AIO/tuning/SAVAGE_TUNE.txt` supersedes initial July backups. It changes Angle/Horizon order, adds BLACKBOX on AUX3, and keeps PREARM on AUX8. No tuning values are transferred.
- Analog OSD: `A65Race2/Setup.txt` rather than older Air65 snapshots. Its mixed per-profile visibility is normalized for reuse. GPS details are adapted onto unused rows of the 30×13 layout.
- HDZero OSD: newest Halo working file. Its 53×20 coordinates differ from the older 50×18 whoop layout; the preset deliberately follows the latest requested default.
- DJI O4 OSD: latest AOS 5 backup `20260623_234912`, explicitly selected by the owner. Video brand cannot be established from CLI DisplayPort commands alone.
- OSD warnings are explicitly visible even when a diff omitted their default position. Current/mAh display is optional and starts off. Alarm thresholds, RSSI packet-rate assumptions and battery sensor calibration are not copied.
- Full old OSD masks are not copied: warning/statistic bit meanings and optional features change. Non-GPS clears all GPS fields after the default checked details option, using the actual upstream parser’s ordered CLI behavior.
- The latest C35 backup is a 45-line near-default diff with no personal mode or rate payload. It contributes 4.4.3 compatibility evidence; no older C35 mode map is silently promoted as current.
- AIO5 has only a stock backup, so it contributes firmware evidence only. Apex3 contains no detected Betaflight CLI dump/diff matching the scanned text formats. Radio backups, flight logs and VTX table files are not personal preset authorities.
- Missing axis values in a diff mean the reset/default values, not the values in an earlier profile. Actual rates defaults in the checked firmware sources are center 70, maximum 670, expo 0. All exported rate presets explicitly write nine values. Unchanged expo in the Tuning profile is filled as zero. Throttle expo is intentionally excluded from rates presets.
- Backups identify the vendor 4.6 build as `norevision`, May 12 2025, MSP 1.47. No exact source commit can be recovered; compatibility is conservative and remains unverified on hardware. Calendar-version alpha builds are also explicitly experimental.
- `gps_set_home_point_once` appears in Halo backups but is absent from the official 2026.6.2 CLI schema. It is not copied. ALT HOLD and POS HOLD are only generated for confirmed calendar-version mode tables. PDOP is not generated for 4.4.
- GPS backups allow arming without a fix. The reusable GPS preset defaults to requiring a fix, with an unchecked option to restore the backup behavior. Rescue sanity checks are enabled. Rescue flight tuning, receiver Stage 1 values, UARTs and physical board settings remain airframe-specific.

## Verification scope

The official preset indexer/checker validates metadata and index structure. The local regression checks validate command names against release-source snapshots, all nine rate values, full mode-table replacement, no unsupported old hold-mode IDs, 524 option combinations, GPS overlay isolation, OSD start-coordinate bounds, and exclusion of PID/filter/motor settings. OSD checks verify element start coordinates, not font widths or actual goggles rendering. The real upstream TypeScript option parser is additionally exercised against generated options. No FC was connected, so firmware acceptance, compiled-feature availability, radio behavior, rescue behavior and actual display appearance remain bench/flight checks.

The public repository can be added directly as a GitHub preset source using branch `main`. The local source remains available for offline use and unpushed edits. Browser local-network permission or an older desktop Configurator may be needed. The launcher is tested to serve preset files with CORS and deny catalog, documentation and Git metadata access.

## Owner refinement: three rate profiles

The original individual rates presets were replaced by one preset installing Standard (60/540/0.20), Race (same roll/pitch, yaw 120/730/0.20), and the recovered Tuning (150/150/0) into slots 1–3. These owner-specified values supersede the broader historical rate selection above. The exclusive final-profile checkboxes select the active slot, defaulting to Standard; profile 4 and throttle/rate-limit values are preserved. Regression checks simulate each final choice and the no-checkbox fallback.
