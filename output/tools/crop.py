import sys
from PIL import Image
f,out,x0,y0,x1,y1,sc=sys.argv[1],sys.argv[2],*map(float,sys.argv[3:8])
im=Image.open(f).convert('RGB').crop((int(x0),int(y0),int(x1),int(y1)))
im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
im.save(out,quality=92)
print(im.size)
