# Further relaxation after literature correction

Fixed candidates; no model changes. Same corrected hidden population across candidates. Calibration seed2026102602/phase0; fresh validation seed2026102603/phase1. Per cell/truth n=4000/10000; all28 scenarios and both A/B directions. Original four gates and conservative comparison family retained. Control calibration widths exactly match the previous corrected run.

| Site | Design | S/L/T/O (%) | Correct lower | Wrong upper | Coverage lower | Max bias CI magnitude | Pass |
|---|---|---|---:|---:|---:|---:|---|
| SPO | control | 5/12.5/7.5/5 | 96.467% | 1.585% | 95.152% | 5.01597e-05 | True |
| SPO | S_x1.25 | 6.25/12.5/7.5/5 | 96.297% | 1.610% | 95.107% | 5.01197e-05 | True |
| SPO | S_x1.5 | 7.5/12.5/7.5/5 | 96.014% | 1.647% | 95.208% | 5.0083e-05 | True |
| SPO | S_x2 | 10/12.5/7.5/5 | 95.196% | 1.598% | 95.308% | 5.00191e-05 | True |
| SPO | L_x1.25 | 5/15.625/7.5/5 | 95.778% | 1.683% | 94.974% | 5.05951e-05 | False |
| SPO | L_x1.5 | 5/18.75/7.5/5 | 94.432% | 1.647% | 95.141% | 5.10883e-05 | True |
| SPO | L_x2 | 5/25/7.5/5 | 89.840% | 1.585% | 95.096% | 5.23205e-05 | True |
| SPO | T_x1.25 | 5/12.5/9.375/5 | 96.172% | 1.683% | 94.963% | 6.02907e-05 | False |
| SPO | T_x1.5 | 5/12.5/11.25/5 | 95.913% | 1.708% | 94.919% | 7.04091e-05 | False |
| SPO | T_x2 | 5/12.5/15/5 | 93.499% | 1.312% | 95.688% | 9.05837e-05 | True |
| SPO | O_x1.25 | 5/12.5/7.5/6.25 | 90.386% | 1.536% | 94.907% | 5.14302e-05 | False |
| SPO | O_x1.5 | 5/12.5/7.5/7.5 | 76.900% | 1.437% | 94.797% | 5.24905e-05 | False |
| SPO | O_x2 | 5/12.5/7.5/10 | 48.015% | 1.412% | 94.963% | 5.3862e-05 | False |
| SPO | all_x1.1 | 5.5/13.75/8.25/5.5 | 93.948% | 1.585% | 95.130% | 5.48668e-05 | True |
| SPO | all_x1.25 | 6.25/15.625/9.375/6.25 | 87.661% | 1.573% | 95.174% | 6.18129e-05 | True |
| SPO | all_x1.5 | 7.5/18.75/11.25/7.5 | 71.995% | 1.610% | 95.085% | 7.30636e-05 | False |
| CGO | control | 7.5/16/7.5/5 | 97.895% | 0.831% | 95.677% | 4.23981e-05 | True |
| CGO | S_x1.25 | 9.375/16/7.5/5 | 97.871% | 1.017% | 95.845% | 4.24518e-05 | True |
| CGO | S_x1.5 | 11.25/16/7.5/5 | 97.717% | 1.223% | 95.722% | 4.25114e-05 | True |
| CGO | S_x2 | 15/16/7.5/5 | 95.330% | 0.912% | 95.823% | 4.26479e-05 | True |
| CGO | L_x1.25 | 7.5/20/7.5/5 | 97.435% | 1.249% | 95.755% | 4.26838e-05 | True |
| CGO | L_x1.5 | 7.5/24/7.5/5 | 95.286% | 1.312% | 95.587% | 4.30857e-05 | True |
| CGO | L_x2 | 7.5/32/7.5/5 | 87.216% | 1.261% | 95.408% | 4.39637e-05 | True |
| CGO | T_x1.25 | 7.5/16/9.375/5 | 97.859% | 0.991% | 95.587% | 5.15082e-05 | True |
| CGO | T_x1.5 | 7.5/16/11.25/5 | 97.859% | 1.095% | 95.778% | 6.06481e-05 | True |
| CGO | T_x2 | 7.5/16/15/5 | 96.025% | 0.938% | 95.980% | 7.90056e-05 | True |
| CGO | O_x1.25 | 7.5/16/7.5/6.25 | 96.093% | 1.198% | 95.666% | 4.31032e-05 | True |
| CGO | O_x1.5 | 7.5/16/7.5/7.5 | 90.761% | 1.185% | 95.453% | 4.37113e-05 | True |
| CGO | O_x2 | 7.5/16/7.5/10 | 71.554% | 1.121% | 95.386% | 4.44983e-05 | False |
| CGO | all_x1.1 | 8.25/17.6/8.25/5.5 | 97.133% | 1.211% | 95.677% | 4.64179e-05 | True |
| CGO | all_x1.25 | 9.375/20/9.375/6.25 | 93.095% | 1.249% | 95.688% | 5.23749e-05 | True |
| CGO | all_x1.5 | 11.25/24/11.25/7.5 | 81.013% | 1.274% | 95.699% | 6.21128e-05 | True |

## Interpretation

All percentages multiply the corrected reference sigma, not the old width. These are tested discrete combinations, not continuous upper bounds. Single-group maxima cannot be combined without testing. Passing supports conditional discrimination only; literature-to-station mapping, scenario widths, independent monthly residual noise and approximate bias intervals remain assumptions. No claim of field feasibility or actual observational support for A/B.

Validation estimates audited: {checked:,}; failed inversions: {failed}. Calibration estimates: {frozen["number_estimates"]:,}.

[Updated absolute errors](../osse_relaxed_constraints/ABSOLUTE_ERRORS.md) | [Parameter references](../osse_literature_correction/PARAMETERS.md) | [All gates CSV](configurations.csv)

## Current SciencePlots figures

![A/B discrimination](relaxed_ab_separation.png)

![Absolute errors](absolute_error_budgets.png)
