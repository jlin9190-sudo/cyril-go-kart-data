"""Re-time segments using each lap's OWN path distance from the timing line (fixed metre gates).
This matches coaching cues ('80 m after line') and is comparable across sessions without a shared ref geometry."""
import pickle, numpy as np, math
R = pickle.load(open('res.pkl','rb'))
SEGS, RECS = R['SEGS'], R['RECS']
PRIOR = R['PRIOR']
GATES = [0] + [s['a'] for s in SEGS[1:]] + [None]  # None = end of lap

def retime(r):
    t0, t1 = r['t0'], r['t0']+r['lt']
    m = (r['t'] >= t0-0.05) & (r['t'] <= t1+0.05)
    t = r['t'][m]; x = r['x'][m]; y = r['y'][m]; v = r['v'][m]; vs = r['vs'][m]
    # own path distance, 0 at t0
    cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    c0 = np.interp(t0, t, cum); cum = cum - c0
    c1 = np.interp(t1, t, cum)
    # times at each gate
    gt = [t0]
    for g in GATES[1:-1]:
        # find crossing of cum==g
        gt.append(float(np.interp(g, cum, t)))
    gt.append(t1)
    segs = []
    for k, sg in enumerate(SEGS):
        ta, tb = gt[k], gt[k+1]
        mm = (t > ta) & (t < tb)
        def iat(tt, arr): return float(np.interp(tt, t, arr))
        vv = np.concatenate([[iat(ta,v)], v[mm], [iat(tb,v)]])
        vss = np.concatenate([[iat(ta,vs)], vs[mm], [iat(tb,vs)]])
        cc = np.concatenate([[iat(ta,cum)], cum[mm], [iat(tb,cum)]])
        xx = np.concatenate([[iat(ta,x)], x[mm], [iat(tb,x)]])
        yy = np.concatenate([[iat(ta,y)], y[mm], [iat(tb,y)]])
        path = float(np.sum(np.hypot(np.diff(xx), np.diff(yy))))
        # for last segment, path to end; gate_end for last = actual path length
        d = dict(seg=sg['name'], time=tb-ta, v_in=vv[0], v_out=vv[-1], path=path,
                 vmin=float(vss.min()), vmax=float(vss.max()),
                 vmin_s=float(cc[np.argmin(vss)]), gate_a=GATES[k],
                 gate_b=(GATES[k+1] if GATES[k+1] is not None else round(c1,1)))
        segs.append(d)
    # braking
    cidx = [k for k,s in enumerate(SEGS) if s['kind']=='C']
    for n,k in enumerate(cidx):
        d = segs[k]; prev_s = segs[cidx[n-1]]['vmin_s'] if n>0 else -1.0
        w = (cum >= prev_s) & (cum <= d['vmin_s']+0.01) & (t >= t0-0.2) & (t <= t1+0.2)
        if w.sum() < 3: d['brake_s']=np.nan; continue
        ws, wv = cum[w], vs[w]
        im = int(np.argmax(wv)); vmax = wv[im]
        after = np.where(wv[im:] < vmax-2)[0]
        d['brake_s'] = float(ws[im+after[0]]) if len(after) else np.nan
        d['brake_vmax'] = float(vmax); d['drop'] = float(vmax - d['vmin'])
    r['segs_own'] = segs
    r['path_len'] = c1
    return r

for r in RECS: retime(r)

def sess(tag):
    return [r for r in RECS if r['tag']==tag and r['vmin']>=28 and r['lt']<65]

def st(r, key='segs_own'): return np.array([d['time'] for d in r[key]])

E, F = sess('E'), sess('F')
bE, bF = min(E,key=lambda r:r['lt']), min(F,key=lambda r:r['lt'])
names = [s['name'] for s in SEGS]
TE = np.array([st(r) for r in E]); TF = np.array([st(r) for r in F])
mE, mF = np.median(TE,0), np.median(TF,0)
Bb = np.array([PRIOR['B']['seg_best'][n] for n in names])
Db = np.array([PRIOR['D']['seg_best'][n] for n in names])
Ab = np.array([PRIOR['A']['seg_best'][n] for n in names])
Cb = np.array([PRIOR['C']['seg_best'][n] for n in names])
Bm = np.array([PRIOR['B']['seg_med'][n] for n in names])

