import sys, json, math, numpy as np, pandas as pd
sys.path.insert(0,'/home/claude/dk-feeds/system/dksys/sim'); import sim
G='/home/claude/dk-feeds/dispatch_out/scoreboard/graded.csv'
g=pd.read_csv(G).dropna(subset=['actual']); g['p']=g[['gotham','sleeper','yahoo']].mean(axis=1); g=g[g.p>0]
SIG={'QB':8.0,'RB':8.0,'WR':8.5,'TE':6.5}; RHO=.14
def normal_win(pa,pb,posa,posb):
    def sv(pos): s=[SIG[p] for p in pos]; ss=sum(x*x for x in s); st=sum(s); return ss+RHO*(st*st-ss)
    v=sv(posa)+sv(posb); return .5*(1+math.erf((sum(pa)-sum(pb))/math.sqrt(2*v)))
def sim_win(noise,pa,pb,posa,posb,rng,n=4000):
    A=sim.draw(noise,rng,[(m,p,'X%d'%i,'') for i,(m,p) in enumerate(zip(pa,posa))],n).sum(1)
    B=sim.draw(noise,rng,[(m,p,'Y%d'%i,'') for i,(m,p) in enumerate(zip(pb,posb))],n).sum(1)
    return float(((A>B)+.5*(A==B)).mean())
def brier(p,y): p=np.array(p); y=np.array(y); return float(((p-y)**2).mean())
def calib(p,y):
    p=np.array(p); y=np.array(y); out=[]
    for lo,hi in [(0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.01)]:
        m=(p>=lo)&(p<hi)
        if m.sum(): out.append(f"{lo:.0%}-{min(hi,1):.0%}: said {p[m].mean():.0%}, won {y[m].mean():.0%} (n={m.sum()})")
    return out
rng=np.random.default_rng(3)
# A) synthetic matchups: fit misses on weeks 2-5, test on weeks 6-7 (and the reverse)
res={}
for fitw,testw in [((2,3,4,5),(6,7)),((5,6,7),(2,3,4))]:
    noise=sim.Noise(G,weeks=fitw); T=g[g.week.isin(testw)]
    PS,PN,Y=[],[],[]
    for _ in range(1500):
        w=rng.choice(sorted(T.week.unique())); d=T[T.week==w]
        need={'QB':1,'RB':2,'WR':3,'TE':1}; side=[]
        okk=True
        for s_ in range(2):
            rows=[]
            for pos,k in need.items():
                c=d[d.pos==pos]
                if len(c)<2*k: okk=False; break
                rows.append(c.sample(k,random_state=int(rng.integers(1e9))))
            if not okk: break
            side.append(pd.concat(rows))
        if not okk: continue
        a,b=side; pa,pb=list(a.p),list(b.p); qa,qb=list(a.pos),list(b.pos)
        y=float(a.actual.sum()>b.actual.sum())
        PS.append(sim_win(noise,pa,pb,qa,qb,rng,1500)); PN.append(normal_win(pa,pb,qa,qb)); Y.append(y)
    res[str(testw)]=dict(n=len(Y),brier_sim=brier(PS,Y),brier_normal=brier(PN,Y),brier_coin=brier([.5]*len(Y),Y),calib_sim=calib(PS,Y),calib_normal=calib(PN,Y))
# B) Dom's real matchups, weeks 5-7: pregame projections, final scores
noise=sim.Noise(G)
real=[]
for w in (5,6,7):
    pre=json.load(open(f'/home/claude/dk-feeds/dispatch_out/scoreboard/pregame_wk{w}.json'))
    met=json.load(open(f'/home/claude/dk-feeds/dispatch_out/meter_wk{w}.json'))
    for lab,l in met['leagues'].items():
        sides={}
        for sd,key in (('me','me'),('op','op')):
            P=[];A=[]
            for p in l['starters'][key]:
                k=f"{lab}|{sd}|{p['player'].lower().replace('.','').replace(chr(39),'')}"
                pr=next((v for kk,v in pre.items() if kk.startswith(f"{lab}|{sd}|") and kk.split('|')[2].replace('.','').replace(chr(39),'').replace(' jr','').replace(' sr','').replace(' ii','').replace(' iii','')==p['player'].lower().replace('.','').replace(chr(39),'').replace(' jr','').replace(' sr','').replace(' ii','').replace(' iii','')),None)
                vals=[x for x in ((pr or {}).get('gotham'),(pr or {}).get('sleeper'),(pr or {}).get('yahoo')) if x is not None] if pr else [x for x in (p.get('gotham'),p.get('sleeper'),p.get('yahoo')) if x is not None]
                m=float(np.mean(vals)) if vals else 0.0
                pos=p.get('pos') or p['slot']; pos=pos if pos in ('QB','RB','WR','TE','K','DEF') else 'WR'
                P.append((m,pos,p.get('team') or '?','')); A.append(p.get('actual') or 0.0)
            sides[sd]=(P,sum(A))
        n=20000
        a=sim.draw(noise,rng,sides['me'][0],n,tf={t:rng.standard_normal(n) for t in {x[2] for x in sides['me'][0]+sides['op'][0]}}).sum(1)
        b=sim.draw(noise,rng,sides['op'][0],n).sum(1)
        ps=float((a>b).mean())
        pa=[x[0] for x in sides['me'][0]]; pb=[x[0] for x in sides['op'][0]]
        SIG.update({'K':4.5,'DEF':6.5})
        pn=normal_win(pa,pb,[x[1] for x in sides['me'][0]],[x[1] for x in sides['op'][0]])
        y=float(sides['me'][1]>sides['op'][1])
        real.append(dict(week=w,league=lab,proj=[round(sum(pa),1),round(sum(pb),1)],final=[round(sides['me'][1],1),round(sides['op'][1],1)],sim=round(ps,3),normal=round(pn,3),won=y))
res['real']=real
res['real_brier']=dict(sim=brier([r['sim'] for r in real],[r['won'] for r in real]),normal=brier([r['normal'] for r in real],[r['won'] for r in real]),coin=.25)
print(json.dumps(res,indent=1))
