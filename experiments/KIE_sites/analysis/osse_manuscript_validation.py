"""Independent calibration/validation of the manuscript phasor workflow.

No station dynamics. Information improvements change errors on auxiliary
estimates and monthly observations, never the hidden truth distribution.
Transport widths and bounded truth sampling are explicit test scenarios.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import time
import numpy as np
from scipy.special import ndtr, ndtri
from scipy.stats import beta, t as student_t
import osse_manuscript_core as core

ROOT=Path(__file__).resolve().parents[3]
TRUTHS=(1.0039,1.0054)
GROUPS=('S','L','T','O')
SEED=2026102517


def scenarios():
    cells=[dict(name='local',nh=0.,trop=0.,kind='main')]
    for nh in (.04,.06,.08,.10):
        for trop in (0.,.1,.2,.3,.4,.5):
            cells.append(dict(name=f'nh{nh:.2f}_t{trop:.1f}',nh=nh,trop=trop,kind='main'))
    cells.extend([
        dict(name='source_low_edge',nh=.1,trop=.5,kind='stress',edge='source_low'),
        dict(name='source_high_edge',nh=.1,trop=.5,kind='stress',edge='source_high'),
        dict(name='sink_edge',nh=.1,trop=.5,kind='stress',edge='sink'),
    ])
    return cells


def designs():
    out={'baseline':dict.fromkeys(GROUPS,1.)}
    for g in GROUPS:out[f'{g}_x0.1']={k:(.1 if k==g else 1.) for k in GROUPS}
    for scale in (.5,.25,.1,.05,.02):out[f'all_x{scale:g}']=dict.fromkeys(GROUPS,scale)
    out['exact_information']=dict.fromkeys(GROUPS,0.)
    return out


def cell_seed(master,phase,site,cell):
    return np.random.SeedSequence([master,phase,site,cell])


def make_bank(site,scenario,n,seed):
    rng=np.random.default_rng(seed)
    # Bounded proposal is a declared test distribution, not an empirical prior.
    latent=ndtri(rng.uniform(ndtr(-2),ndtr(2),size=(n,len(core.NAMES))))
    truth=core.nominal_parameters()+latent*core.widths()
    truth[:,17]=scenario['nh'];truth[:,18]=scenario['trop']
    edge=scenario.get('edge')
    if edge in ('source_low','source_high'):
        sign=-1 if edge=='source_low' else 1
        truth[:,0]=-62+sign*10
        truth[:,8:11]=core.nominal_parameters()[8:11]+sign*2*core.widths()[8:11]
    if edge=='sink':truth[:,11:14]=[.76,.055,.10]
    truth=core.constrain_parameters(truth)
    return dict(truth=truth,aux_z=rng.normal(size=truth.shape),
                noise_z=rng.normal(size=(n,len(site['t']),2)))


def observation_package(bank,site,scales):
    multiplier=np.ones(len(core.NAMES))
    for g,idx in core.GROUP_INDEX.items():multiplier[idx]=scales[g]
    raw=bank['truth']+bank['aux_z']*core.widths()*multiplier
    auxiliary=core.constrain_parameters(raw)
    noise=bank['noise_z']@np.linalg.cholesky(site['residual_cov']).T*scales['O']
    return dict(auxiliary=auxiliary,aux_raw=raw,noise=noise)


def blind_estimate(monthly,auxiliary,site):
    """Only observed data and estimated nuisance parameters enter this API."""
    return core.invert_phasors(core.fit_observed(monthly,site),auxiliary)


def evaluate_bank(bank,site,truth,scales):
    package=observation_package(bank,site,scales)
    monthly=core.synthesize(truth,bank['truth'],site,package['noise'])
    estimates=blind_estimate(monthly,package['auxiliary'],site)
    projected=np.any(abs(package['auxiliary']-package['aux_raw'])>1e-12,axis=1)
    return estimates,int(projected.sum())


def tolerance_quantile(errors,probability,failure_probability):
    """Order-statistic tolerance bound, without subtracting mean error.

    With confidence 1-failure_probability this bound covers at least the
    specified fraction of absolute errors, for the stated iid cell population.
    Failures are infinite errors, so they cannot disappear from calibration.
    """
    errors=np.asarray(errors,float)
    errors=np.where(np.isfinite(errors),abs(errors),np.inf)
    n=len(errors);k=np.arange(1,n+1)
    lower=beta.ppf(failure_probability,k,n+1-k)
    possible=np.flatnonzero(lower>=probability)
    if not len(possible):raise ValueError('Insufficient calibration size for tolerance guarantee')
    return max(float(np.sort(errors)[possible[0]]),1e-12)


def proportion_interval(k,n,alpha):
    return [float(beta.ppf(alpha/2,k,n-k+1)) if k else 0.,
            float(beta.ppf(1-alpha/2,k+1,n-k)) if k<n else 1.]


def classify(estimates,halfwidth):
    finite=np.isfinite(estimates)
    a=abs(estimates-TRUTHS[0])<=halfwidth
    b=abs(estimates-TRUTHS[1])<=halfwidth
    return np.where(~finite,'failed',np.where(a&b,'both',np.where(a,'A',np.where(b,'B','neither'))))


def metrics(estimates,truth,coverage_width,selection_width,alpha):
    x=np.asarray(estimates,float);n=len(x);finite=np.isfinite(x)
    labels=classify(x,selection_width)
    target='A' if truth==TRUTHS[0] else 'B';wrong='B' if target=='A' else 'A'
    counts={k:int(np.sum(labels==k)) for k in ('A','B','both','neither','failed')}
    covered=int(np.sum(finite&(abs(x-truth)<=coverage_width)))
    ci_correct=proportion_interval(counts[target],n,alpha)
    ci_wrong=proportion_interval(counts[wrong],n,alpha)
    ci_coverage=proportion_interval(covered,n,alpha)
    error=x[finite]-truth
    bias=float(np.mean(error)) if len(error) else None
    if len(error)>1:
        sd=float(np.std(error,ddof=1));margin=float(student_t.ppf(1-alpha/2,len(error)-1)*sd/np.sqrt(len(error)))
        bias_ci=[bias-margin,bias+margin]
    else:sd=None;bias_ci=[None,None]
    bias_pass=bool(finite.all() and len(error)>1 and max(abs(v) for v in bias_ci)<=.00015)
    gates=dict(correct=ci_correct[0]>=.8,wrong=ci_wrong[1]<=.05,
               coverage=ci_coverage[0]>=.95,bias=bias_pass)
    calibration_finite=bool(np.isfinite(coverage_width) and np.isfinite(selection_width))
    if not calibration_finite:gates={k:False for k in gates}
    return dict(n=n,failed=counts['failed'],counts=counts,calibration_finite=calibration_finite,
                correct=counts[target]/n,correct_ci=ci_correct,
                wrong=counts[wrong]/n,wrong_ci=ci_wrong,
                coverage=covered/n,coverage_ci=ci_coverage,
                raw_bias=bias,raw_bias_ci=bias_ci,bias_denominator=int(finite.sum()),
                sd=sd,rmse=float(np.sqrt(np.mean(error**2))) if len(error) else None,
                gates=gates,passes=all(gates.values()))


def json_ready(value):
    """Keep failed/unbounded results representable; null is never a success."""
    if isinstance(value,dict):return {k:json_ready(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [json_ready(v) for v in value]
    if isinstance(value,(float,np.floating)) and not np.isfinite(value):return None
    return value


def run(n_cal=2000,n_val=2000,seed=SEED,output=None):
    started=time.monotonic();cells=scenarios();plans=designs()
    out=Path(output) if output else core.EXPT_DIR/'results/osse_manuscript_validation'
    out.mkdir(parents=True,exist_ok=True)
    # Frozen family includes two sites, both truth directions, all cells/designs.
    count=2*len(cells)*len(plans)*2
    validation_alpha=.05/(count*4)
    calibration_failure=.05/(count*2)
    tolerance_quantile(np.zeros(n_cal),.975,calibration_failure)
    result=dict(metadata=dict(seed=seed,n_cal=n_cal,n_val=n_val,designs=plans,cells=cells,
        truth_distribution='bounded +/-2 reference-width Gaussian proposals, projected physically; same across information designs',
        scopes='Conditional on manuscript annual phasors, fixed corrected D sink anchor, stated nuisance/noise distributions and finite grid; no dynamical model',
        uncertainty_parameters=[dict(name=k,width=float(w),group=next(g for g,idx in core.GROUP_INDEX.items() if i in idx),
            provenance='S test scenario' if i>=17 else 'R inherited code setting') for i,(k,w) in enumerate(zip(core.NAMES,core.widths()))],
        calibration='independent stream; max per-cell absolute-error tolerance bounds over both truths; 95% coverage and conservative 97.5% selection targets; point estimates unshifted',
        validation_alpha=validation_alpha,calibration_failure_probability=calibration_failure,
        bias_ci='Student t Monte Carlo approximation; no distribution-free mean-bias guarantee for heavy-tailed ratios',
        coverage_gate='simultaneous binomial lower bound >=0.95; conservative overcoverage allowed only if discrimination also passes',
        physical_projection='nearest simplex for four sink fractions and three response weights; nonlinear projection bias remains in raw results',
        input_sha256={},code_sha256={},git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        sites={}),results=[],truth_hashes={})
    input_paths=[core.EXPT_DIR/'data/wetland_seasonality.json',core.EXPT_DIR/'supplementary_information_first_draft.md']
    records={}
    for si,code in enumerate(('CGO','SPO')):
        site=core.load_site(code);input_paths.append(Path(site['input_path']))
        result['metadata']['sites'][code]=dict(paired_months=len(site['t']),residual_cov=site['residual_cov'].tolist(),
            sink_d=[site['sink_d'].real,site['sink_d'].imag],
            role='real values set residual covariance and common D signal anchor; no A/B evidence inference on observed carbon isotope series')
        banks={}
        for phase,n in ((0,n_cal),(1,n_val)):
            for ci,cell in enumerate(cells):
                bank=make_bank(site,cell,n,cell_seed(seed,phase,si,ci));banks[phase,ci]=bank
                result['truth_hashes'][f'{code}/{phase}/{cell["name"]}']=hashlib.sha256(bank['truth'].tobytes()).hexdigest()
        for name,scale in plans.items():
            calibration=[];cal_records=[]
            for ci,cell in enumerate(cells):
                for truth in TRUTHS:
                    estimated,projections=evaluate_bank(banks[0,ci],site,truth,scale)
                    error=estimated-truth
                    width=tolerance_quantile(error,.95,calibration_failure)
                    selection=tolerance_quantile(error,.975,calibration_failure)
                    calibration.append(dict(cell=cell['name'],truth=truth,coverage_width=width,selection_width=selection,
                        failed=int(np.sum(~np.isfinite(error))),projected_auxiliary=projections))
                    cal_records.append(estimated)
            coverage_width=max(c['coverage_width'] for c in calibration)
            selection_width=max(c['selection_width'] for c in calibration)
            row=dict(site=code,design=name,scales=scale,coverage_halfwidth=coverage_width,selection_halfwidth=selection_width,
                calibration=calibration,cells=[],averages={})
            val_records=[];main_values={a:[] for a in TRUTHS}
            for ci,cell in enumerate(cells):
                for truth in TRUTHS:
                    estimated,projections=evaluate_bank(banks[1,ci],site,truth,scale)
                    score=metrics(estimated,truth,coverage_width,selection_width,validation_alpha)
                    row['cells'].append(dict(cell=cell['name'],kind=cell['kind'],truth=truth,projected_auxiliary=projections,**score))
                    val_records.append(estimated)
                    if cell['kind']=='main':main_values[truth].append(estimated)
            # Main-grid population is a frozen equal mixture; rate CIs use cell-wise
            # simultaneous bounds averaged across strata, not iid pooled binomial.
            for truth,values in main_values.items():
                members=[x for x in row['cells'] if x['kind']=='main' and x['truth']==truth]
                pooled=np.concatenate(values)
                avg=dict(n=len(pooled),failed=int(np.sum(~np.isfinite(pooled))),raw_bias=float(np.mean(pooled-truth)) if np.isfinite(pooled).all() else None,
                         scope='equal-weight mean of 25 fixed strata; stress cells excluded')
                for measure in ('correct','wrong','coverage'):
                    avg[measure]=float(np.mean([x[measure] for x in members]))
                    avg[measure+'_ci']=[float(np.mean([x[measure+'_ci'][j] for x in members])) for j in (0,1)]
                row['averages'][str(truth)]=avg
            row['all_cells_pass']=all(x['passes'] for x in row['cells'])
            row['failing_cell_directions']=sum(not x['passes'] for x in row['cells'])
            result['results'].append(row)
            records[f'{code}__{name}__cal']=np.array(cal_records)
            records[f'{code}__{name}__val']=np.array(val_records)
            print(code,name,'selection width',f'{selection_width:.6g}','failed gates',row['failing_cell_directions'],flush=True)
    for p in input_paths:
        result['metadata']['input_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for p in [Path(__file__),Path(core.__file__),Path(core.phase6.__file__)]:
        result['metadata']['code_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    result['metadata']['elapsed_seconds']=time.monotonic()-started
    result['metadata']['number_estimates']=sum(v.size for v in records.values())
    result['metadata']['record_order']='within each array: cell order from metadata, then truths A/B; columns replicate index. Seed phase0=calibration,1=validation.'
    (out/'summary.json').write_text(json.dumps(json_ready(result),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    np.savez_compressed(out/'estimates.npz',**records)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--n-cal',type=int,default=2000);parser.add_argument('--n-val',type=int,default=2000);parser.add_argument('--seed',type=int,default=SEED);parser.add_argument('--output')
    args=parser.parse_args()
    if args.n_cal<2 or args.n_val<2:parser.error('sample counts must be >=2')
    run(args.n_cal,args.n_val,args.seed,args.output)
