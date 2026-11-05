import csv
import os

import numpy as np

E={'PSG':1953,'Bayern':2045,'Real Madrid':1973,'Liverpool':1931,'Inter':1945,'Man City':2028,'Arsenal':2039,'Barcelona':2017,'Atletico':1888,'Dortmund':1894,'Roma':1852,'Sporting':1882,'Aston Villa':1891,'Porto':1827,'Man United':1888,'Club Brugge':1802,'Real Betis':1811,'PSV':1790,'Feyenoord':1707,'Lille':1784,'Bodo':1786,'Napoli':1832,'Leipzig':1818,'Villarreal':1795,'Fenerbahce':1778,'Shakhtar':1685,'Galatasaray':1805,'Slavia':1756,'Slovan':1555,'Stuttgart':1831,'AEK':1707,'LASK':1644,'Como':1815,'Lens':1822,'Viking':1687,'Sabah':1561}
PRESEASON=E.copy()

# Official UEFA schedule; home team first. Six completed games are fixed below.
raw='''AEK|LASK
Club Brugge|Aston Villa
Dortmund|Villarreal
Porto|Man City
Lille|Real Betis
Real Madrid|Inter
Barcelona|Feyenoord
Stuttgart|Viking
Liverpool|Atletico
PSG|Slovan
Sporting|Galatasaray
Napoli|Arsenal
Fenerbahce|Roma
PSV|Shakhtar
Como|Leipzig
Bayern|Bodo
Man United|Sabah
Slavia|Lens
Lens|Sporting
Sabah|Slavia
Arsenal|Lille
Atletico|Man United
Inter|Club Brugge
Galatasaray|Barcelona
Leipzig|PSV
Viking|Bayern
Villarreal|Napoli
Feyenoord|Como
LASK|Liverpool
Roma|Real Madrid
Aston Villa|Fenerbahce
Shakhtar|AEK
Bodo|Dortmund
Man City|PSG
Real Betis|Porto
Slovan|Stuttgart
Fenerbahce|Slavia
Sabah|Dortmund
Roma|Slovan
Porto|PSV
Liverpool|Villarreal
Man City|AEK
PSG|Barcelona
Napoli|Bodo
Stuttgart|Atletico
Como|Man United
Lille|Galatasaray
Aston Villa|Viking
Club Brugge|Lens
Bayern|Arsenal
Inter|Shakhtar
Real Madrid|Leipzig
Real Betis|Feyenoord
Sporting|LASK
Shakhtar|Sporting
Galatasaray|Stuttgart
Atletico|Bayern
Barcelona|Aston Villa
Feyenoord|Inter
Bodo|Lille
LASK|Slovan
Man United|Roma
Villarreal|PSG
AEK|Real Madrid
Fenerbahce|Liverpool
Dortmund|Real Betis
Porto|Napoli
PSV|Club Brugge
Leipzig|Man City
Lens|Como
Slavia|Arsenal
Viking|Sabah
Bodo|LASK
Galatasaray|Aston Villa
Arsenal|Dortmund
Como|AEK
Feyenoord|Porto
Man City|Napoli
Leipzig|Lens
Real Madrid|PSV
Slovan|Real Betis
Sabah|Barcelona
Slavia|Villarreal
Atletico|Viking
Club Brugge|Liverpool
Inter|Stuttgart
Shakhtar|Fenerbahce
Lille|Bayern
PSG|Roma
Sporting|Man United
Viking|Feyenoord
Villarreal|Sabah
AEK|Galatasaray
Roma|Sporting
Aston Villa|PSG
Barcelona|Man City
Bayern|Slavia
Man United|Leipzig
Napoli|Club Brugge
Real Betis|Como
Slovan|Shakhtar
Arsenal|Real Madrid
Dortmund|Inter
LASK|Fenerbahce
Liverpool|Porto
PSV|Atletico
Lens|Bodo
Stuttgart|Lille
Bodo|Atletico
Galatasaray|Feyenoord
AEK|Roma
Aston Villa|Dortmund
Inter|Liverpool
Porto|Slavia
Lille|Slovan
Real Madrid|LASK
Stuttgart|Club Brugge
Fenerbahce|Villarreal
Sabah|Napoli
Como|PSG
Man United|Bayern
Leipzig|Shakhtar
Lens|Man City
Real Betis|Arsenal
Sporting|Barcelona
Viking|PSV
Arsenal|Sabah
Roma|Lille
Atletico|Fenerbahce
Dortmund|AEK
Club Brugge|Bodo
Bayern|Real Betis
Barcelona|Como
Shakhtar|Real Madrid
Feyenoord|Leipzig
LASK|Porto
Liverpool|Lens
Man City|Sporting
PSG|Galatasaray
PSV|Stuttgart
Slavia|Aston Villa
Napoli|Viking
Villarreal|Man United
Slovan|Inter'''
games=[tuple(x.split('|')) for x in raw.splitlines()]
assert len(games)==144 and len({frozenset(x) for x in games})==144
fixed={("AEK","LASK"):(1,0),("Club Brugge","Aston Villa"):(2,3),("Dortmund","Villarreal"):(3,2),("Porto","Man City"):(0,2),("Lille","Real Betis"):(2,3),("Real Madrid","Inter"):(2,1),
("Barcelona","Feyenoord"):(5,1),("Stuttgart","Viking"):(3,1),("Liverpool","Atletico"):(2,1),("PSG","Slovan"):(6,1),("Sporting","Galatasaray"):(3,1),("Napoli","Arsenal"):(0,1),
("Fenerbahce","Roma"):(1,1),("PSV","Shakhtar"):(1,1),("Como","Leipzig"):(4,1),("Bayern","Bodo"):(5,0),("Man United","Sabah"):(4,0),("Slavia","Lens"):(2,3)}
md1=fixed.copy()

