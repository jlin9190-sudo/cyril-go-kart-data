import pickle, numpy as np, csv, os
import matplotlib; matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif']=['Noto Sans CJK SC']; matplotlib.rcParams['axes.unicode_minus']=False
matplotlib.rcParams['font.size']=10
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

R = pickle.load(open('summ.pkl','rb'))
RECS, SEGS, PRIOR = R['RECS'], R['SEGS'], R['PRIOR']
S, SX, SY, TX, TY, Lref = R['S'], R['SX'], R['SY'], R['TX'], R['TY'], R['Lref']
names = R['names']; N = len(S)
E, F, bE, bF = R['E'], R['F'], R['bE'], R['bF']
Bb, Bm, Db = R['Bb'], R['Bm'], R['Db']
FIG='fig'; os.makedirs(FIG, exist_ok=True)
CE, CF, CB = '#2ca02c', '#ff7f0e', '#d62728'

def st(r, key='segs_own'): return np.array([d['time'] for d in r[key]])
def prof(r):
    m=(r['t']>=r['t0']-0.05)&(r['t']<=r['t0']+r['lt']+0.05)
    s=r['sr'][m]; o=np.argsort(s); return s[o], r['vs'][m][o], (r['t'][m]-r['t0'])[o]
def gate(ax,s,col='k',w=9,ls='-',lw=1.2):
    s=min(int(s),N-1); gx,gy,tx,ty=SX[s],SY[s],TX[s],TY[s]
    ax.plot([gx-w*ty,gx+w*ty],[gy+w*tx,gy-w*tx],color=col,ls=ls,lw=lw,zorder=5)
def inr(r,s0,s1):
    return (r['sr']>=s0)&(r['sr']<=s1)&(r['t']>=r['t0']-0.05)&(r['t']<=r['t0']+r['lt']+0.05)

# ---- 1. speed vs distance ----
fig,(ax,ax2)=plt.subplots(2,1,figsize=(13,7.6),sharex=True,gridspec_kw=dict(height_ratios=[2.2,1]))
for sg in SEGS:
    if sg['kind']=='C':
        for a in (ax,ax2): a.axvspan(sg['a'],sg['b'],color='#eeeeee',zorder=0)
        ax.text((sg['a']+sg['b'])/2, 65.5, '%s%s'%(sg['name'],'左' if sg['dir']=='L' else '右'),
                ha='center',fontsize=10,fontweight='bold')
# synthetic B speed from prior: we don't have B trace; plot E and F only, annotate B best time
for r,c,lw in ((bE,CE,2.2),(bF,CF,2.0)):
    s,v,_=prof(r); ax.plot(s,v,color=c,lw=lw,label='%s 第%d圈 %.3f'%(r['tag'],r['lap'],r['lt']))
ax.axhline(np.nan, color=CB, lw=1.5, label='9/27 最快圈 59.327（无原始轨迹，仅作时间参照）')
ax.set_ylim(28,67.5); ax.set_ylabel('速度 km/h（GPS，5点平滑）'); ax.grid(alpha=0.3)
ax.legend(loc='lower right',fontsize=9)
ax.set_title('速度-距离：10/17 15:17(E) 与 16:04(F) 最快圈（灰底=弯道；参考线=E第8圈）',fontsize=12)
# cumulative delta E vs F
sE,vE,tE=prof(bE); G=np.arange(0,min(Lref, S[-1]),1.0)
sF,vF,tF=prof(bF)
ax2.plot(G, np.interp(G,sE,tE)-np.interp(G,sF,tF), color='#333', lw=1.6, label='E最快 - F最快（正=E慢）')
ax2.axhline(0,color='k',lw=0.8); ax2.set_ylabel('累计时间差 (秒)'); ax2.grid(alpha=0.3)
ax2.legend(fontsize=9); ax2.set_xlabel('距计时线距离（米，投影到参考线）'); ax2.set_xlim(0,Lref)
plt.tight_layout(); plt.savefig(f'{FIG}/speed_vs_distance.png',dpi=160); plt.close()

