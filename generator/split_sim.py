import numpy as np, subprocess, wave, colorsys, sys, json
TX=json.loads(sys.argv[1]); OUT=sys.argv[2]
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,DUR=1080,1920,30,22
CX,CY,R=W/2,1060,440
MAX=2000
rng=np.random.default_rng(7)
pos=np.array([[CX,CY-150.0]]); vel=np.array([[260.0,-120.0]]); hue=np.array([0.0])
g=np.array([0,500.0]); dt=1/FPS; sub=4
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",150)
f2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",64)
f3=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",52)
sr=44100; audio=np.zeros(sr*DUR)
ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
done=None
for fr in range(FPS*DUR):
    t=fr/FPS; hits=0
    if done is not None and t>done+2.5: break
    for _ in range(sub):
        h=dt/sub; vel+=g*h; pos+=vel*h
        d=pos-[CX,CY]; dist=np.linalg.norm(d,axis=1); br=9
        out=dist>R-br
        if out.any():
            n=d[out]/dist[out,None]
            pos[out]=[CX,CY]+n*(R-br)
            vn=(vel[out]*n).sum(1,keepdims=True)
            vel[out]=vel[out]-2*vn*n
            k=out.sum(); hits+=k
            if len(pos)<MAX:
                k2=min(k,MAX-len(pos)); idx=np.where(out)[0][:k2]
                ang=rng.uniform(-0.6,0.6,k2)
                c,s=np.cos(ang),np.sin(ang); v=vel[idx]
                nv=np.stack([v[:,0]*c-v[:,1]*s,v[:,0]*s+v[:,1]*c],1)
                pos=np.vstack([pos,pos[idx]]); vel=np.vstack([vel,nv]); hue=np.concatenate([hue,(hue[idx]+0.03)%1])
    if done is None and len(pos)>=MAX: done=t
    if hits:
        st=int(t*sr); L=int(0.03*sr); tt=np.arange(L)/sr
        f=500+min(len(pos),MAX)/MAX*900
        audio[st:st+L]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*120)*min(0.25,0.06*np.sqrt(hits))
    img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
    dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(240,240,255),width=6)
    for p,hh in zip(pos,hue):
        r,g_,b=[int(x*255) for x in colorsys.hsv_to_rgb(hh,0.85,1)]
        dr.ellipse([p[0]-9,p[1]-9,p[0]+9,p[1]+9],fill=(r,g_,b))
    dr.text((W/2,230),TX["l1"],font=f2,anchor="mm",fill=(255,255,255))
    dr.text((W/2,310),TX["l2"],font=f2,anchor="mm",fill=(255,210,60))
    dr.text((W/2,480),f"{len(pos)}",font=font,anchor="mm",fill=(255,255,255))
    dr.text((W/2,1640),TX["q"],font=f3,anchor="mm",fill=(200,200,220))
    dr.text((W/2,1720),(f"{t:4.1f} {TX['s']}" if done is None else TX["done"].format(done)),font=f3,anchor="mm",fill=(120,220,140))
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
a=np.clip(audio,-1,1); 
with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT])
