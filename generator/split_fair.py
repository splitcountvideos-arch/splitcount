"""'No-cheating' split (from viewer comments): a ball may only split on a real bounce
(normal speed > VMIN) and at most once every COOLDOWN seconds. The ball with the most
splits wears a crown (MVP). Usage: python3 split_fair.py OUT.mp4 TARGET COOLDOWN [--dry]"""
import numpy as np, subprocess, wave, colorsys, sys, os
OUT=sys.argv[1]; TARGET=int(sys.argv[2]); COOL=float(sys.argv[3]); DRY="--dry" in sys.argv
W,H,FPS=1080,1920,30; CX,CY,R=W/2,900,400; VMIN=120.0; MAXDUR=90
rng=np.random.default_rng(5)
pos=np.array([[CX,CY-150.0]]); vel=np.array([[260.0,-120.0]]); hue=np.array([0.0])
last=np.array([-9.0]); splits=np.array([0]); g=np.array([0,500.0]); dt=1/FPS; sub=3
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font=ImageFont.truetype(F,150); f2=ImageFont.truetype(F,58); f3=ImageFont.truetype(F,50); f4=ImageFont.truetype(F,84); f5=ImageFont.truetype(F,34)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","30","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
sr=44100; audio=np.zeros(sr*MAXDUR); done=None; fr=0
while True:
    t=fr/FPS
    if done is not None and t>done+3.5: break
    if t>MAXDUR-1: break
    n=len(pos); br=max(3.0,9.0*(1-np.log10(max(n,1))/5)); hits=0
    for _ in range(sub):
        h=dt/sub; tt=t
        vel+=g*h; pos+=vel*h
        d=pos-[CX,CY]; dist=np.linalg.norm(d,axis=1); out=dist>R-br
        if out.any():
            nrm=d[out]/dist[out,None]; pos[out]=[CX,CY]+nrm*(R-br)
            vn=(vel[out]*nrm).sum(1); vel[out]=vel[out]-2*vn[:,None]*nrm
            idx=np.where(out)[0]; ok=(vn>VMIN)&(tt-last[idx]>COOL)
            idx=idx[ok][:max(0,TARGET-len(pos))]; hits+=len(idx)
            if len(idx):
                ang=rng.uniform(-0.6,0.6,len(idx)); c,s=np.cos(ang),np.sin(ang); v=vel[idx]
                nv=np.stack([v[:,0]*c-v[:,1]*s,v[:,0]*s+v[:,1]*c],1)
                last[idx]=tt; splits[idx]+=1
                pos=np.vstack([pos,pos[idx]]); vel=np.vstack([vel,nv]); hue=np.concatenate([hue,(hue[idx]+0.02)%1])
                last=np.concatenate([last,np.full(len(idx),tt)]); splits=np.concatenate([splits,np.zeros(len(idx),int)])
    n=len(pos)
    if done is None and n>=TARGET: done=t
    if hits and int(t*sr)<len(audio)-2000:
        st=int(t*sr); L=int(0.03*sr); a=np.arange(L)/sr; f=400+n/TARGET*1100
        audio[st:st+L]+=np.sin(2*np.pi*f*a)*np.exp(-a*120)*min(0.22,0.05*np.sqrt(hits))
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(240,240,255),width=6)
        for p,hh in zip(pos,hue):
            col=tuple(int(x*255) for x in colorsys.hsv_to_rgb(hh,0.85,1)); dr.ellipse([p[0]-br,p[1]-br,p[0]+br,p[1]+br],fill=col)
        m=int(np.argmax(splits)); mx,my=pos[m]; s=max(br,7)*2.2
        dr.ellipse([mx-br-3,my-br-3,mx+br+3,my+br+3],outline=(255,215,0),width=3)
        cy0=my-br-6; dr.polygon([(mx-s,cy0),(mx+s,cy0),(mx+s,cy0-s),(mx+s/2,cy0-s/2),(mx,cy0-s*1.2),(mx-s/2,cy0-s/2),(mx-s,cy0-s)],fill=(255,215,0))
        dr.text((W/2,150),"\"It's a bug!\" – you said.",font=f5,anchor="mm",fill=(170,170,190))
        dr.text((W/2,215),"NO-CHEATING VERSION",font=f2,anchor="mm",fill=(255,210,60))
        dr.text((W/2,280),"1 split per real bounce",font=f3,anchor="mm",fill=(255,255,255))
        dr.text((W/2,400),f"{n:,}",font=font,anchor="mm",fill=(255,255,255))
        dr.text((W/2,1340),f"MVP ball: {int(splits[m])} splits",font=f5,anchor="mm",fill=(255,215,0))
        dr.text((W/2,1410),f"How long to {TARGET:,} now?",font=f3,anchor="mm",fill=(200,200,220))
        if done is None: dr.text((W/2,1480),f"{t:4.1f} s",font=f3,anchor="mm",fill=(120,220,140))
        else: dr.text((W/2,1485),f"{done:.1f} s!",font=f4,anchor="mm",fill=(120,220,140))
        ff.stdin.write(img.tobytes())
    fr+=1
print("done_at",done,"duration",fr/FPS,"mvp_splits",int(splits.max()))
if not DRY:
    ff.stdin.close(); ff.wait(); a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT]); os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
