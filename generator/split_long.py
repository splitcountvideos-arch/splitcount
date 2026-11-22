"""TikTok long version (>60 s): balls split with probability P on wall hits; ball radius shrinks as count grows.
Milestone banners at 100 / 1,000 / 5,000 / 10,000. Usage: python3 split_long.py OUT.mp4 [P] [--dry]"""
import numpy as np, subprocess, wave, colorsys, sys
OUT=sys.argv[1]; P=float(sys.argv[2]) if len(sys.argv)>2 else 0.12; DRY="--dry" in sys.argv
W,H,FPS=1080,1920,30; CX,CY,R=W/2,900,400; MAX=10000; MAXDUR=80
rng=np.random.default_rng(11)
pos=np.array([[CX,CY-150.0]]); vel=np.array([[260.0,-120.0]]); hue=np.array([0.0])
g=np.array([0,500.0]); dt=1/FPS; sub=3
MIL=[100,1000,5000,10000]; mil_t={}
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font=ImageFont.truetype(F,150); f2=ImageFont.truetype(F,64); f3=ImageFont.truetype(F,52); f4=ImageFont.truetype(F,90)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","32","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
sr=44100; audio=np.zeros(sr*MAXDUR)
done=None; fr=0
while True:
    t=fr/FPS
    if done is not None and t>done+3.5: break
    if t>MAXDUR-1: break
    n=len(pos); br=max(3.0,9.0*(1-np.log10(max(n,1))/5)); hits=0
    for _ in range(sub):
        h=dt/sub; vel+=g*h; pos+=vel*h
        d=pos-[CX,CY]; dist=np.linalg.norm(d,axis=1)
        out=dist>R-br
        if out.any():
            nrm=d[out]/dist[out,None]; pos[out]=[CX,CY]+nrm*(R-br)
            vn=(vel[out]*nrm).sum(1,keepdims=True); vel[out]=vel[out]-2*vn*nrm
            k=out.sum(); hits+=k
            if len(pos)<MAX:
                idx=np.where(out)[0]; idx=idx[rng.random(len(idx))<P][:MAX-len(pos)]
                if len(idx):
                    ang=rng.uniform(-0.6,0.6,len(idx)); c,s=np.cos(ang),np.sin(ang); v=vel[idx]
                    nv=np.stack([v[:,0]*c-v[:,1]*s,v[:,0]*s+v[:,1]*c],1)
                    pos=np.vstack([pos,pos[idx]]); vel=np.vstack([vel,nv]); hue=np.concatenate([hue,(hue[idx]+0.02)%1])
    n=len(pos)
    for m in MIL:
        if n>=m and m not in mil_t: mil_t[m]=t
    if done is None and n>=MAX: done=t
    if hits and int(t*sr)<len(audio)-2000:
        st=int(t*sr); L=int(0.03*sr); tt=np.arange(L)/sr; f=400+n/MAX*1100
        audio[st:st+L]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*120)*min(0.22,0.05*np.sqrt(hits))
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(240,240,255),width=6)
        cols=[tuple(int(x*255) for x in colorsys.hsv_to_rgb(hh,0.85,1)) for hh in hue]
        for p,col in zip(pos,cols): dr.ellipse([p[0]-br,p[1]-br,p[0]+br,p[1]+br],fill=col)
        dr.text((W/2,190),"Every wall hit has a",font=f2,anchor="mm",fill=(255,255,255))
        dr.text((W/2,265),"chance to split the ball!",font=f2,anchor="mm",fill=(255,210,60))
        dr.text((W/2,375),f"{n:,}",font=font,anchor="mm",fill=(255,255,255))
        # milestone flash
        for m,mt in mil_t.items():
            if 0<=t-mt<1.2 and m<MAX: dr.text((W/2,462),f"{m:,} reached!",font=f3,anchor="mm",fill=(120,220,140))
        dr.text((W/2,1360),"Will it hit 10,000",font=f3,anchor="mm",fill=(200,200,220)); dr.text((W/2,1420),"before 1 minute?",font=f3,anchor="mm",fill=(200,200,220))
        if done is None: dr.text((W/2,1490),f"{t:4.1f} s",font=f3,anchor="mm",fill=(120,220,140))
        else:
            ok=done<60; dr.text((W/2,1495),(f"YES! {done:.1f} s" if ok else f"NO! {done:.1f} s"),font=f4,anchor="mm",fill=(120,220,140) if ok else (255,90,90))
        ff.stdin.write(img.tobytes())
    fr+=1
print("done_at",done,"milestones",mil_t,"duration",fr/FPS)
if not DRY:
    ff.stdin.close(); ff.wait()
    a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT])
    import os; os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
