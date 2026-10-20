#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the JLULLM public site using Python's standard library only."""
from pathlib import Path
from datetime import date
from html import escape as e
from urllib.parse import urlparse
import json, shutil, re, sys, hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

def valid_url(url):
    return isinstance(url,str) and urlparse(url).scheme in ('http','https') and bool(urlparse(url).netloc)

def validate(d):
    for key in ('id','title','date','source_type','status','topics'):
        if not d.get(key): raise ValueError(f'Missing {key}')
    if not SLUG.fullmatch(d['id']): raise ValueError('id must be a lowercase URL slug')
    date.fromisoformat(d['date'])
    if d.get('event_date'): date.fromisoformat(d['event_date'])
    if d['source_type'] not in ('chat','recording'): raise ValueError('Unknown source_type')
    if d['status'] not in ('draft','published'): raise ValueError('Unknown status')
    if d['status']=='published' and not d.get('reviewed_by','').strip(): raise ValueError('Published digest needs reviewed_by')
    for key in ('subtitle','summary','source_note','duration','reviewed_by'):
        if key in d and not isinstance(d[key],str): raise ValueError(f'{key} must be text')
    if not isinstance(d.get('tags',[]),list) or any(not isinstance(t,str) for t in d.get('tags',[])): raise ValueError('tags must be text list')
    if not isinstance(d.get('sources',[]),list): raise ValueError('sources must be a list')
    if not isinstance(d.get('followups',[]),list): raise ValueError('followups must be a list')
    for action in d.get('followups',[]):
        if not isinstance(action,dict) or not isinstance(action.get('kind'),str) or not isinstance(action.get('text'),str): raise ValueError('Followup needs kind and text')
    if not isinstance(d['topics'],list): raise ValueError('topics must be a list')
    ids=set()
    for t in d['topics']:
        if not SLUG.fullmatch(t.get('id','')) or t['id'] in ids: raise ValueError('Topic IDs must be unique slugs')
        ids.add(t['id'])
        for key in ('time_range','editor_note'):
            if key in t and not isinstance(t[key],str): raise ValueError(f'{key} must be text')
        for key in ('quotes','links'):
            if not isinstance(t.get(key,[]),list): raise ValueError(f'{key} must be a list')
        if not t.get('title') or not t.get('category'): raise ValueError('Topic needs title and category')
        if not isinstance(t.get('paragraphs'),list) or not all(isinstance(x,str) and x.strip() for x in t['paragraphs']) or not t['paragraphs']: raise ValueError('Topic needs nonempty paragraphs')
        for link in t.get('links',[]):
            if not valid_url(link.get('url')) or not link.get('title'): raise ValueError('Links need a title and http(s) URL')
        for q in t.get('quotes',[]):
            if not q.get('text') or not q.get('speaker'): raise ValueError('Quote needs text and speaker')
    for link in d.get('sources',[]):
        if not valid_url(link.get('url')) or not link.get('title'): raise ValueError('Sources need a title and http(s) URL')
    return d

def badge(d): return '录音整理' if d['source_type']=='recording' else '群聊精选'

def digest_card(d, prefix='', featured=False):
    tags=''.join(f'<span class="tag">{e(t)}</span>' for t in d.get('tags',[])[:3])
    return f'''<a class="digest-card {'featured' if featured else ''}" href="{prefix}daily/{e(d['id'])}/"><div class="card-top"><span class="pill">{badge(d)}</span><time>{e(d['date'])}</time></div><h3>{e(d['title'])}</h3><p>{e(d.get('subtitle',''))}</p><div class="tags">{tags}</div><div class="card-bottom"><span>{len(d['topics'])} 个话题 · {'录音 '+e(d.get('duration','')) if d['source_type']=='recording' else '社区讨论'}</span><span class="arrow">↗</span></div></a>'''

