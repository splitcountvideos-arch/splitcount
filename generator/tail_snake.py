"""Snake ball: one ball bounces (with gravity) in a circle and leaves a tail behind it.
The tail grows with every bounce. If the ball touches its own tail -> GAME OVER. How long does it survive?
Usage: GROW=40 L0=150 python3 generator/tail_snake.py OUT.mp4 SEED [--long] [--dry]"""
import numpy as np, subprocess, wave, sys, os, colorsys
OUT=sys.argv[1]; SEED=int(sys.argv[2]); LONG="--long" in sys.argv; DRY="--dry" in sys.argv
W,H,FPS=1080,1920,30; CX,CY,R=W/2,900,400; dt=1/FPS; SUB=8; MAXDUR=100; BR=14.0; TW=10
G=float(os.environ.get('G','900')); GROW=float(os.environ.get('GROW','40')); L0=float(os.environ.get('L0','150'))
VMIN,VMAX=float(os.environ.get('VMIN','550')),float(os.environ.get('VMAX','950')); TARGET=60.0
EXCL=float(os.environ.get("EXCL","90")); KILL=float(os.environ.get("KILL","8"))
rng=np.random.default_rng(SEED)
a0=rng.uniform(0,2*np.pi); pos=np.array([CX,CY-150.0]); vel=np.array([np.cos(a0),np.sin(a0)])*650
NMAX=SUB*FPS*MAXDUR; TP=np.zeros((NMAX,2)); TS=np.zeros(NMAX); n=0; s_now=0.0
TP[0]=pos; n=1
sr=44100; audio=np.zeros(sr*(MAXDUR+6))
SCALE=[261.6,293.7,329.6,392.0,440.0]
def tone(t,f,L,a,decay):
    st=int(t*sr); m=int(L*sr); tt=np.arange(m)/sr
    if st+m<len(audio): audio[st:st+m]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*decay)*a
def crash(t):
    st=int(t*sr); m=int(0.8*sr); tt=np.arange(m)/sr
    audio[st:st+m]+=rng.normal(0,1,m)*np.exp(-tt*6)*0.35+np.sin(2*np.pi*(110-60*tt)*tt)*np.exp(-tt*3)*0.4
parts=[]; flash=[]; done=None; fr=0; nb=0; last_b=-1; near=0; last_near=-9
def L(): return L0+GROW*nb
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FC={}
    def font(s): return FC.get(s) or FC.setdefault(s,ImageFont.truetype(F,s))
    def text(dr,y,s,size,col,maxw=960,bg=False):
        while size>20 and dr.textlength(s,font=font(size))>maxw: size-=2
        if bg:
            w2=dr.textlength(s,font=font(size))/2+30; dr.rounded_rectangle([W/2-w2,y-size*0.75,W/2+w2,y+size*0.75],radius=24,fill=(12,12,20),outline=(80,80,100),width=3)
        dr.text((W/2,y),s,font=font(size),anchor="mm",fill=col)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
def burst(t,x,y,col,k=90):
    for _ in range(k):
        a=rng.uniform(0,2*np.pi); sp=rng.uniform(80,420)
        parts.append([x,y,np.cos(a)*sp,np.sin(a)*sp,t,col,rng.uniform(4,10)])
def segdist(p,A,B):
    AB=B-A; l2=(AB*AB).sum(1)+1e-9; u=np.clip(((p-A)*AB).sum(1)/l2,0,1)
    return np.linalg.norm(A+AB*u[:,None]-p,axis=1)
