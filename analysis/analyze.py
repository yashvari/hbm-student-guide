"""Run: python analyze.py. Dependencies: numpy, scipy, matplotlib.
Reads supplied data only; does not modify simulation inputs. See README.md.
"""
from pathlib import Path
import csv, io, json, zipfile, hashlib
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
D=ROOT/'data'
with (D/'head_drop_final_history.csv').open() as f:
    r=csv.reader(f); headers=next(r); a=np.array(list(r),float)
assert np.isfinite(a).all(), 'Nonfinite history values'
t=a[:,0]; assert np.all(np.diff(t)>0)
def col(name): return a[:,headers.index(name)]
def match(marker,suffix):
    ids=[i for i,h in enumerate(headers) if marker in h and h.strip().split()[-1]==suffix]
    assert len(ids)==1,(marker,suffix,ids)
    return a[:,ids[0]]
def pairs(path,delimiter=',',skip=0,cols=(0,1)):
    rows=list(csv.reader(path.open(),delimiter=delimiter))[skip:]
    x=np.array([[float(r[i]) for i in cols] for r in rows if len(r)>max(cols) and all(r[i].strip() for i in cols)])
    return x[np.argsort(x[:,0])]
# Reuse the named upstream implementation without importing unrelated Dynasaur dependencies.
# The original wheel and its GPL licence are retained in vendor/.
wheel=ROOT/'vendor/dynasaur-1.3.18-py3-none-any.whl'
with zipfile.ZipFile(wheel) as z: source=z.read('dynasaur/calc/cfc.py')
ns={}; exec(compile(source,'dynasaur/calc/cfc.py','exec'),ns)
# Actual output times vary slightly. Interpolate onto 1100 uniformly spaced points.
u=np.linspace(t[0],t[-1],len(t))
raw_components=np.column_stack([match('TH_NODE_BNDOUT', 'REAC'+axis) for axis in 'XYZ'])
components=np.column_stack([np.interp(u,t,raw_components[:,i]) for i in range(3)])
filt=ns['CFC'](1000,(u[1]-u[0])*1e-3).filter(components.T,u[:,None],1000,False).T
force=np.linalg.norm(filt,axis=1); raw=np.linalg.norm(raw_components,axis=1)
exp=pairs(D/'experiment_average.csv'); exp[:,0]*=1000;exp[:,1]/=1000
upper=pairs(D/'experiment_corridor.csv',';',1,(0,1));lower=pairs(D/'experiment_corridor.csv',';',1,(2,3))
for x in [upper,lower]: x[:,0]*=1000;x[:,1]/=1000
refs=[pairs(D/'lsdyna_mat124.csv',';',4),pairs(D/'lsdyna_mat81.csv',';',4)]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'axes.titleweight':'bold'})
TEAL='#007f86'; BLUE='#4169ae'; ORANGE='#c0762b'; GRAY='#374151'
def save(fig,name,note):
    fig.text(.08,.02,note,fontsize=8,color=GRAY,va='bottom')
    fig.savefig(ROOT.parent/'figures'/(name+'.png'),dpi=240)
    fig.savefig(ROOT.parent/'figures'/(name+'.pdf'))
    plt.close(fig)