print('path lengths E:', [round(r['path_len'],1) for r in E], 'med', round(np.median([r['path_len'] for r in E]),1))
print('path lengths F:', [round(r['path_len'],1) for r in F], 'med', round(np.median([r['path_len'] for r in F]),1))
print('(prior B path ~834, A ~831, C ~825, D ~?)')

print('\n%-4s %6s %6s %6s %6s | Eb-Bb Fb-Bb | Eb-Db Fb-Db | Em-Bm Fm-Bm | Em-Fm'%('seg','Ebest','Fbest','Emed','Fmed'))
for k,n in enumerate(names):
    print('%-4s %6.3f %6.3f %6.3f %6.3f | %+.3f %+.3f | %+.3f %+.3f | %+.3f %+.3f | %+.3f'%(
        n, st(bE)[k], st(bF)[k], mE[k], mF[k],
        st(bE)[k]-Bb[k], st(bF)[k]-Bb[k], st(bE)[k]-Db[k], st(bF)[k]-Db[k],
        mE[k]-Bm[k], mF[k]-Bm[k], mE[k]-mF[k]))
sk=[k for k,s in enumerate(SEGS) if s['kind']=='S']; ck=[k for k,s in enumerate(SEGS) if s['kind']=='C']
for lab,ii in (('straights',sk),('corners',ck),('ALL',list(range(15)))):
    print(lab,' Eb-Bb %+.3f Fb-Bb %+.3f | Em-Bm %+.3f Fm-Bm %+.3f | Em-Fm %+.3f'%(
        st(bE)[ii].sum()-Bb[ii].sum(), st(bF)[ii].sum()-Bb[ii].sum(),
        mE[ii].sum()-Bm[ii].sum(), mF[ii].sum()-Bm[ii].sum(), mE[ii].sum()-mF[ii].sum()))

print('\n=== CORNERS (own-path) ===')
for cn in ('T1','T2','T3','T5','T6','T8'):
    k = names.index(cn)
    print(f'\n-- {cn} --')
    for tag,rs,br in (('E',E,bE),('F',F,bF)):
        d=br['segs_own'][k]
        paths=[r['segs_own'][k]['path'] for r in rs]
        print(f" {tag} med path {np.median(paths):.1f} ({min(paths):.1f}-{max(paths):.1f}) "
              f"vmin {np.median([r['segs_own'][k]['vmin'] for r in rs]):.1f} "
              f"vout {np.median([r['segs_own'][k]['v_out'] for r in rs]):.1f} "
              f"brake {np.nanmedian([r['segs_own'][k].get('brake_s',np.nan) for r in rs]):.0f} "
              f"time {np.median([r['segs_own'][k]['time'] for r in rs]):.3f}")
        print(f" {tag} best: path {d['path']:.1f} vmin {d['vmin']:.1f} vout {d['v_out']:.1f} "
              f"brake {d.get('brake_s',float('nan')):.0f} time {d['time']:.3f}  (vs B best {PRIOR['B']['seg_best'][cn]:+.3f}s)")
    for pk in ('B','D','C','A'):
        cb = PRIOR[pk].get('corner_best',{}).get(cn) or PRIOR[pk].get('corner_med',{}).get(cn)
        if cb:
            print(f" {pk}: path {cb['path']:.1f} vmin {cb['vmin']:.1f} vout {cb['vout']:.1f} brake {cb.get('brake',float('nan')):.0f} time {cb['time']:.3f}")

