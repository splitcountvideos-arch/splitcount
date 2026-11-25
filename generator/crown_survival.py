"""Crown survival (comment idea 'MVP crown'): N balls bounce in a circle, a red lava arc on the
wall grows and spins; touching it pops a ball. One ball wears the crown - is it the last one standing?
Usage: python3 crown_survival.py OUT.mp4 SEED N GROW_SECONDS [--long] [--dry]"""
import numpy as np, subprocess, wave, colorsys, sys, os
OUT=sys.argv[1]; SEED=int(sys.argv[2]); N=int(sys.argv[3]); TG=float(sys.argv[4])
LONG="--long" in sys.argv; DRY="--dry" in sys.argv
BASE=float(os.environ.get("BASE","0.04")); W,H,FPS=1080,1920,30; CX,CY,R=W/2,900,400; BR=13.0; MAXDUR=100; dt=1/FPS; sub=4
rng=np.random.default_rng(SEED)
ang=rng.uniform(0,2*np.pi,N); rad=np.sqrt(rng.uniform(0,1,N))*(R-60)
pos=np.stack([CX+np.cos(ang)*rad,CY+np.sin(ang)*rad],1)
vel=rng.normal(0,220,(N,2)); alive=np.ones(N,bool); hue=rng.uniform(0,1,N)
CROWN=int(np.argmin(np.linalg.norm(pos-[CX,CY],axis=1))); hue[CROWN]=0.13
g=np.array([0,520.0]); place=np.zeros(N,int); arc_w=0.0; arc_c=-np.pi/2; spin=0.9
parts=[]; events=[]; done=None; fr=0; crown_out=None
MIL={N//2:"HALF GONE",20:"TOP 20",10:"TOP 10",3:"FINAL 3",2:"FINAL DUEL"}; shown={}
sr=44100; audio=np.zeros(sr*MAXDUR)
def tone(t,f,L,amp,dec):
    st=int(t*sr); a=np.arange(int(L*sr))/sr
    if st+len(a)<len(audio): audio[st:st+len(a)]+=np.sin(2*np.pi*f*a)*np.exp(-a*dec)*amp
if not DRY:
    from PIL import Image, ImageDraw, ImageFont
    F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fbig=ImageFont.truetype(F,140); f2=ImageFont.truetype(F,60); f3=ImageFont.truetype(F,48); f4=ImageFont.truetype(F,80); f5=ImageFont.truetype(F,36)
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","28","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
def crown(dr,x,y,s):
    dr.polygon([(x-s,y),(x+s,y),(x+s,y-s),(x+s/2,y-s/2),(x,y-s*1.25),(x-s/2,y-s/2),(x-s,y-s)],fill=(255,215,0))
while True:
    t=fr/FPS; n=int(alive.sum())
    if done is not None and t>done+4.0: break
    if t>MAXDUR-1: break
    if done is None:
        arc_w=(BASE+(0.85-BASE)*min(1.0,t/TG)**2)*2*np.pi
        spin=0.9+1.2*min(1,t/TG); arc_c+=spin*dt
    for _ in range(sub):
        if done is not None: break
        h=dt/sub; idx=np.where(alive)[0]
        vel[idx]+=g*h; pos[idx]+=vel[idx]*h
        # ball-ball collisions
        p=pos[idx]; d=p[:,None,:]-p[None,:,:]; dist=np.linalg.norm(d,axis=2)+np.eye(len(idx))*1e9
        ii,jj=np.where(np.triu(dist<2*BR,1))
        for a,b in zip(ii,jj):
            A,B=idx[a],idx[b]; nv=(pos[A]-pos[B]); L=np.linalg.norm(nv)+1e-9; nv/=L
            rv=((vel[A]-vel[B])*nv).sum()
            if rv<0: vel[A]-=rv*nv; vel[B]+=rv*nv
            ov=2*BR-L; pos[A]+=nv*ov/2; pos[B]-=nv*ov/2
        d=pos[idx]-[CX,CY]; dist=np.linalg.norm(d,axis=1); out=dist>R-BR
        for k in np.where(out)[0]:
            i=idx[k]; nrm=d[k]/dist[k]; pos[i]=[CX,CY]+nrm*(R-BR)
            vn=(vel[i]*nrm).sum(); vel[i]-=2*vn*nrm
            if np.linalg.norm(vel[i])<380: vel[i]*=1.04  # keep energy
            a=np.arctan2(nrm[1],nrm[0]); diff=(a-arc_c+np.pi)%(2*np.pi)-np.pi
            if abs(diff)<arc_w/2 and alive.sum()>1:
                alive[i]=False; place[i]=int(alive.sum())+1
                if i==CROWN: crown_out=(t,place[i])
                col=(255,215,0) if i==CROWN else tuple(int(x*255) for x in colorsys.hsv_to_rgb(hue[i],0.85,1))
                for _ in range(14):
                    th=rng.uniform(0,2*np.pi); sp=rng.uniform(80,320)
                    parts.append([pos[i][0],pos[i][1],np.cos(th)*sp-nrm[0]*150,np.sin(th)*sp-nrm[1]*150,0.6,col])
                tone(t,180+rng.uniform(-20,20),0.12,0.25 if i!=CROWN else 0.5,30)
            else: tone(t,520+(N-alive.sum())*6,0.03,0.04,120)
    n=int(alive.sum())
    for m,txt in MIL.items():
        if n<=m and m not in shown and N>m: shown[m]=t; tone(t,880,0.3,0.15,8); tone(t,1320,0.3,0.1,8)
    if done is None and n==1:
        done=t; w=int(np.where(alive)[0][0]); place[w]=1
        for k,f in enumerate([523,659,784,1047]): tone(t+k*0.12,f,0.5,0.2,5)
    for q in parts: q[0]+=q[2]*dt; q[1]+=q[3]*dt; q[3]+=600*dt; q[4]-=dt
    parts=[q for q in parts if q[4]>0]
    if not DRY:
        img=Image.new("RGB",(W,H),(12,12,20)); dr=ImageDraw.Draw(img)
        dr.ellipse([CX-R-6,CY-R-6,CX+R+6,CY+R+6],outline=(230,230,250),width=6)
        if arc_w>0.01:
            a0=np.degrees(arc_c-arc_w/2); a1=np.degrees(arc_c+arc_w/2)
            dr.arc([CX-R-10,CY-R-10,CX+R+10,CY+R+10],a0,a1,fill=(255,60,40),width=16)
        for q in parts:
            s=4*q[4]/0.6+1; dr.ellipse([q[0]-s,q[1]-s,q[0]+s,q[1]+s],fill=q[5])
        for i in np.where(alive)[0]:
            if i==CROWN: continue
            col=tuple(int(x*255) for x in colorsys.hsv_to_rgb(hue[i],0.8,1)); x,y=pos[i]
            dr.ellipse([x-BR,y-BR,x+BR,y+BR],fill=col)
        if alive[CROWN]:
            x,y=pos[CROWN]; dr.ellipse([x-BR-4,y-BR-4,x+BR+4,y+BR+4],fill=(255,215,0),outline=(255,255,255),width=3)
            crown(dr,x,y-BR-6,16)
        dr.text((W/2,170),"CAN THE CROWN SURVIVE?",font=f2,anchor="mm",fill=(255,215,0))
        dr.text((W/2,240),"Touch the red = you're out",font=f5,anchor="mm",fill=(255,120,100))
        dr.text((W/2,370),f"{n}",font=fbig,anchor="mm",fill=(255,255,255))
        dr.text((W/2,455),"balls left",font=f5,anchor="mm",fill=(170,170,190))
        if shown and done is None:
            m=min(shown); ts=shown[m]
            if t-ts<1.6: dr.text((W/2,1360),MIL[m],font=f4,anchor="mm",fill=(255,255,255))
        if done is None:
            st="CROWN: ALIVE" if alive[CROWN] else f"CROWN OUT: #{crown_out[1]}"
            dr.text((W/2,1460),st,font=f3,anchor="mm",fill=(255,215,0) if alive[CROWN] else (255,90,80))
        else:
            if alive[CROWN]: dr.text((W/2,1370),"THE CROWN SURVIVED!",font=f2,anchor="mm",fill=(255,215,0))
            else: dr.text((W/2,1370),f"Crown finished #{crown_out[1]}",font=f2,anchor="mm",fill=(255,90,80))
            dr.text((W/2,1450),f"{done:.1f} s",font=f3,anchor="mm",fill=(120,220,140))
        ff.stdin.write(img.tobytes())
    fr+=1
print("seed",SEED,"done",round(done or -1,1),"dur",round(fr/FPS,1),"crown_place",place[CROWN],"crown_out",crown_out,"milestones",{k:round(v,1) for k,v in shown.items()})
if not DRY:
    ff.stdin.close(); ff.wait(); a=np.clip(audio[:int(fr/FPS*sr)],-1,1)
    with wave.open(OUT+".wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32000).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",OUT+".v.mp4","-i",OUT+".wav","-c:v","copy","-c:a","aac","-shortest",OUT]); os.remove(OUT+".v.mp4"); os.remove(OUT+".wav")
