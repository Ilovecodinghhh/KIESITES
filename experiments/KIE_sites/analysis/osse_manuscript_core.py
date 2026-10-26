"""Conditional OSSE using the manuscript's harmonic and phasor workflow.

This module adds no station dynamics. It uses the Phase 2 joint trend/annual
fit, Phase 6 vector source subtraction and multisink inversion, and Phase 14
weighted source responses. The final three nuisance widths are test scenarios,
not observed transport uncertainties. Isotope order is always [d13C, dD].
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import phase6_phasor as phase6

EXPT_DIR = Path(__file__).resolve().parents[1]
NAMES = [
    "d13_source", "q_annual", "B_SH", "C_SH", "B_T", "C_T", "B_NH", "C_NH",
    "dD_SH", "dD_T", "dD_NH", "f_oh", "f_cl", "f_soil", "alpha_d_oh",
    "alpha_c_cl", "alpha_d_cl", "w_nh", "w_trop", "lag_months",
]
GROUP_INDEX = {"S": list(range(11)), "L": list(range(11, 17)), "T": list(range(17, 20))}


def nominal_parameters():
    """Return a fresh parameter vector using the manuscript wetland B/C data."""
    wetland = json.loads((EXPT_DIR / "data" / "wetland_seasonality.json").read_text(encoding="utf-8"))
    coefficients = [wetland["bands"][band][key]
                    for band in ["SH_extra", "Tropics", "NH_high"]
                    for key in ["B_Q_Tg_month", "C_Q_Tg_month"]]
    return np.array([-62, 580, *coefficients, -301, -301, -374,
                     .84, .035, .06, 1.294, 1.066, 1.508, 0, 0, 2.8], dtype=float)


def widths():
    """Reference nuisance widths; w_nh/w_trop/lag widths are test scenarios."""
    return np.array([5, 50, *(.2 * np.abs(nominal_parameters()[2:8])),
                     15, 15, 10, .04, .01, .02, .01, .005, .05, .02, .1, .5])


def _project_simplex(values):
    """Euclidean nearest projection of each final-axis vector onto sum=1,x>=0."""
    ordered = np.sort(values, axis=-1)[..., ::-1]
    cumulative = np.cumsum(ordered, axis=-1) - 1
    ranks = np.arange(1, values.shape[-1] + 1)
    active = ordered - cumulative / ranks > 0
    rho = np.sum(active, axis=-1) - 1
    theta = np.take_along_axis(cumulative, rho[..., None], axis=-1)[..., 0] / (rho + 1)
    return np.maximum(values - theta[..., None], 0)


def constrain_parameters(p):
    """Copy parameters, enforce physical supports, and jointly project fractions.

    Sink projection acts on [OH, Cl, soil, 1-OH-Cl-soil]; source response
    projection acts on [SH, Tropics, NH]. Zero OH remains zero and is rejected
    by inversion. Delay remains unconstrained because its rotation is periodic.
    """
    p = np.array(p, dtype=float, copy=True)
    if p.ndim == 0 or p.shape[-1] != len(NAMES) or not np.all(np.isfinite(p)):
        raise ValueError("Parameters must be finite with final dimension 20")
    p[..., [0, 8, 9, 10]] = np.maximum(p[..., [0, 8, 9, 10]], np.nextafter(-999., np.inf))
    p[..., 1] = np.maximum(p[..., 1], 300)
    p[..., 14:17] = np.maximum(p[..., 14:17], np.finfo(float).eps)
    fractions = np.concatenate([p[..., 11:14], 1 - p[..., 11:14].sum(axis=-1, keepdims=True)], axis=-1)
    p[..., 11:14] = _project_simplex(fractions)[..., :3]
    weights = np.stack([1-p[..., 17]-p[..., 18], p[..., 18], p[..., 17]], axis=-1)
    projected = _project_simplex(weights)
    p[..., 17] = projected[..., 2]
    p[..., 18] = projected[..., 1]
    return p


def source_phasors(p):
    """Return (...,2) weighted source phasors in the Phase 2 B+iC convention."""
    p = np.asarray(p, dtype=float)
    raw = p[..., 2:8:2] + 1j * p[..., 3:8:2]
    midpoint = raw * np.exp(-1j * np.pi / 12)
    delay = np.stack([np.ones_like(p[..., 19]), np.ones_like(p[..., 19]),
                      np.exp(-1j * 2 * np.pi * p[..., 19] / 12)], axis=-1)
    weights = np.stack([1-p[..., 17]-p[..., 18], p[..., 18], p[..., 17]], axis=-1)
    fractional = midpoint * delay * weights / (p[..., 1, None] / 12)
    carbon = (p[..., 0] - phase6.D13C_ATM) * fractional.sum(axis=-1)
    deuterium = ((p[..., 8:11] - phase6.DD_ATM) * fractional).sum(axis=-1)
    return np.stack([carbon, deuterium], axis=-1)


def bulk_ratio(alpha, p):
    """Forward multisink epsilon ratio, algebraically inverse to Phase 6."""
    p = np.asarray(p, dtype=float)
    strat = 1 - p[..., 11:14].sum(axis=-1)
    carbon = (p[..., 11] * (np.asarray(alpha)-1)
              + p[..., 12] * (p[..., 15]-1)
              + p[..., 13] * (phase6.ALPHA_13C_SOIL-1)
              + strat * (phase6.ALPHA_13C_STRAT-1))
    deuterium = (p[..., 11] * (p[..., 14]-1)
                 + p[..., 12] * (p[..., 16]-1)
                 + p[..., 13] * (phase6.ALPHA_D_SOIL-1)
                 + strat * (phase6.ALPHA_D_STRAT-1))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(carbon / deuterium)


def invert_phasors(zobs, p):
    """Subtract the source vector, take the amplitude ratio, and call Phase 6.

    No alpha-range filtering or clipping is applied. A zero D sink amplitude,
    nonpositive OH fraction, or nonfinite calculation returns NaN.
    """
    p = np.asarray(p, dtype=float)
    sink = np.asarray(zobs, dtype=complex) - source_phasors(p)
    denominator = np.abs(sink[..., 1])
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.abs(sink[..., 0]) / denominator
        alpha = phase6.ratio_to_alpha_13c(
            ratio, p[..., 14], p[..., 11], p[..., 12], p[..., 13],
            1-p[..., 11:14].sum(axis=-1), p[..., 15], p[..., 16],
        )
    valid = (denominator > 0) & (p[..., 11] > 0) & np.isfinite(alpha)
    return np.asarray(np.where(valid, alpha, np.nan))


def load_site(code):
    """Load CGO/SPO monthly means, retaining the stored Phase 2 decimal years.

    The paired residual covariance includes all variation left by the joint
    annual/trend fit; it is not an instrument-only precision estimate. The D
    sink is fixed from the nominal local-source-corrected observed phasor.
    """
    if code not in ("CGO", "SPO"):
        raise ValueError("This Southern Hemisphere OSSE supports CGO and SPO")
    input_path = EXPT_DIR / "results" / "phase1_data" / f"site_monthly_{code}.csv"
    monthly = pd.read_csv(input_path, encoding="utf-8")
    t = monthly["decimal_year"].to_numpy(dtype=float)
    y = monthly[["d13C_mean", "dD_mean"]].to_numpy(dtype=float)
    if len(t) <= 4 or not np.isfinite(t).all() or not np.isfinite(y).all():
        raise ValueError("Site data require more than four finite paired months")
    X = np.column_stack([np.ones_like(t), t-t.mean(), np.sin(2*np.pi*t), np.cos(2*np.pi*t)])
    coefficient, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    if rank != 4:
        raise ValueError("Site harmonic design must have rank four")
    residual = y - X @ coefficient
    return {
        "code": code, "t": t, "X": X, "pinv": np.linalg.pinv(X),
        "baseline_coeff": coefficient,
        "residual_cov": residual.T @ residual / (len(t)-4),
        "sink_d": coefficient[2, 1]+1j*coefficient[3, 1]-source_phasors(nominal_parameters())[1],
        "observed": y, "input_path": str(input_path),
    }


def synthesize(alpha, p, site, noise):
    """Generate (...,n,2) monthly data from fixed D sink and shared trend.

    The same fitted intercept/trend is reused for either laboratory truth.
    The seasonal signal is not demeaned on the irregular observation calendar.
    Noise is supplied by the caller; this function draws no random quantities.
    """
    ratio = bulk_ratio(alpha, p)
    sink = np.stack([ratio * site["sink_d"], np.ones_like(ratio) * site["sink_d"]], axis=-1)
    phasor = sink + source_phasors(p)
    baseline = site["X"][:, :2] @ site["baseline_coeff"][:2]
    seasonal = (site["X"][:, 2, None] * phasor.real[..., None, :]
                + site["X"][:, 3, None] * phasor.imag[..., None, :])
    return baseline + seasonal + np.asarray(noise, dtype=float)


def fit_observed(y, site):
    """Fit intercept, trend and annual harmonic jointly; return (...,2) B+iC."""
    coefficients = np.einsum("kn,...ni->...ki", site["pinv"], np.asarray(y, dtype=float))
    return coefficients[..., 2, :] + 1j * coefficients[..., 3, :]