# accel curves
print('\n=== ACCEL vs SPEED (straights) ===')
def sm(a,w):
    k=np.ones(w)/w; return np.convolve(np.pad(a,(w//2,w//2),mode='edge'),k,'valid')
def accel_curve(rs):
    V=[]; Aa=[]
    for r in rs:
        t=r['t']; keep=np.concatenate([[True], np.diff(t)>1e-6])
        t=t[keep]; v=sm(r['v'][keep],7); s=r['sr'][keep]
        # own-path zones approximating straights: after T4 (~366-480) and main (~769-end + 0-68)
        # use own cum
        m0=(r['t']>=r['t0'])&(r['t']<=r['t0']+r['lt'])
        cum=np.concatenate([[0],np.cumsum(np.hypot(np.diff(r['x'][m0]),np.diff(r['y'][m0])))])
        # map t->cum
        tt=r['t'][m0]; 
        # recompute on cleaned
        t2=r['t'][keep]; x2=r['x'][keep]; y2=r['y'][keep]
        m=(t2>=r['t0'])&(t2<=r['t0']+r['lt'])
        cum2=np.zeros(len(t2)); 
        xx,yy=x2[m],y2[m]; cc=np.concatenate([[0],np.cumsum(np.hypot(np.diff(xx),np.diff(yy)))])
        cum2[m]=cc
        zone=((cum2>372)&(cum2<500))|((cum2>775))|((cum2>=0)&(cum2<68)&(t2>=r['t0']))
        a=np.gradient(v,t2); sel=m&(zone)&(a>0.2)
        V+=list(v[sel]); Aa+=list(a[sel])
    V=np.array(V); Aa=np.array(Aa)
    bins={}
    for b in range(44,64,2):
        q=(V>=b)&(V<b+2)
        if q.sum()>20: bins[b+1]=float(np.median(Aa[q]))
    return bins, V, Aa

for tag,rs in (('E',E),('F',F)):
    bins,_,_=accel_curve(rs)
    print(tag, ' '.join(f'{b}:{v:.2f}' for b,v in sorted(bins.items())))
for pk in ('A','B','C','D'):
    bins=PRIOR[pk]['accel_bins']
    print(pk, ' '.join(f'{b}:{v:.2f}' for b,v in sorted(bins.items())))

# 44->58 time estimate
def t_accel(bins, v0=44, v1=58):
    bs=np.array(sorted(bins.keys())); av=np.array([bins[b] for b in bs])
    vv=np.arange(v0,v1+0.01,0.1); aa=np.interp(vv, bs, av)
    aa=np.maximum(aa,0.3)
    return float(np.sum(0.1/aa)), float(np.sum(0.1/aa*vv/3.6))

print('\n44->58 km/h:')
for tag,rs in (('E',E),('F',F)):
    bins,_,_=accel_curve(rs); dt,dist=t_accel(bins); print(f' {tag}: {dt:.2f}s / {dist:.0f}m')
for pk in ('A','B','C','D'):
    dt,dist=t_accel(PRIOR[pk]['accel_bins']); print(f' {pk}: {dt:.2f}s / {dist:.0f}m')

# matched position speeds on own path
print('\n=== SPEEDS AT MATCHED OWN-PATH POSITIONS ===')
def at_own(r, p):
    m=(r['t']>=r['t0'])&(r['t']<=r['t0']+r['lt'])
    cum=np.concatenate([[0],np.cumsum(np.hypot(np.diff(r['x'][m]),np.diff(r['y'][m])))])
    return float(np.interp(p, cum, r['vs'][m]))
for tag,rs,br in (('E',E,bE),('F',F,bF)):
    main_med=np.median([[at_own(r,p) for p in (769,790,810)]+[r['vmax']] for r in rs],0)
    back_med=np.median([[at_own(r,p) for p in (366,420,480)] for r in rs],0)
    print(f'{tag} main med @769/790/810/vmax: {np.round(main_med,1)}')
    print(f'{tag} back med @366/420/480: {np.round(back_med,1)}')
    print(f'{tag} best main:', [round(at_own(br,p),1) for p in (769,790,810)], 'vmax', round(br['vmax'],1),
          'back', [round(at_own(br,p),1) for p in (366,420,480)])

pickle.dump(dict(RECS=RECS,SEGS=SEGS,PRIOR=PRIOR,bE=bE,bF=bF,E=E,F=F,TE=TE,TF=TF,mE=mE,mF=mF,
                 Bb=Bb,Db=Db,Ab=Ab,Cb=Cb,Bm=Bm,names=names,S=R['S'],SX=R['SX'],SY=R['SY'],TX=R['TX'],TY=R['TY'],Lref=R['Lref']),
            open('summ.pkl','wb'))
print('\nok')
