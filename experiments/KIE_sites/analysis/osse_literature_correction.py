"""Versioned literature error conventions; unchanged manuscript forward/inverse."""
from pathlib import Path
import argparse
import json
import hashlib
import numpy as np
from scipy.special import ndtr, ndtri
import osse_conditional_requirements as m
v=m.v
OUT=v.core.EXPT_DIR/'results/osse_literature_correction'
SEED=2026102602
VERSIONS=('legacy','literature')


def parameters(version):
    p=v.core.nominal_parameters();w=v.core.widths()
    if version=='literature':
        p[0]=-62.1;w[0]=.7
        w[8:11]/=1.96
        w[14]=.018/2
        w[15]=.002/2
        w[16]=.041/2
    elif version!='legacy':raise ValueError(version)
    return p,w


def plans(site):
    return {'baseline':dict.fromkeys(v.GROUPS,1.),'all_2pct':dict.fromkeys(v.GROUPS,.02),
            'all_5pct':dict.fromkeys(v.GROUPS,.05),
            'relaxed':dict(zip(v.GROUPS,(.05,.125,.075,.05) if site=='SPO' else (.075,.16,.075,.05)))}


def bank(site,cell,n,seed,version):
    p,w=parameters(version);rng=np.random.default_rng(seed)
    latent=ndtri(rng.uniform(ndtr(-2),ndtr(2),size=(n,len(p))))
    truth=p+latent*w
    truth[:,17]=cell['nh'];truth[:,18]=cell['trop']
    if cell.get('edge') in ('source_low','source_high'):
        sign=-1 if cell['edge']=='source_low' else 1
        truth[:,0]=p[0]+sign*2*w[0]
        truth[:,8:11]=p[8:11]+sign*2*w[8:11]
    if cell.get('edge')=='sink':truth[:,11:14]=[.76,.055,.10]
    return dict(truth=v.core.constrain_parameters(truth),aux_z=rng.normal(size=truth.shape),
                noise_z=rng.normal(size=(n,len(site['t']),2)))


def estimate(b,site,truth,scales,version):
    _,w=parameters(version);mult=np.ones(len(w))
    for g,idx in v.core.GROUP_INDEX.items():mult[idx]=scales[g]
    raw=b['truth']+b['aux_z']*w*mult
    aux=v.core.constrain_parameters(raw)
    noise=b['noise_z']@np.linalg.cholesky(site['residual_cov']).T*scales['O']
    y=v.core.synthesize(truth,b['truth'],site,noise)
    return v.blind_estimate(y,aux,site),int(np.any(abs(aux-raw)>1e-12,axis=1).sum())


def evaluate(site,banks,plan,version,calibrate):
    row=dict(plan);details=[];records=[]
    for cell,b in zip(v.scenarios(),banks):
        for truth in v.TRUTHS:
            x,proj=estimate(b,site,truth,plan['scales'],version);records.append(x)
            d=dict(cell=cell['name'],truth=truth,projected_auxiliary=proj)
            if calibrate:
                e=np.sort(np.where(np.isfinite(x),abs(x-truth),np.inf))
                d.update(coverage_width=max(float(e[m.calibration_rank(len(e),.95)]),1e-12),
                         selection_width=max(float(e[m.calibration_rank(len(e),.975)]),1e-12))
            else:d.update(v.metrics(x,truth,plan['coverage_halfwidth'],plan['selection_halfwidth'],m.ALPHA))
            details.append(d)
    if calibrate:
        row.update(coverage_halfwidth=max(d['coverage_width'] for d in details),
                   selection_halfwidth=max(d['selection_width'] for d in details),calibration=details)
    else:row.update(cells=details,all_cells_pass=all(d['passes'] for d in details))
    return row,np.array(records)


def run(stage):
    OUT.mkdir(exist_ok=True);target=OUT/('frozen.json' if stage=='prepare' else 'confirmation.json')
    if target.exists():raise FileExistsError(target)
    meta=m.metadata()
    meta.update(seed=SEED,versions=VERSIONS,new_script_sha256=m.hash_file(Path(__file__)),
                parameter_versions={s:dict(nominal=parameters(s)[0].tolist(),sigma=parameters(s)[1].tolist()) for s in VERSIONS},
                scope='Same workflow and configurations; paired random draws across versions. Truth reference widths change between versions, not between information designs.',
                plans={s:plans(s) for s in ('CGO','SPO')},
                phases={'calibration':0,'independent_confirmation':1},
                selection='Four prespecified configurations per site, both parameter versions; no screening or adaptive search',
                n_screen=0)
    frozen=None
    if stage=='confirm':
        frozen=json.loads((OUT/'frozen.json').read_text())
        assert frozen['metadata']==json.loads(json.dumps(meta))
        meta={**meta,'frozen_sha256':m.hash_file(OUT/'frozen.json')}
    result=dict(metadata=meta,results=[],truth_hashes={})
    phase=0 if stage=='prepare' else 1;n=m.N_CAL if phase==0 else m.N_CONFIRM
    for si,code in enumerate(('CGO','SPO')):
        site=v.core.load_site(code);records={}
        for version in VERSIONS:
            banks=[bank(site,cell,n,v.cell_seed(SEED,phase,si,ci),version) for ci,cell in enumerate(v.scenarios())]
            for ci,b in enumerate(banks):result['truth_hashes'][f'{code}/{version}/{ci}']=hashlib.sha256(b['truth'].tobytes()).hexdigest()
            for name,scales in plans(code).items():
                plan=dict(design=name,scales=scales,site=code,version=version)
                if frozen:
                    old=next(r for r in frozen['results'] if all(r[k]==plan[k] for k in ('site','version','design')))
                    plan.update({k:old[k] for k in ('coverage_halfwidth','selection_halfwidth')})
                row,raw=evaluate(site,banks,plan,version,phase==0)
                result['results'].append(row);records[f'{version}__{name}']=raw
                print(stage,code,version,name,row.get('all_cells_pass','calibrated'),flush=True)
        np.savez_compressed(OUT/f'{stage}_{code}.npz',**records)
    result['number_estimates']=len(result['results'])*56*n
    m.write_json(target,result)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','confirm'])
    run(parser.parse_args().stage)
