"""Compare existing paired-month residuals with tested OSSE budgets; no simulation."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EXPT = ROOT / 'experiments/KIE_sites'
OUT = EXPT / 'results/osse_real_feasibility'
configs_path = EXPT / 'results/osse_corrected_relaxation/configurations.csv'
configs = pd.read_csv(configs_path)
result = {'method': 'Joint intercept, linear trend and annual sine/cosine; residual covariance divided by n-4',
          'input_sha256': {str(configs_path.relative_to(ROOT)): hashlib.sha256(configs_path.read_bytes()).hexdigest()},
          'sites': {}}
for site, design in [('SPO', 'all_x1.25'), ('CGO', 'all_x1.5')]:
    path = EXPT / f'results/phase1_data/site_monthly_{site}.csv'
    df = pd.read_csv(path)
    t = df.decimal_year.to_numpy()
    y = df[['d13C_mean', 'dD_mean']].to_numpy()
    x = np.column_stack([np.ones_like(t), t-t.mean(), np.sin(2*np.pi*t), np.cos(2*np.pi*t)])
    coef, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    assert rank == 4 and np.isfinite(y).all()
    residual = y-x@coef
    sigma = np.sqrt(np.diag(residual.T@residual/(len(t)-4)))
    row = configs[(configs.site == site) & (configs.design == design)].iloc[0]
    assert bool(row.passes)
    max_o = configs[(configs.site == site) & configs.passes].O.max()
    result['input_sha256'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    result['sites'][site] = {
        'design': design, 'paired_months': len(df),
        'year_min': int(df.year.min()), 'year_max': int(df.year.max()),
        'scales': {g: float(row[g]) for g in ['S','L','T','O']},
        'largest_O_among_tested_passing_points': float(max_o),
        'actual_residual_sigma_permil_C_D': sigma.tolist(),
        'target_residual_sigma_permil_C_D': (sigma*row.O).tolist(),
        'actual_to_target_sigma_ratio': float(1/row.O),
        'monthly_sample_counts': {iso: {'min': int(df[f'{iso}_n'].min()),
                                      'median': float(df[f'{iso}_n'].median()),
                                      'max': int(df[f'{iso}_n'].max()),
                                      'single_sample_months': int((df[f'{iso}_n']==1).sum())}
                                  for iso in ['d13C','dD']},
        'source_reference_to_target_sigma_ratio': float(1/row.S),
        'sink_KIE_reference_to_target_sigma_ratio': float(1/row.L),
        'lag_target_sigma_days': float(.5*row['T']*365.25/12),
    }
OUT.mkdir(exist_ok=True)
(OUT/'evidence.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps(result['sites'], indent=2))
