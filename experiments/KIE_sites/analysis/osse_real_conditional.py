"""Apply frozen OSSE decision intervals to unchanged real-data point estimates.

This is conditional scenario analysis, not new real-data coverage validation.
No random draws, refitting of thresholds, or shrinking of real observations.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scienceplots
import osse_literature_correction as e

v = e.v
ROOT = Path(__file__).resolve().parents[3]
OUT = v.core.EXPT_DIR / 'results/osse_real_conditional'
BASE = v.core.EXPT_DIR / 'results/osse_corrected_relaxation'
SELECTED = {'SPO': 'all_x1.25', 'CGO': 'all_x1.5'}


def run():
    OUT.mkdir(exist_ok=True)
    frozen = json.loads((BASE/'frozen.json').read_text(encoding='utf-8'))
    confirmed = json.loads((BASE/'confirmation.json').read_text(encoding='utf-8'))
    audit = json.loads((v.core.EXPT_DIR/'results/osse_real_feasibility/evidence.json').read_text(encoding='utf-8'))
    for name, digest in audit['input_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    rows, summary = [], {}
    inputs = [BASE/'frozen.json', BASE/'confirmation.json', v.core.EXPT_DIR/'data/wetland_seasonality.json',
              Path(__file__), Path(e.__file__), Path(v.__file__), Path(v.core.__file__), Path(v.core.phase6.__file__)]
    for code, design in SELECTED.items():
        plan = next(r for r in frozen['results'] if r['site']==code and r['design']==design)
        confirmation = next(r for r in confirmed['results'] if r['site']==code and r['design']==design)
        assert confirmation['all_cells_pass']
        for key in ['selection_halfwidth', 'coverage_halfwidth', 'scales']:
            assert plan[key] == confirmation[key]
        site = v.core.load_site(code)
        inputs.append(Path(site['input_path']))
        observed_copy = site['observed'].copy()
        p, w = e.parameters('literature')
        for cell in v.scenarios():
            q = p.copy()
            q[17:19] = [cell['nh'], cell['trop']]
            if cell.get('edge') in ['source_low', 'source_high']:
                sign = -1 if cell['edge']=='source_low' else 1
                q[0] += sign*2*w[0]
                q[8:11] += sign*2*w[8:11]
            if cell.get('edge')=='sink':
                q[11:14] = [.76, .055, .10]
            q = v.core.constrain_parameters(q)
            estimate = float(v.blind_estimate(site['observed'], q, site))
            half = plan['selection_halfwidth']
            label = str(v.classify(np.array([estimate]), half)[0])
            # Independent scalar check of the frozen interval rule.
            compatible = [abs(estimate-a)<=half for a in v.TRUTHS]
            expected = {(True,False):'A', (False,True):'B', (True,True):'both', (False,False):'neither'}[tuple(compatible)]
            assert label == expected and np.isfinite(estimate)
            rows.append(dict(site=code, design=design, scenario=cell['name'], kind=cell['kind'],
                             w_nh=cell['nh'], w_trop=cell['trop'], alpha=estimate,
                             selection_low=estimate-half, selection_high=estimate+half,
                             selection_halfwidth=half, coverage_halfwidth=plan['coverage_halfwidth'],
                             coverage_low=estimate-plan['coverage_halfwidth'], coverage_high=estimate+plan['coverage_halfwidth'],
                             compatible_A=bool(compatible[0]), compatible_B=bool(compatible[1]), classification=label,
                             corrected_D_amplitude=float(abs(v.core.fit_observed(site['observed'],site)[1]-v.core.source_phasors(q)[1])),
                             auxiliary_center=q.tolist()))
        assert np.array_equal(site['observed'], observed_copy)
        main = [r for r in rows if r['site']==code and r['kind']=='main']
        summary[code] = dict(design=design, scales=plan['scales'], selection_halfwidth=plan['selection_halfwidth'],
                             local=main[0], main_counts={k:sum(r['classification']==k for r in main) for k in ['A','B','both','neither','failed']},
                             main_alpha_range=[min(r['alpha'] for r in main),max(r['alpha'] for r in main)],
                             osse_fixed_D_anchor_amplitude=float(abs(site['sink_d'])))
    assert len(rows)==56
    result = dict(scope='Conditional fixed-center scenario analysis; frozen OSSE intervals are transferred, not real-data validated confidence intervals.',
                  random_seed=None, selected_before_real_data_analysis=SELECTED, summaries=summary, rows=rows,
                  sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    frame = pd.DataFrame(rows).drop(columns='auxiliary_center')
    frame.to_csv(OUT/'scenarios.csv',index=False,encoding='utf-8')
    plt.style.use(['science','no-latex'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig, axes = plt.subplots(1,2,figsize=(12,9),sharey=True,sharex=True)
    palette={'A':'#0072B2','B':'#D55E00','both':'#009E73','neither':'#888888'}
    for ax, code in zip(axes,SELECTED):
        records=[r for r in rows if r['site']==code]
        for i,r in enumerate(records):
            ax.plot([r['selection_low'],r['selection_high']],[i,i],color=palette[r['classification']],lw=1.5)
            ax.scatter(r['alpha'],i,color=palette[r['classification']],s=18,zorder=3)
        for val,label,color in zip(v.TRUTHS,['A = 1.0039','B = 1.0054'],['#0072B2','#D55E00']):
            ax.axvline(val,color=color,ls='--',lw=1,label=label)
        ax.axhline(24.5,color='black',lw=.6)
        ax.set_title(code+' | '+SELECTED[code],fontsize=12)
        ax.set_xlabel('Inferred carbon KIE (OH)')
        ax.grid(axis='x',alpha=.15)
        ax.legend(loc='lower left',fontsize=8)
    axes[0].set_yticks(range(28),[r['scenario'] for r in rows[:28]])
    axes[0].invert_yaxis()
    fig.suptitle('Real observations under hypothetical improved precision',fontsize=15,y=.98)
    fig.text(.5,.94,'Unchanged real-data centers; frozen OSSE selection intervals; all pre-existing scenarios shown',ha='center',fontsize=10)
    fig.text(.16,.025,'Blue: A only | Orange: B only | Green: both | Grey: neither. Bottom three rows: stress scenarios.\nScenario counts are not probabilities. Interval coverage for real observations has not been established.',fontsize=9)
    fig.subplots_adjust(left=.18,right=.98,top=.9,bottom=.11,wspace=.13)
    for ext in ['png','pdf','svg']:
        fig.savefig(OUT/f'conditional_real_ab.{ext}',dpi=200,facecolor='white')
    plt.close(fig)
    for code,s in summary.items():
        print(code, 'local',s['local']['alpha'],s['local']['classification'],'counts',s['main_counts'])


if __name__=='__main__':
    run()
