"""Single-source Obsidian notes + Canvas + local HTML viewer. Standard library only."""
import argparse
import hashlib
import json
import re
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse

CANVAS = '大模型学习知识地图.canvas'
HTML = '大模型学习知识地图.html'

def metadata(text):
    values = {}
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?', text, re.S)
    if match:
        for line in match[1].splitlines():
            if ':' not in line: continue
            k, v = line.split(':', 1)
            v = v.strip()
            try: v = json.loads(v)
            except (ValueError, TypeError): v = v.strip('"\'')
            values[k.strip()] = v
        text = text[match.end():]
    return values, text

def section(body, name):
    m = re.search(r'^## '+re.escape(name)+r'\s*\n(.*?)(?=^## |\Z)',body,re.M|re.S)
    return m.group(1).strip() if m else ''

def safe_file(vault, relative):
    p = (vault / relative).resolve()
    if not p.is_relative_to(vault.resolve()): raise ValueError('Note path outside vault')
    return p

class Atlas:
    def __init__(self, root):
        self.root = root.resolve()
        self.vault = next((p for p in [self.root, *self.root.parents] if (p/'.obsidian').is_dir()), self.root.parents[1])
        self.tool = self.root/'.atlas'
        self.seed = json.loads((self.tool/'seed.json').read_text(encoding='utf-8'))
        self.template = (self.tool/'viewer-template.html').read_text(encoding='utf-8')

    def snapshot(self):
        raw_canvas = (self.root/CANVAS).read_bytes()
        canvas = json.loads(raw_canvas)
        seeds = {n['id']: n for n in self.seed['nodes']}
        nodes=[]; digest=hashlib.sha256(raw_canvas)
        for c in canvas['nodes']:
            if c['type']=='group': continue
            old = seeds.get(c['id'], {})
            n=dict(old)
            n['id']=c['id']
            n.setdefault('group',0)
            # New Canvas cards inherit their enclosing group's region.
            for g in canvas['nodes']:
                if g['type']=='group' and g['x']<=c['x']<g['x']+g['width'] and g['y']<=c['y']<g['y']+g['height']:
                    try: n['group']=int(g['id'].replace('group',''))
                    except ValueError: pass
            n['group']=max(0,min(5,n['group']))
            n['canvasX']=c['x']; n['canvasY']=c['y']
            if c['type']=='file':
                path=safe_file(self.vault,c['file'])
                try: raw=path.read_bytes(); text=raw.decode('utf-8-sig')
                except FileNotFoundError: raw=b'';text='# 笔记暂时找不到\n\n请在 Canvas 检查文件路径。'
                digest.update(raw)
                props,body=metadata(text)
                title=re.search(r'^#+\s+(.+)$',body,re.M)
                n['label']=str(props.get('title') or (title.group(1) if title else path.stem))
                n['kind']=props.get('kind',old.get('kind','概念'))
                if n['kind'] not in ['概念','资料','项目']: n['kind']='概念'
                n['desc']=section(body,'学习范围') or old.get('desc','在 Obsidian 中补充学习范围。')
                n['goal']=section(body,'验收标准') or old.get('goal','在 Obsidian 中补充验收标准。')
                url=re.search(r'\]\((https?://[^\s)]+)\)',section(body,'资料'))
                n['url']=url.group(1) if url else old.get('url','')
                n['status']=props.get('status','未开始')
                n['body']=body
                n['notePath']=c['file']
                n['noteUri']='obsidian://open?path='+quote(str(path),safe='')
            else:
                body=c.get('text',c.get('url',''))
                title=re.search(r'^#+\s+(.+)$',body,re.M)
                n['label']=title.group(1) if title else body.split('\n')[0][:40] or c['id']
                n.setdefault('kind','概念');n.setdefault('desc',body);n.setdefault('goal','')
                n['body']=body;n['status']='未开始';n['noteUri']='';n['notePath']=''
            nodes.append(n)
        ids={n['id'] for n in nodes}
        edges=[dict(a=e['fromNode'],b=e['toNode'],kind=e.get('label','一般关联')) for e in canvas.get('edges',[]) if e['fromNode'] in ids and e['toNode'] in ids]
        # Personal wikilinks to other map notes also become graph relations.
        titles={Path(n.get('notePath','')).stem:n['id'] for n in nodes if n.get('notePath')}
        for n in nodes:
            for link in re.findall(r'\[\[([^\]|#]+)(?:[^\]]*)\]\]',n['body']):
                target=titles.get(Path(link).stem)
                if target and target!=n['id'] and not any(e['a']==n['id'] and e['b']==target for e in edges):
                    edges.append(dict(a=n['id'],b=target,kind='笔记链接'))
        return dict(nodes=nodes,edges=edges,groups=self.seed['groups'],revision=digest.hexdigest())

    def render(self):
        d=self.snapshot()
        # Escape script terminators in personal note content.
        data=json.dumps(d,ensure_ascii=False).replace('<','\\u003c')
        return self.template.replace('__DATA__',data).encode('utf-8')

def handler(atlas):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_GET(self):
            route=urlparse(self.path).path
            try:
                if route=='/api/health': data=json.dumps({'app':'obsidian-learning-atlas','root':str(atlas.root)}).encode();ctype='application/json'
                elif route=='/api/snapshot': data=json.dumps(atlas.snapshot(),ensure_ascii=False).encode('utf-8');ctype='application/json; charset=utf-8'
                elif route=='/api/stop':
                    data=b'Stopped';ctype='text/plain'
                    threading.Thread(target=self.server.shutdown,daemon=True).start()
                elif route in ['/', '/index.html']: data=atlas.render();ctype='text/html; charset=utf-8'
                else: self.send_error(404);return
                self.send_response(200);self.send_header('Content-Type',ctype);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            except (OSError,ValueError,KeyError) as exc:
                self.send_error(503,'Files are being saved; retry shortly')
    return Handler

def export(atlas):
    output=atlas.root/HTML
    temp=output.with_suffix('.html.tmp')
    temp.write_bytes(atlas.render());temp.replace(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--port',type=int,default=8765);p.add_argument('--export',action='store_true');p.add_argument('--open',action='store_true');a=p.parse_args()
    atlas=Atlas(a.root)
    if a.export: export(atlas);return
    server=ThreadingHTTPServer(('127.0.0.1',a.port),handler(atlas))
    def watch():
        revision=None
        while True:
            try:
                current=atlas.snapshot()['revision']
                if current!=revision: export(atlas);revision=current
            except (OSError,ValueError,KeyError): pass  # Canvas can be briefly incomplete during an editor save.
            time.sleep(1)
    threading.Thread(target=watch,daemon=True).start()
    if a.open:webbrowser.open(f'http://127.0.0.1:{a.port}/')
    server.serve_forever();server.server_close()

if __name__=='__main__':main()