# ---- 2. line overlays ----
cfg=[('T1',[]),('T2',[]),('T6',[]),('T5',[]),('T8',[])]
fig,axs=plt.subplots(2,3,figsize=(18,13)); axs=axs.ravel(); axs[5].axis('off')
for ax,(cn,_) in zip(axs,cfg):
    k=names.index(cn); sg=SEGS[k]; s0,s1=sg['a']-12, sg['b']+12
    for r in E+F:
        m=inr(r,s0,s1); ax.plot(r['x'][m],r['y'][m],color='#dddddd',lw=0.7,zorder=1)
    for r,c,lb in ((bE,CE,'E 第%d圈（本场最快 %.3f）'%(bE['lap'],bE['lt'])),
                   (bF,CF,'F 第%d圈（本场最快 %.3f）'%(bF['lap'],bF['lt']))):
        d=r['segs'][k]; m=inr(r,s0,s1)
        ax.plot(r['x'][m],r['y'][m],color=c,lw=2.4,zorder=3,
                label='%s\n  段时%.3fs 路径%.1fm 最低%.1f 出弯%.1f'%(lb,d['time'],d['path'],d['vmin'],d['v_out']))
        mm=inr(r,sg['a'],sg['b']); j=np.where(mm)[0]
        if len(j):
            jj=j[np.argmin(r['vs'][j])]; ax.plot(r['x'][jj],r['y'][jj],'o',ms=7,mfc='white',mec=c,mew=2,zorder=6)
    gate(ax,sg['a']); gate(ax,sg['b'],ls='--')
    s=sg['a']; ax.annotate('',xy=(SX[min(s+6,N-1)],SY[min(s+6,N-1)]),xytext=(SX[max(s-6,0)],SY[max(s-6,0)]),
                           arrowprops=dict(arrowstyle='->',lw=1.5,color='k'))
    ms=(S>=s0)&(S<=s1)
    ax.set_xlim(SX[ms].min()-10,SX[ms].max()+10); ax.set_ylim(SY[ms].min()-10,SY[ms].max()+10)
    ax.set_aspect('equal',adjustable='datalim'); ax.grid(alpha=0.25); ax.tick_params(labelsize=8)
    pE=np.median([r['segs'][k]['path'] for r in E]); pF=np.median([r['segs'][k]['path'] for r in F])
    ax.set_title('%s（%s）路径中位 E %.1f / F %.1f m（B参考见正文）'%(cn,'左' if sg['dir']=='L' else '右',pE,pF),fontsize=10)
    ax.legend(fontsize=7.5,loc='upper center',bbox_to_anchor=(0.5,-0.04),framealpha=0.9)
fig.suptitle('T1 / T2 / T6 / T5 / T8 走线：10/17 E(绿) vs F(橙)\n灰=其余干净圈；○=最低速；实线短横=入口门，虚线=出口门',fontsize=13)
plt.tight_layout(); plt.savefig(f'{FIG}/line_corners.png',dpi=130); plt.close()

# ---- 3. segment delta ----
TE=np.array([st(r) for r in E]); TF=np.array([st(r) for r in F])
dEb=st(bE)-Bb; dFb=st(bF)-Bb; dEm=np.median(TE,0)-Bm; dFm=np.median(TF,0)-Bm
# mark 直7 as unreliable
fig,axs=plt.subplots(1,2,figsize=(14,6.5))
y=np.arange(15)
ax=axs[0]
ax.barh(y-0.2,dEb,0.4,color=CE,label='E最快 - B最快（合计 %+.2f；含直7偏差）'%dEb.sum())
ax.barh(y+0.2,dFb,0.4,color=CF,label='F最快 - B最快（合计 %+.2f；含直7偏差）'%dFb.sum())
ax.set_yticks(y); ax.set_yticklabels([n+('*' if n=='直7' else '') for n in names]); ax.invert_yaxis()
ax.axvline(0,color='k',lw=0.8); ax.grid(axis='x',alpha=0.3)
ax.set_xlabel('秒（正=比B慢）；*直7受圈长差异影响，不可直接比')
ax.set_title('各段用时差 vs 9/27最快圈（B）\n真实圈速差：E +0.44s / F +0.63s',fontsize=11)
ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(0.5,-0.1))
ax=axs[1]
dEF=st(bE)-st(bF); dEFm=np.median(TE,0)-np.median(TF,0)
ax.barh(y-0.2,dEF,0.4,color='#555',label='E最快 - F最快（合计 %+.2f）'%dEF.sum())
ax.barh(y+0.2,dEFm,0.4,color='#999',label='E中位 - F中位（合计 %+.2f）'%dEFm.sum())
ax.set_yticks(y); ax.set_yticklabels(names); ax.invert_yaxis()
ax.axvline(0,color='k',lw=0.8); ax.grid(axis='x',alpha=0.3)
ax.set_xlabel('秒（正=E更慢）'); ax.set_title('E vs F（同一天两场，同套计时段）',fontsize=11)
ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(0.5,-0.1))
plt.tight_layout(); plt.savefig(f'{FIG}/segment_delta.png',dpi=150); plt.close()

