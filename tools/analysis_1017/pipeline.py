#!/usr/bin/env python3
"""Foshan P1 analysis for 2026-10-17 sessions E and F."""
import math, pickle, csv, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Noto Sans CJK JP']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 10
import matplotlib.pyplot as plt

OUT = '/workspace/report_1017'
FIG = OUT + '/fig'
os.makedirs(FIG, exist_ok=True)

# ---- known finish line from prior reports ----
FL_LAT, FL_LON = 22.875316, 113.266340
FL_HDG = 206.63  # degrees
R_EARTH = 6371000.0
LAT0, LON0 = 22.8753, 113.2663
C0 = math.cos(math.radians(LAT0))

# Corner / segment gates (metres after timing line along ref lap) — same as analyze.py
CORNERS = [
    ('T1', 73, 155, 'L'),
    ('T2', 188, 268, 'R'),
    ('T3', 268, 292, 'L'),
    ('T4', 314, 366, 'L'),
    ('T5', 480, 573, 'R'),
    ('T6', 573, 626, 'L'),
    ('T7', 659, 695, 'L'),
    ('T8', 725, 769, 'L'),
]
STRAIGHT_NAMES = {
    0: '主直道→T1', 155: 'T1→T2 短直', 292: 'T3→T4 连接段',
    366: '后直道', 626: 'T6→T7 连接段', 695: 'T7→T8 连接段', 769: 'T8→计时线 主直道',
}

