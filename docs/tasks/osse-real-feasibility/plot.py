"""Plot the audited evidence without modifying scientific calculations."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter
import scienceplots

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'experiments/KIE_sites/results/osse_real_feasibility'
evidence = json.loads((OUT/'evidence.json').read_text(encoding='utf-8'))
for name, digest in evidence['input_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
sites = evidence['sites']
colors = {'SPO': '#0072B2', 'CGO': '#D55E00'}
plt.style.use(['science', 'no-latex'])
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12,
                     'axes.labelsize': 10, 'savefig.dpi': 220})
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
fig.subplots_adjust(left=.09, right=.97, top=.85, bottom=.19, wspace=.32, hspace=.58)
fig.suptitle('Can available evidence meet the tested A/B discrimination conditions?', fontsize=16, y=.98)
fig.text(.5, .936, 'Current station residuals exceed the tested targets; several auxiliary constraints remain unverified.',
         ha='center', fontsize=11)
legend = [Line2D([0],[0], marker='o', color='none', markerfacecolor='#444444', markeredgecolor='#444444', label='Current monthly residual'),
          Line2D([0],[0], marker='D', color='none', markerfacecolor='white', markeredgecolor='#444444', label='Tested OSSE target')]
fig.legend(handles=legend, loc='upper center', bbox_to_anchor=(.5,.91), ncol=2, frameon=False)
for k, title in enumerate(['(a) Carbon isotope residual', '(b) Hydrogen isotope residual']):
    ax = axes[0,k]
    for y, (name, d) in enumerate(sites.items()):
        current = d['actual_residual_sigma_permil_C_D'][k]
        target = d['target_residual_sigma_permil_C_D'][k]
        assert np.isclose(current/target, d['actual_to_target_sigma_ratio'])
        ax.plot([target,current],[y,y], color=colors[name], lw=3, alpha=.5)
        ax.scatter(current,y,c=colors[name],s=65,zorder=3)
        ax.scatter(target,y,facecolors='white',edgecolors=colors[name],marker='D',s=65,zorder=3)
        fmt = '.5f' if k==0 else '.3f'
        ax.annotate(format(target,fmt),(target,y),xytext=(0,-22),textcoords='offset points',ha='center',fontsize=9)
        ax.annotate(format(current,fmt),(current,y),xytext=(0,-22),textcoords='offset points',ha='center',fontsize=9)
        ax.text(np.sqrt(current*target), y+.17, f"{d['actual_to_target_sigma_ratio']:.2f} times target",ha='center',fontsize=10,color=colors[name])
    ax.set_xscale('log')
    ax.set_xlim((.0025,.16) if k==0 else (.10,5))
    ax.set_xticks([.005,.01,.05,.1] if k==0 else [.1,.2,.5,1,2,5])
    ax.set_xticklabels(['0.005','0.01','0.05','0.1'] if k==0 else ['0.1','0.2','0.5','1','2','5'])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylim(-.55,1.5)
    ax.set_yticks([0,1], ['SPO','CGO'])
    ax.set_xlabel('Monthly residual standard deviation (per mil; log scale)')
    ax.set_title(title,loc='left',pad=12)
    ax.grid(axis='x',which='major',alpha=.15)

ax = axes[1,0]
labels = ['O: observed residuals', 'S: cited source-isotope widths', 'L: cited laboratory KIE widths']
keys = ['actual_to_target_sigma_ratio','source_reference_to_target_sigma_ratio','sink_KIE_reference_to_target_sigma_ratio']
for i,(name,d) in enumerate(sites.items()):
    y=np.arange(3)+(i-.5)*.26
    vals=[d[key] for key in keys]
    ax.barh(y, vals, height=.24, color=colors[name], label=name, alpha=.9)
    for yy,v in zip(y,vals):ax.text(v+.25,yy,f'{v:.2f}',va='center',fontsize=9)
ax.axvline(1,color='#555555',ls='--',lw=1)
ax.set_yticks(np.arange(3),labels,fontsize=9)
ax.invert_yaxis();ax.set_xlim(0,19)
ax.set_xlabel('Available / target standard deviation')
ax.set_title('(c) Size of the precision gap',loc='left',pad=12)
ax.legend(frameon=False,loc='lower right',fontsize=9)
ax.grid(axis='x',alpha=.15)

ax = axes[1,1];ax.axis('off')
ax.set_title('(d) Evidence still needed',loc='left',pad=12)
blocks=[('SOURCE / SINK', 'Emission-seasonality errors and effective sink fractions:\nno verified station-specific precision at the target level.'),
        ('TRANSPORT', 'NH-response lag target: SPO 1.43 days; CGO 1.71 days.\nLag and response-weight precision remain unverified.'),
        ('OBSERVATION SUPPORT', 'SPO: 33 paired months; median 3 D samples/month.\nCGO: 29 paired months; median 2 D samples/month.'),
        ('INTERPRETATION', 'Conditional OSSE success is established.\nReal-data A/B discrimination is not yet demonstrated.')]
for y,(heading,body) in zip([.98,.72,.46,.20],blocks):
    ax.text(0,y,heading,transform=ax.transAxes,va='top',fontsize=9,fontweight='bold',color='#555555')
    ax.text(0,y-.075,body,transform=ax.transAxes,va='top',fontsize=9,linespacing=1.55)
fig.text(.09,.055,'Targets: SPO all_x1.25; CGO all_x1.5. These are tested passing configurations, not proven feasibility boundaries.\nO includes unexplained monthly variation, not instrument noise alone. S/L ratios compare cited widths, not measured station errors.',fontsize=9,linespacing=1.6)
for ext in ['png','pdf','svg']:
    fig.savefig(OUT/f'feasibility_gap.{ext}',facecolor='white')
plt.close(fig)
print('Verified input hashes and ratios; saved feasibility_gap.png/pdf/svg')
