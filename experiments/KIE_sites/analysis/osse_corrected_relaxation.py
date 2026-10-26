"""Fixed local relaxation using the literature-normalized error version."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import osse_literature_correction as e
OUT=e.OUT.parent/'osse_corrected_relaxation'
SEED=2026102603


def plans(code):
    anchor=e.plans(code)['relaxed'];p={'control':dict(anchor)}
    for g in e.v.GROUPS:
        for f in (1.25,1.5,2.):p[f'{g}_x{f:g}']={k:round(v*(f if k==g else 1),8) for k,v in anchor.items()}
    for f in (1.1,1.25,1.5):p[f'all_x{f:g}']={k:round(v*f,8) for k,v in anchor.items()}
    assert len(p)==16 and all(all(s[g]>=anchor[g] for g in e.v.GROUPS) for s in p.values())
    return p


def run(stage):
    OUT.mkdir(exist_ok=True);target=OUT/('frozen.json' if stage=='prepare' else 'confirmation.json')
    if target.exists():raise FileExistsError(target)
    original=json.loads((e.OUT/'frozen.json').read_text())
    assert original['metadata']['new_script_sha256']==e.m.hash_file(Path(e.__file__))
    for sec in ('input_sha256','code_sha256'):
        for path,digest in original['metadata'][sec].items():assert e.m.hash_file(e.v.ROOT/path)==digest
    meta=dict(calibration_seed=e.SEED,confirmation_seed=SEED,phases={'calibration':0,'confirmation':1},
              n_cal=e.m.N_CAL,n_confirm=e.m.N_CONFIRM,alpha=e.m.ALPHA,calibration_failure=e.m.CAL_FAILURE,
              plans={code:plans(code) for code in ('CGO','SPO')},version='literature',
              original_frozen_sha256=e.m.hash_file(e.OUT/'frozen.json'),
              runner_sha256=e.m.hash_file(Path(__file__)),core_runner_sha256=e.m.hash_file(Path(e.__file__)),
              scope='Fixed corrected truth population across all plans; no new model terms or adaptive retries')
    frozen=None
    if stage=='confirm':
        frozen=json.loads((OUT/'frozen.json').read_text());assert frozen['metadata']==meta
        meta={**meta,'frozen_sha256':e.m.hash_file(OUT/'frozen.json')}
    result=dict(metadata=meta,results=[],truth_hashes={})
    cal=stage=='prepare';n=e.m.N_CAL if cal else e.m.N_CONFIRM
    for si,code in enumerate(('CGO','SPO')):
        site=e.v.core.load_site(code);records={}
        banks=[e.bank(site,c,n,e.v.cell_seed(e.SEED if cal else SEED,0 if cal else 1,si,ci),'literature') for ci,c in enumerate(e.v.scenarios())]
        for ci,b in enumerate(banks):result['truth_hashes'][f'{code}/{ci}']=hashlib.sha256(b['truth'].tobytes()).hexdigest()
        for name,scales in plans(code).items():
            plan=dict(design=name,scales=scales,site=code,version='literature')
            if frozen:
                f=next(r for r in frozen['results'] if r['site']==code and r['design']==name)
                plan.update({k:f[k] for k in ('coverage_halfwidth','selection_halfwidth')})
            r,x=e.evaluate(site,banks,plan,'literature',cal)
            if cal and name=='control':
                old=next(r for r in original['results'] if r['site']==code and r['version']=='literature' and r['design']=='relaxed')
                for k in ('coverage_halfwidth','selection_halfwidth'):assert r[k]==old[k]
            records[name]=x;result['results'].append(r)
            print(stage,code,name,r.get('all_cells_pass','calibrated'),flush=True)
        np.savez_compressed(OUT/f'{stage}_{code}.npz',**records)
    result['number_estimates']=len(result['results'])*56*n
    e.m.write_json(target,result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','confirm']);run(p.parse_args().stage)
