"""Conditional error requirements; reuse the manuscript estimator unchanged."""
from pathlib import Path
from functools import lru_cache
from itertools import product
import argparse
import hashlib
import json
import time
import numpy as np
import osse_manuscript_validation as v

LEVELS=(.05,.075,.1,.15,.25,.5,1.)
MAX_DESIGNS=64
SEED=2026102521
N_CAL,N_SCREEN,N_CONFIRM=4000,2000,10000
ALPHA=.05/(2*MAX_DESIGNS*28*2*4)
CAL_FAILURE=.05/(2*MAX_DESIGNS*28*2*2)
OUT=v.core.EXPT_DIR/'results/osse_conditional_requirements'


def single_designs():
    plans={'base':dict.fromkeys(v.GROUPS,.05)}
    for group in v.GROUPS:
        for scale in LEVELS[1:]:
            plans[f'{group}_{scale:g}']={g:scale if g==group else .05 for g in v.GROUPS}
    return plans


def screen_pass(row):
    return all(c['failed']==0 and c['raw_bias'] is not None and abs(c['raw_bias'])<=.00015
               and c['correct']>=.8 and c['wrong']<=.05 and c['coverage']>=.95
               for c in row['cells'])


def joint_designs(rows):
    maxima={g:max([.05]+[r['scales'][g] for r in rows if screen_pass(r)
                and all(r['scales'][other]==.05 for other in v.GROUPS if other!=g)]) for g in v.GROUPS}
    seen={tuple(r['scales'][g] for g in v.GROUPS) for r in rows}
    candidates=list(product(*[(.05,maxima[g]) for g in v.GROUPS]))
    candidates.append(tuple(LEVELS[max(0,LEVELS.index(maxima[g])-1)] for g in v.GROUPS))
    plans={}
    for values in candidates:
        if values not in seen:
            plans[f'joint_{len(plans)+1:02d}']=dict(zip(v.GROUPS,values));seen.add(values)
    assert len(rows)+len(plans)<=MAX_DESIGNS
    return plans


def frontier(rows):
    passed=[r for r in rows if r['all_cells_pass']]
    return [r for r in passed if not any(
        all(q['scales'][g]>=r['scales'][g] for g in v.GROUPS)
        and any(q['scales'][g]>r['scales'][g] for g in v.GROUPS) for q in passed)]


@lru_cache(None)
def calibration_rank(n,probability):
    # Reuse the exact legacy order-statistic calculation once per sample size.
    return int(v.tolerance_quantile(np.arange(n,dtype=float),probability,CAL_FAILURE))


def evaluate_design(site,banks,design,calibrate):
    row={key:design[key] for key in ('design','scales')}
    estimates=[];details=[]
    if not calibrate:
        row.update({key:design[key] if design[key] is not None else np.inf for key in ('coverage_halfwidth','selection_halfwidth')})
    for cell,bank in zip(v.scenarios(),banks):
        for truth in v.TRUTHS:
            estimated,projected=v.evaluate_bank(bank,site,truth,design['scales'])
            estimates.append(estimated)
            detail=dict(cell=cell['name'],kind=cell['kind'],truth=truth,projected_auxiliary=projected)
            if calibrate:
                errors=np.sort(np.where(np.isfinite(estimated),abs(estimated-truth),np.inf))
                detail.update(coverage_width=max(float(errors[calibration_rank(len(errors),.95)]),1e-12),
                              selection_width=max(float(errors[calibration_rank(len(errors),.975)]),1e-12),
                              failed=int(np.sum(~np.isfinite(estimated))))
            else:
                detail.update(v.metrics(estimated,truth,row['coverage_halfwidth'],row['selection_halfwidth'],ALPHA))
            details.append(detail)
    if calibrate:
        row.update(calibration=details,coverage_halfwidth=max(c['coverage_width'] for c in details),
                   selection_halfwidth=max(c['selection_width'] for c in details))
    else:
        row.update(cells=details,all_cells_pass=all(c['passes'] for c in details))
        row['screen_pass']=screen_pass(row)
    return row,np.array(estimates)


