import sys,glob,os
from PIL import Image,ImageDraw
src,out=sys.argv[1],sys.argv[2]
files=sorted(glob.glob(src+'/p-*.jpg'))
per=24;cols=6
for k in range(0,len(files),per):
    chunk=files[k:k+per]
    w,h=300,424
    rows=(len(chunk)+cols-1)//cols
    sh=Image.new('RGB',(cols*w,rows*(h+18)),'white')
    d=ImageDraw.Draw(sh)
    for i,f in enumerate(chunk):
        im=Image.open(f).convert('RGB').resize((w,h))
        x,y=(i%cols)*w,(i//cols)*(h+18)
        sh.paste(im,(x,y+18)); d.text((x+4,y+2),os.path.basename(f),fill='red')
    sh.save(f'{out}/sheet_{k//per+1:02d}.jpg',quality=80)
