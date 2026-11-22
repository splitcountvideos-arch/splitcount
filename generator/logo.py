from PIL import Image, ImageDraw, ImageFilter, ImageFont
import colorsys, math
S=3200; img=Image.new("RGB",(S,S),(12,12,20)); d=ImageDraw.Draw(img)
c=S/2
# ring
R=1150; d.ellipse([c-R,c-R,c+R,c+R],outline=(240,240,255),width=70)
# glow layer for balls
glow=Image.new("RGB",(S,S),(0,0,0)); g=ImageDraw.Draw(glow)
def ball(dr,x,y,r,h):
    col=tuple(int(v*255) for v in colorsys.hsv_to_rgb(h,0.85,1)); dr.ellipse([x-r,y-r,x+r,y+r],fill=col)
# split: one ball upper-left center trail, splitting into two
balls=[(c-120,c-80,300,0.0),(c+430,c-430,190,0.09),(c+470,c+170,190,0.33)]
# trails
for (x,y,r,h),ang in [((c+430,c-430,190,0.09),None),((c+470,c+170,190,0.33),None)]:
    for i in range(1,6):
        t=i/6; px=c-120+(x-(c-120))*t; py=c-80+(y-(c-80))*t
        ball(g,px,py,60+20*t,h); 
for b in balls: ball(g,*b)
glow=glow.filter(ImageFilter.GaussianBlur(90))
img=Image.blend(img,Image.eval(glow,lambda v:v),0.0)
from PIL import ImageChops
img=ImageChops.add(img,glow)
d=ImageDraw.Draw(img)
for (x,y,r,h) in [((c+430,c-430,190,0.09)),((c+470,c+170,190,0.33))]:
    for i in range(1,6):
        t=i/6; px=c-120+(x-(c-120))*t; py=c-80+(y-(c-80))*t
        col=tuple(int(v*255*(0.35+0.4*t)) for v in colorsys.hsv_to_rgb(h,0.85,1))
        rr=40+25*t; d.ellipse([px-rr,py-rr,px+rr,py+rr],fill=col)
for b in balls: ball(d,*b)
# small sparkle highlight
for (x,y,r,h) in balls: d.ellipse([x-r*0.55,y-r*0.6,x-r*0.15,y-r*0.2],fill=(255,255,255))
img.resize((800,800),Image.LANCZOS).save("splitcount_profil.png")
# circle preview
m=Image.new("L",(800,800),0); ImageDraw.Draw(m).ellipse([0,0,800,800],fill=255)
p=Image.new("RGB",(800,800),(255,255,255)); p.paste(Image.open("splitcount_profil.png"),(0,0),m); p.resize((200,200)).save("preview.png")