def layout(title, content, page='home', prefix='', scripts='', description=None):
    site=json.loads((ROOT/'content/site.json').read_text())
    asset_version=hashlib.sha256((ROOT/'web/assets/style.css').read_bytes()).hexdigest()[:10]
    nav=[('home','首页','Home',''),('daily','社区日报','Journal','daily/'),('about','关于社区','About','about/')]
    links=''.join('<a href="'+prefix+(path or './')+'"'+(' aria-current="page"' if page==key else '')+'><span>'+zh+'</span><small>'+en+'</small></a>' for key,zh,en,path in nav)
    links+='<a href="'+site['repository']+'" target="_blank" rel="noopener"><span>GitHub ↗</span><small>Open Source</small></a>'
    brand=f'<img src="{prefix}assets/jlullm-mark.svg" alt="" width="44" height="44"><span class="brand-name">JLULLM</span><span class="brand-tagline">AI 交流与实践社区</span>'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(description or site['description'],quote=True)}"><meta name="theme-color" content="#ffffff"><title>{e(title)} · JLULLM AI 社区</title><link rel="icon" href="{prefix}assets/favicon.svg?v={asset_version}" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css?v={asset_version}"></head><body class="page-{page}"><a class="skip" href="#main">跳到正文</a><header class="site-header"><a class="brand" href="{prefix or './'}" aria-label="JLULLM 首页">{brand}</a><button class="menu-toggle" id="menu-toggle" aria-label="打开导航" aria-controls="site-navigation" aria-expanded="false"><span></span><span></span></button><nav class="site-nav" id="site-navigation" aria-label="主导航">{links}</nav></header><main id="main">{content}</main><footer class="site-footer"><div class="footer-main"><a class="brand footer-brand" href="{prefix or './'}" aria-label="JLULLM 首页">{brand}</a><p>让交流成为积累，让想法走向实践。</p></div><nav class="footer-nav" aria-label="页脚导航"><a href="{prefix}daily/">Journal</a><a href="{prefix}about/">About</a><a href="{site['repository']}" target="_blank" rel="noopener">GitHub ↗</a></nav><p class="copyright">© 2026 JLULLM AI 社区</p></footer><script src="{prefix}assets/site.js?v={asset_version}" defer></script>{scripts}</body></html>'''

def home(ds):
    latest=ds[0] if ds else None
    latest_link=(f'<a class="latest-note" href="daily/{e(latest["id"])}/"><span>LATEST JOURNAL / {e(latest["date"])}</span><strong>{e(latest["title"])}</strong><i>↗</i></a>' if latest else '')
    return layout('首页',f'''<section class="home-hero" aria-labelledby="home-title"><div class="hero-copy"><p class="eyebrow">JLULLM · AI COMMUNITY</p><h1 id="home-title">探索 AI，<br>与同行一起向前</h1><p class="hero-lede">和对 AI 充满好奇的伙伴，<br>一起交流研究，把想法做成实践。</p><div class="hero-actions"><a class="button dark" href="daily/">阅读社区日报 <span>→</span></a><a class="text-link" href="about/">认识社区 <span>→</span></a></div></div><div class="hero-visual"><img src="assets/research-table.png" alt="研究桌上的论文、网络结构图、实验草稿与笔记" width="1536" height="1024" fetchpriority="high"></div></section><section class="latest-strip" aria-label="最新一期日报">{latest_link}<a class="latest-all" href="daily/">全部社区日报 <span>→</span></a></section>''')

