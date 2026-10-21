import re,sys
d=open(sys.argv[1]+'/word/document.xml',encoding='utf-8').read()
rels=open(sys.argv[1]+'/word/_rels/document.xml.rels',encoding='utf-8').read()
rm=dict(re.findall(r'Id="(rId\w+)"[^>]*Target="([^"]+)"',rels))
rm.update({a:b for b,a in re.findall(r'Target="([^"]+)"[^>]*Id="(rId\w+)"',rels)})
paras=re.findall(r'<w:p[ >].*?</w:p>',d,flags=re.S)
n=0
for i,p in enumerate(paras):
    ids=re.findall(r'r:embed="(rId\w+)"',p)
    txt=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',p))
    if ids:
        # next text paragraph as caption
        cap=''
        for q in paras[i+1:i+3]:
            t=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',q))
            if t.strip(): cap=t;break
        ext=re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"',p)
        for k,r in enumerate(ids):
            n+=1
            e=ext[k] if k<len(ext) else ('0','0')
            print(n,i,rm.get(r),f'{int(e[0])/360000:.1f}x{int(e[1])/360000:.1f}cm','|',(txt or cap)[:110])