# Published prior-session numbers (from earlier reports; VBO files no longer on box)
PRIOR = {
    'A': dict(tag='7/25', best_lt=59.469, best_lap=3, vmax_med=63.7,
              accel_bins={45:2.93,47:2.70,49:2.28,51:1.79,53:1.95,55:2.05,57:1.70,59:1.62,61:1.56,63:1.18},
              seg_best={'直1':4.278,'T1':5.310,'直2':2.353,'T2':6.199,'T3':1.913,'直3':1.654,'T4':3.870,
                        '直4':8.091,'T5':6.787,'T6':4.093,'直5':2.678,'T7':2.895,'直6':2.039,'T8':3.444,'直7':3.864},
              corner_best={
                  'T1':dict(path=73.8,vmin=42.5,vout=46.5,brake=82.1,time=5.310),
                  'T2':dict(path=79.5,vmin=41.3,vout=44.2,brake=204.9,time=6.199),
                  'T3':dict(path=23.7,vmin=43.3,vout=46.4,time=1.913),
                  'T5':dict(path=97.1,vmin=44.3,vout=46.2,brake=517.8,time=6.787),
                  'T6':dict(path=46.7,vmin=35.6,vout=39.1,brake=584.9,time=4.093),
                  'T8':dict(path=47.8,vmin=47.9,vout=50.1,brake=741.4,time=3.444),
              }),
    'B': dict(tag='9/27', best_lt=59.327, best_lap=6, vmax_med=63.1,
              accel_bins={45:2.95,47:2.96,49:2.75,51:2.55,53:2.33,55:1.79,57:1.87,59:1.75,61:1.21,63:0.97},
              seg_best={'直1':4.316,'T1':5.813,'直2':2.240,'T2':6.087,'T3':1.928,'直3':1.640,'T4':4.204,
                        '直4':7.612,'T5':6.513,'T6':4.540,'直5':2.559,'T7':2.665,'直6':2.113,'T8':3.215,'直7':3.879},
              seg_med={'直1':4.321,'T1':5.776,'直2':2.298,'T2':6.087,'T3':2.016,'直3':1.661,'T4':4.279,
                       '直4':7.773,'T5':6.671,'T6':4.617,'直5':2.596,'T7':2.714,'直6':2.143,'T8':3.344,'直7':3.917},
              corner_best={
                  'T1':dict(path=82.0,vmin=45.6,vout=49.5,brake=83.4,time=5.813),
                  'T2':dict(path=80.0,vmin=41.3,vout=44.3,brake=204.6,time=6.087),
                  'T2_ref':dict(path=77.3,vmin=41.2,vout=42.8,brake=204.5,time=5.93,note='9/27 L4'),
                  'T3':dict(path=24.0,vmin=44.2,vout=46.2,time=1.928),
                  'T5':dict(path=93.0,vmin=43.2,vout=46.0,brake=514.4,time=6.513),
                  'T6':dict(path=53.0,vmin=37.6,vout=41.4,brake=587.5,time=4.540),
                  'T8':dict(path=44.0,vmin=46.9,vout=49.9,brake=736.5,time=3.215),
              },
              corner_med={
                  'T1':dict(path=79.8,vmin=45.6,vout=48.9,brake=82.5,time=5.78),
                  'T2':dict(path=80.9,vmin=42.3,vout=44.3,brake=204.5,time=6.09),
                  'T3':dict(path=24.8,vmin=43.1,vout=45.6,time=2.02),
                  'T5':dict(path=95.8,vmin=43.3,vout=46.2,brake=514.4,time=6.67),
                  'T6':dict(path=53.0,vmin=36.8,vout=40.9,brake=587.5,time=4.62),
                  'T8':dict(path=45.1,vmin=46.9,vout=49.2,brake=739.9,time=3.34),
              }),
    'C': dict(tag='10/01 13:29', best_lt=61.384, best_lap=1, vmax_med=58.5,
              accel_bins={45:2.60,47:2.32,49:1.96,51:1.68,53:1.41,55:1.44,57:1.13,59:0.82},
              seg_best={'直1':4.611,'T1':5.697,'直2':2.397,'T2':6.349,'T3':1.970,'直3':1.672,'T4':4.046,
                        '直4':8.075,'T5':6.951,'T6':4.352,'直5':2.656,'T7':2.777,'直6':2.160,'T8':3.504,'直7':4.169},
              corner_med={
                  'T1':dict(path=73.0,vmin=42.5,vout=45.7,brake=82.1,time=5.52),
                  'T2':dict(path=82.3,vmin=42.9,vout=44.2,brake=205.6,time=6.40),
                  'T3':dict(path=24.9,vmin=43.2,vout=45.4,time=2.01),
                  'T5':dict(path=97.6,vmin=43.2,vout=44.6,brake=515.6,time=7.07),
                  'T6':dict(path=49.6,vmin=36.5,vout=39.9,brake=592.3,time=4.36),
                  'T8':dict(path=46.9,vmin=45.8,vout=48.7,brake=739.7,time=3.50),
              }),
    'D': dict(tag='10/01 14:16', best_lt=60.375, best_lap=4, vmax_med=62.6,
              accel_bins={45:2.74,47:2.62,49:2.19,51:1.84,53:1.65,55:1.98,57:1.71,59:1.48,61:1.36,63:0.96},
              seg_best={'直1':4.363,'T1':5.494,'直2':2.488,'T2':6.089,'T3':2.086,'直3':1.627,'T4':3.965,
                        '直4':8.137,'T5':6.651,'T6':4.377,'直5':2.721,'T7':2.733,'直6':2.157,'T8':3.480,'直7':4.009},
              corner_med={
                  'T1':dict(path=71.7,vmin=42.1,vout=44.6,brake=79.0,time=5.44),
                  'T2':dict(path=81.0,vmin=43.0,vout=45.1,brake=206.5,time=6.27),
                  'T3':dict(path=26.0,vmin=43.9,vout=45.6,time=2.09),
                  'T5':dict(path=96.9,vmin=44.5,vout=46.5,brake=515.6,time=6.89),
                  'T6':dict(path=50.4,vmin=36.6,vout=38.5,brake=587.2,time=4.38),
                  'T8':dict(path=47.1,vmin=46.2,vout=48.5,brake=741.0,time=3.59),
              }),
}

def load_vbo(path):
    rows = []; d = False
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line == '[data]': d = True; continue
        if d and line:
            p = line.split()
            t = p[1]; s = int(t[:2])*3600 + int(t[2:4])*60 + float(t[4:])
            lat = float(p[2])/60; lon = -float(p[3])/60
            x = (lon - LON0) * C0 * math.pi/180 * R_EARTH
            y = (lat - LAT0) * math.pi/180 * R_EARTH
            rows.append(dict(t=s, lat=lat, lon=lon, x=x, y=y, v=float(p[4]), h=float(p[5]), sats=int(p[0])))
    return rows

