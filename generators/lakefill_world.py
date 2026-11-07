"""
lakefill_world.py: the Lakefill National Bank operational loss world for
ERM 424, Modules 5 to 10.

PUBLIC MODULE. This file may be published to students. It contains the schema
(business lines, event types, regions, reporting channels, root-cause tags,
column order), the dated facts the data dictionary also states, a clean
generator that produces the schema with no planted structure (for practicum
cells that show what Poisson counts and lognormal losses look like), the panel
builder every Stage 3 to 6 notebook uses, and loaders. Nothing in this file
describes a planted effect, a planted data quirk, an answer-key value, or a
seed of any published course file. Those live in lakefill_world_private.py,
which is never published.

Course:  ERM 424, Statistics and Data Analytics for Risk Management,
         Northwestern University School of Professional Studies, Winter 2027.
World:   Lakefill National Bank, a fictional mid-size Midwestern commercial
         bank. Regions are real places; event types are the Basel level-1
         operational event types; everything else is invented. No third-party
         data is loaded, transformed, or redistributed.

Seeds in this file:
    DEMO_SEED  424   the clean demonstration world a notebook may generate
The seeds of the published course files live in the instructor's build module.

Determinism: numpy.random.RandomState (the legacy stream NumPy guarantees to
stay fixed across versions, NEP 19), fixed column order, fixed CSV formatting.
Vectorized throughout; the only Python loop is over business line x month.

Usage in Colab:
    from lakefill_world import load_events, load_exposure, build_panel
    ev = load_events("lakefill_checkpoint1.csv")
    ex = load_exposure("lakefill_exposure_monthly.csv")
    panel = build_panel(ev, ex)

Dependencies: numpy and pandas only.
"""

from __future__ import annotations

import hashlib
import os
from typing import Iterable, Optional

import numpy as np
import pandas as pd

__version__ = "1.0.0"

DEMO_SEED = 424

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

LINES = [
    "Retail Banking",
    "Commercial Lending",
    "Payments",
    "Asset Management",
    "Trading and Treasury",
    "Shared Services",
]

EVENT_TYPES = [
    "Internal Fraud",
    "External Fraud",
    "Employment Practices and Workplace Safety",
    "Clients, Products and Business Practices",
    "Damage to Physical Assets",
    "Business Disruption and System Failures",
    "Execution, Delivery and Process Management",
]

REGIONS = ["Chicago Metro", "Illinois", "Wisconsin", "Indiana and Michigan"]

REPORTING_CHANNELS = ["Branch", "Call Center", "System Alert", "Internal Audit", "Customer Complaint"]

ROOT_CAUSE_TAGS = ["manual error", "system defect", "vendor", "cyber", "process gap", "external event", "policy breach"]

EVENT_COLUMNS = [
    "event_id",
    "business_line",
    "event_type",
    "region",
    "reporting_channel",
    "occurrence_date",
    "discovery_date",
    "reporting_date",
    "status",
    "close_date",
    "days_open",
    "initial_estimate",
    "final_reserve",
    "gross_loss",
    "recoveries",
    "net_loss",
    "threshold_era",
    "post_verification",
    "post_migration",
    "transaction_volume",
    "account_count",
    "control_maturity_score",
    "staffing_ratio",
    "system_age",
    "automation_flag",
    "root_cause_tags",
]

EXPOSURE_COLUMNS = [
    "month",
    "business_line",
    "transaction_volume",
    "account_count",
    "control_maturity_score",
    "staffing_ratio",
    "system_age",
    "automation_flag",
]

DATE_COLUMNS = ["occurrence_date", "discovery_date", "reporting_date", "close_date"]

# Columns whose values are whole numbers; written without decimals.
INTEGER_COLUMNS = ["days_open", "post_verification", "post_migration", "transaction_volume",
                   "account_count", "system_age", "automation_flag"]

# Availability marks, as the data dictionary states them.
#   D = known at discovery; C = known at close; R = reference, copied from the
#   line-period exposure table.
AVAILABILITY = {
    "event_id": "D", "business_line": "D", "event_type": "D", "region": "D", "reporting_channel": "D",
    "occurrence_date": "D", "discovery_date": "D", "reporting_date": "D", "status": "D",
    "close_date": "C", "days_open": "C", "initial_estimate": "D", "final_reserve": "C",
    "gross_loss": "C", "recoveries": "C", "net_loss": "C",
    "threshold_era": "D", "post_verification": "D", "post_migration": "D",
    "transaction_volume": "R", "account_count": "R", "control_maturity_score": "R",
    "staffing_ratio": "R", "system_age": "R", "automation_flag": "R", "root_cause_tags": "D",
}

