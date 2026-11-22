#!/usr/bin/env python3
"""Rebuild the self-contained SVG assets. Python 3, no dependencies.

The hero recreates the reference's #0d1117 canvas, contribution palette,
three-second rotating fade and 40ms column stagger using original geometry.
"""
from pathlib import Path
from html import escape
import json
import random
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, BORDER, FG, MUTED = '#0d1117', '#111820', '#26303b', '#e6edf3', '#8b949e'
GREEN = '#3fb950'
FONT = 'Segoe UI,Ubuntu,Helvetica Neue,Arial,sans-serif'
MONO = 'DejaVu Sans Mono,Consolas,monospace'

def text(x, y, value, size=16, color=FG, anchor='start', family=FONT, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="{family}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'

def svg(w, h, body, title, styles=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><style>{styles}</style>{body}</svg>\n'

def save(name, value):
    (ASSETS/name).write_text(value)

def rect(x,y,w,h,fill=PANEL,rx=10,stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'

def line(x,y,x2,y2,color=BORDER):
    return f'<path d="M{x} {y}H{x2}" stroke="{color}"/>' if y==y2 else f'<path d="M{x} {y}L{x2} {y2}" stroke="{color}"/>'

GENERIC = {
 'portfolio':'<rect x="2" y="3" width="20" height="18" rx="3"/><path d="m9 9-3 3 3 3m6-6 3 3-3 3M3 7h18"/>',
 'sql':'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
 'ec2':'<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M8 2v3m8-3v3M8 19v3m8-3v3M2 8h3m-3 8h3m14-8h3m-3 8h3"/>',
 's3':'<path d="M4 5h16l-2 15H6zM4 5c0-4 16-4 16 0M7 10h10M8 14h8"/>',
 'rag':'<path d="M3 3h11v15H3zM6 7h5M6 11h5M17 8h4v13H10v-3M16 15l2 2-2 2m2-2h-5"/>',
 'agents':'<rect x="4" y="7" width="16" height="13" rx="4"/><path d="M12 7V3m-4 9v2m8-2v2m-7 3h6M1 11v5m22-5v5"/><circle cx="12" cy="2" r="1"/>',
 'neetcode':'<path d="m7 4-5 8 5 8m10-16 5 8-5 8M9 17V7l6 10V7"/>'
}

def icon(name,x,y,size=32,color=FG,instance=''):
    if name in GENERIC:
        return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{GENERIC[name]}</g></svg>'
    source = ASSETS/'icons'/f'{name}.svg'
    root = ET.fromstring(source.read_text())
    for el in root.iter():
        el.tag = el.tag.split('}')[-1]
    for child in list(root):
        if child.tag in ('title','metadata'): root.remove(child)
    monochrome = name in {'openai','langchain','qdrant','leetcode','youtube','gmail','x','tableau','aws','vercel','pandas'}
    if monochrome:
        for el in root.iter():
            if el.tag not in ('svg','defs','clipPath'):
                if el.attrib.get('fill') != 'none': el.set('fill',color)
                if el.attrib.get('stroke') and el.attrib.get('stroke')!='none':el.set('stroke',color)
    root.set('x',str(x));root.set('y',str(y));root.set('width',str(size));root.set('height',str(size))
    root.set('fill', '#000000' if name == 'nextjs' else color)
    out=ET.tostring(root,encoding='unicode')
    ids=re.findall(r'\bid="([^"]+)"',out)
    for id_ in ids:
        new=f'{name}-{instance}-{id_}'
        out=out.replace(f'id="{id_}"',f'id="{new}"').replace(f'#{id_}',f'#{new}')
    return out

GLYPHS = {
 'D':['1110','1001','1001','1001','1110'],
 'I':['111','010','010','010','111'],
 'V':['10001','10001','01010','01010','00100'],
 'Y':['101','101','010','010','010'],
 'A':['0110','1001','1111','1001','1001'],
 'N':['1001','1101','1011','1001','1001'],
 'S':['0111','1000','0110','0001','1110'],
 'H':['1001','1001','1111','1001','1001'],
 'U':['1001','1001','1001','1001','0110'],
 'G':['0111','1000','1011','1001','0111'],
 'R':['1110','1001','1110','1010','1001'],
 ' ':['00']*5,
}

def hero():
    rows=['']*5
    for ch in 'DIVYANSHU DUGAR':
        for j in range(5):rows[j]+=GLYPHS[ch][j]+'0'
    rows=[r[:-1] for r in rows]
    cols=len(rows[0]);w=60+cols*16-4;h=190
    rng=random.Random(455)
    colors=['#216e39','#2ea043','#30a14e','#40c463','#9be9a8']
    body=rect(0,0,w,h,BG,8);styles='';cells=[]
    i=0
    for row in range(5):
        for col in range(cols):
            x,y=30+col*16,30+row*16
            if rows[row][col]=='1':
                c=rng.choice(colors);angle=rng.randint(-720,720);delay=col*.04
                styles+=f'@keyframes tile{i}{{0%{{transform:rotate({angle}deg);opacity:0}}50%{{transform:rotate(0deg);opacity:1}}100%{{fill:{c};transform:rotate(0deg);opacity:1}}}}'
                body+=f'<rect class="tile" x="{x}" y="{y}" width="12" height="12" rx="2" fill="{c}" style="animation:tile{i} 3s ease-in-out {delay:.2f}s infinite;transform-origin:{x+6}px {y+6}px"/>'
                cells.append(dict(x=x,y=y,color=c,angle=angle,delay=delay));i+=1
            else:body+=f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="#161b22" opacity=".4"/>'
    body+=text(w/2,149,'Full-Stack Developer  |  Educator  |  AI Builder  |  Lifelong Learner',16,MUTED,'middle',letter_spacing='1.2')
    styles+='@media(prefers-reduced-motion:reduce){.tile{animation:none!important;opacity:1!important;transform:none!important}}'
    save('hero.svg',svg(w,h,body,'Divyanshu Dugar | Full-Stack Developer | Educator | AI Builder | Lifelong Learner',styles))
    (ASSETS/'hero-geometry.json').write_text(json.dumps(dict(width=w,height=h,rows=rows,cells=cells)))

def social():
    links=[('portfolio','Portfolio','#a78bfa'),('linkedin','LinkedIn','#70b7ff'),('x','Twitter / X',FG),('leetcode','LeetCode','#ffa116'),('youtube','YouTube','#ff5964'),('gmail','Email','#f38b82'),('neetcode','NeetCode','#6ee7b7')]
    for name,label,col in links:
        body=rect(.5,.5,139,47,PANEL,11,BORDER)+icon(name,15,13,22,col)+text(47,29,label,14,FG,font_weight='600')
        save(f'contact-{name}.svg',svg(140,48,body,label))

def terminal():
    w,h=1040,405
    body=rect(.5,.5,w-1,h-1,BG,14,BORDER)+rect(1,1,w-2,43,PANEL,13)
    body+=rect(1,25,w-2,19,PANEL,0)+line(0,44,w,44)
    for x,c in [(23,'#ff5f57'),(43,'#febc2e'),(63,'#28c840')]:body+=f'<circle cx="{x}" cy="22" r="5" fill="{c}"/>'
    body+=text(w/2,27,'divyanshu@toronto  ~  zsh',13,MUTED,'middle',MONO)
    body+=text(30,83,'divyanshu@github',16,'#7ee787',family=MONO)+text(195,83,'~ % whoami',16,FG,family=MONO)
    body+=text(30,124,'Divyanshu Dugar',25,FG,font_weight='650')
    body+=text(30,151,'Full-Stack Developer · Educator · AI Builder · Lifelong Learner',16,MUTED)
    data=[('location','Toronto, Canada'),('education','Seneca Polytechnic · CPA graduate · High Honours'),('building','Finvest AI · Fincraft AI'),('focus','Full-stack apps · RAG pipelines · AI products'),('teaching','Code, problem solving, and the ideas behind them'),('open to','Full-time roles · Open source · Collaborations')]
    for i,(key,val) in enumerate(data):
        y=188+i*27;body+=text(30,y,key,15,'#79c0ff',family=MONO)+text(166,y,val,15,FG,family=MONO)
    body+=line(30,342,1010,342)
    body+=text(30,377,'~ %',16,'#7ee787',family=MONO)+text(76,377,'echo "1% better, every day."',16,FG,family=MONO)
    body+='<rect class="cursor" x="357" y="363" width="9" height="18" rx="1" fill="#7ee787"/>'
    styles='@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cursor{animation:blink 1.2s step-end infinite}@media(prefers-reduced-motion:reduce){.cursor{animation:none}}'
    save('whoami.svg',svg(w,h,body,'About Divyanshu: Toronto-based developer and educator; Seneca CPA graduate; building Finvest AI and Fincraft AI; open to full-time roles and collaboration.',styles))

GROUPS=[
 ('01','Full Stack','#61dafb',[('react','React'),('nextjs','Next.js'),('typescript','TypeScript'),('nodejs','Node.js'),('spring','Spring Boot'),('fastapi','FastAPI'),('react','React Native'),('tailwind','Tailwind')],['Web · Mobile · APIs']),
 ('02','Cloud & DevOps','#a78bfa',[('aws','AWS'),('azure','Azure'),('docker','Docker'),('githubactions','Actions'),('git','Git'),('vercel','Vercel'),('ec2','EC2'),('s3','S3')],['ECS · Cognito · CI/CD']),
 ('03','Data & Databases','#ffc76c',[('postgres','PostgreSQL'),('mongodb','MongoDB'),('dynamodb','DynamoDB'),('sql','SQL'),('python','Python'),('pandas','Pandas'),('matplotlib','Matplotlib'),('tableau','Tableau')],['Storage · Analysis · Insights']),
 ('04','AI & Vision','#73e2a7',[('openai','OpenAI'),('langchain','LangChain'),('qdrant','Qdrant'),('rag','RAG'),('agents','AI Agents'),('tensorflow','TensorFlow'),('keras','Keras'),('opencv','OpenCV')],['LLMs · Retrieval · Vision'])
]

def stack():
    w,h=1040,446
    body=rect(.5,.5,w-1,h-1,BG,14,BORDER)
    styles='@keyframes breathe{0%,100%{stroke-opacity:.18}50%{stroke-opacity:.7}}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}@keyframes spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.halo,.float,.react-spin{animation:none!important}}'
    colors={'aws':'#ff9900','vercel':FG,'nextjs':FG,'pandas':'#b4a6ff','tableau':'#79c0ff','openai':FG,'langchain':'#80d8bb','qdrant':'#f84c72','leetcode':'#ffa116'}
    for g,(num,title,c,items,notes) in enumerate(GROUPS):
        x=g*260
        if g:body+=line(x,26,x,374)
        body+=text(x+21,37,num,11,c,family=MONO,letter_spacing='1')
        body+=text(x+21,65,title,20,FG,font_weight='600')
        body+=line(x+21,81,x+239,81)
        for i,(name,label) in enumerate(items):
            cx=x+51+(i%3)*79;cy=119+(i//3)*83
            body+=f'<g class="float" style="animation:float {5+i*.25:.2f}s ease-in-out {-i*.65-g}s infinite">'
            body+=f'<rect class="halo" x="{cx-24}" y="{cy-24}" width="48" height="48" rx="13" fill="{PANEL}" stroke="{c}" style="animation:breathe 6s ease-in-out {-i*.7-g}s infinite"/>'
            if name=='react':body+=f'<g class="react-spin" style="transform-origin:{cx}px {cy}px;animation:spin 24s linear infinite">'
            body+=icon(name,cx-15,cy-15,30,colors.get(name,c),f'{g}-{i}')
            if name=='react':body+='</g>'
            body+='</g>'+text(cx,cy+43,label,12.5,FG,'middle')
        body+=text(x+130,365,notes[0],12,MUTED,'middle')
    body+=line(21,387,1019,387)+text(25,420,'QUALITY',11,'#7ee787',family=MONO,letter_spacing='1.5')
    body+=text(130,420,'JUnit  ·  PyTest  ·  Jest  ·  Playwright  ·  Postman  ·  SonarQube',15,FG)
    save('tech-stack.svg',svg(w,h,body,'Tech stack: Full Stack, Cloud and DevOps, Data and Databases, AI and Vision. Testing: JUnit, PyTest, Jest, Playwright, Postman, SonarQube.',styles))

def neetcode():
    body=rect(.5,.5,1039,159,BG,14,BORDER)+icon('neetcode',28,35,43,'#6ee7b7')
    body+=text(91,55,'NeetCode',23,FG,font_weight='600')+text(91,83,'EternalGenin455',16,MUTED,family=MONO)
    body+=text(28,132,'Data structures · Algorithms · Consistent practice',16,MUTED)
    body+=rect(782,54,227,47,PANEL,10,BORDER)+text(895,84,'View my progress  ↗',16,'#7ee787','middle')
    save('neetcode.svg',svg(1040,160,body,'NeetCode: EternalGenin455. Open the public profile to view current progress.'))

if __name__=='__main__':
    hero();social();terminal();stack()
    if not (ASSETS/'neetcode.svg').exists(): neetcode()
    print('Built hero, terminal, stack, seven contact icons and NeetCode card.')