# Matchday 2 official results. Power ratings are refreshed from the MD1 baseline
# with a standard Elo update (K=20, 65-point home advantage) before simulating.
md2={("Lens","Sporting"):(0,2),("Sabah","Slavia"):(2,0),("Arsenal","Lille"):(3,0),("Atletico","Man United"):(2,0),("Inter","Club Brugge"):(3,4),("Galatasaray","Barcelona"):(1,4),("Leipzig","PSV"):(1,0),("Viking","Bayern"):(3,3),("Villarreal","Napoli"):(3,1),
("Feyenoord","Como"):(3,2),("LASK","Liverpool"):(3,6),("Roma","Real Madrid"):(3,4),("Aston Villa","Fenerbahce"):(6,0),("Shakhtar","AEK"):(3,1),("Bodo","Dortmund"):(1,0),("Man City","PSG"):(2,4),("Real Betis","Porto"):(3,2),("Slovan","Stuttgart"):(0,3)}
for (h,a),(hg,ag) in md2.items():
 expected=1/(1+10**(-(E[h]+65-E[a])/400))
 actual=1.0 if hg>ag else (0.5 if hg==ag else 0.0)
 delta=20*(actual-expected)
 E[h]+=delta; E[a]-=delta
fixed.update(md2)

# Matchday 3 official results (20-21 October 2026). Refresh the ratings again
# before simulating the five remaining league-phase matchdays.
md3={("Fenerbahce","Slavia"):(2,2),("Sabah","Dortmund"):(1,2),("Roma","Slovan"):(4,0),("Porto","PSV"):(0,1),("Liverpool","Villarreal"):(4,3),("Man City","AEK"):(5,1),("PSG","Barcelona"):(4,2),("Napoli","Bodo"):(4,3),("Stuttgart","Atletico"):(1,1),
("Como","Man United"):(4,1),("Lille","Galatasaray"):(2,4),("Aston Villa","Viking"):(3,1),("Club Brugge","Lens"):(3,0),("Bayern","Arsenal"):(2,2),("Inter","Shakhtar"):(1,0),("Real Madrid","Leipzig"):(4,1),("Real Betis","Feyenoord"):(1,0),("Sporting","LASK"):(2,3)}
for (h,a),(hg,ag) in md3.items():
 expected=1/(1+10**(-(E[h]+65-E[a])/400))
 actual=1.0 if hg>ag else (0.5 if hg==ag else 0.0)
 delta=20*(actual-expected)
 E[h]+=delta; E[a]-=delta
fixed.update(md3)

