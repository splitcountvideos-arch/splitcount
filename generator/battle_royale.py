"""Battle royale: 12 colored balls in a circle. On contact the ball that wins the bite (usually the bigger one,
probability ~ area share) takes a chunk of the other's area. Ball pops when it gets too small. Last one wins.
Usage: python3 battle_royale.py OUT.mp4 SEED BITE [--long] [--dry]"""
import numpy as np, subprocess, wave, sys, os
OUT=sys.argv[1]; SEED=int(sys.argv[2]); BITE=float(sys.argv[3]); LONG="--long" in sys.argv; DRY="--dry" in sys.argv
W,H,FPS=1080,1920,30; CX,CY,R=W/2,900,400; dt=1/FPS; SUB=4; MAXDUR=90
NAMES=["RED","ORANGE","YELLOW","LIME","GREEN","CYAN","BLUE","PURPLE","PINK","WHITE","GRAY","BROWN"]
COLS=[(235,55,55),(255,140,20),(255,220,30),(165,255,70),(25,170,80),(20,215,230),(50,100,255),(155,70,235),(255,110,200),(240,240,240),(135,135,150),(155,95,45)]
N=12; rng=np.random.default_rng(SEED)
ang=np.linspace(0,2*np.pi,N,endpoint=False)+rng.uniform(0,0.3)
rad=rng.uniform(26,36,N); pos=np.stack([CX+260*np.cos(ang),CY+260*np.sin(ang)],1)
th=rng.uniform(0,2*np.pi,N); vel=np.stack([np.cos(th),np.sin(th)],1)
alive=np.ones(N,bool); BASE=330 if LONG else 520; POP=9.0; STEER=float(os.environ.get('STEER','0.15')); EAT=float(os.environ.get('EAT','0.06')); Z0=float(os.environ.get('Z0','15')); ZR=float(os.environ.get('ZR','4.5')); RMIN=float(os.environ.get('RMIN','180')); TAKE0=float(sys.argv[4]) if len(sys.argv)>4 and not sys.argv[4].startswith('--') else 300
def spd(r): return BASE*(30/r)**0.35*(1+0.08*(N-alive.sum()))
sr=44100; audio=np.zeros(sr*MAXDUR)
def tone(t,f,L,a,decay):
    st=int(t*sr); n=int(L*sr); tt=np.arange(n)/sr
    if st+n<len(audio): audio[st:st+n]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*decay)*a
