#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a draft JSON file; never overwrite an existing issue."""
from pathlib import Path
from datetime import date
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='新建 JLULLM 日报草稿')
p.add_argument('--type',choices=['chat','recording'],required=True)
p.add_argument('--date',required=True,help='整理日期 YYYY-MM-DD')
p.add_argument('--slug',required=True,help='英文短标题，如 proactive-agent')
p.add_argument('--title',required=True)
a=p.parse_args()
date.fromisoformat(a.date)
if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',a.slug):p.error('--slug 仅支持小写英文、数字、连字符')
d=json.loads((ROOT/f'templates/{a.type}.json').read_text())
d.update(id=f'{a.date}-{a.slug}',title=a.title,date=a.date)
if a.type=='recording':d['duration']='';d['topics'][0]['time_range']=''
target=ROOT/'content/digests'/f'{d["id"]}.json'
with target.open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(f'Created draft: {target}')
