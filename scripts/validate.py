#!/usr/bin/env python3
"""Compatibility, option-interaction and scope regression checks."""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'catalog.json').read_text())
GPS=['gps_sats','gps_speed','home_dir','home_dist','gps_lat','gps_lon','compass_bar','altitude','flight_dist']

def options(text):
    return [(m[2],m[1]=='CHECKED') for m in re.finditer(r'^\s*#\$ OPTION BEGIN \((CHECKED|UNCHECKED)\): (.+)$',text,re.M)]

def payload(text,checked):
    """Match the upstream parser's single-level option exclusion semantics."""
    out=[];skip=False
    for line in text.splitlines():
        s=line.strip()
        if s.startswith('#$'):
            m=re.match(r'#\$ OPTION BEGIN \((?:CHECKED|UNCHECKED)\): (.+)',s)
            if m:skip=m[1] not in checked
            elif s=='#$ OPTION END':skip=False
        elif not skip and s and not s.startswith('#'):out.append(s)
    return out

def state(lines):
    return dict(re.findall(r'^set (\w+) = (.+)$','\n'.join(lines),re.M))

count=0
for p in sorted((ROOT/'presets').rglob('*.txt')):
    text=p.read_text();versions=re.findall(r'^#\$ FIRMWARE_VERSION: (.+)$',text,re.M)
    names=[x[0] for x in options(text)]
    assert len(set(names))==len(names),p
    assert 'defaults nosave' not in text and not re.search(r'^\s*(save|profile)\b',text,re.M),p
    if p.parent.name!='rates':assert not re.search(r'^\s*rateprofile\b',text,re.M),p
    for version in versions:
        allowed=set(CAT['schemas'][version]['settings'])
        for key,value in re.findall(r'^\s*set (\w+) = (.+)$',text,re.M):
            assert key in allowed,(p,version,'unknown setting',key)
            assert not re.match(r'(?:p_|i_|d_|f_|gyro_|dterm_|dyn_notch_|rpm_filter|simplified_|feedforward|tpa_|motor_)',key),(p,key)
    if '/osd_' in str(p):
        gpslabel='GPS-equipped drone';nongps='Non-GPS drone'
        optional=[name for name,default in options(text) if name not in [gpslabel,nongps]]
        for gps in [False,True]:
            for mask in itertools.product([False,True],repeat=len(optional)):
                checked={name for name,selected in zip(optional,mask) if selected}|{gpslabel if gps else nongps}
                s=state(payload(text,checked));count+=1
                assert s['report_cell_voltage']==('ON' if 'Single-cell battery reporting' in checked else 'OFF'),p
                for field in GPS:
                    value=int(s.get('osd_'+field+'_pos',0))
                    if not gps:assert value==0,(p,field,'non-GPS leak')
                    elif field=='gps_sats':assert value&14336,(p,'missing satellites')
                    elif 'More GPS details' not in checked:assert value==0,(p,field,'details off leak')
                if gps and 'More GPS details' in checked:
                    for f in ['home_dir','home_dist','gps_speed','gps_lat','gps_lon','altitude']:
                        assert int(s['osd_'+f+'_pos'])&14336,(p,f,'details missing')
                if 'osd_gps_sats_show_pdop' in s:
                    assert s['osd_gps_sats_show_pdop']==('ON' if gps and 'More GPS details' in checked else 'OFF'),p
                width,height=(30,13) if p.stem=='osd_analog' else (53,20)
                for k,v in s.items():
                    if k.endswith('_pos') and int(v)&14336:
                        n=int(v);x=(n&31)|((n&1024)>>5);y=(n>>5)&31
                        assert 0<=x<width and 0<=y<height,(p,k,x,y)
    elif '/modes_' in str(p):
        default={n for n,c in options(text) if c}
        layouts=[n for n in names if n.startswith(('Newest ', 'Legacy '))]
        for layout in layouts:
            checked=default-set(layouts)|{layout}
            lines=payload(text,checked);s=state(lines);count+=1
            slots={}
            for l in lines:
                if l.startswith('aux '):
                    a=list(map(int,l.split()[1:]));slots[a[0]]=a[1:]
            assert len(slots)==20,p
            active=[v for v in slots.values() if v[2]<v[3]]
            assert sum(v[0]==0 for v in active)==1,(p,layout,'arm count')
            assert any(v[0]==36 for v in active),(p,layout,'no prearm')
            gps=p.stem=='modes_gps'
            assert s['failsafe_procedure']==('GPS-RESCUE' if gps else 'DROP'),p
            assert any(v[0]==46 for v in active)==gps,p
            if versions[0] in ['4.4','4.5','4.6']:
                assert not any(v[0] in [3,11] for v in active),p
    else:
        assert p.name=='three_profiles.txt' and len(CAT['rates'])==3,p
        assert len(names)==3 and [n for n,c in options(text) if c]==[names[0]],p
        # Independently specify the requested values; simulate CLI profile switching.
        expected=[[(6,54,20)]*3,[(6,54,20),(6,54,20),(12,73,20)],[(15,15,0)]*3]
        for selected in [None,0,1,2]:
            profiles=[{'thr_expo':'37','roll_rate_limit':'1900'} for i in range(4)]
            profiles[3]['sentinel']='unchanged';active=3;written=[set() for i in range(4)]
            checked=set() if selected is None else {names[selected]}
            for line in payload(text,checked):
                m=re.fullmatch(r'rateprofile (\d+)',line)
                if m:
                    active=int(m[1]);assert active in [0,1,2],p
                else:
                    m=re.fullmatch(r'set (\w+) = (.+)',line);assert m,(p,line)
                    profiles[active][m[1]]=m[2];written[active].add(m[1])
            count+=1
            assert active==(0 if selected is None else selected),(p,'final active profile')
            assert profiles[3]=={'thr_expo':'37','roll_rate_limit':'1900','sentinel':'unchanged'},p
            for i,axes in enumerate(expected):
                s=profiles[i];assert s['rates_type']=='ACTUAL',p
                assert s['rateprofile_name']==['60|54|20','Race','Tuning'][i],p
                assert len(written[i])==11,(p,'must write type, name and all 9 axis values')
                assert s['thr_expo']=='37' and s['roll_rate_limit']=='1900',p
                for axis,values in zip(['roll','pitch','yaw'],axes):
                    for key,value in zip(['rc_rate','srate','expo'],values):
                        assert int(s[axis+'_'+key])==value,(p,i,axis,key)

index=(ROOT/'index.json').read_bytes()
assert hashlib.sha256(index).hexdigest()==(ROOT/'index_hash.txt').read_text().strip(),'Index hash stale'
print(f'PASS: {len(list((ROOT/"presets").rglob("*.txt")))} presets; {count} option combinations; version schemas, GPS isolation, OSD bounds, mode replacement and PID/filter exclusions.')
