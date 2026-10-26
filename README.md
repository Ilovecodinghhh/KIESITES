# KIESITES

Current OSSE and conditional real-data analysis checkpoint, exported from source commit 3f20fdd on 2026-10-26. This repository starts with a single commit and does not contain the old multi-gigabyte Git history.

## Results

- [Conditional real-data report](experiments/KIE_sites/results/osse_real_conditional/REPORT.md)
- [Available-evidence feasibility audit](experiments/KIE_sites/results/osse_real_feasibility/REPORT.md)
- [Version scope](docs/tasks/osse-real-conditional/VERSION.md)
- [Original checkpoint hashes](docs/tasks/osse-real-conditional/MANIFEST.json)

At the default auxiliary centers, both sites are compatible only with B under the hypothetical improved precision. This conclusion is not robust across source/transport scenarios. Real-data coverage of transferred OSSE intervals has not been established. This is conditional analysis, not proof that current observations select B.

## Reproduce the conditional analysis

Install requirements.txt, then run from this repository root:

    python experiments/KIE_sites/analysis/osse_real_conditional.py

Recompute the feasibility audit and figure:

    python docs/tasks/osse-real-feasibility/check.py
    python docs/tasks/osse-real-feasibility/plot.py

The original task notes contain machine-specific environment paths; they are historical execution records. The commands above use the active Python environment.

## Scope

Includes selected scripts, paired monthly data, wetland coefficients, frozen calibration and confirmation JSON, reports and figures. Raw external datasets, local reference-library files, and large Monte Carlo NPZ arrays are not included. Links into ImportantReferences refer to the original local library; publication DOI links remain the source references. Some historical reports refer to earlier outputs outside this selected checkpoint. This is a results checkpoint, not a full archive or a self-contained rerun of every historical OSSE stage.

File bytes are preserved to retain scientific input hashes; .gitattributes disables automatic line-ending conversion.
