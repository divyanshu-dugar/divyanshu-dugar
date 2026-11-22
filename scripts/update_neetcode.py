#!/usr/bin/env python3
"""Refresh the card from the same unauthenticated endpoint as the public profile.

No account token, cookies, or private data are used. If NeetCode changes its
undocumented endpoint, validation fails before replacing the last good card.
"""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import urllib.request
from build_assets import svg, rect, text, icon, line, BG, PANEL, BORDER, FG, MUTED, MONO

ROOT = Path(__file__).resolve().parents[1]
HANDLE = 'EternalGenin455'
ENDPOINT = 'https://neetcode.io/api/callableFunctionHttp'

def validate(data):
    if data.get('anonUsername', '').lower() != HANDLE.lower():
        raise ValueError('NeetCode returned a different or missing profile')
    stats = data['ncAllDifficultyStats']
    for level in ('easy', 'medium', 'hard'):
        for key in ('completed', 'total'):
            value=stats[level][key]
            if type(value) is not int or value < 0:
                raise ValueError(f'Invalid {level}.{key}')
        if stats[level]['completed'] > stats[level]['total']:
            raise ValueError('Completed exceeds total')
    for key in ('currentStreak','maxStreak'):
        if type(data[key]) is not int or data[key] < 0:
            raise ValueError(f'Invalid {key}')
    if data['currentStreak'] > data['maxStreak']:
        raise ValueError('Current streak exceeds longest streak')
    return data

def render(data, date):
    stats=data['ncAllDifficultyStats']
    solved=sum(stats[k]['completed'] for k in stats)
    body=rect(.5,.5,1039,259,BG,14,BORDER)
    body+=icon('neetcode',26,25,35,'#6ee7b7')+text(76,42,'NeetCode',22,FG,font_weight='600')
    body+=text(76,65,HANDLE,13,MUTED,family=MONO)+text(1010,39,'Open profile',13,'#7ee787','end')
    body+=line(26,86,1014,86)
    for x,number,label,color in [(30,solved,'PROBLEMS SOLVED',FG),(285,data['currentStreak'],'CURRENT STREAK','#6ee7b7'),(550,data['maxStreak'],'LONGEST STREAK','#ffc76c')]:
        body+=text(x,142,str(number),38,color,font_weight='650')
        if label!='PROBLEMS SOLVED':body+=text(x+60,141,'days',14,MUTED)
        body+=text(x,167,label,11,MUTED,letter_spacing='1.2')
    for x in (250,515,780):body+=line(x,110,x,176)
    for i,(key,col) in enumerate([('easy','#6ee7b7'),('medium','#ffc76c'),('hard','#ff7b86')]):
        body+=text(811,119+i*25,key.title(),14,col)+text(1007,119+i*25,str(stats[key]['completed']),16,FG,'end',MONO)
    body+=line(26,197,1014,197)+text(27,233,'PUBLIC PROFILE',10,MUTED,family=MONO,letter_spacing='1')
    body+=text(1010,233,f'Updated {date} UTC',12,MUTED,'end')
    return svg(1040,260,body,f'NeetCode: {solved} problems solved; Easy {stats["easy"]["completed"]}, Medium {stats["medium"]["completed"]}, Hard {stats["hard"]["completed"]}; current streak {data["currentStreak"]} days; longest streak {data["maxStreak"]} days. Updated {date} UTC.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--from-json',type=Path,help='Render a previously fetched public response')
    args=parser.parse_args()
    if args.from_json:
        payload=json.loads(args.from_json.read_text())
    else:
        request=urllib.request.Request(ENDPOINT,data=json.dumps({'data':{'functionId':'getProfileByHandle','handle':HANDLE}}).encode(),headers={'Content-Type':'application/json','User-Agent':'divyanshu-dugar-profile/1.0'})
        with urllib.request.urlopen(request,timeout=30) as response:
            payload=json.load(response)
    data=validate(payload['data'])
    result=render(data,datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    output=ROOT/'assets/neetcode.svg'
    tmp=output.with_suffix('.tmp')
    tmp.write_text(result)
    tmp.replace(output)
    print(f'Updated NeetCode card for {HANDLE}')

if __name__=='__main__':
    main()