def archive(ds):
    cards=''.join(digest_card(d,'../') for d in ds)
    data=[{'id':d['id'],'title':d['title'],'subtitle':d.get('subtitle',''),'summary':d.get('summary',''),'tags':d.get('tags',[]),'type':d['source_type'],'date':d['date'],'topic_text':' '.join(t['title']+' '+' '.join(t['paragraphs']) for t in d['topics'])} for d in ds]
    return layout('社区日报',f'''<section class="wrap page-intro"><div class="eyebrow">COMMUNITY JOURNAL</div><h1>让每次交流，<br>成为共同的积累。</h1><p>社区的讨论、实践与思考，在这里持续记录。<br>从群聊到线下交流，找到值得继续探索的问题。</p></section><section class="wrap archive-section"><div class="archive-tools"><div class="filter-tabs" role="group" aria-label="内容类型"><button class="active" data-filter="all" aria-pressed="true">全部</button><button data-filter="chat" aria-pressed="false">群聊精选</button><button data-filter="recording" aria-pressed="false">录音整理</button></div><label class="search-box"><span>⌕</span><input id="search" type="search" aria-label="搜索日报" placeholder="搜索标题、话题或关键词"></label></div><div class="results-line" id="results" aria-live="polite">共 {len(ds)} 期日报</div><div class="archive-grid" id="digest-list">{cards}</div><div class="empty-state" id="empty" hidden><span>⌕</span><h3>这里暂时没有对应的日报</h3><p>试试其他关键词，或把这次讨论整理成新一期。</p><button class="button dark" id="reset-filters">查看全部日报</button></div></section>''',page='daily',prefix='../',scripts=f'<script type="application/json" id="digest-data">{safe_json(data)}</script><script src="../assets/archive.js" defer></script>')

def detail(d):
    topic_nav=''.join(f'<a href="#{e(t["id"])}"><span>{i:02d}</span>{e(t["category"])}</a>' for i,t in enumerate(d['topics'],1))
    parts=[]
    for i,t in enumerate(d['topics'],1):
        ps=''.join(f'<p>{e(p)}</p>' for p in t['paragraphs'])
        quotes=''.join(f'<blockquote><p>{e(q["text"])}</p><cite>{e(q["speaker"])}'+(' · '+e(q['time']) if q.get('time') else '')+'</cite></blockquote>' for q in t.get('quotes',[]))
        links=''.join(f'<a href="{e(l["url"],quote=True)}" target="_blank" rel="noopener">{e(l["title"])} ↗</a>' for l in t.get('links',[]))
        note=f'<aside class="editor-note"><b>AI 锐评 / 编辑评论</b><p>{e(t["editor_note"])}</p></aside>' if t.get('editor_note') else ''
        extra=f'<details><summary>查看讨论摘录</summary>{quotes}<small>摘录依来源整理，删去部分重复口头语；公开范围见本期来源说明。</small></details>' if quotes else ''
        parts.append(f'<article class="topic-article" id="{e(t["id"])}"><div class="eyebrow">{i:02d} / {e(t["category"])}</div><h2>{e(t["title"])}</h2><div class="article-time">{e(t.get("time_range",""))}</div>{ps}{note}{extra}<div class="related-links">{links}</div></article>')
    actions=''.join(f'<li><span>{e(a["kind"])}</span>{e(a["text"])}</li>' for a in d.get('followups',[]))
    source_links=''.join(f'<li><a href="{e(l["url"],quote=True)}" target="_blank" rel="noopener">{e(l["title"])}</a></li>' for l in d.get('sources',[]))
    public_sources=f'<ul>{source_links}</ul>' if source_links else ''
    content=f'''<div class="wrap reading-top"><a class="text-link" href="../">← 返回日报目录</a><button class="small-button" id="print-page">打印 / 保存 PDF</button></div><div class="wrap reading-layout"><nav class="reading-nav" aria-label="本期话题"><b>本期目录</b>{topic_nav}</nav><div class="reading-body"><header class="article-header"><div class="eyebrow">{badge(d)} · {e(d['date'])}</div><h1>{e(d['title'])}</h1><p class="article-subtitle">{e(d.get('subtitle',''))}</p><div class="article-meta">{len(d['topics'])} 个话题 {'· '+e(d['duration']) if d.get('duration') else ''} · 审核：{e(d['reviewed_by'])}</div><div class="source-note">{e(d.get('source_note',''))}</div></header>{''.join(parts)}<section class="followups"><div class="eyebrow">KEEP THE CONVERSATION GOING</div><h2>把讨论接下去</h2><ul>{actions}</ul>{public_sources}<p class="muted">文中预测与经验归属于发言者。相关技术说法未经独立事实核查；AI 锐评为编辑评论。</p></section><div class="article-next"><a href="../">← 更多社区日报</a></div></div></div>'''
    return layout(d['title'],content,page='daily',prefix='../../',description=d.get('summary'),scripts='<script src="../../assets/article.js" defer></script>')

