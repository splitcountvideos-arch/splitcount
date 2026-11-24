"""Escape the rings: a ball bounces (with gravity) inside 15 concentric spinning rings, each with a gap.
Passing through a gap pops that ring. How long until it escapes them all?
Usage: GAP=40 python3 generator/escape_rings.py OUT.mp4 SEED [--long] [--dry]
  GAP = gap width in degrees (smaller = slower). --long adds the 1:00 target/timer for TikTok."""
import numpy as np, subprocess, wave, sys, os, colorsys
OUT=sys.argv[1]; SEED=int(sys.argv[2]); LONG="--long" in sys.argv; DRY="--dry" in sys.argv
W,H,FPS=1080,1920,30; CX,CY=W/2,900; dt=1/FPS; SUB=10; MAXDUR=95
NR=15; R0,R1=72,420; RADS=np.linspace(R0,R1,NR); BR=13.0
GAP=np.radians(float(os.environ.get('GAP','40'))); G=float(os.environ.get('G','1100'))
VMIN,VMAX=float(os.environ.get('VMIN','520')),900.0; TARGET=60.0
rng=np.random.default_rng(SEED)
th0=rng.uniform(0,2*np.pi,NR); om=rng.uniform(0.9,1.8,NR)*np.where(np.arange(NR)%2==0,1,-1)
alive=np.ones(NR,bool); pos=np.array([CX,CY],float); a0=rng.uniform(0,2*np.pi); vel=np.array([np.cos(a0),np.sin(a0)])*600
COLS=[tuple(int(c*255) for c in colorsys.hsv_to_rgb(k/NR*0.85,0.75,1.0)) for k in range(NR)]
sr=44100; audio=np.zeros(sr*MAXDUR)
SCALE=[261.6,293.7,329.6,392.0,440.0]
def tone(t,f,L,a,decay):
    st=int(t*sr); n=int(L*sr); tt=np.arange(n)/sr
    if st+n<len(audio): audio[st:st+n]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*decay)*a
def wrap(x): return (x+np.pi)%(2*np.pi)-np.pi
parts=[]  # [x,y,vx,vy,t0,col,size]
flash=[]; pops={}; done=None; fr=0; nb=0; last_b=-1
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FC={}
    def font(s): return FC.get(s) or FC.setdefault(s,ImageFont.truetype(F,s))
    def text(dr,y,s,size,col,maxw=960):
        while size>20 and dr.textlength(s,font=font(size))>maxw: size-=2
        dr.text((W/2,y),s,font=font(size),anchor="mm",fill=col)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
def burst(t,r,col,n=60,ang=None):
    for _ in range(n):
        a=rng.uniform(0,2*np.pi) if ang is None else ang+rng.normal(0,0.6)
        x,y=CX+r*np.cos(a),CY+r*np.sin(a); sp=rng.uniform(80,380)
        parts.append([x,y,np.cos(a)*sp,np.sin(a)*sp,t,col,rng.uniform(4,9)])
while True:
    t=fr/FPS
    if done is not None and t>done+(4.5 if LONG else 3.0): break
    if t>MAXDUR-1: break
    if done is None:
        for _ in range(SUB):
            h=dt/SUB; vel[1]+=G*h; pos+=vel*h
            ang=th0+om*(t)
            i=int(np.argmax(alive)); r=RADS[i]
            d=pos-[CX,CY]; dist=np.linalg.norm(d)
            if dist>r-BR:
                phi=np.arctan2(d[1],d[0]); ingap=abs(wrap(phi-ang[i]))<GAP/2-np.arcsin(BR/r)*0.6
                if dist>r+BR or (dist>r and not ingap):
                    alive[i]=False; pops[i]=t; burst(t,r,COLS[i],70)
                    left=alive.sum(); tone(t,SCALE[i%5]*2*(1+i//5),0.35,0.3,7); tone(t,SCALE[i%5]*3*(1+i//5),0.25,0.12,9)
                    if left in (10,5): flash.append((t,f"{left} RINGS LEFT!",(255,210,60)))
                    if left==1: flash.append((t,"LAST RING!",(255,90,90)))
                    if left==0:
                        done=t; burst(t,dist,(255,255,255),120)
                        for k,f in enumerate([523,659,784,1047]): tone(t+0.15*k,f,0.45,0.25,5)
                        break
                elif not ingap:
                    nrm=d/dist; pos[:]=[CX,CY]+nrm*(r-BR); vn=vel@nrm
                    if vn>0:
                        vel-=2*vn*nrm; vel+=rng.normal(0,25,2)
                        s=np.linalg.norm(vel); vel*=np.clip(s,VMIN,VMAX)/s
                        if t-last_b>0.06:
                            last_b=t; nb+=1; tone(t,SCALE[nb%5]*(1+(nb//5)%2),0.12,0.16,22)
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        ang=th0+om*(t if done is None else done)
        for i in range(NR):
            if not alive[i]: continue
            r=RADS[i]; g=np.degrees(GAP/2); c=np.degrees(ang[i])
            dr.arc([CX-r,CY-r,CX+r,CY+r],c+g,c+360-g,fill=COLS[i],width=7)
        for p in parts:
            age=t-p[4]
            if 0<=age<1.2:
                x,y=p[0]+p[2]*age,p[1]+p[3]*age+300*age*age; s=p[6]*(1-age/1.2)
                if 150<y<1480: dr.ellipse([x-s,y-s,x+s,y+s],fill=p[5])
        if done is None: dr.ellipse([pos[0]-BR,pos[1]-BR,pos[0]+BR,pos[1]+BR],fill=(255,255,255))
        else:
            text(dr,CY-60,f"{done:.2f} s",150,(255,255,255))
            if LONG: text(dr,CY+80,"JUST IN TIME!" if done<TARGET else "TOO LATE!",90,(120,255,150) if done<TARGET else (255,90,90))
            else: text(dr,CY+80,"Was your guess closer?",60,(255,210,60))
        left=int(alive.sum())
        if LONG:
            text(dr,180,"15 spinning rings.",62,(255,255,255)); text(dr,255,"Can it escape them all before 1:00?",56,(255,210,60))
        else:
            text(dr,180,"15 spinning rings.",62,(255,255,255)); text(dr,255,"Can the ball escape?",62,(255,210,60))
        if done is None: text(dr,370,f"RINGS LEFT: {left}",100,(255,255,255))
        else: text(dr,370,"ESCAPED!",110,(120,255,150))
        fl=[(ft,s,c) for ft,s,c in flash if 0<=t-ft<1.5]
        if fl: text(dr,1395,fl[-1][1],92,fl[-1][2])
        else:
            l1,l2=(("How long will it take?","Guess the time in the comments!") if done is None else ("Did you guess right?","Tell us in the comments!"))
            text(dr,1385,l1,50,(200,200,220)); text(dr,1445,l2,50,(200,200,220))
        tt=t if done is None else done; m,s=divmod(tt,60)
        if LONG:
            col=(120,220,140) if tt<45 else ((255,210,60) if tt<TARGET else (255,90,90))
            text(dr,1505,f"{int(m)}:{s:05.2f}  /  1:00",52,col)
        else:
            text(dr,1505,f"{int(m)}:{s:05.2f}",52,(120,220,140))
        ff.stdin.write(img.tobytes())
    fr+=1
print("seed",SEED,"escape",None if done is None else round(done,2),"dur",round(fr/FPS,1),"pops",[round(pops[k],1) for k in sorted(pops)])
if not DRY:
    ff.stdin.close(); ff.wait()
    a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT])
    os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
