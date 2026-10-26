"""Recompute saved validation metrics and report discrete relaxed budgets."""
import csv
import json
from pathlib import Path
import numpy as np
import osse_corrected_relaxation as r


def main():
    out=r.OUT;result=json.loads((out/'confirmation.json').read_text());frozen=json.loads((out/'frozen.json').read_text())
    assert r.e.m.hash_file(out/'frozen.json')==result['metadata']['frozen_sha256']
    assert r.e.m.hash_file(Path(r.__file__))==result['metadata']['runner_sha256']
    assert r.e.m.hash_file(Path(r.e.__file__))==result['metadata']['core_runner_sha256']
    rows=[];checked=0;failed=0
    for site in ['SPO','CGO']:
        with np.load(out/f'confirm_{site}.npz') as raw:
            for q in [q for q in result['results'] if q['site']==site]:
                f=next(f for f in frozen['results'] if f['site']==site and f['design']==q['design'])
                for k in ['scales','coverage_halfwidth','selection_halfwidth']:assert f[k]==q[k]
                for x,c in zip(raw[q['design']],q['cells']):
                    m=r.e.v.metrics(x,c['truth'],q['coverage_halfwidth'],q['selection_halfwidth'],r.e.m.ALPHA)
                    assert all(c[k]==m[k] for k in m)
                    checked+=len(x);failed+=m['failed']
                failures={g:sum(not c['gates'][g] for c in q['cells']) for g in ['correct','wrong','coverage','bias']}
                rows.append(dict(site=site,design=q['design'],**q['scales'],passes=q['all_cells_pass'],
                    correct_lower=min(c['correct_ci'][0] for c in q['cells']),wrong_upper=max(c['wrong_ci'][1] for c in q['cells']),
                    coverage_lower=min(c['coverage_ci'][0] for c in q['cells']),bias_bound=max(abs(v) for c in q['cells'] for v in c['raw_bias_ci']),
                    **{'failed_'+g:n for g,n in failures.items()}))
    assert checked==result['number_estimates']
    with (out/'configurations.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    lines=['# Further relaxation after literature correction','','Fixed candidates; no model changes. Same corrected hidden population across candidates. Calibration seed2026102602/phase0; fresh validation seed2026102603/phase1. Per cell/truth n=4000/10000; all28 scenarios and both A/B directions. Original four gates and conservative comparison family retained. Control calibration widths exactly match the previous corrected run.','','| Site | Design | S/L/T/O (%) | Correct lower | Wrong upper | Coverage lower | Max bias CI magnitude | Pass |','|---|---|---|---:|---:|---:|---:|---|']
    for q in rows:
        s='/'.join(f'{q[g]*100:g}' for g in r.e.v.GROUPS)
        lines.append(f'| {q["site"]} | {q["design"]} | {s} | {100*q["correct_lower"]:.3f}% | {100*q["wrong_upper"]:.3f}% | {100*q["coverage_lower"]:.3f}% | {q["bias_bound"]:.6g} | {q["passes"]} |')
    lines+=['','## Interpretation','','All percentages multiply the corrected reference sigma, not the old width. These are tested discrete combinations, not continuous upper bounds. Single-group maxima cannot be combined without testing. Passing supports conditional discrimination only; literature-to-station mapping, scenario widths, independent monthly residual noise and approximate bias intervals remain assumptions. No claim of field feasibility or actual observational support for A/B.',f'','Validation estimates audited: {checked:,}; failed inversions: {failed}. Calibration estimates: {frozen["number_estimates"]:,}.','', '[Updated absolute errors](../osse_relaxed_constraints/ABSOLUTE_ERRORS.md) | [Parameter references](../osse_literature_correction/PARAMETERS.md) | [All gates CSV](configurations.csv)']
    (out/'REPORT.md').write_text(chr(10).join(lines)+chr(10),encoding='utf-8')
    r.e.m.write_json(out/'audit.json',dict(estimates=checked,nonfinite=failed,script_sha256=r.e.m.hash_file(Path(__file__))))
    for site in ['SPO','CGO']:
        rr=[q for q in rows if q['site']==site]
        print(site,'passed',sum(q['passes'] for q in rr),'of',len(rr))
        for q in rr:
            if q['design'].startswith('all') or q['design'].endswith('x2') or q['design']=='control':print(q)

if __name__=='__main__':main()
