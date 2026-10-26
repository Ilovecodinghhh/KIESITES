# Absolute error budgets for plotted configurations

> **2026-10-26 provenance audit:** These are code-used error scales, not uniformly literature-supported 1σ uncertainties. Douglas source δD widths have a 95% CI versus 1σ mismatch; several other widths are scenario assumptions. SPO/CGO sigma columns are conditional OSSE targets, not observed precision. See [the full parameter-by-parameter audit](PARAMETER_PROVENANCE.md).

All numbers are pre-projection Gaussian standard deviations of auxiliary estimation errors; not hard bounds. Hidden truth variability is unchanged. S/L/T/O: SPO .05/.125/.075/.05; CGO .075/.16/.075/.05.

| Parameter | Nominal reference | Reference width | SPO sigma | CGO sigma |
|---|---:|---:|---:|---:|
| d13_source | -62 | 5 | 0.25 | 0.375 |
| q_annual | 580 | 50 | 2.5 | 3.75 |
| B_SH | 0.0044 | 0.00088 | 4.4e-05 | 6.6e-05 |
| C_SH | 0.0776 | 0.01552 | 0.000776 | 0.001164 |
| B_T | 0.2729 | 0.05458 | 0.002729 | 0.0040935 |
| C_T | -0.5848 | 0.11696 | 0.005848 | 0.008772 |
| B_NH | -0.1985 | 0.0397 | 0.001985 | 0.0029775 |
| C_NH | -1.2436 | 0.24872 | 0.012436 | 0.018654 |
| dD_SH | -301 | 15 | 0.75 | 1.125 |
| dD_T | -301 | 15 | 0.75 | 1.125 |
| dD_NH | -374 | 10 | 0.5 | 0.75 |
| f_oh | 0.84 | 0.04 | 0.005 | 0.0064 |
| f_cl | 0.035 | 0.01 | 0.00125 | 0.0016 |
| f_soil | 0.06 | 0.02 | 0.0025 | 0.0032 |
| alpha_d_oh | 1.294 | 0.01 | 0.00125 | 0.0016 |
| alpha_c_cl | 1.066 | 0.005 | 0.000625 | 0.0008 |
| alpha_d_cl | 1.508 | 0.05 | 0.00625 | 0.008 |
| w_nh | 0 | 0.02 | 0.0015 | 0.0015 |
| w_trop | 0 | 0.1 | 0.0075 | 0.0075 |
| lag_months | 2.8 | 0.5 | 0.0375 | 0.0375 |

q_annual: Tg CH4/year reference normalization, not a station-local emission flux. B/C: Tg CH4/month source harmonic coefficients, not total source uncertainty. Isotope delta: per mil; alpha and fractions: dimensionless. Transport weights are effective regional source-response weights, not air-mass fractions. lag_months affects the NH response.

Monthly noise covariance is 0.05 squared times the fitted residual covariance; months are independent in the generator. It includes unexplained variability, not only instrument error.
- SPO: 33 paired months; reference sigma d13C/dD = 0.0724138723/2.92551372 per mil; scaled = 0.00362069361/0.146275686 per mil; correlation 0.0705331748.
- CGO: 29 paired months; reference sigma d13C/dD = 0.0957617888/2.50770074 per mil; scaled = 0.00478808944/0.125385037 per mil; correlation 0.0959589625.

Sink fractions and transport weights are physically projected: near boundaries actual errors are neither independent nor exactly Gaussian. Stratospheric sink fraction is the remainder; soil and stratospheric KIE constants are fixed. Approximate 95% marginal pre-projection intervals use +/-1.96 sigma; they are not joint bounds. These conditional budgets do not establish field feasibility.

Computed directly from analysis/osse_manuscript_core.py nominal_parameters, widths, load_site, and checked against analysis/osse_manuscript_validation.py observation_package. No simulation or scientific code changed.