# Matchday 4 official results (3-4 November 2026). Refresh the ratings again
# before simulating the four remaining league-phase matchdays.
md4={("Shakhtar","Sporting"):(0,1),("Galatasaray","Stuttgart"):(2,0),("Atletico","Bayern"):(0,2),("Barcelona","Aston Villa"):(3,0),("Feyenoord","Inter"):(0,3),("Bodo","Lille"):(0,0),("LASK","Slovan"):(4,0),("Man United","Roma"):(3,2),("Villarreal","PSG"):(0,6),
("AEK","Real Madrid"):(2,3),("Fenerbahce","Liverpool"):(3,2),("Dortmund","Real Betis"):(2,1),("Porto","Napoli"):(4,1),("PSV","Club Brugge"):(1,2),("Leipzig","Man City"):(2,3),("Lens","Como"):(1,9),("Slavia","Arsenal"):(1,2),("Viking","Sabah"):(4,1)}
for (h,a),(hg,ag) in md4.items():
 expected=1/(1+10**(-(E[h]+65-E[a])/400))
 actual=1.0 if hg>ag else (0.5 if hg==ag else 0.0)
 delta=20*(actual-expected)
 E[h]+=delta; E[a]-=delta
fixed.update(md4)

# Form-aware rating rebuild. Start from the pre-tournament rating and replay all
# four matchdays in order. Recent rounds get moderately larger K values and the
# update is scaled by margin of victory (capped to prevent one result dominating).
E=PRESEASON.copy()
for round_results,k in zip((md1,md2,md3,md4),(20,24,30,36)):
 for (h,a),(hg,ag) in round_results.items():
  expected=1/(1+10**(-(E[h]+65-E[a])/400))
  actual=1.0 if hg>ag else (0.5 if hg==ag else 0.0)
  margin=min(2.35,1+0.55*np.log1p(abs(hg-ag))) if hg!=ag else 1.0
  delta=k*margin*(actual-expected)
  E[h]+=delta; E[a]-=delta

# Attack/defence form from the four UCL games, shrunk toward the tournament
# average by six prior-match equivalents so that four games cannot dominate.
gf_obs={t:0 for t in E}; ga_obs={t:0 for t in E}
for (h,a),(hg,ag) in fixed.items():
 gf_obs[h]+=hg; ga_obs[h]+=ag; gf_obs[a]+=ag; ga_obs[a]+=hg
observed_total=sum(gf_obs.values())/len(fixed)
base_total=0.55*3.05+0.45*observed_total
mu=observed_total/2; prior_matches=6
attack={t:((gf_obs[t]+prior_matches*mu)/(4+prior_matches))/mu for t in E}
defence={t:((ga_obs[t]+prior_matches*mu)/(4+prior_matches))/mu for t in E}
for t in E:
 attack[t]=float(np.clip(attack[t],0.72,1.45))
 defence[t]=float(np.clip(defence[t],0.72,1.45))
# Exact five-season UEFA club coefficients available at the start of 2026/27
# (seasons 2021/22--2025/26). For clubs below their association floor, UEFA's
# effective coefficient is the higher country-part value. The coefficient is
# converted conservatively to an Elo-like history rating; it is only 20% of the
# final blend, so European pedigree informs rather than overwhelms current form.
COEFF5={'Bayern':147.500,'Real Madrid':144.500,'PSG':132.000,'Liverpool':130.000,
'Inter':127.000,'Man City':125.500,'Arsenal':119.000,'Barcelona':113.250,
'Atletico':104.750,'Dortmund':100.750,'Roma':97.750,'Sporting':84.000,
'Aston Villa':83.000,'Porto':80.750,'Man United':76.500,'Club Brugge':75.250,
'Real Betis':74.500,'PSV':71.250,'Feyenoord':71.000,'Lille':68.750,
'Bodo':64.000,'Napoli':63.000,'Leipzig':61.000,'Villarreal':59.000,
'Fenerbahce':57.750,'Shakhtar':56.250,'Galatasaray':53.500,'Slavia':44.000,
'Slovan':36.000,'Stuttgart':27.500,'AEK':24.000,'LASK':21.000,
'Como':19.989,'Lens':16.699,'Viking':8.247,'Sabah':6.000}
assert set(COEFF5)==set(E)
HISTORY={t:float(np.clip(1700+2.5*COEFF5[t],1660,2080)) for t in E}