# ---- 4. accel ----
def sm(a,w):
    k=np.ones(w)/w; return np.convolve(np.pad(a,(w//2,w//2),mode='edge'),k,'valid')
def accel_bins(rs):
    V=[];Aa=[]
    for r in rs:
        t=r['t']; keep=np.concatenate([[True],np.diff(t)>1e-6])
        t=t[keep]; v=sm(r['v'][keep],7); 
        m0=(r['t']>=r['t0'])&(r['t']<=r['t0']+r['lt'])
        # own cum approx via sr for zone (imperfect but ok)
        s=r['sr'][keep]
        a=np.gradient(v,t)
        m=(t>=r['t0'])&(t<=r['t0']+r['lt'])
        zone=((s>372)&(s<500))|((s>775)|(s<68)&(t>=r['t0']))
        sel=m&zone&(a>0.2); V+=list(v[sel]); Aa+=list(a[sel])
    V=np.array(V); Aa=np.array(Aa)
    out=[]
    for b in range(44,64,2):
        q=(V>=b)&(V<b+2)
        if q.sum()>20: out.append((b+1, float(np.median(Aa[q]))))
    return out

fig,ax=plt.subplots(figsize=(8,5))
for tag,rs,c in (('E',E,CE),('F',F,CF)):
    b=accel_bins(rs); ax.plot([x[0] for x in b],[x[1] for x in b],'o-',color=c,label='10/17 '+tag)
for pk,c,ls in (('B',CB,'--'),('A','#1f77b4',':'),('D','#9467bd','-.'),('C','#7f7f7f',':')):
    bins=PRIOR[pk]['accel_bins']
    bs=sorted(bins); ax.plot(bs,[bins[b] for b in bs],ls=ls,color=c,label=PRIOR[pk]['tag'])
ax.set_xlabel('速度 km/h'); ax.set_ylabel('加速度 km/h 每秒'); ax.grid(alpha=0.3)
ax.legend(fontsize=8,ncol=2); ax.set_title('同速度下直道加速度（反映车辆/条件）',fontsize=11)
plt.tight_layout(); plt.savefig(f'{FIG}/accel_vs_speed.png',dpi=160); plt.close()

# ---- CSVs ----
for tag,rs in (('E', [r for r in RECS if r['tag']=='E']), ('F',[r for r in RECS if r['tag']=='F'])):
    clean_rs = [r for r in rs if r['vmin']>=28 and r['lt']<65]
    Tclean=np.array([st(r) for r in clean_rs]) if clean_rs else None
    med = np.median(Tclean,0) if Tclean is not None else np.zeros(15)
    with open(f'{tag}_1017_lap_segment_metrics.csv','w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f)
        w.writerow(['session','lap','excluded','lap_time_gps_s','path_length_m','vmax_kmh','vmin_kmh',
                    'segment','type','direction','gate_start_m','gate_end_m','segment_time_s',
                    'delta_vs_session_median_s','delta_vs_B_best_s',
                    'entry_speed_kmh','min_speed_kmh','min_speed_pos_m','exit_speed_kmh',
                    'brake_point_m','path_length_projected_m'])
        for r in rs:
            excl = int(r['vmin']<28 or r['lt']>65)
            for k,sg in enumerate(SEGS):
                d=r['segs_own'][k]; dp=r['segs'][k]
                w.writerow([tag,r['lap'],excl,round(r['lt'],3),round(r['path_len'],1),round(r['vmax'],1),round(r['vmin'],1),
                    sg['name'], 'corner' if sg['kind']=='C' else 'straight', sg.get('dir',''),
                    sg['a'], sg['b'] if sg['b'] is not None else '',
                    round(d['time'],3), round(d['time']-med[k],3) if not excl else '',
                    round(d['time']-Bb[k],3),
                    round(d['v_in'],1),round(d['vmin'],1),round(d['vmin_s'],1),round(d['v_out'],1),
                    '' if np.isnan(d.get('brake_s',np.nan)) else round(d['brake_s'],1),
                    round(dp['path'],2)])
print('figures+csv ok')