# ---------------------------------------------------------------------------
# Dated facts (also stated in the data dictionary)
# ---------------------------------------------------------------------------

HISTORY_START = "2021-01"
HISTORY_END = "2025-12"
SYSTEM_CHANGE_DATE = pd.Timestamp("2023-01-01")     # ORMS replaces the legacy GL feed
VERIFICATION_DATE = pd.Timestamp("2023-04-01")      # retail payment verification live
MIGRATION_DATE = pd.Timestamp("2023-07-01")         # payments platform migration
ASSET_MANAGEMENT_ONBOARDED = pd.Timestamp("2023-07-01")
TT_AUTOMATION_DATE = pd.Timestamp("2024-01-01")     # trading and treasury straight-through processing
BANK_THRESHOLD = 10000.0                            # collection threshold, every line, every year
SHARED_SERVICES_LEGACY_THRESHOLD = 20000.0          # shared services before 2023-01-01


def collection_threshold(business_line, discovery_date) -> np.ndarray:
    """The collection threshold in force for each event (vectorized)."""
    line = np.asarray(business_line, dtype=object)
    date = pd.to_datetime(pd.Series(discovery_date)).to_numpy()
    legacy_shared = (line == "Shared Services") & (date < SYSTEM_CHANGE_DATE.to_datetime64())
    return np.where(legacy_shared, SHARED_SERVICES_LEGACY_THRESHOLD, BANK_THRESHOLD)


def threshold_era(discovery_date) -> np.ndarray:
    date = pd.to_datetime(pd.Series(discovery_date)).to_numpy()
    return np.where(date < SYSTEM_CHANGE_DATE.to_datetime64(), "before 2023", "2023 onward").astype(object)


# ---------------------------------------------------------------------------
# Loaders and writers
# ---------------------------------------------------------------------------

def load_events(path: str) -> pd.DataFrame:
    """Read an event file (raw, Checkpoint 1, Q1 slice or Q2 extract) with the
    date columns parsed. Reads exactly what a student would otherwise read with
    pd.read_csv, plus the parse."""
    df = pd.read_csv(path)
    for c in DATE_COLUMNS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
    return df


def load_exposure(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def write_csv(df: pd.DataFrame, path: str) -> None:
    """Fixed formatting so the same frame gives the same bytes everywhere."""
    out = df.copy()
    for c in INTEGER_COLUMNS:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c]).round().astype("Int64")
    for c in DATE_COLUMNS:
        if c in out.columns and np.issubdtype(out[c].dtype, np.datetime64):
            out[c] = out[c].dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False, float_format="%.2f", lineterminator="\n", encoding="utf-8")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# The panel (Module 7 onward)
# ---------------------------------------------------------------------------

def net_loss(events: pd.DataFrame) -> pd.Series:
    """gross_loss minus recoveries; NaN where either is NaN (the file's own
    net_loss column is built the same way)."""
    return events["gross_loss"] - events["recoveries"]


