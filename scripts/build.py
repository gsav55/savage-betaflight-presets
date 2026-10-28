#!/usr/bin/env python3
"""Rebuild personal presets from the reviewed, portable catalog (no backups needed)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / 'catalog.json').read_text())
VERSIONS = ['4.4', '4.5', '4.6', '2025.12', '2026.6']

def emit(path, title, versions, category, description, body, warning=None):
    p = ROOT / 'presets' / path
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'#$ TITLE: Savage - {title}']
    lines += [f'#$ FIRMWARE_VERSION: {v}' for v in versions]
    lines += [f'#$ CATEGORY: {category}', '#$ STATUS: EXPERIMENTAL', '#$ AUTHOR: gsav55',
              '#$ KEYWORDS: Savage, personal, setup', '#$ FORCE_OPTIONS_REVIEW: true']
    lines += [f'#$ DESCRIPTION: {d}' for d in description]
    if warning:
        lines += [f'#$ WARNING: {warning}']
    p.write_text('\n'.join(lines + [''] + body) + '\n')

def option(label, commands, checked=False):
    return [f'#$ OPTION BEGIN ({"CHECKED" if checked else "UNCHECKED"}): {label}'] + [f'    {c}' for c in commands] + ['#$ OPTION END']

def group(label, options):
    return [f'#$ OPTION_GROUP BEGIN: (EXCLUSIVE) {label}'] + ['    '+l for opt in options for l in opt] + ['#$ OPTION_GROUP END']

def setlines(settings):
    return [f'set {k} = {v}' for k, v in settings.items()]

def aux(rows):
    return ['aux '+str(i)+' '+' '.join(map(str,row)) for i,row in enumerate(rows)]

def pos(x,y):
    return (x & 31) | ((x & 32) << 5) | (y << 5) | 14336

for version in VERSIONS:
    modern = version in ['2025.12','2026.6']
    for gps in [False,True]:
        rows = CAT['modes']['latest']
        # IDs 3 and 11 were unavailable before the calendar-version releases.
        rows = [r for r in rows if (gps and modern) or r[0] not in [3,11]]
        if not gps:
            rows = [r for r in rows if r[0] != 46]
        body = ['# Replace all mode slots and clear old in-flight adjustments.']
        body += [f'aux {i} 0 0 900 900 0 0' for i in range(20)]
        body += [f'adjrange {i} 0 0 900 900 0 0 0 0' for i in range(30)]
        alternatives = [option('Newest six-position selector layout', aux(rows), True)]
        for key,label in [('analog','Legacy analog whoop layout'),('hdzero','Legacy HDZero whoop layout'),('twiggy','Legacy Twiggy layout')]:
            alternative = CAT['modes'][key]
            if gps:
                alternative = alternative + [[46,1,1950,2100,0,0]]
                # Existing legacy HORIZON ranges end at 2100: rescue gets AUX7 instead.
                alternative[-1] = [46,6,1700,2100,0,0]
            alternatives.append(option(label + (' (rescue on AUX7)' if gps else ''),aux(alternative)))
        body += group('Switch layout - choose exactly one',alternatives)
        body += ['feature GPS' if gps else 'feature -GPS',
                 f'set failsafe_procedure = {"GPS-RESCUE" if gps else "DROP"}',
                 'set failsafe_delay = 15']
        if gps:
            body += ['set gps_rescue_allow_arming_without_fix = OFF', 'set gps_rescue_sanity_checks = RESCUE_SANITY_ON']
            body += option('Allow arming without GPS fix (as in backups; rescue unavailable until fix and home acquired)',
                           ['set gps_rescue_allow_arming_without_fix = ON'])
            body += option('UBLOX receiver: WAAS and Galileo', ['set gps_sbas_mode = WAAS','set gps_ublox_use_galileo = ON'])
        body += option('Rate-profile selection on AUX4 (newest layout only)', ['adjrange 0 0 3 900 2100 29 3 0 0'])
        emit(f'{version}/modes_{"gps" if gps else "no_gps"}.txt',
             f'{"GPS rescue" if gps else "Non-GPS drop failsafe"} and modes ({version})', [version], 'OTHER',
             ['Replaces all 20 mode slots and clears all 30 adjustment ranges. AUX channel numbers in the description are one-based.',
              'Newest layout: AUX1 ARM 1500-2100; AUX2 HORIZON 1125-1275, ANGLE 1325-1450, PREARM 1300-1625.' +
              (' AUX2 ALT HOLD 1550-1675, POS HOLD 1750-1875, RESCUE 1950-2100.' if gps and modern else (' AUX2 RESCUE 1950-2100.' if gps else '')),
              'AUX3 BEEPER 1900-2100 and TURTLE 1400-1600. Review the alternatives against your transmitter.',
              'GPS preset requires GPS and GPS rescue support; altitude/position hold additionally require the corresponding firmware features and sensors.' if gps else 'Sets DROP failsafe and disables GPS. Stage 1 delay is explicitly 1.5 seconds.',
              'GPS rescue trajectory, throttle and receiver Stage 1 channel behavior need airframe-specific setup; those values are preserved.' if gps else 'Receiver channel mapping, UARTs, PID settings and filters are preserved.',
              '4.6 is the vendor development firmware from your backups; verify on that exact build.' if version=='4.6' else 'Select only the preset matching your firmware generation.'], body,
             'Remove props and verify every mode and failsafe on the bench before flight. GPS rescue requires a valid home fix and airframe-specific rescue setup.' if gps else 'Remove props and verify arming, prearm, turtle and receiver-loss behavior after replacing the mode table.')

    for system in ['analog','hdzero','dji_o4']:
        settings = CAT['osd'][system]['settings']
        allowed = set(CAT['schemas'][version]['settings'])
        body = ['feature OSD', 'set osd_profile = 1', 'set report_cell_voltage = OFF']
        # Clear portable layout fields before applying the selected layout.
        keys = sorted(k for k in CAT['position_fields'] if k in allowed)
        body += [f'set {k} = 0' for k in keys]
        for k,val in settings.items():
            if k not in allowed or not k.endswith('_pos') or k not in keys: continue
            n=int(val)
            if n & 14336:
                # Use the same visible layout in all three OSD profiles.
                n=(n & ~14336) | 14336
                # Element-type bits are not portable to older OSD formats.
                if version in ['4.4','4.5','4.6']: n &= 16383
                body += [f'set {k} = {n}']
        body += ['set osd_displayport_device = '+('MAX7456' if system=='analog' else 'MSP'),
                 'set vcd_video_system = '+('NTSC' if system=='analog' else 'HD'),
                 'set osd_canvas_width = '+('30' if system=='analog' else '53'),
                 'set osd_canvas_height = '+('13' if system=='analog' else '20')]
        # Always restore visible warning text, including backups that omitted the default field.
        body += [f'set osd_warnings_pos = {pos(9,7) if system=="analog" else pos(21,10)}']
        body += option('Single-cell battery reporting', ['set report_cell_voltage = ON'], True)
        gpsfields=['osd_gps_sats_pos','osd_gps_speed_pos','osd_home_dir_pos','osd_home_dist_pos','osd_gps_lat_pos','osd_gps_lon_pos','osd_compass_bar_pos','osd_altitude_pos','osd_flight_dist_pos']
        # GPS selection controls display only, never enables a flight feature or changes failsafe.
        body += [f'set {k} = 0' for k in gpsfields if k in allowed]
        if 'osd_gps_sats_show_pdop' in allowed: body += ['set osd_gps_sats_show_pdop = OFF']
        sat = pos(12,1) if system=='analog' else (int(settings.get('osd_gps_sats_pos',pos(0,4))) & ~14336) | 14336
        if system=='analog':
            details={'osd_home_dir_pos':pos(13,0),'osd_home_dist_pos':pos(18,0),'osd_gps_speed_pos':pos(0,4),'osd_altitude_pos':pos(21,4),'osd_gps_lat_pos':pos(0,5),'osd_gps_lon_pos':pos(0,6)}
        else:
            details={k:v for k,v in CAT['osd'][system]['settings'].items() if k in gpsfields and k!='osd_gps_sats_pos' and int(v)&14336}
            details={k:(int(v)&~14336)|14336 for k,v in details.items()}
            if not modern:details={k:v&16383 for k,v in details.items()}
        if 'osd_gps_sats_show_pdop' in allowed:details['osd_gps_sats_show_pdop']='ON'
        detailcommands=setlines(details)
        body += option('More GPS details', detailcommands, True)
        # Last-write-wins: the default non-GPS choice clears every GPS field AFTER details.
        # Selecting GPS keeps checked details, or sats only when details is unchecked.
        clear_gps = [f'set {k} = 0' for k in gpsfields if k in allowed]
        if 'osd_gps_sats_show_pdop' in allowed: clear_gps += ['set osd_gps_sats_show_pdop = OFF']
        body += group('GPS display - choose exactly one', [option('Non-GPS drone', clear_gps,True),option('GPS-equipped drone', [f'set osd_gps_sats_pos = {sat}'])])
        body += option('Imperial units (feet and mph)', ['set osd_units = IMPERIAL'])
        body += ['set osd_current_pos = 0', 'set osd_mah_drawn_pos = 0']
        body += option('Current and mAh reporting (requires calibrated current sensor)',
                       [f'set osd_current_pos = {pos(0,11) if system=="analog" else pos(0,18)}', f'set osd_mah_drawn_pos = {pos(0,12) if system=="analog" else pos(0,19)}'])
        emit(f'{version}/osd_{system}.txt',f'{system.replace("_"," ").upper()} OSD ({version})',[version],'OSD',
             [f'Layout based on {CAT["osd"][system]["source"]}. Layout visibility is normalized across all OSD profiles; active profile is 1.',
              'Single-cell battery reporting and more GPS details are checked by default. GPS display is off by default; select GPS-equipped drone to enable GPS overlays.',
              'OSD selection does not set flight GPS or failsafe; apply the matching modes preset separately.',
              'Analog uses NTSC 30x13. HD uses 53x20; configure the VTX UART for MSP DisplayPort separately and check the negotiated goggles canvas.',
              'More details includes home direction/distance, speed, altitude and coordinates; PDOP is unavailable in 4.4.',
              'No signal-strength alarm threshold is copied because it depends on the receiver packet rate.'],body)

# This directory is generated: retire the former individual rate presets.
for old in (ROOT/'presets'/'rates').glob('*.txt'):
    old.unlink()
body = ['# Install profiles 1-3 (zero-based CLI indices 0-2).']
for slot,item in enumerate(CAT['rates']):
    body += [f'rateprofile {slot}', 'set rates_type = ACTUAL',
             'set rateprofile_name = '+item['name']] + setlines(item['settings'])
body += ['# Safe fallback if all final-profile checkboxes are cleared.', 'rateprofile 0']
body += group('Active rate profile after applying - choose one',
              [option(f'Finish on profile {i+1}: {item["name"]}', [f'rateprofile {i}'], i==0)
               for i,item in enumerate(CAT['rates'])])
emit('rates/three_profiles.txt','Three rate profiles - Standard, Race, Tuning',VERSIONS,'RATES',
     ['Writes rate profiles 1, 2 and 3 in this order: Standard, Race, Tuning. Profile 4 is preserved.',
      'Standard: Actual 60 center, 540 maximum, 0.20 expo on all axes.',
      'Race: roll/pitch 60 center, 540 maximum, 0.20 expo; yaw 120 center, 730 maximum, 0.20 expo.',
      'Tuning: Actual 150 center, 150 maximum, zero expo on all axes, recovered from SB405-AIO/tuning/SAVAGE_TUNE.txt.',
      'Choose the active profile in the exclusive checkbox group. Standard is selected by default and is also the fallback if none is checked.',
      'Throttle curves, rate limits, PID profiles and filters are preserved.'],body)

print('Generated',len(list((ROOT/'presets').rglob('*.txt'))),'presets')