def to_xy_fl():
    x = (FL_LON - LON0) * C0 * math.pi/180 * R_EARTH
    y = (FL_LAT - LAT0) * math.pi/180 * R_EARTH
    return x, y

def crossings(rows, flpt=None, hdg=None, rad=8.0):
    if flpt is None: flpt = to_xy_fl()
    if hdg is None: hdg = FL_HDG
    rx, ry = flpt
    hx, hy = math.sin(math.radians(hdg)), math.cos(math.radians(hdg))
    out = []
    for i in range(1, len(rows)):
        x0, y0 = rows[i-1]['x'], rows[i-1]['y']
        x1, y1 = rows[i]['x'], rows[i]['y']
        a = (x0-rx)*hx + (y0-ry)*hy; b = (x1-rx)*hx + (y1-ry)*hy
        if a < 0 <= b:
            fr = -a/(b-a); x = x0+fr*(x1-x0); y = y0+fr*(y1-y0)
            if math.hypot(x-rx, y-ry) < rad:
                t = rows[i-1]['t'] + fr*(rows[i]['t']-rows[i-1]['t'])
                if not out or t - out[-1] > 30:
                    out.append(t)
    return out

def sm(a, w=5):
    a = np.asarray(a, float)
    k = np.ones(w)/w
    return np.convolve(np.pad(a, (w//2, w//2), mode='edge'), k, 'valid')

def build_segs():
    segs = []; prev = 0
    for nm, a, b, d in CORNERS:
        if a > prev:
            segs.append(dict(name='直'+str(len([s for s in segs if s['kind']=='S'])+1),
                             kind='S', a=prev, b=a, label=STRAIGHT_NAMES[prev]))
        segs.append(dict(name=nm, kind='C', a=a, b=b, dir=d)); prev = b
    segs.append(dict(name='直'+str(len([s for s in segs if s['kind']=='S'])+1),
                     kind='S', a=prev, b=None, label=STRAIGHT_NAMES[prev]))
    return segs

SEGS = build_segs()

def make_ref(rows, t0, t1, step=1.0):
    """Resample one lap to 1 m along own path; return S,X,Y,V and also build FL-relative coords with wrap."""
    idx = [i for i in range(len(rows)) if t0 - 0.2 <= rows[i]['t'] <= t1 + 0.2]
    t = np.array([rows[i]['t'] for i in idx])
    x = np.array([rows[i]['x'] for i in idx]); y = np.array([rows[i]['y'] for i in idx])
    v = np.array([rows[i]['v'] for i in idx])
    m = (t >= t0) & (t <= t1)
    t, x, y, v = t[m], x[m], y[m], v[m]
    # start exactly at FL by interpolating
    cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    S = np.arange(0, cum[-1], step)
    return S, np.interp(S, cum, x), np.interp(S, cum, y), np.interp(S, cum, v)

def project(x, y, SX, SY, STX, STY, S):
    N = len(S); sr = np.zeros(len(x)); la = np.zeros(len(x)); last = 0
    for k in range(len(x)):
        lo = max(last-15, 0); hi = min(last+40, N)
        if k == 0: lo, hi = 0, 40
        d = (SX[lo:hi]-x[k])**2 + (SY[lo:hi]-y[k])**2
        j = lo + int(np.argmin(d))
        dx = x[k]-SX[j]; dy = y[k]-SY[j]
        along = dx*STX[j] + dy*STY[j]
        sr[k] = S[j] + along; la[k] = STX[j]*dy - STY[j]*dx
        last = j
    return sr, la

def gate_cross(t, x, y, SX, SY, STX, STY, sidx, tmin):
    gx, gy, tx, ty = SX[sidx], SY[sidx], STX[sidx], STY[sidx]
    a = (x-gx)*tx + (y-gy)*ty; lat = (x-gx)*(-ty) + (y-gy)*tx
    for k in range(1, len(t)):
        if t[k] < tmin: continue
        if a[k-1] < 0 <= a[k] and abs(lat[k]) < 15:
            fr = -a[k-1]/(a[k]-a[k-1])
            return t[k-1]+fr*(t[k]-t[k-1])
    raise RuntimeError(f'no cross gate {sidx} after {tmin}')

def process_session(tag, path, site_best):
    rows = load_vbo(path)
    cr = crossings(rows)
    lts = [cr[i+1]-cr[i] for i in range(len(cr)-1)]
    print(f'\n=== {tag} === samples {len(rows)} dur {rows[-1]["t"]-rows[0]["t"]:.1f}s')
    print(f' crossings {len(cr)} laps {[round(x,3) for x in lts]}')
    # pick contiguous block whose min is closest to site_best
    best_off, best_err = 0, 1e9
    for off in range(max(1, len(lts))):
        # take from off to end, find closest to site_best among them
        for i in range(off, len(lts)):
            err = abs(lts[i] - site_best)
            # prefer blocks that start near out-lap discard: if first lap >65 maybe skip
            if err < best_err:
                best_err = err; best_i = i
    # use all laps after any obvious outlap (first if >70 or <50 discard as incomplete)
    use = []
    for i, lt in enumerate(lts):
        if lt < 50 or lt > 90: continue  # incomplete / stop
        use.append(i)
    # if first usable is much slower and looks like outlap (>66), keep it but flag
    laps = []
    for k, i in enumerate(use):
        t0, t1 = cr[i], cr[i+1]
        idx = [j for j in range(len(rows)) if t0 <= rows[j]['t'] <= t1]
        vs = [rows[j]['v'] for j in idx]
        laps.append(dict(tag=tag, lap=k+1, lt=t1-t0, t0=t0, t1=t1, idx=idx, rows=rows,
                         vmax=max(vs), vmin=min(vs)))
    print(f' kept {len(laps)} laps: {[round(L["lt"],3) for L in laps]}')
    print(f' site best {site_best:.3f}; gps best {min(L["lt"] for L in laps):.3f}; diff {min(L["lt"] for L in laps)-site_best:+.3f}')
    print(f' vmax/vmin per lap: {[(round(L["vmax"],1), round(L["vmin"],1)) for L in laps]}')
    return rows, cr, laps

# Load both sessions
E_PATH = '/home/box/Downloads/佛山P1国际赛车场_2026-10-17_15_17_37.vbo'
F_PATH = '/home/box/Downloads/佛山P1国际赛车场_2026-10-17_16_04_10.vbo'
rowsE, crE, lapsE = process_session('E', E_PATH, 59.766)
rowsF, crF, lapsF = process_session('F', F_PATH, 59.957)

# Build reference from overall fastest lap among E+F (prefer clean)
all_clean = [L for L in lapsE+lapsF if L['vmin'] > 25]
refL = min(all_clean, key=lambda L: L['lt'])
print(f'\nReference lap: {refL["tag"]} L{refL["lap"]} {refL["lt"]:.3f}')
S, SX, SY, SV = make_ref(refL['rows'], refL['t0'], refL['t1'])
Xs, Ys = sm(SX, 5), sm(SY, 5)
HD = np.unwrap(np.arctan2(np.gradient(Xs), np.gradient(Ys)))
CURV = sm(np.degrees(np.gradient(HD)), 9)
TX = np.gradient(Xs); TY = np.gradient(Ys); nn = np.hypot(TX, TY); TX /= nn; TY /= nn
# use smoothed geometry for projection
SX, SY = Xs, Ys
Lref = float(S[-1])
print(f'ref length {Lref:.1f} m')
# apex of each corner
for sg in SEGS:
    if sg['kind']=='C':
        seg = slice(sg['a'], min(sg['b']+1, len(CURV)))
        sg['apex_s'] = int(sg['a'] + np.argmax(np.abs(CURV[seg])))

def analyse_lap(L):
    rows = L['rows']; t0, t1 = L['t0'], L['t0']+L['lt']
    # include a bit of pre/post
    ii = [i for i in range(len(rows)) if t0-0.5 <= rows[i]['t'] <= t1+0.5]
    # unique times
    t = np.array([rows[i]['t'] for i in ii])
    keep = np.concatenate([[True], np.diff(t) > 1e-6])
    t = t[keep]; x = np.array([rows[i]['x'] for i in ii])[keep]
    y = np.array([rows[i]['y'] for i in ii])[keep]
    v = np.array([rows[i]['v'] for i in ii])[keep]
    vs = sm(v, 5)
    sr, la = project(x, y, SX, SY, TX, TY, S)
    cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    # gates
    gt = [t0]
    for sg in SEGS[1:]:
        gt.append(gate_cross(t, x, y, SX, SY, TX, TY, sg['a'], gt[-1]+0.3))
    gt.append(t1)
    rec = dict(tag=L['tag'], lap=L['lap'], lt=L['lt'], t0=t0, t=t, x=x, y=y, v=v, vs=vs,
               sr=sr, la=la, cum=cum, vmax=L['vmax'], vmin=L['vmin'], segs=[])
    for k, sg in enumerate(SEGS):
        ta, tb = gt[k], gt[k+1]
        m = (t > ta) & (t < tb)
        def iat(tt, arr): return float(np.interp(tt, t, arr))
        tt = np.concatenate([[ta], t[m], [tb]])
        xx = np.concatenate([[iat(ta,x)], x[m], [iat(tb,x)]])
        yy = np.concatenate([[iat(ta,y)], y[m], [iat(tb,y)]])
        vv = np.concatenate([[iat(ta,v)], v[m], [iat(tb,v)]])
        vss = np.concatenate([[iat(ta,vs)], vs[m], [iat(tb,vs)]])
        ss = np.concatenate([[iat(ta,sr)], sr[m], [iat(tb,sr)]])
        path = float(np.sum(np.hypot(np.diff(xx), np.diff(yy))))
        d = dict(seg=sg['name'], time=tb-ta, ta=ta, tb=tb, v_in=vv[0], v_out=vv[-1], path=path,
                 vmin=float(vss.min()), vmax=float(vss.max()), vmin_s=float(ss[np.argmin(vss)]))
        rec['segs'].append(d)
    # braking for corners
    cidx = [k for k,s in enumerate(SEGS) if s['kind']=='C']
    m = (t >= t0-0.2) & (t <= t1+0.2)
    s = sr[m].copy(); vv2 = vs[m]
    for n, k in enumerate(cidx):
        sg = SEGS[k]; d = rec['segs'][k]
        prev_s = (rec['segs'][cidx[n-1]]['vmin_s'] if n>0 else -1.0)
        w = (s >= prev_s) & (s <= d['vmin_s']+0.01)
        if w.sum() < 3: d['brake_s'] = np.nan; d['brake_vmax'] = np.nan; continue
        ws = s[w]; wv = vv2[w]
        im = int(np.argmax(wv)); vmax = wv[im]
        after = np.where(wv[im:] < vmax-2)[0]
        if len(after)==0: d['brake_s']=np.nan; d['brake_vmax']=vmax
        else: d['brake_s']=float(ws[im+after[0]]); d['brake_vmax']=float(vmax)
        d['drop'] = float(vmax - d['vmin'])
    return rec

print('\nAnalysing laps...')
RECS = []
for L in lapsE + lapsF:
    try:
        RECS.append(analyse_lap(L))
        print(f"  {L['tag']} L{L['lap']} {L['lt']:.3f} sumseg {sum(d['time'] for d in RECS[-1]['segs']):.3f}")
    except Exception as e:
        print(f"  FAIL {L['tag']} L{L['lap']}: {e}")

pickle.dump(dict(SEGS=SEGS, RECS=RECS, S=S, SX=SX, SY=SY, TX=TX, TY=TY, Lref=Lref,
                 CURV=CURV, PRIOR=PRIOR, lapsE=lapsE, lapsF=lapsF),
            open(f'{OUT}/res.pkl','wb'))
print('saved res.pkl', len(RECS), 'laps')