def about():
    return layout('关于社区','''<section class="wrap page-intro"><div class="eyebrow">HELLO, WE ARE JLULLM</div><h1>好奇心把我们聚在一起，<br>实践让讨论继续。</h1><p>JLULLM AI 社区是一个围绕大模型、智能体与 AI 实践持续交流的地方。<br>我们希望把聊天中的灵感、研究中的困惑、动手后的经验，变成可以分享和复用的知识。</p></section><section class="wrap about-grid"><div><div class="eyebrow">WHAT WE CARE ABOUT</div><h2>关注技术，也关注<br>技术如何进入真实生活。</h2><p>我们聊模型与后训练，聊 Agent 与工具，聊推理加速和具身智能，也聊怎样选题、怎样学习，以及怎样判断一个问题值不值得做。</p><p>具体的问题比宽泛的口号更容易开启讨论。可以带来一篇读不懂的论文、一段跑不顺的代码，或一次与预期不同的实验。</p></div><div class="principles"><div><span>01</span><h3>分享具体经验</h3><p>说清场景、方法与限制，让别人的尝试少走一点弯路。</p></div><div><span>02</span><h3>给分歧留位置</h3><p>不把个人判断写成全体共识，欢迎追问、补充和修正。</p></div><div><span>03</span><h3>让知识继续生长</h3><p>通过日报、资料和实际项目，把讨论变成持续积累。</p></div></div></section><section class="wrap join-panel"><div><div class="eyebrow">BUILD WITH US</div><h2>从你手上的一个问题开始。</h2><p>在 GitHub Discussions 发起交流；通过 Issue 提交内容建议与勘误；<br>也可以用日报模板整理一次讨论，再提交 Pull Request。</p></div><div class="button-row"><a class="button dark" href="https://github.com/goya4140/jlullm-ai-community/discussions" target="_blank" rel="noopener">参与社区讨论 ↗</a><a class="button outline" href="https://github.com/goya4140/jlullm-ai-community/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">日报贡献说明 ↗</a></div></section>''',page='about',prefix='../')

def build():
    ds=[]
    for p in sorted((ROOT/'content/digests').glob('*.json')):
        d=json.loads(p.read_text())
        if d.get('status')=='draft': continue
        if d.get('status')!='published': raise ValueError(f'{p.name}: unknown or missing status')
        try: validate(d)
        except (ValueError,KeyError,TypeError) as exc: raise ValueError(f'{p.name}: {exc}') from exc
        ds.append(d)
    ds.sort(key=lambda d:(d['date'],d['id']),reverse=True)
    if len({d['id'] for d in ds})!=len(ds): raise ValueError('Duplicate digest ID')
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'web/assets',OUT/'assets')
    pages={'index.html':home(ds),'daily/index.html':archive(ds),'about/index.html':about()}
    for d in ds: pages[f'daily/{d["id"]}/index.html']=detail(d)
    for file,body in pages.items():
        p=OUT/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
    (OUT/'.nojekyll').touch()
    (OUT/'404.html').write_text(layout('页面未找到','<section class="wrap page-intro"><div class="eyebrow">404</div><h1>这个话题，还没到这里。</h1><p>页面可能已经移动，回到首页继续看看。</p><a class="button dark" href="/jlullm-ai-community/">返回社区首页 ↗</a></section>',prefix='/jlullm-ai-community/'))
    print(f'Built {len(pages)+1} pages, {len(ds)} published digest(s) → {OUT}')
    return ds

if __name__=='__main__': build()