def write_json(path,value):
    path.write_text(json.dumps(v.json_ready(value),ensure_ascii=False,indent=2,allow_nan=False)+chr(10),encoding='utf-8')


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata():
    old_path=v.core.EXPT_DIR/'results/osse_manuscript_validation/summary.json'
    old=json.loads(old_path.read_text(encoding='utf-8'))
    for section in ('input_sha256','code_sha256'):
        for relative,digest in old['metadata'][section].items():
            assert hash_file(v.ROOT/relative)==digest,relative
    codes=[Path(__file__),Path(v.__file__),Path(v.core.__file__),Path(v.core.phase6.__file__)]
    return dict(seed=SEED,levels=LEVELS,max_designs_per_site=MAX_DESIGNS,
                n_cal=N_CAL,n_screen=N_SCREEN,n_confirm=N_CONFIRM,alpha=ALPHA,calibration_failure=CAL_FAILURE,
                phases={'single_cal':0,'single_screen':1,'joint_cal':2,'joint_screen':3,'confirm':4},
                original_scan_sha256=hash_file(old_path),input_sha256=old['metadata']['input_sha256'],
                code_sha256={str(p.relative_to(v.ROOT)):hash_file(p) for p in codes},
                cells=v.scenarios(),sites=old['metadata']['sites'],
                scope='Same hidden-truth population and manuscript model; conditional discrete tested configurations, not real feasibility or continuous bounds',
                selection='Single-group screening uses point gates only; maxima form joint corners plus one preceding-level combination. All scanned designs receive fresh confirmation.',
                record_order='cell order from metadata, then truths 1.0039/1.0054; columns replicate index',
                bias_ci='Unshifted mean and Student t approximation; not distribution-free')


def banks_for(site,si,phase,n,hashes):
    banks=[]
    for ci,cell in enumerate(v.scenarios()):
        bank=v.make_bank(site,cell,n,v.cell_seed(SEED,phase,si,ci));banks.append(bank)
        hashes[f'{site["code"]}/{phase}/{cell["name"]}']=hashlib.sha256(bank['truth'].tobytes()).hexdigest()
    return banks


def scan():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'frozen.json').exists():raise FileExistsError('Frozen scan already exists; refusing overwrite')
    started=time.monotonic();result=dict(metadata=metadata(),results=[],truth_hashes={})
    for si,code in enumerate(('CGO','SPO')):
        site=v.core.load_site(code);site_rows=[];records={}
        for kind,phase in (('single',0),('joint',2)):
            plans=single_designs() if kind=='single' else joint_designs(site_rows)
            cal_banks=banks_for(site,si,phase,N_CAL,result['truth_hashes'])
            screen_banks=banks_for(site,si,phase+1,N_SCREEN,result['truth_hashes'])
            for name,scales in plans.items():
                calibrated,raw_cal=evaluate_design(site,cal_banks,dict(design=name,scales=scales),True)
                row,raw_screen=evaluate_design(site,screen_banks,calibrated,False)
                row.update(site=code,kind=kind,calibration=calibrated['calibration'])
                site_rows.append(row)
                records[f'{name}__cal']=raw_cal;records[f'{name}__screen']=raw_screen
                print('screen',code,name,scales,'candidate',row['screen_pass'],flush=True)
        assert len(site_rows)<=MAX_DESIGNS
        result['results'].extend(site_rows)
        np.savez_compressed(OUT/f'scan_{code}.npz',**records)
    result['metadata']['elapsed_seconds']=time.monotonic()-started
    result['metadata']['number_estimates']=len(result['results'])*56*(N_CAL+N_SCREEN)
    write_json(OUT/'frozen.json',result)
    print('Candidate set and all thresholds frozen before confirmation',flush=True)


def confirm():
    target=OUT/'confirmation.json'
    if target.exists():raise FileExistsError('Confirmation already exists; no retries allowed')
    started=time.monotonic();path=OUT/'frozen.json';frozen=json.loads(path.read_text(encoding='utf-8'))
    current=metadata()
    for key in ('seed','alpha','code_sha256','input_sha256','n_confirm','phases'):
        assert current[key]==frozen['metadata'][key],key
    result=dict(metadata={**frozen['metadata'],'frozen_sha256':hash_file(path)},results=[],truth_hashes={})
    for si,code in enumerate(('CGO','SPO')):
        site=v.core.load_site(code);banks=banks_for(site,si,4,N_CONFIRM,result['truth_hashes']);records={}
        for design in (r for r in frozen['results'] if r['site']==code):
            row,raw=evaluate_design(site,banks,design,False)
            row.update(site=code,kind=design['kind']);result['results'].append(row)
            records[row['design']]=raw
            failed=sum(not c['passes'] for c in row['cells'])
            print('confirm',code,row['design'],'failing cell-directions',failed,flush=True)
        np.savez_compressed(OUT/f'confirmation_{code}.npz',**records)
    result['metadata']['elapsed_seconds']=time.monotonic()-started
    result['metadata']['number_estimates']=len(result['results'])*56*N_CONFIRM
    write_json(target,result)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['scan','confirm'])
    args=parser.parse_args()
    scan() if args.stage=='scan' else confirm()
