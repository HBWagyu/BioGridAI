# BioGridAI Tesla Platform

Farmer-owned multi-agent OS for agrivoltaics + livestock.

**Core mandate (do not violate)**
- Robotics: Tesla Optimus only
- Energy: Tesla Opticaster / Energy stack only
- Livestock: Ceres Gen 6 ear tags only
- Field equipment: John Deere Operations Center / autonomy only
- Universal: no live farm coordinates hard-coded; demo parcel is generic and replaceable

**Optional vendor (not core)**
- Noumenal Labs **Whiplash** + **Thermobrain** as an under-array vegetation adapter
- Scheduled by Grazing + Operations Synthesis
- Uncertainty events become BioGridAI HITL approvals
- Never a peer of Optimus; never allowed to move animals or dispatch energy

Repo: [HBWagyu/BioGridAI](https://github.com/HBWagyu/BioGridAI)

## Quick start (simulation — no hardware keys)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make test
make ui
```

Open http://localhost:8501

Optional API:

```bash
make api
# http://localhost:8000/docs
```

## What the demo shows

1. **05:30 Briefing** — five Tesla-core agents produce a daily plan.
2. **Live Map** — parcel, solar array, Ceres animals, Optimus, John Deere, and Whiplash (labeled VENDOR).
3. **Vendor: Whiplash** — understory mission is blocked while Ceres tags remain in the array; Thermobrain uncertainty opens HITL.
4. **HITL Queue** — approve / override / request video. Approving a Thermobrain gate simulates a cut and lowers understory height.
5. **Traceability** — hash-chained event log.

## Architecture

```
Layer 1  Ceres + Tesla Energy + Optimus + John Deere ingest
         + optional Noumenal Whiplash telemetry (sim)
Layer 2  Optimus Fleet · Grazing/Carbon · Herd Health · Energy · Ops Synthesis
Layer 3  Dispatch + HITL (Thermobrain maps here)
Layer 4  Hash-chain audit
```

See `docs/architecture.md` and `docs/noumenal_adapter.md`.

## Tesla synergy

Optimus collects real under-array herding and inspection traces. Opticaster sees robot + optional dock loads against agrivoltaic export. The farmer keeps ownership of code and data.

Prepared by the BioGridAI Tesla Coding Agent.
