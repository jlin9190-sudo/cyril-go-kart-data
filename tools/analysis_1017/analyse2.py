import pickle, numpy as np, csv
R = pickle.load(open('res.pkl','rb'))
SEGS, RECS, S, SX, SY, TX, TY, Lref, PRIOR = R['SEGS'], R['RECS'], R['S'], R['SX'], R['SY'], R['TX'], R['TY'], R['Lref'], R['PRIOR']
names = [s['name'] for s in SEGS]

def sess(tag, exclude_incidents=True):
    rs = [r for r in RECS if r['tag']==tag]
    if exclude_incidents:
        # exclude laps with vmin < 28 or lt > 65
        rs = [r for r in rs if r['vmin'] >= 28 and r['lt'] < 65]
    return rs

def st(r): return np.array([d['time'] for d in r['segs']])

# ---- Incidents ----
print('=== INCIDENTS ===')
for r in RECS:
    if r['vmin'] < 28 or r['lt'] > 65:
        # find where min speed occurs
        m = (r['t']>=r['t0'])&(r['t']<=r['t0']+r['lt'])
        j = np.argmin(r['v'][m]); srj = r['sr'][m][j]; tj = r['t'][m][j]-r['t0']
        # which segment
        seg = '?'
        for d in r['segs']:
            if d['ta'] <= r['t'][m][j] <= d['tb']: seg = d['seg']; break
        print(f"{r['tag']} L{r['lap']} lt={r['lt']:.3f} vmin={r['vmin']:.1f} @s={srj:.0f}m t={tj:.1f}s seg={seg}")
        # slow window
        slow = np.where((r['v'][m] < 15))[0]
        if len(slow):
            print(f"  v<15 from t={r['t'][m][slow[0]]-r['t0']:.1f} to {r['t'][m][slow[-1]]-r['t0']:.1f}s, s={r['sr'][m][slow[0]]:.0f}-{r['sr'][m][slow[-1]]:.0f}")

E = sess('E'); F = sess('F')
bE = min(E, key=lambda r: r['lt']); bF = min(F, key=lambda r: r['lt'])
print(f'\nClean E: {len(E)} laps best L{bE["lap"]} {bE["lt"]:.3f} median {np.median([r["lt"] for r in E]):.3f} sd {np.std([r["lt"] for r in E],ddof=1):.3f}')
print(f'Clean F: {len(F)} laps best L{bF["lap"]} {bF["lt"]:.3f} median {np.median([r["lt"] for r in F]):.3f} sd {np.std([r["lt"] for r in F],ddof=1):.3f}')
print('E all laps:', [(r['lap'], round(r['lt'],3), round(r['vmax'],1), round(r['vmin'],1)) for r in RECS if r['tag']=='E'])
print('F all laps:', [(r['lap'], round(r['lt'],3), round(r['vmax'],1), round(r['vmin'],1)) for r in RECS if r['tag']=='F'])

# segment tables
TE = np.array([st(r) for r in E]); TF = np.array([st(r) for r in F])
mE, mF = np.median(TE,0), np.median(TF,0)
Bb = np.array([PRIOR['B']['seg_best'][n] for n in names])
Ab = np.array([PRIOR['A']['seg_best'][n] for n in names])
Cb = np.array([PRIOR['C']['seg_best'][n] for n in names])
Db = np.array([PRIOR['D']['seg_best'][n] for n in names])
Bm = np.array([PRIOR['B']['seg_med'][n] for n in names])

print('\n%-4s %6s %6s %6s %6s | Eb-Bb Fb-Bb Eb-Db Fb-Db | Em-Bm Fm-Bm Em-Fm'%('seg','Ebest','Fbest','Emed','Fmed'))
for k,n in enumerate(names):
    print('%-4s %6.3f %6.3f %6.3f %6.3f | %+.3f %+.3f %+.3f %+.3f | %+.3f %+.3f %+.3f'%(
        n, st(bE)[k], st(bF)[k], mE[k], mF[k],
        st(bE)[k]-Bb[k], st(bF)[k]-Bb[k], st(bE)[k]-Db[k], st(bF)[k]-Db[k],
        mE[k]-Bm[k], mF[k]-Bm[k], mE[k]-mF[k]))
sk=[k for k,s in enumerate(SEGS) if s['kind']=='S']; ck=[k for k,s in enumerate(SEGS) if s['kind']=='C']
for lab,ii in (('straights',sk),('corners',ck),('ALL',list(range(15)))):
    print(lab, 'Eb-Bb %+.3f Fb-Bb %+.3f Eb-Db %+.3f | Em-Bm %+.3f Fm-Bm %+.3f Em-Fm %+.3f'%(
        st(bE)[ii].sum()-Bb[ii].sum(), st(bF)[ii].sum()-Bb[ii].sum(), st(bE)[ii].sum()-Db[ii].sum(),
        mE[ii].sum()-Bm[ii].sum(), mF[ii].sum()-Bm[ii].sum(), mE[ii].sum()-mF[ii].sum()))

print('sum best segs E %.3f F %.3f | B %.3f'% (TE.min(0).sum(), TF.min(0).sum(), Bb.sum()))

# corners detail
print('\n=== CORNERS ===')
for cn in ('T1','T2','T3','T5','T6','T8'):
    k = names.index(cn)
    print(f'\n-- {cn} --')
    for tag, rs, br in (('E',E,bE),('F',F,bF)):
        paths=[r['segs'][k]['path'] for r in rs]
        vmins=[r['segs'][k]['vmin'] for r in rs]
        vouts=[r['segs'][k]['v_out'] for r in rs]
        brakes=[r['segs'][k].get('brake_s',np.nan) for r in rs]
        times=[r['segs'][k]['time'] for r in rs]
        d=br['segs'][k]
        print(f" {tag} med path {np.median(paths):.1f} ({min(paths):.1f}-{max(paths):.1f}) vmin {np.median(vmins):.1f} vout {np.median(vouts):.1f} brake {np.nanmedian(brakes):.0f} time {np.median(times):.3f}")
        print(f" {tag} best L{br['lap']}: path {d['path']:.1f} vmin {d['vmin']:.1f} vout {d['v_out']:.1f} brake {d.get('brake_s',float('nan')):.0f} time {d['time']:.3f}")
    for pk in ('B','D','C','A'):
        cb = PRIOR[pk].get('corner_best',{}).get(cn) or PRIOR[pk].get('corner_med',{}).get(cn)
        cm = PRIOR[pk].get('corner_med',{}).get(cn)
        if cb: print(f" {pk} best: path {cb['path']:.1f} vmin {cb['vmin']:.1f} vout {cb['vout']:.1f} brake {cb.get('brake',float('nan')):.0f} time {cb['time']:.3f}")
        if cm and cm is not cb: print(f" {pk} med:  path {cm['path']:.1f} vmin {cm['vmin']:.1f} vout {cm['vout']:.1f} brake {cm.get('brake',float('nan')):.0f} time {cm['time']:.3f}")
    if cn=='T2' and 'T2_ref' in PRIOR['B']['corner_best']:
        cb=PRIOR['B']['corner_best']['T2_ref']; print(f" B L4 ref: path {cb['path']:.1f} time {cb['time']:.3f}")

pickle.dump(dict(bE=bE,bF=bF,E=E,F=F,TE=TE,TF=TF,mE=mE,mF=mF,Bb=Bb,Ab=Ab,Cb=Cb,Db=Db,Bm=Bm), open('summ.pkl','wb'))
