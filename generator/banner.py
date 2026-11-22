from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import colorsys, random
W,H=2560,1440; random.seed(3)
img=Image.new("RGB",(W,H),(12,12,20))
glow=Image.new("RGB",(W,H),(0,0,0)); g=ImageDraw.Draw(glow)
balls=[]
sx0,sx1,sy0,sy1=(W-1546)/2,(W+1546)/2,(H-423)/2,(H+423)/2
while len(balls)<170:
    x,y=random.uniform(0,W),random.uniform(0,H)
    # keep text zone clear
    if sx0-40<x<sx1+40 and sy0-60<y<sy1+60: continue
    dx=min(abs(x-W/2)/(W/2),1)
    r=random.uniform(8,26)*(0.6+dx)
    h=random.choice([0.0,0.09,0.15,0.33,0.5,0.58])
    balls.append((x,y,r,h))
def col(h,v=1): return tuple(int(c*255*v) for c in colorsys.hsv_to_rgb(h,0.85,1))
for x,y,r,h in balls: g.ellipse([x-r,y-r,x+r,y+r],fill=col(h))
glow=glow.filter(ImageFilter.GaussianBlur(28))
img=ImageChops.add(img,glow); d=ImageDraw.Draw(img)
for x,y,r,h in balls:
    d.ellipse([x-r,y-r,x+r,y+r],fill=col(h))
    d.ellipse([x-r*0.55,y-r*0.6,x-r*0.15,y-r*0.2],fill=(255,255,255))
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
t=ImageFont.truetype(F,170); s=ImageFont.truetype(F,50)
cx,cy=W/2,H/2
# title: "SPLIT" white "COUNT" yellow
a,b="SPLIT ","COUNT"
wa=d.textlength(a,font=t); wb=d.textlength(b,font=t); x0=cx-(wa+wb)/2
d.text((x0,cy-40),a,font=t,anchor="lm",fill=(255,255,255))
d.text((x0+wa,cy-40),b,font=t,anchor="lm",fill=(255,210,60))
d.text((cx,cy+105),"A new simulation every day  •  Guess before it ends!",font=s,anchor="mm",fill=(200,200,220))
img.save("splitcount_banner.png")
img.crop((int(sx0),int(sy0),int(sx1),int(sy1))).resize((773,212)).save("banner_safe.png")
img.resize((1280,720)).save("banner_small.png")
