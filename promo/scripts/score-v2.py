"""Original procedural score/SFX. No recordings, samples, model, paid service or voice."""
from pathlib import Path
import math,wave,struct,random,json
root=Path(__file__).resolve().parents[1]
sr=48000

def score(name,duration,boundaries):
 n=int(sr*duration);from array import array
 l=array('f',[0])*n;r=array('f',[0])*n
 # Understated A-minor bed, increasing in presence after the opening.
 for j in range(n):
  t=j/sr;fade=min(1,t/1.5,(duration-t)/1.5);energy=.25 if t<5 else .65
  v=(math.sin(2*math.pi*110*t)+.3*math.sin(2*math.pi*164.8138*t)+.24*math.sin(2*math.pi*220*t))*.035*fade*energy
  l[j]=v;r[j]=v*.94
 def tone(start,freq,amp,length=.7,pan=0):
  a=int(start*sr);count=min(int(length*sr),n-a)
  for k in range(max(0,count)):
   t=k/sr;en=min(1,t/.008)*math.exp(-t*7)*min(1,(length-t)/.05)
   v=(math.sin(2*math.pi*freq*t)+.13*math.sin(2*math.pi*freq*2*t))*amp*en
   l[a+k]+=v*(1-pan*.3);r[a+k]+=v*(1+pan*.3)
 notes=[220,261.6256,329.6276,293.6648,220,391.9954,329.6276,261.6256]
 for beat in range(int((duration-5)/.375)):
  t=5+beat*.375
  if t>duration-2:break
  tone(t,notes[beat%8],.065 if beat%2==0 else .04,.65,(-1 if beat%2 else 1)*.5)
  if beat%2==0:tone(t,55,.11,.4)
  if beat%4==2:tone(t,880,.018,.18,.4)
 # Original filtered-noise transition brush plus low rounded impact.
 rng=random.Random(1948)
 for b in boundaries:
  tone(max(.01,b),73.416,.13,.7)
  begin=max(0,int((b-.25)*sr));end=min(n,begin+int(.62*sr));prev=0
  for j in range(begin,end):
   x=(j-begin)/(end-begin);z=rng.uniform(-1,1);prev=prev*.88+z*.12
   v=prev*math.sin(math.pi*x)**2*.09;l[j]+=v;r[j]+=v*.85
 # UI selections / sentiment arc punctuation. Not recorded application audio.
 for t in ([23.7,25.5,27.5,30.5,30.9,31.3] if duration>40 else [7,9.5,12.5,13,13.5]):tone(t,659.255,.045,.22,.3)
 for freq in [220,261.6256,329.6276,440]:tone(duration-4,freq,.06,3)
 peak=max(max(map(abs,l)),max(map(abs,r)));gain=.40/max(.01,peak)
 data=bytearray(n*4)
 for j in range(n):
  fade=min(1,(n-j)/(sr*.65));struct.pack_into('<hh',data,j*4,int(l[j]*gain*fade*32767),int(r[j]*gain*fade*32767))
 dest=root/'public/v2'/name
 with wave.open(str(dest),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(data)
 return {'file':name,'duration':duration,'sampleRate':sr,'channels':2,'peakDbFS':round(20*math.log10(.4),2),'source':'Original deterministic synthesis; transition and UI effects authored by code'}
results=[score('score-youtube.wav',70,[0,5,12,20,30,42,50,59,65]),score('score-reel.wav',30,[0,2,6,12,21,26])]
(root/'docs/audio-source.json').write_text(json.dumps(results,indent=2))
print('Original V2 score and effects rendered, no external audio assets.')
