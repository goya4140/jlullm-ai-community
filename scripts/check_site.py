#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check generated pages for broken local links, anchors, and draft-only content."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,unquote
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
BASE='/jlullm-ai-community/'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a:self.links.append(a[key])
def check():
    errors=[];pages={p.resolve():Page(p.read_text()) for p in OUT.rglob('*.html')};count=0
    for p,page in pages.items():
        for link in page.links:
            u=urlparse(link)
            if u.scheme or u.netloc:
                if u.scheme not in ('http','https','mailto'):errors.append(f'{p.name}: invalid scheme {link}')
                if u.hostname in ('localhost','127.0.0.1'):errors.append(f'{p.name}: local preview link')
                continue
            path=unquote(u.path)
            if path.startswith(BASE):target=OUT/path[len(BASE):]
            elif path.startswith('/'):errors.append(f'{p.name}: absolute path escapes project {link}');continue
            else:target=p.parent/path if path else p
            target=target.resolve()
            try:target.relative_to(OUT.resolve())
            except ValueError:errors.append(f'{p.name}: link escapes site {link}');continue
            if target.is_dir():target=target/'index.html'
            if not target.exists():errors.append(f'{p.relative_to(OUT)}: missing {link}');continue
            if u.fragment and target.suffix=='.html':
                parsed=pages.get(target) or Page(target.read_text())
                if unquote(u.fragment) not in parsed.ids:errors.append(f'{p.name}: missing anchor {link}')
            count+=1
    for p in (ROOT/'content/digests').glob('*.json'):
        d=json.loads(p.read_text())
        if d.get('status')=='draft' and (OUT/'daily'/d['id']).exists():errors.append(f'Draft leaked: {p.name}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'Checked {len(pages)} HTML pages and {count} local links/anchors; no broken targets or draft pages.')
if __name__=='__main__':check()