fig,ax=plt.subplots(figsize=(10,6.8));fig.subplots_adjust(left=.09,right=.97,bottom=.19,top=.86)
g=np.linspace(max(upper[0,0],lower[0,0]),min(upper[-1,0],lower[-1,0]),700)
ax.fill_between(g,np.interp(g,lower[:,0],lower[:,1]),np.interp(g,upper[:,0],upper[:,1]),color='#dde2e7',label='Published experimental corridor')
ax.plot(exp[:,0],exp[:,1],color='#222222',lw=2,label='Published experimental average')
for x,color,label in zip(refs,[BLUE,ORANGE],['LS-DYNA: cortical MAT124','LS-DYNA: cortical MAT81']): ax.plot(x[:,0]-1,x[:,1],lw=1.7,color=color,ls='--',label=label+' (published)')
ax.plot(t-1,raw,color=TEAL,lw=.6,alpha=.28,label='OpenRadioss: raw support reaction')
ax.plot(u-1,force,color=TEAL,lw=2.4,label='OpenRadioss: CFC1000 support reaction')
ax.set(xlim=(0,10),ylim=(0,None),xlabel='Comparison time [ms] — simulation time minus 1 ms',ylabel='Resultant support reaction [kN]')
ax.grid(alpha=.17);ax.legend(fontsize=8.7,frameon=False,loc='upper right')
fig.suptitle('Head lateral drop at 3.5 m/s | Force comparison',x=.09,ha='left',fontsize=17,fontweight='bold')
save(fig,'01_force_comparison','Experimental data and LS-DYNA curves: VIVA+ Yoganandan-2004 validation archive.\nAll simulations use the published −1 ms plotting offset; no peak alignment. OpenRadioss uses Dynasaur 1.3.18 CFC1000.\nAdapted educational model: reference model/version equivalence and experimental agreement are not established.')
fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True,gridspec_kw={'height_ratios':[2,1,1]});fig.subplots_adjust(left=.11,right=.96,bottom=.14,top=.9,hspace=.23)
for name,color in [('INTERNAL ENERGY',ORANGE),('KINETIC ENERGY',BLUE)]:axs[0].plot(t,col(name),label=name.title(),color=color,lw=2)
axs[0].set_ylabel('Energy [J]');axs[0].legend(frameon=False,ncol=2)
for name,color in [('HOURGLASS ENERGY','#9467bd'),('CONTACT ENERGY',TEAL),('EXTERNAL WORK',GRAY)]:axs[1].plot(t,col(name),label=name.title(),color=color,lw=1.6)
axs[1].set_ylabel('Energy / work [J]');axs[1].legend(frameon=False,ncol=3,fontsize=8.5)
axs[2].plot(t,col('PERCENTAGE ADDED MASS'),color=TEAL);axs[2].set_ylabel('Added mass [%]');axs[2].set_xlabel('Simulation time [ms]');axs[2].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
for ax in axs:ax.grid(alpha=.17);ax.set_xlim(0,11)
fig.suptitle('Numerical checks | Energy histories and added mass',fontsize=16,fontweight='bold')
save(fig,'02_energy_checks','Kinetic energy = energy of motion; internal energy = energy stored or dissipated within the model.\nGlobal values include the head and test setup. Small negative added mass is numerical round-off (about −0.3 mg).\nThese traces are diagnostics; no claim of complete energy-balance validation is made.')
fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True);fig.subplots_adjust(left=.11,right=.96,bottom=.20,top=.9,hspace=.26)
node='1090010'
axs[0].plot(t,match(node,'DZ'),color=TEAL,lw=2);axs[0].set_ylabel('Z displacement [mm]')
axs[1].plot(t,match(node,'VZ'),color=BLUE,lw=2);axs[1].axhline(0,color=GRAY,lw=.7,ls=':');axs[1].set_ylabel('Z velocity [m/s]')
acc=np.column_stack([match(node,'A'+x) for x in 'XYZ']);accg=np.linalg.norm(acc,axis=1)/.00980665
acc_uniform=np.column_stack([np.interp(u,t,acc[:,i]) for i in range(3)])
# SAE J211-1 (1995), Appendix C coefficient equations; two-pole section
# run forward/backward. Reflect >=10 ms about endpoint values for startup.
dt_s=(u[1]-u[0])*1e-3
wa=np.tan(np.pi*1000*2.0775*dt_s)
den=1+np.sqrt(2)*wa+wa*wa
bb=np.array([wa*wa,2*wa*wa,wa*wa])/den
aa=np.array([1,2*(wa*wa-1)/den,(1-np.sqrt(2)*wa+wa*wa)/den])
pad=int(np.ceil(.010/dt_s)); assert pad<len(u)-1
acc_filtered=signal.filtfilt(bb,aa,acc_uniform,axis=0,padtype='odd',padlen=pad)
acc_filtered_g=np.linalg.norm(acc_filtered,axis=1)/.00980665
assert np.isfinite(acc_filtered_g).all()
axs[2].plot(t,accg,color='#b8bec5',alpha=.45,lw=.7,label='Raw')
axs[2].plot(u,acc_filtered_g,color=ORANGE,lw=2,label='CFC1000: components filtered first')
axs[2].legend(frameon=False,fontsize=8,loc='upper right')
axs[2].set_ylabel('Resultant acceleration [g]');axs[2].set_xlabel('Simulation time [ms]')
for ax in axs:ax.grid(alpha=.17);ax.set_xlim(0,11)
fig.suptitle('Head motion | Global accelerometer node 1090010',fontsize=16,fontweight='bold')
save(fig,'03_head_motion','Displacement and velocity are raw; acceleration uses CFC1000 on X/Y/Z before calculating the resultant.\nForward–backward Butterworth, uniform resampling, 10 ms endpoint reflection. Gravity retained; 1 g = 0.00980665 mm/ms².\nSAE J211-style digital processing; not certification of the model or measurement channel. No injury claim.')
fig,ax=plt.subplots(figsize=(10,6.4));fig.subplots_adjust(left=.1,right=.96,bottom=.21,top=.86)
ax.plot(t,accg,color='#b8bec5',alpha=.55,lw=.8,label='Raw resultant')
ax.plot(u,acc_filtered_g,color=ORANGE,lw=2.3,label='CFC1000 — X/Y/Z filtered before resultant')
ax.set(xlim=(0,11),ylim=(0,None),xlabel='Simulation time [ms]',ylabel='Resultant head acceleration [g]')
ax.grid(alpha=.17);ax.legend(frameon=False,fontsize=9)
fig.suptitle('Head acceleration | Raw and CFC1000 filtered',fontsize=17,fontweight='bold')
save(fig,'04_acceleration_filtered','Node 1090010, global acceleration. CFC1000 selected from head-impact testing practice.\nSAE J211-style forward–backward filter; 10 ms endpoint reflection; gravity retained.\nThe filter suppresses fast oscillations. It does not establish experimental agreement or injury validity.')
with (ROOT/'processed_head_acceleration.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['simulation_time_ms','AX_CFC1000_mm_ms2','AY_CFC1000_mm_ms2','AZ_CFC1000_mm_ms2','resultant_CFC1000_g']);w.writerows(np.column_stack([u,acc_filtered,acc_filtered_g]))
series=[('Experiment average',exp[:,0],exp[:,1]),('Published LS-DYNA MAT124',refs[0][:,0]-1,refs[0][:,1]),('Published LS-DYNA MAT81',refs[1][:,0]-1,refs[1][:,1]),('OpenRadioss CFC1000',u-1,force),('OpenRadioss raw',t-1,raw)]
with (ROOT/'force_metrics.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['series','peak_force_kN','time_of_peak_comparison_ms','peak_difference_from_experimental_average_percent'])
 for name,x,y in series:
  ix=np.argmax(y);w.writerow([name,y[ix],x[ix],100*(y[ix]/exp[:,1].max()-1)])
with (ROOT/'processed_support_force.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['simulation_time_ms','comparison_time_ms','support_resultant_CFC1000_kN']);w.writerows(zip(u,u-1,force))
metrics={'rows':len(t),'columns':len(headers),'all_values_finite':bool(np.isfinite(a).all()),'final_time_ms':t[-1], 'raw_dt_min_ms':np.diff(t).min(),'raw_dt_max_ms':np.diff(t).max(),'uniform_dt_ms':u[1]-u[0],'mass_initial_kg':col('MASS')[0],'mass_final_kg':col('MASS')[-1],'initial_kinetic_energy_J':col('KINETIC ENERGY')[0],'final_internal_energy_J':col('INTERNAL ENERGY')[-1],'final_kinetic_energy_J':col('KINETIC ENERGY')[-1],'final_hourglass_energy_J':col('HOURGLASS ENERGY')[-1],'peak_hourglass_over_initial_KE_percent':100*np.max(np.abs(col('HOURGLASS ENERGY')))/col('KINETIC ENERGY')[0], 'final_Z_velocity_m_s':match(node,'VZ')[-1],'peak_raw_acceleration_g':accg.max(),'peak_raw_contact_normal_resultant_kN':np.linalg.norm(np.column_stack([match('100000 impactor contact','FN'+x) for x in 'XYZ']),axis=1).max()}
metrics.update({'peak_CFC1000_acceleration_g':float(acc_filtered_g.max()),'peak_CFC1000_acceleration_time_ms':float(u[np.argmax(acc_filtered_g)]),'acceleration_padding_samples_each_end':pad})
(ROOT/'numerical_checks.json').write_text(json.dumps(metrics,indent=2)+'\n')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.iterdir())}
manifest[str(wheel.relative_to(ROOT))]=hashlib.sha256(wheel.read_bytes()).hexdigest()
(ROOT/'input_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print((ROOT/'force_metrics.csv').read_text());print(json.dumps(metrics,indent=2))