def build_panel(events: pd.DataFrame, exposure: pd.DataFrame,
                lines: Optional[Iterable[str]] = None,
                event_types: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """One row per business line x event type x month, with the event count and
    the exposure table's columns joined. Months with no events are kept as zero
    cells. A line's months are the months it has an exposure row for (Asset
    Management begins when it was onboarded). Rows with a blank event_type are
    counted under the level "Uncoded" so no event is lost; drop that level if
    your model excludes them, and say so.
    """
    ev = events.copy()
    ev["month"] = pd.to_datetime(ev["discovery_date"]).dt.strftime("%Y-%m")
    ev["event_type"] = ev["event_type"].fillna("Uncoded")
    lines = list(lines) if lines is not None else LINES
    types = list(event_types) if event_types is not None else EVENT_TYPES + ["Uncoded"]
    counts = (ev[ev["business_line"].isin(lines) & ev["event_type"].isin(types)]
              .groupby(["business_line", "event_type", "month"]).size().rename("event_count"))
    ex = exposure[exposure["business_line"].isin(lines)]
    grid = (ex[["business_line", "month"]].drop_duplicates()
            .merge(pd.DataFrame({"event_type": types}), how="cross"))
    panel = grid.merge(counts.reset_index(), on=["business_line", "event_type", "month"], how="left")
    panel["event_count"] = panel["event_count"].fillna(0).astype(int)
    panel = panel.merge(ex, on=["business_line", "month"], how="left")
    panel = panel.sort_values(["business_line", "event_type", "month"]).reset_index(drop=True)
    return panel[["business_line", "event_type", "month", "event_count"] + EXPOSURE_COLUMNS[2:]]


# ---------------------------------------------------------------------------
# The clean demonstration world
# ---------------------------------------------------------------------------

_DEMO_RATE = {"Retail Banking": 35.0, "Commercial Lending": 6.0, "Payments": 20.0,
              "Asset Management": 14.0, "Trading and Treasury": 12.0, "Shared Services": 16.0}
_DEMO_MEDIAN = {"Retail Banking": 25000.0, "Commercial Lending": 70000.0, "Payments": 28000.0,
                "Asset Management": 50000.0, "Trading and Treasury": 40000.0, "Shared Services": 27000.0}
_DEMO_MIX = np.array([0.05, 0.20, 0.08, 0.20, 0.05, 0.14, 0.28])


def generate_clean_world(seed: int = DEMO_SEED, start: str = HISTORY_START, end: str = HISTORY_END,
                         as_of: Optional[str] = None) -> pd.DataFrame:
    """A homogeneous world in the Lakefill schema: Poisson monthly counts at a
    fixed rate per line, lognormal gross losses (log-sd 1.0), a fixed type mix,
    constant reference columns, no quirks, no effects, no drift. Every event is
    closed unless `as_of` is given. For practicum cells that show what the
    textbook assumptions look like before the real file is opened.
    """
    rs = np.random.RandomState(seed)
    months = pd.period_range(start, end, freq="M")
    frames = []
    for line in LINES:
        for m in months:
            n = int(rs.poisson(_DEMO_RATE[line]))
            if n == 0:
                continue
            types = rs.choice(len(EVENT_TYPES), size=n, p=_DEMO_MIX)
            gross = np.exp(np.log(_DEMO_MEDIAN[line]) + rs.normal(0.0, 1.0, n))
            gross = np.maximum(gross, BANK_THRESHOLD)
            day = rs.randint(0, m.days_in_month, n)
            disc = m.to_timestamp() + pd.to_timedelta(day, unit="D")
            frames.append(pd.DataFrame({
                "business_line": line,
                "event_type": np.array(EVENT_TYPES, dtype=object)[types],
                "region": rs.choice(REGIONS, size=n),
                "reporting_channel": rs.choice(REPORTING_CHANNELS, size=n),
                "discovery_date": disc,
                "gross": gross,
            }))
    ev = pd.concat(frames, ignore_index=True)
    n = len(ev)
    ev["event_id"] = ["OL%07d" % i for i in rs.permutation(9_000_000)[:n] + 1_000_000]
    ev["occurrence_date"] = ev["discovery_date"] - pd.to_timedelta(np.floor(rs.exponential(20.0, n)), unit="D")
    ev["reporting_date"] = ev["discovery_date"] + pd.to_timedelta(np.rint(rs.exponential(4.0, n)), unit="D")
    days = np.clip(np.rint(np.exp(np.log(60.0) + rs.normal(0.0, 0.5, n))), 1, 540).astype(int)
    ev["close_date"] = ev["discovery_date"] + pd.to_timedelta(days, unit="D")
    ev["days_open"] = days
    ev["initial_estimate"] = np.rint(ev["gross"] * np.exp(rs.normal(0.0, 0.7, n)) / 100.0) * 100.0
    ev["final_reserve"] = np.rint(ev["gross"] * np.exp(rs.normal(0.0, 0.2, n)) / 100.0) * 100.0
    ev["gross_loss"] = np.rint(ev["gross"])
    ev["recoveries"] = np.rint(ev["gross_loss"] * rs.beta(1.0, 6.0, n))
    ev["net_loss"] = ev["gross_loss"] - ev["recoveries"]
    ev["status"] = "Closed"
    ev["threshold_era"] = threshold_era(ev["discovery_date"])
    ev["post_verification"] = (ev["discovery_date"] >= VERIFICATION_DATE).astype(int)
    ev["post_migration"] = (ev["discovery_date"] >= MIGRATION_DATE).astype(int)
    ev["transaction_volume"] = 1_000_000.0
    ev["account_count"] = 100_000.0
    ev["control_maturity_score"] = 3.0
    ev["staffing_ratio"] = 1.0
    ev["system_age"] = 5.0
    ev["automation_flag"] = 0
    ev["root_cause_tags"] = rs.choice(ROOT_CAUSE_TAGS, size=n)
    if as_of is not None:
        cut = pd.Timestamp(as_of)
        ev = ev[ev["discovery_date"] <= cut].copy()
        open_mask = ev["close_date"] > cut
        ev.loc[open_mask, "status"] = "Open"
        for c in ["close_date", "days_open", "final_reserve", "recoveries", "net_loss"]:
            ev.loc[open_mask, c] = np.nan
    ev = ev.sort_values(["discovery_date", "event_id"]).reset_index(drop=True)
    return ev[EVENT_COLUMNS]


if __name__ == "__main__":
    demo = generate_clean_world()
    print(demo.shape)
    print(demo.head())
