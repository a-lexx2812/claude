import xml.etree.ElementTree as ET, sys, json, math
t=ET.parse(sys.argv[1]).getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in t.iter('node')}
ntags={}
for n in t.iter('node'):
    tg={x.get('k'):x.get('v') for x in n.findall('tag')}
    if tg: ntags[n.get('id')]=tg
ways=[]
for w in t.iter('way'):
    tg={x.get('k'):x.get('v') for x in w.findall('tag')}
    pts=[nodes[nd.get('ref')] for nd in w.findall('nd') if nd.get('ref') in nodes]
    ways.append({'id':w.get('id'),'tags':tg,'pts':pts})
rels=[]
for r in t.iter('relation'):
    tg={x.get('k'):x.get('v') for x in r.findall('tag')}
    mem=[(m.get('type'),m.get('ref'),m.get('role')) for m in r.findall('member')]
    rels.append({'id':r.get('id'),'tags':tg,'members':mem})
json.dump({'ways':ways,'rels':rels,'ntags':{k:[nodes[k],v] for k,v in ntags.items()}},open(sys.argv[2],'w'))
from collections import Counter
c=Counter()
for w in ways:
    for k in ('waterway','power','highway','building','landuse','natural','leisure','amenity','bridge'):
        if k in w['tags']: c[(k,w['tags'][k])]+=1
for k,v in sorted(c.items()): print(k,v)
for w in ways:
    tg=w['tags']
    if 'waterway' in tg or 'power' in tg or tg.get('highway') in ('primary','secondary','tertiary','residential','unclassified') or 'name' in tg:
        print(w['id'],{k:tg[k] for k in tg if k in('waterway','power','highway','name','name:en','voltage','bridge','landuse','natural')},len(w['pts']))
for r in rels:
    print('REL',r['id'],r['tags'].get('type'),r['tags'].get('name'),r['tags'].get('waterway'),r['tags'].get('landuse'),r['tags'].get('natural'))
for k,(p,v) in ntags.items():
    if any(x in v for x in ('highway','public_transport','power','name')): print('N',k,p,{a:v[a] for a in v if a in('highway','public_transport','power','name')})