# Separate current-form rating from long-run strength, then blend them. Recent
# UCL form gets 50%, preseason team strength 30%, and five-season Europe 20%.
FORM={t:PRESEASON[t]+1.60*(E[t]-PRESEASON[t])+85*np.log(attack[t]/defence[t]) for t in E}
POWER={t:0.30*PRESEASON[t]+0.20*HISTORY[t]+0.50*FORM[t] for t in E}
ATT=np.array([attack[t] for t in E]); DEF=np.array([defence[t] for t in E])

T=list(E); ix={t:i for i,t in enumerate(T)}
N=int(os.getenv('CHAMPIONS_PATH_SIMS','300000'))
bs=min(10_000,N)
rng=np.random.default_rng(int(os.getenv('CHAMPIONS_PATH_SEED','20261106'))); out=np.zeros((36,3),int); stages=np.zeros((36,5),int); ps=np.zeros(36); rs=np.zeros(36)
for z in range(0,N,bs):
 n=min(bs,N-z); p=np.zeros((n,36),np.int16); gd=np.zeros_like(p); gf=np.zeros_like(p)
 # Parameter uncertainty: one persistent team-strength and attack/defence draw
 # per tournament simulation, not just match-result randomness.
 sim_power=np.array([POWER[t] for t in T])[None,:]+rng.normal(0,30,(n,36))
 sim_att=ATT[None,:]*np.exp(rng.normal(0,0.08,(n,36)))
 sim_def=DEF[None,:]*np.exp(rng.normal(0,0.08,(n,36)))
 rows=np.arange(n)

 def sample_match(home,away,home_adv=65,factor=1.0):
  gap=sim_power[rows,home]+home_adv-sim_power[rows,away]
  ratio=10**(gap/400)
  lh=base_total*ratio/(1+ratio)*(sim_att[rows,home]*sim_def[rows,away])**0.32*factor
  la=base_total/(1+ratio)*(sim_att[rows,away]*sim_def[rows,home])**0.32*factor
  lh=np.clip(lh,0.05,4.8); la=np.clip(la,0.05,4.8)
  # A small shared component allows correlated scorelines versus independent
  # Poisson goals, while retaining the fitted marginal means.
  shared_mean=np.minimum(0.10*factor,np.minimum(lh,la)*0.35)
  shared=rng.poisson(shared_mean)
  return rng.poisson(np.maximum(0.01,lh-shared_mean))+shared, rng.poisson(np.maximum(0.01,la-shared_mean))+shared

 for h,a in games:
  if (h,a) in fixed: hg=np.full(n,fixed[h,a][0]); ag=np.full(n,fixed[h,a][1])
  else:
   hg,ag=sample_match(ix[h],ix[a])
  hi,ai=ix[h],ix[a]; p[:,hi]+=np.where(hg>ag,3,np.where(hg==ag,1,0)); p[:,ai]+=np.where(ag>hg,3,np.where(hg==ag,1,0)); gd[:,hi]+=hg-ag;gd[:,ai]+=ag-hg;gf[:,hi]+=hg;gf[:,ai]+=ag
 order=np.empty((n,36),int); jit=rng.random((n,36))*1e-6
 for j in range(n): order[j]=np.lexsort((jit[j],gf[j],gd[j],p[j]))[::-1]
 rank=np.empty_like(order); rank[np.arange(n)[:,None],order]=np.arange(1,37)
 out[:,0]+=(rank<=8).sum(0);out[:,1]+=((rank>8)&(rank<=24)).sum(0);out[:,2]+=(rank>24).sum(0);ps+=p.sum(0);rs+=rank.sum(0)
 # Two-legged knockout tie: lower seed hosts the first leg, higher seed the
 # second. Aggregate ties go to extra time and then a near-even shoot-out.
 def two_leg(high,low):
  l1h,l1a=sample_match(low,high)
  l2h,l2a=sample_match(high,low)
  hs=l1a+l2h; ls=l1h+l2a
  winner=np.where(hs>ls,high,low); tied=hs==ls
  if np.any(tied):
   eh,el=sample_match(high,low,home_adv=35,factor=1/3)
   winner=np.where(tied & (eh>el),high,winner)
   winner=np.where(tied & (el>eh),low,winner)
   still=tied & (eh==el)
   pen=1/(1+10**(-(sim_power[rows,high]-sim_power[rows,low])/1200))
   draw=rng.random(n)
   winner=np.where(still & (draw<pen),high,winner)
   winner=np.where(still & (draw>=pen),low,winner)
  return winner

 def single_leg(x,y):
  xg,yg=sample_match(x,y,home_adv=0)
  winner=np.where(xg>yg,x,y); tied=xg==yg
  if np.any(tied):
   ex,ey=sample_match(x,y,home_adv=0,factor=1/3)
   winner=np.where(tied & (ex>ey),x,winner)
   winner=np.where(tied & (ey>ex),y,winner)
   still=tied & (ex==ey)
   pen=1/(1+10**(-(sim_power[rows,x]-sim_power[rows,y])/1200))
   draw=rng.random(n)
   winner=np.where(still & (draw<pen),x,winner)
   winner=np.where(still & (draw>=pen),y,winner)
  return winner

 # UEFA paired-position draw: 9/10 vs 23/24, 11/12 vs 21/22, etc.
 seeded=order[:,8:16]; unseeded=order[:,16:24]
 po=np.empty((n,8),int)
 for b in range(4):
  s0,s1=seeded[:,2*b],seeded[:,2*b+1]
  u0,u1=unseeded[:,7-2*b],unseeded[:,6-2*b]
  swap=rng.random(n)<0.5
  po[:,2*b]=two_leg(s0,np.where(swap,u0,u1))
  po[:,2*b+1]=two_leg(s1,np.where(swap,u1,u0))

 # Top-eight paired-position draw into the round of 16.
 r16=np.empty((n,16),int)
 for b in range(4):
  t0,t1=order[:,2*b],order[:,2*b+1]
  p0,p1=po[:,2*(3-b)],po[:,2*(3-b)+1]
  swap=rng.random(n)<0.5
  r16[:,4*b]=t0; r16[:,4*b+1]=np.where(swap,p0,p1)
  r16[:,4*b+2]=t1; r16[:,4*b+3]=np.where(swap,p1,p0)
 for k in range(16): stages[:,0]+=np.bincount(r16[:,k],minlength=36)
 r16w=np.empty((n,8),int)
 for k in range(8): r16w[:,k]=two_leg(r16[:,2*k],r16[:,2*k+1])
 for k in range(8): stages[:,1]+=np.bincount(r16w[:,k],minlength=36)
 qfw=np.empty((n,4),int)
 for k in range(4): qfw[:,k]=two_leg(r16w[:,2*k],r16w[:,2*k+1])
 for k in range(4): stages[:,2]+=np.bincount(qfw[:,k],minlength=36)
 sfw=np.empty((n,2),int)
 for k in range(2): sfw[:,k]=two_leg(qfw[:,2*k],qfw[:,2*k+1])
 for k in range(2): stages[:,3]+=np.bincount(sfw[:,k],minlength=36)
 champ=single_leg(sfw[:,0],sfw[:,1]); stages[:,4]+=np.bincount(champ,minlength=36)
rows=[]
for i in np.argsort(-stages[:,4]):
 rows.append({
  'team':T[i], 'expected_points':round(ps[i]/N,2),
  'top_8_pct':round(out[i,0]/N*100,1), 'rank_9_24_pct':round(out[i,1]/N*100,1),
  'eliminated_pct':round(out[i,2]/N*100,1), 'round_of_16_pct':round(stages[i,0]/N*100,1),
  'quarterfinal_pct':round(stages[i,1]/N*100,1), 'semifinal_pct':round(stages[i,2]/N*100,1),
  'final_pct':round(stages[i,3]/N*100,1), 'champion_pct':round(stages[i,4]/N*100,1)})

output_path=os.getenv('CHAMPIONS_PATH_OUTPUT')
if output_path:
 with open(output_path,'w',newline='',encoding='utf-8') as output_file:
  writer=csv.DictWriter(output_file,fieldnames=rows[0].keys())
  writer.writeheader(); writer.writerows(rows)

for row in rows:
 print('|'.join(str(row[key]) for key in row))
