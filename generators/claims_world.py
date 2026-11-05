"""
claims_world.py: the Corvane Mutual claims world for ERM 424, Modules 1 to 4.

PUBLIC MODULE. This file is published to students. It contains the clean world
only: the schema, the category lists, and the generator students call in the
Module 2 First Contact notebook (Stage 3) to build a 2,000,000-row frame in
their own Colab session. Nothing in this file describes a planted data defect.
The planted defects, the Module 3 pair, the Module 4 cleaner, and the answer
keys live in claims_world_private.py, which is never published.

Course:  ERM 424, Statistics and Data Analytics for Risk Management,
         Northwestern University School of Professional Studies, Winter 2027.
World:   Corvane Mutual Insurance Company, a fictional auto insurance carrier.
         Vehicle makes are real manufacturer names; everything else is invented.
         No third-party data is loaded, transformed, or redistributed.

Seeds in this file:
    SEED_POOL     424000   master policy-id pool and adjuster caseload weights
    STUDENT_SEED  424      the Stage 3 large frame
The seeds of the published course files live in the instructor's build module.

Determinism: this module uses numpy.random.RandomState, the legacy generator
whose bit stream NumPy guarantees to stay fixed across versions (NEP 19). The
modern default_rng() stream carries no such guarantee, and the course needs the
same seed to reproduce byte-identical CSVs on Colab, on the instructor's
machine, and on the build machine. Vectorized throughout; no Python row loops.

Usage in Colab (Stage 3):
    from claims_world import generate_claims
    big = generate_claims(n_rows=2_000_000, seed=424)

Dependencies: numpy and pandas only.
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional

import numpy as np
import pandas as pd

__version__ = "1.1.0"

# ---------------------------------------------------------------------------
# Seeds
# ---------------------------------------------------------------------------

SEED_POOL = 424000
STUDENT_SEED = 424

# ---------------------------------------------------------------------------
# Date windows (inclusive)
# ---------------------------------------------------------------------------

M1_WINDOW = ("2023-01-01", "2023-12-31")
M2_WINDOW = ("2024-01-01", "2025-06-30")
M3_WINDOW = ("2025-07-01", "2026-06-30")

# Month weights for incident dates: winter heavier, summer lighter.
MONTH_WEIGHT = {1: 1.25, 2: 1.25, 3: 1.0, 4: 1.0, 5: 1.0, 6: 0.9,
                7: 0.9, 8: 0.9, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.25}
REPORT_LAG_MEAN_DAYS = 3.0
REPORT_LAG_MAX_DAYS = 30

# ---------------------------------------------------------------------------
# Categories and weights
# ---------------------------------------------------------------------------

CLAIM_TYPES = ["Collision", "Property Damage Liability", "Comprehensive",
               "Bodily Injury Liability", "Personal Injury Protection",
               "Uninsured Motorist"]
CLAIM_TYPE_W = np.array([0.38, 0.20, 0.18, 0.10, 0.08, 0.06])

SEVERITIES = ["Minor", "Moderate", "Major", "Total Loss"]
SEVERITY_W = np.array([0.46, 0.32, 0.17, 0.05])

# vehicles_involved: probability of 1, 2, 3, 4 vehicles, by claim type (rows
# follow CLAIM_TYPES order).
VEHICLES_INVOLVED_P = np.array([
    [0.30, 0.60, 0.08, 0.02],   # Collision
    [0.00, 0.80, 0.15, 0.05],   # Property Damage Liability
    [1.00, 0.00, 0.00, 0.00],   # Comprehensive
    [0.00, 0.80, 0.15, 0.05],   # Bodily Injury Liability
    [0.40, 0.50, 0.10, 0.00],   # Personal Injury Protection
    [0.00, 0.90, 0.10, 0.00],   # Uninsured Motorist
])

MAKES = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Hyundai", "Kia",
         "Subaru", "Jeep", "Ram", "GMC", "Dodge", "Volkswagen", "Mazda", "BMW",
         "Mercedes-Benz", "Audi", "Lexus", "Tesla", "Buick", "Chrysler",
         "Cadillac", "Lincoln", "Acura", "Infiniti", "Volvo", "Mitsubishi",
         "Mini", "Porsche", "Land Rover", "Jaguar", "Genesis", "Fiat",
         "Alfa Romeo", "Rivian", "Polestar", "Scion", "Saturn", "Pontiac",
         "Mercury"]
_rank = np.arange(1, len(MAKES) + 1)
MAKE_W = (1.0 / _rank ** 0.9)
MAKE_W = MAKE_W / MAKE_W.sum()

LUXURY_MAKES = {"BMW", "Mercedes-Benz", "Audi", "Lexus", "Porsche", "Land Rover",
                "Jaguar", "Tesla", "Genesis", "Cadillac", "Lincoln", "Acura",
                "Infiniti", "Volvo", "Rivian", "Polestar", "Alfa Romeo"}
ECONOMY_MAKES = {"Saturn", "Pontiac", "Mercury", "Scion", "Fiat", "Mitsubishi"}
TIER_BASE = np.array([52000.0 if m in LUXURY_MAKES else
                      18000.0 if m in ECONOMY_MAKES else 30000.0
                      for m in MAKES])
# Last model year for discontinued makes; others run to the current year.
LAST_MODEL_YEAR = {"Saturn": 2010, "Pontiac": 2010, "Mercury": 2011,
                   "Scion": 2016, "Fiat": 2024}
CURRENT_MODEL_YEAR = 2025
OLDEST_MODEL_YEAR = 2004
LAST_YEAR_BY_MAKE = np.array([LAST_MODEL_YEAR.get(m, CURRENT_MODEL_YEAR)
                              for m in MAKES])
DEPRECIATION_PER_YEAR = 0.88
VALUE_NOISE_SIGMA = 0.28
VALUE_MIN, VALUE_MAX = 1500.0, 120000.0

REGIONS = ["IL", "WI", "IN", "MI", "OH", "MN", "MO", "IA", "KY", "TN"]
REGION_W = np.array([0.28, 0.12, 0.12, 0.11, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03])

CHANNELS = ["Mobile App", "Web Portal", "Phone", "Agent", "Email"]
CHANNEL_W = np.array([0.30, 0.25, 0.25, 0.15, 0.05])

ADJUSTER_IDS = np.arange(5101, 5126)   # 25 adjusters

# Amount design (SCHEMA_PROPOSAL section 9). Rows follow CLAIM_TYPES order.
P_VEHICLE = np.array([0.98, 0.60, 0.99, 0.55, 0.50, 0.85])
P_PROPERTY = np.array([0.45, 1.00, 0.05, 0.40, 0.10, 0.10])
P_INJURY = np.array([0.15, 0.05, 0.01, 1.00, 1.00, 0.50])
# Rows follow SEVERITIES order.
DAMAGE_FRAC_LO = np.array([0.02, 0.10, 0.30, 0.90])
DAMAGE_FRAC_HI = np.array([0.10, 0.30, 0.75, 1.00])
SEVERITY_FACTOR = np.array([0.6, 1.0, 1.8, 2.5])
P_SEVERE_INJURY = np.array([0.00, 0.03, 0.20, 0.35])
PROPERTY_MEDIAN, PROPERTY_SIGMA, PROPERTY_CAP = 2800.0, 1.0, 150000.0
INJURY_MEDIAN, INJURY_SIGMA, INJURY_CAP = 6500.0, 1.1, 250000.0
TAIL_XMIN, TAIL_ALPHA, TAIL_CAP = 50000.0, 1.6, 2000000.0

CLAIM_ID_LOW, CLAIM_ID_SPAN = 1_000_000, 9_000_000     # 7-digit ids
POLICY_ID_LOW, POLICY_ID_SPAN = 100_000, 900_000       # 6-digit ids
POOL_SIZE = 2000                                        # the carrier's book

# Column order of the published Module 2 file (18 columns).
M2_COLUMNS = ["claim_id", "policy_id", "incident_date", "report_date",
              "claim_type", "severity", "vehicles_involved", "vehicle_make",
              "vehicle_year", "vehicle_value", "region", "report_channel",
              "adjuster_id", "injury_amount", "property_amount",
              "vehicle_amount", "total_amount", "notes"]
AMOUNT_COLUMNS = ["injury_amount", "property_amount", "vehicle_amount",
                  "total_amount"]
M1_COLUMNS = ["claim_id", "incident_date", "claim_type", "severity",
              "vehicle_year", "injury_amount", "property_amount",
              "vehicle_amount", "total_amount"]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def policy_pool(size: int = POOL_SIZE) -> np.ndarray:
    """The carrier's policy ids: a fixed permutation of 6-digit integers.

    The first POOL_SIZE ids are the book used by Modules 2 and 3, so the same
    policy ids recur across modules. Larger frames extend along the same
    permutation.
    """
    rs = np.random.RandomState(SEED_POOL)
    perm = rs.permutation(POLICY_ID_SPAN) + POLICY_ID_LOW
    return perm[:size]


def adjuster_weights() -> np.ndarray:
    """Fixed caseload weights for the 25 adjusters (some are busier)."""
    rs = np.random.RandomState(SEED_POOL + 1)
    w = 1.0 + 0.5 * rs.random_sample(len(ADJUSTER_IDS))
    return w / w.sum()


def _weighted_days(start: str, end: str):
    days = pd.date_range(start, end, freq="D")
    w = np.array([MONTH_WEIGHT[m] for m in days.month], dtype=float)
    return days, w / w.sum()


def _cents(x: np.ndarray) -> np.ndarray:
    return np.rint(x * 100.0).astype(np.int64)


def generate_core(n_rows: int, rs: np.random.RandomState, window,
                  policy_ids: Optional[np.ndarray] = None) -> pd.DataFrame:
    """The clean claims world: 17 columns, no defects, no `notes` column.

    All randomness comes from `rs`, consumed in a fixed order. `policy_ids`,
    when given, overrides the policy assignment (the Module 3 builder uses it
    to tie claims to a policyholder table).
    """
    n = int(n_rows)
    start, end = window

    # Identifiers
    claim_id = rs.permutation(CLAIM_ID_SPAN)[:n] + CLAIM_ID_LOW
    if policy_ids is None:
        pool_size = min(POLICY_ID_SPAN, max(POOL_SIZE, int(np.ceil(n / 1.2))))
        pool = policy_pool(pool_size)
        weights = rs.dirichlet(np.full(pool_size, 2.0))   # uneven caseloads
        policy_id = rs.choice(pool, size=n, p=weights)
    else:
        policy_id = np.asarray(policy_ids, dtype=np.int64)
        if len(policy_id) != n:
            raise ValueError("policy_ids must have n_rows entries")

    # Dates
    days, dw = _weighted_days(start, end)
    incident = days.values[rs.choice(len(days), size=n, p=dw)]
    lag = np.minimum(np.floor(rs.exponential(REPORT_LAG_MEAN_DAYS, n)),
                     REPORT_LAG_MAX_DAYS).astype("timedelta64[D]")
    report = incident + lag

    # Claim descriptors
    ct = rs.choice(len(CLAIM_TYPES), size=n, p=CLAIM_TYPE_W)
    sv = rs.choice(len(SEVERITIES), size=n, p=SEVERITY_W)
    cum = np.cumsum(VEHICLES_INVOLVED_P, axis=1)[:, :3]
    u = rs.random_sample(n)
    vehicles_involved = 1 + (u[:, None] > cum[ct]).sum(axis=1)

    # Vehicle block
    mk = rs.choice(len(MAKES), size=n, p=MAKE_W)
    age = np.floor(rs.gamma(2.2, 3.2, n))
    year = np.clip(CURRENT_MODEL_YEAR - age, OLDEST_MODEL_YEAR, CURRENT_MODEL_YEAR)
    year = np.minimum(year, LAST_YEAR_BY_MAKE[mk]).astype(np.int64)
    value = (TIER_BASE[mk] * DEPRECIATION_PER_YEAR ** (CURRENT_MODEL_YEAR - year)
             * np.exp(rs.normal(0.0, VALUE_NOISE_SIGMA, n)))
    value = np.rint(np.clip(value, VALUE_MIN, VALUE_MAX) / 100.0) * 100.0
    value = value.astype(np.int64)

    # Process fields
    rg = rs.choice(len(REGIONS), size=n, p=REGION_W)
    ch = rs.choice(len(CHANNELS), size=n, p=CHANNEL_W)
    adjuster = ADJUSTER_IDS[rs.choice(len(ADJUSTER_IDS), size=n, p=adjuster_weights())]

    # Amounts (SCHEMA_PROPOSAL section 9)
    frac = rs.uniform(DAMAGE_FRAC_LO[sv], DAMAGE_FRAC_HI[sv])
    has_v = rs.random_sample(n) < P_VEHICLE[ct]
    has_p = rs.random_sample(n) < P_PROPERTY[ct]
    has_i = rs.random_sample(n) < P_INJURY[ct]
    has_v = has_v | ~(has_v | has_p | has_i)        # every claim pays something
    f = SEVERITY_FACTOR[sv]
    vehicle = np.where(has_v, value * frac, 0.0)
    prop = np.exp(rs.normal(np.log(PROPERTY_MEDIAN * f), PROPERTY_SIGMA, n))
    prop = np.where(has_p, np.minimum(prop, PROPERTY_CAP), 0.0)
    inj = np.exp(rs.normal(np.log(INJURY_MEDIAN * f), INJURY_SIGMA, n))
    inj = np.where(has_i, np.minimum(inj, INJURY_CAP), 0.0)
    severe = has_i & (rs.random_sample(n) < P_SEVERE_INJURY[sv])
    k = int(severe.sum())
    if k > 0:
        probs = (np.arange(k) + 0.5) / k
        tail = TAIL_XMIN * (1.0 - probs) ** (-1.0 / TAIL_ALPHA)
        tail = np.minimum(tail, TAIL_CAP)[rs.permutation(k)]
        inj[severe] = tail
    injury_c, property_c, vehicle_c = _cents(inj), _cents(prop), _cents(vehicle)
    total_c = injury_c + property_c + vehicle_c

    df = pd.DataFrame({
        "claim_id": claim_id.astype(np.int64),
        "policy_id": policy_id,
        "incident_date": pd.to_datetime(incident),
        "report_date": pd.to_datetime(report),
        "claim_type": pd.Categorical.from_codes(ct, CLAIM_TYPES),
        "severity": pd.Categorical.from_codes(sv, SEVERITIES, ordered=True),
        "vehicles_involved": vehicles_involved.astype(np.int64),
        "vehicle_make": pd.Categorical.from_codes(mk, MAKES),
        "vehicle_year": year,
        "vehicle_value": pd.array(value, dtype="Int64"),
        "region": pd.Categorical.from_codes(rg, REGIONS),
        "report_channel": pd.Categorical.from_codes(ch, CHANNELS),
        "adjuster_id": adjuster.astype(np.int64),
        "injury_amount": injury_c / 100.0,
        "property_amount": property_c / 100.0,
        "vehicle_amount": vehicle_c / 100.0,
        "total_amount": total_c / 100.0,
    })
    df = df.sort_values(["report_date", "claim_id"], kind="mergesort")
    return df.reset_index(drop=True)


def add_notes_column(df: pd.DataFrame) -> pd.DataFrame:
    """Append the `notes` column (adjuster free text) so the frame matches the
    published 18-column schema."""
    out = df.copy()
    out["notes"] = np.full(len(out), np.nan)
    return out


# ---------------------------------------------------------------------------
# Public generators
# ---------------------------------------------------------------------------

def generate_claims(n_rows: int = 2_000_000, seed: int = STUDENT_SEED,
                    with_defects: bool = False) -> pd.DataFrame:
    """Generate `n_rows` claims in the Module 2 schema (18 columns).

    Students call this in the First Contact notebook, Stage 3, to build a
    2,000,000-row frame in their own session. The string columns come back as
    pandas Categorical and the dates as datetime64, which keeps the frame
    small; a CSV written from it loads exactly like m2_claims.csv.

    `with_defects=True` requires the instructor's build module, which is not
    distributed.
    """
    rs = np.random.RandomState(seed)
    df = generate_core(n_rows, rs, M2_WINDOW)
    if with_defects:
        try:
            from claims_world_private import apply_module2_defects
        except ImportError as exc:
            raise ImportError(
                "with_defects=True needs claims_world_private.py, which is "
                "part of the instructor build and is not distributed."
            ) from exc
        df, _records = apply_module2_defects(df, rs)
        return df
    return add_notes_column(df)


def generate_sample(n_rows: int, seed: int) -> pd.DataFrame:
    """The Module 1 Toolkit Check sample: 9 columns, 2023 incidents, no defects."""
    rs = np.random.RandomState(seed)
    df = generate_core(n_rows, rs, M1_WINDOW)
    return df[M1_COLUMNS].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Writing and hashing (fixed formatting so regeneration is byte-identical)
# ---------------------------------------------------------------------------

def write_csv(df: pd.DataFrame, path: str) -> None:
    """Write a frame with the course's fixed CSV conventions."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n", float_format="%.2f",
              date_format="%Y-%m-%d", encoding="utf-8")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    # Quick self-check; the full regeneration lives in claims_world_private.py.
    small = generate_claims(1500, seed=STUDENT_SEED)
    print(small.shape, list(small.columns) == M2_COLUMNS)
    print(small.dtypes.to_string())
