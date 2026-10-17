import pickle, numpy as np
R = pickle.load(open('summ.pkl','rb'))
RECS, SEGS, PRIOR = R['RECS'], R['SEGS'], R['PRIOR']
names = [s['name'] for s in SEGS]

def clean(tag):
    return [r for r in RECS if r['tag']==tag and r['vmin']>=28 and r['lt']<65]

E, F = clean('E'), clean('F')
bE = min(E, key=lambda r:r['lt']); bF = min(F, key=lambda r:r['lt'])

# Use PROJECTED segs for path (varies with line); OWN-path segs for time (comparable metres)
print('=== PROJECTED path lengths (line quality) ===')
for cn in ('T1','T2','T3','T5','T6','T8'):
    k = names.index(cn)
    print(f'\n{cn}:')
    for tag,rs,br in (('E',E,bE),('F',F,bF)):
        paths = [r['segs'][k]['path'] for r in rs]
        print(f"  {tag} path med {np.median(paths):.1f} ({min(paths):.1f}-{max(paths):.1f})  best L{br['lap']} {br['segs'][k]['path']:.1f}")
        print(f"       own-time med {np.median([r['segs_own'][k]['time'] for r in rs]):.3f} best {br['segs_own'][k]['time']:.3f}  "
              f"vmin {br['segs'][k]['vmin']:.1f} vout {br['segs'][k]['v_out']:.1f} brake {br['segs'][k].get('brake_s',float('nan')):.0f}")
    for pk in ('B','D','A'):
        cb = PRIOR[pk].get('corner_best',{}).get(cn) or PRIOR[pk].get('corner_med',{}).get(cn)
        cm = PRIOR[pk].get('corner_med',{}).get(cn)
        if cb: print(f"  {pk} best path {cb['path']:.1f} time {cb['time']:.3f} vmin {cb['vmin']:.1f} vout {cb['vout']:.1f}")
        if cm and pk=='B': print(f"  B med  path {cm['path']:.1f} time {cm['time']:.3f}")
    if cn=='T2':
        print(f"  B L4 ref path 77.3 time 5.93")

# Incident detail
print('\n=== INCIDENT DETAIL ===')
for r in RECS:
    if not (r['vmin']<28 or r['lt']>65): continue
    m = (r['t']>=r['t0'])&(r['t']<=r['t0']+r['lt'])
    j = int(np.argmin(r['v'][m]))
    # course around min
    idx = np.where(m)[0]
    i0 = max(0, j-40); i1 = min(len(idx)-1, j+40)
    print(f"{r['tag']} L{r['lap']}: vmin {r['vmin']:.1f} at s_ref={r['sr'][m][j]:.0f} t={r['t'][m][j]-r['t0']:.1f}s")
    # which own-path segment
    for d in r['segs_own']:
        if d.get('ta') is None: break
    # find by time
    tt = r['t'][m][j]
    for d in r['segs']:
        if d['ta'] <= tt <= d['tb']:
            print(f"  projected seg {d['seg']} time {d['time']:.2f} (seg vmin {d['vmin']:.1f})")
            break
    # heading change through slow zone
    slow = np.where(r['v'][m] < max(15, r['vmin']+5))[0]
    if len(slow)>5:
        sl = slow
        dx = np.diff(r['x'][m][sl]); dy = np.diff(r['y'][m][sl])
        h = np.degrees(np.unwrap(np.arctan2(dx, dy)))
        print(f"  slow window t={r['t'][m][sl[0]]-r['t0']:.1f}-{r['t'][m][sl[-1]]-r['t0']:.1f}s  course change {h[-1]-h[0]:+.0f} deg  path {np.hypot(dx,dy).sum():.1f}m")

# Consistency outliers
print('\n=== CONSISTENCY (own-path seg vs session median) ===')
for tag,rs in (('E',E),('F',F)):
    T = np.array([[d['time'] for d in r['segs_own']] for r in rs])
    med = np.median(T,0)
    print(f'{tag} lap sd {np.std([r["lt"] for r in rs],ddof=1):.3f} median {np.median([r["lt"] for r in rs]):.3f}')
    print(f'  sum seg IQR {sum(np.subtract(*np.percentile(T[:,k],[75,25])) for k in range(15)):.2f}')
    for i,r in enumerate(rs):
        bad = [(names[k], T[i,k]-med[k]) for k in range(15) if T[i,k]-med[k] > 0.25]
        if bad:
            print(f"  L{r['lap']} {r['lt']:.3f}: " + ', '.join(f'{n} {d:+.2f}' for n,d in bad))

# Kart estimate: compare straight times adjusted roughly
# Simple: time on 直4+直7+直1 (main power straights) vs B
print('\n=== KART PROXY: power-straight times (own-path) ===')
for tag,rs,br in (('E',E,bE),('F',F,bF)):
    for sn in ('直1','直4','直7'):
        k = names.index(sn)
        print(f"  {tag} {sn}: best {br['segs_own'][k]['time']:.3f} med {np.median([r['segs_own'][k]['time'] for r in rs]):.3f}  | B best {PRIOR['B']['seg_best'][sn]:.3f} med {PRIOR['B']['seg_med'][sn]:.3f}")

# E vs F head to head
print('\n=== E vs F ===')
print(f"Best: E {bE['lt']:.3f} (L{bE['lap']}) vs F {bF['lt']:.3f} (L{bF['lap']})  delta F-E {bF['lt']-bE['lt']:+.3f}")
print(f"Median clean: E {np.median([r['lt'] for r in E]):.3f} vs F {np.median([r['lt'] for r in F]):.3f}")
print(f"Clean laps: E {len(E)}/9  F {len(F)}/9")
TE = np.array([[d['time'] for d in r['segs_own']] for r in E])
TF = np.array([[d['time'] for d in r['segs_own']] for r in F])
dmed = np.median(TE,0)-np.median(TF,0)
print('Em-Fm per seg:', ' '.join(f'{n}{d:+.2f}' for n,d in zip(names,dmed)))
print(f'sum Em-Fm {dmed.sum():+.3f}')

# Estimate kart vs driving for E vs B
# Accel deficit: E 6.39s vs B 5.95s for 44-58 = +0.44s per full pull
# Two major pulls per lap (back + main) but starts from different speeds; rough kart effect 0.3-0.7s
# Lap gap +0.44; if kart ~0.4 then driving ~0.0
print('\n=== KART VS DRIVING (rough) ===')
print('E best - B best lap: +0.439s')
print('Accel 44-58: E +0.44s vs B per pull; E/F karts look close to A, a bit behind B midrange')
print('E reaches vmax 63.4 (vs B 63.3) and T8 exit is FASTER than B — kart top-end is fine')
print('Main losses E vs B (own-path best): T1 +0.39, T2 +0.30, T5 +0.44, T6 +0.15, T4 +0.14')
print('Main gains: 直4 -0.03, T8 -0.03, T3 -0.07 (plus 直7 artifact)')