MS=[15,30,45] if LONG else []
hit_at=None
while True:
    t=fr/FPS
    if done is not None and t>done+(4.5 if LONG else 3.2): break
    if t>MAXDUR-1: break
    if done is None:
        for ms in MS:
            if abs(t-ms)<dt/2: flash.append((t,f"{ms} SECONDS!",(255,210,60))); tone(t,880,0.4,0.2,5)
        for _ in range(SUB):
            h=dt/SUB; vel[1]+=G*h; step=vel*h; pos+=step; s_now+=np.linalg.norm(step)
            d=pos-[CX,CY]; dist=np.linalg.norm(d)
            if dist>R-BR:
                nrm=d/dist; pos[:]=[CX,CY]+nrm*(R-BR); vn=vel@nrm
                if vn>0:
                    vel-=2*vn*nrm; vel+=rng.normal(0,30,2)
                    sp=np.linalg.norm(vel); vel*=np.clip(sp,VMIN,VMAX)/sp
                    if t-last_b>0.08:
                        last_b=t; nb+=1; tone(t,SCALE[nb%5]*(1+min(3,nb//15)),0.12,0.16,22)
                        if nb in (10,25,50): flash.append((t,f"{nb} BOUNCES!",(120,220,255)))
            TP[n]=pos; TS[n]=s_now; n+=1
            # collision with own tail
            lo=np.searchsorted(TS[:n],s_now-L()); hi=np.searchsorted(TS[:n],s_now-EXCL)
            if hi-lo>=2:
                dd=segdist(pos,TP[lo:hi-1],TP[lo+1:hi]); m=dd.min()
                if m<KILL:
                    done=t; hit_at=pos.copy(); burst(t,pos[0],pos[1],(255,90,90),110); burst(t,pos[0],pos[1],(255,255,255),40)
                    crash(t); flash.append((t,"GAME OVER",(255,90,90))); break
                if m<BR+22 and t-last_near>1.0 and t>1:
                    last_near=t; near+=1; flash.append((t,"CLOSE CALL!",(255,160,60))); tone(t,1320,0.15,0.12,15)
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(230,230,240),width=6)
        lo=np.searchsorted(TS[:n],s_now-L()); idx=list(range(lo,n,2))+[n-1]
        pts=TP[idx]; k=len(pts)
        for j in range(k-1):
            fcol=j/max(1,k-1); c=colorsys.hsv_to_rgb((0.55+0.45*fcol+ t*0.02)%1,0.8,0.4+0.6*fcol)
            dr.line([tuple(pts[j]),tuple(pts[j+1])],fill=tuple(int(x*255) for x in c),width=TW)
        for p in parts:
            age=t-p[4]
            if 0<=age<1.3:
                x,y=p[0]+p[2]*age,p[1]+p[3]*age+300*age*age; s=p[6]*(1-age/1.3)
                if 150<y<1480: dr.ellipse([x-s,y-s,x+s,y+s],fill=p[5])
        hx,hy=pos
        if done is None or (t-done)%0.4<0.2:
            dr.ellipse([hx-BR,hy-BR,hx+BR,hy+BR],fill=(255,255,255) if done is None else (255,90,90))
        text(dr,180,"Touch its own tail = GAME OVER",58,(255,255,255))
        text(dr,255,"Can it survive 1:00?" if LONG else "The tail grows on every bounce.",56,(255,210,60))
        tt=t if done is None else done
        if done is None: text(dr,370,f"TAIL: {int(L())} px",90,(255,255,255))
        else: text(dr,370,f"SURVIVED {tt:.2f} s",100,(255,90,90) if not LONG or tt<TARGET else (120,255,150))
        if done is not None and t-done>0.8:
            if LONG: text(dr,CY,"IT MADE IT!" if tt>=TARGET else "SO CLOSE!",110,(120,255,150) if tt>=TARGET else (255,210,60),bg=True)
            else: text(dr,CY,"Was your guess right?",64,(255,210,60),bg=True)
        fl=[(ft,s,c) for ft,s,c in flash if 0<=t-ft<1.3]
        if fl: text(dr,1395,fl[-1][1],92,fl[-1][2])
        else:
            l1,l2=(("How long will it survive?","Guess in the comments!") if done is None else ("Did you guess right?","Tell us in the comments!"))
            text(dr,1385,l1,50,(200,200,220)); text(dr,1445,l2,50,(200,200,220))
        m_,s_=divmod(tt,60)
        if LONG:
            col=(120,220,140) if tt<45 else ((255,210,60) if tt<TARGET else (120,255,150))
            text(dr,1505,f"{int(m_)}:{s_:05.2f}  /  1:00",52,col)
        else: text(dr,1505,f"{int(m_)}:{s_:05.2f}",52,(120,220,140))
        ff.stdin.write(img.tobytes())
    fr+=1
print("seed",SEED,"dead",None if done is None else round(done,2),"dur",round(fr/FPS,1),"bounces",nb,"tail",int(L()),"near",near)
if not DRY:
    ff.stdin.close(); ff.wait()
    a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT])
    os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