events=[]; elim_t={}; done=None; winner=None; fr=0; cool={}
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fT=ImageFont.truetype(F,62); fB=ImageFont.truetype(F,120); fS=ImageFont.truetype(F,50); fN=ImageFont.truetype(F,22); fW=ImageFont.truetype(F,96); FN={}
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","28","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
flash=[]  # (t, text, color)
zone_flashed=False
while True:
    t=fr/FPS
    if done is not None and t>done+4.0: break
    if t>MAXDUR-1: break
    if done is None:
        R=max(RMIN,400-max(0,t-Z0)*ZR)
        for _ in range(SUB):
            h=dt/SUB; pos[alive]+=vel[alive]*h
            for i in np.where(alive)[0]:
                d=pos[i]-[CX,CY]; dist=np.linalg.norm(d)
                if dist>R-rad[i]:
                    nrm=d/dist; pos[i]=[CX,CY]+nrm*(R-rad[i]); vn=vel[i]@nrm
                    if vn>0: vel[i]-=2*vn*nrm
            idx=np.where(alive)[0]
            for a in range(len(idx)):
                for b in range(a+1,len(idx)):
                    i,j=idx[a],idx[b]
                    if not (alive[i] and alive[j]): continue
                    d=pos[j]-pos[i]; dist=np.linalg.norm(d)+1e-9
                    if dist<rad[i]+rad[j]:
                        nrm=d/dist; ov=rad[i]+rad[j]-dist
                        mi,mj=rad[i]**2,rad[j]**2
                        pos[i]-=nrm*ov*mj/(mi+mj); pos[j]+=nrm*ov*mi/(mi+mj)
                        rv=(vel[j]-vel[i])@nrm
                        if rv<0:
                            imp=2*rv/(mi+mj); vel[i]+=imp*mj*nrm; vel[j]-=imp*mi*nrm
                        key=(i,j)
                        if t-cool.get(key,-9)>0.25:
                            cool[key]=t
                            pw=mi/(mi+mj); eat,vic=(i,j) if rng.random()<pw else (j,i)
                            take=min(max(rad[vic]**2*BITE,TAKE0,EAT*rad[eat]**2),rad[vic]**2); rad[eat]=np.sqrt(rad[eat]**2+take); rad[vic]=np.sqrt(rad[vic]**2-take)
                            tone(t,300+rad[eat]*4,0.05,0.18,60)
                            if rad[vic]<POP or rad[vic]**2<1:
                                rad[eat]=np.sqrt(rad[eat]**2+rad[vic]**2); alive[vic]=False; elim_t[vic]=t
                                tone(t,180,0.25,0.35,14); tone(t,900,0.12,0.15,30)
                                left=alive.sum()
                                if left in (6,3): flash.append((t,f"TOP {left}!",(255,210,60)))
                                if left==2: flash.append((t,"FINAL DUEL!",(255,90,90)))
                                if left==1:
                                    done=t; winner=int(np.where(alive)[0][0])
                                    for k,f in enumerate([523,659,784,1047]): tone(t+0.15*k,f,0.4,0.25,5)
            ids=np.where(alive)[0]
            for i in ids:
                if len(ids)>1:
                    o=[j for j in ids if j!=i]; dd=pos[o]-pos[i]; k=np.argmin(np.linalg.norm(dd,axis=1))
                    u=dd[k]/(np.linalg.norm(dd[k])+1e-9); vel[i]+=u*spd(rad[i])*STEER*(1+0.25*(N-len(ids)))*h
                vel[i]+=rng.normal(0,30,2)*h*10
                s=np.linalg.norm(vel[i])+1e-9; vel[i]*=spd(rad[i])/s
    if done is None and not zone_flashed and t>=Z0: zone_flashed=True; flash.append((t,"ZONE CLOSING!",(255,90,90)))
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        if R<400: dr.ellipse([CX-406,CY-406,CX+406,CY+406],outline=(70,30,40),width=3)
        dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(255,90,90) if R<400 else (240,240,255),width=6)
        for i in np.where(alive)[0]:
            x,y=pos[i]; r=rad[i]; dr.ellipse([x-r,y-r,x+r,y+r],fill=COLS[i])
            if r>=26:
                fz=min(34,int(1.7*r/max(1,len(NAMES[i]))*1.0)); 
                if fz>=13:
                    fnt=FN.get(fz) or FN.setdefault(fz,ImageFont.truetype(F,fz))
                    if dr.textlength(NAMES[i],font=fnt)<1.75*r: dr.text((x,y),NAMES[i],font=fnt,anchor="mm",fill=(0,0,0) if sum(COLS[i])>400 else (255,255,255))
        dr.text((W/2,185),"12 balls. Bigger eats smaller.",font=fT,anchor="mm",fill=(255,255,255))
        dr.text((W/2,260),"Last one standing wins!",font=fT,anchor="mm",fill=(255,210,60))
        if done is None:
            dr.text((W/2,370),f"ALIVE: {alive.sum()}",font=fB,anchor="mm",fill=(255,255,255))
        else:
            dr.text((W/2,370),f"{NAMES[winner]} WINS!",font=fW,anchor="mm",fill=COLS[winner])
        for k in range(N):  # roster row
            x=W/2+(k-5.5)*72; y=465; c=COLS[k] if alive[k] else (50,50,60)
            dr.ellipse([x-22,y-22,x+22,y+22],fill=c)
            if not alive[k]: dr.line([x-18,y-18,x+18,y+18],fill=(255,80,80),width=5); dr.line([x-18,y+18,x+18,y-18],fill=(255,80,80),width=5)
        for (ft,txt,col) in flash:
            if 0<=t-ft<1.5: dr.text((W/2,1385),txt,font=fW,anchor="mm",fill=col)
        if not any(0<=t-ft<1.5 for ft,_,_ in flash):
            l1,l2=("Which color wins?","Pick yours in the comments!") if done is None else ("Did you guess right?","Tell us in the comments!")
            dr.text((W/2,1385),l1,font=fS,anchor="mm",fill=(200,200,220))
            dr.text((W/2,1445),l2,font=fS,anchor="mm",fill=(200,200,220))
        m,s=divmod(int(min(t,done if done else t)),60); dr.text((W/2,1500),f"{m}:{s:02d}",font=fS,anchor="mm",fill=(120,220,140))
        ff.stdin.write(img.tobytes())
    fr+=1
order=sorted(elim_t,key=elim_t.get)
print("seed",SEED,"done",None if done is None else round(done,1),"winner",None if winner is None else NAMES[winner],"dur",round(fr/FPS,1),"elims",[round(elim_t[k],1) for k in order])
if not DRY:
    ff.stdin.close(); ff.wait()
    a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT])
    os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
