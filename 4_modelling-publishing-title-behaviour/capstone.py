"""
capstone.py — shared contract loader and helpers for the Project 4 notebooks.

Place at the project root, beside data/. Every analysis notebook starts with:

    %load_ext autoreload
    %autoreload 2
    from capstone import *
    df = load_scoped()

Why a module and not a copied cell: the book definition lives in exactly one
place (notebook 01, serialised to JSON). A notebook that retypes a filter
string creates a second source of truth that drifts silently. This module is
the only permitted reader of that JSON.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

# ═══════════════════════════════════════════════════════════════════════
# Paths and constants
# ═══════════════════════════════════════════════════════════════════════

PROJECT   = Path(__file__).resolve().parent
DATA      = PROJECT / "data"
PROCESSED = DATA / "processed"
LOOKUP    = DATA / "lookup"
FIGURES   = PROJECT / "figures"

SCOPED_PARQUET = PROCESSED / "sales_scoped.parquet"
CONTRACT_JSON  = LOOKUP / "analysis_filters.json"
BOOK_MASTER    = LOOKUP / "book_master.csv"

EXPECTED_VERSION = 1
FROZEN_ROWS      = 94_872

# engine="python" on every .query(): numexpr cannot evaluate pandas extension
# dtypes (client_excluded is nullable `boolean`).
Q = dict(engine="python")

# Columns an analysis notebook must never read. `Name` is the customer's
# business name; `Customer ID` is the only permitted customer identifier.
FORBIDDEN_COLS = ["Name"]


# ═══════════════════════════════════════════════════════════════════════
# Contract
# ═══════════════════════════════════════════════════════════════════════

def load_contract(strict: bool = True) -> dict:
    """Read the serialised filter contract written by notebook 01 §10.3.

    strict=True asserts the version. Set False only to inspect an old
    contract deliberately, never to silence a version mismatch.
    """
    if not CONTRACT_JSON.exists():
        raise FileNotFoundError(
            f"{CONTRACT_JSON} not found: run notebook 01 first")

    c = json.loads(CONTRACT_JSON.read_text())
    if not isinstance(c, dict) or "filters" not in c:
        raise ValueError("contract has no 'filters' key: re-run notebook 01")

    if strict:
        got = c.get("contract_version")
        assert got == EXPECTED_VERSION, (
            f"contract is v{got}, this module expects v{EXPECTED_VERSION}. "
            "Re-run notebook 01, or bump EXPECTED_VERSION deliberately.")
    return c


def _contract_or_none():
    """Notebook 01 imports this module before the contract exists."""
    try:
        return load_contract()
    except FileNotFoundError:
        return None


CONTRACT   = _contract_or_none()
FILTERS    = CONTRACT["filters"] if CONTRACT else {}
BOOK_SCOPE = CONTRACT["book_scope"] if CONTRACT else None
BOOK_TYPES = CONTRACT.get("book_types", []) if CONTRACT else []
CTRL       = CONTRACT.get("control_totals", {}) if CONTRACT else {}


# ═══════════════════════════════════════════════════════════════════════
# Display vocabulary
# ═══════════════════════════════════════════════════════════════════════

def generalise_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Replace brand-specific category labels with generic ones.

    `Channel` is the publishing arm; anything other than the generic
    'Commercial' and 'Not recorded' arms is shown as 'Trade imprint'.
    `source_tab` names the masterlist tab a title was matched from.
    """
    if "Channel" in df:
        generic = df["Channel"].isin(["Commercial", "Not recorded"]) | df["Channel"].isna()
        df["Channel"] = df["Channel"].where(generic, "Trade imprint")
    if "source_tab" in df:
        s = df["source_tab"].astype(str).str.lower()
        tab = np.where(s.str.contains("ebook"), "eBook masterlist",
              np.where(s.str.contains("old"), "Print masterlist (archived)",
                       "Print masterlist"))
        df["source_tab"] = pd.Series(tab, index=df.index).where(df["source_tab"].notna())
    return df


_PSEUDO: dict = {}


def pseudonym(value, prefix: str = "Title"):
    """Stable display alias for a confidential label (title, description, ISBN).

    The first distinct value seen for a prefix becomes '<prefix> 001', the next
    '<prefix> 002', and so on. Aliases are sequential rather than hashed, so
    they cannot be reversed against a public catalogue.
    """
    if value is None or (not isinstance(value, (list, tuple)) and pd.isna(value)):
        return value
    reg = _PSEUDO.setdefault(prefix, {})
    if value not in reg:
        reg[value] = f"{prefix} {len(reg) + 1:03d}"
    return reg[value]


def mask_index(obj, prefix: str = "Title"):
    """Copy of a Series or DataFrame with every index label aliased."""
    out = obj.copy()
    out.index = [pseudonym(v, prefix) for v in out.index]
    return out


def mask_cols(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    """Copy of a DataFrame with the given columns aliased, e.g.
    mask_cols(frame, {"item_desc": "Item", "title": "Title"})."""
    out = df.copy()
    for c, prefix in cols.items():
        if c in out:
            out[c] = out[c].map(lambda v: pseudonym(v, prefix))
    return out


# ═══════════════════════════════════════════════════════════════════════
# Frames
# ═══════════════════════════════════════════════════════════════════════

_CACHE: dict = {}


def load_scoped(verbose: bool = True) -> pd.DataFrame:
    """Load the scoped line frame and verify it against the contract.

    Cached per kernel. Delete _CACHE['scoped'] if the parquet is rebuilt
    mid-session.
    """
    if "scoped" in _CACHE:
        return _CACHE["scoped"]

    assert CONTRACT is not None, "no filter contract: run notebook 01 first"
    if not SCOPED_PARQUET.exists():
        raise FileNotFoundError(f"{SCOPED_PARQUET} not found: run notebook 01 first")

    df = pd.read_parquet(SCOPED_PARQUET)

    # Asserts capable of failing on plausible data
    assert len(df) == FROZEN_ROWS, (
        f"{len(df):,} rows, expected {FROZEN_ROWS:,}: "
        "a row-removing step entered the build")

    required = ["book_scope", "scope_reason", "line_role",
                "amt_sign", "qty_sign", "has_genre", "isbn_key", "ym", "Qty"]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"scoped parquet lacks contract columns: {missing}"

    if CONTRACT.get("frozen_rows") is not None:
        assert len(df) == CONTRACT["frozen_rows"], (
            "parquet and contract disagree on row count: they were built "
            "from different runs. Re-run notebook 01 end to end.")

    # ym is period[M] for aggregation; ym_ts is Timestamp for plotting only.
    # matplotlib cannot place Period objects on a date axis.
    if "ym_ts" not in df.columns:
        df["ym_ts"] = df["ym"].dt.to_timestamp()

    df = generalise_labels(df)
    _CACHE["scoped"] = df

    if verbose:
        print(f"scoped   {len(df):,} lines · {df['ym'].nunique()} months "
              f"· contract v{CONTRACT['contract_version']}")
    return df


def load_master(verbose: bool = True) -> pd.DataFrame:
    """Load the ISBN-grain title master."""
    if "master" in _CACHE:
        return _CACHE["master"]

    bm = pd.read_csv(BOOK_MASTER, index_col=0,
                     parse_dates=["first_sale", "last_sale"])
    assert bm.index.is_unique, "isbn_key is not unique in book_master"
    _CACHE["master"] = bm

    if verbose:
        print(f"master   {len(bm):,} ISBNs · "
              f"{int(bm['has_genre'].sum()):,} with genre · "
              f"{int(bm['has_priced_sale'].sum()):,} commercially active")
    return bm


def pop(key: str, df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Apply a named filter. The ONLY sanctioned way to subset.

    Never write a filter string inline in a notebook: that is how two
    populations diverge without an error being raised.
    """
    if key not in FILTERS:
        raise KeyError(f"'{key}' not in contract. Available: {sorted(FILTERS)}")
    d = load_scoped(verbose=False) if df is None else df
    return d.query(FILTERS[key], **Q)


def populations(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Population registry. Figure captions interpolate from this, never from
    a typed literal, so a scope change propagates to every caption."""
    d = load_scoped(verbose=False) if df is None else df
    rows = []
    for k in FILTERS:
        s = d.query(FILTERS[k], **Q)
        rows.append({"filter": k,
                     "lines": len(s),
                     "units": s["Qty"].sum(),
                     "revenue": s["Amount"].sum(),
                     "isbns": s["isbn_key"].nunique(),
                     "months": s["ym"].nunique()})
    out = pd.DataFrame(rows).set_index("filter")

    # Drift detector: compares live counts to the contract's stored totals.
    if CTRL:
        drift = {k: int(out.loc[k, "lines"]) - v
                 for k, v in CTRL.items()
                 if k in out.index and int(out.loc[k, "lines"]) != v}
        if drift:
            raise AssertionError(
                f"live counts differ from contract control totals: {drift}. "
                "The parquet and JSON came from different runs.")
    return out


# ═══════════════════════════════════════════════════════════════════════
# Series builders: one population decision each, made once
# ═══════════════════════════════════════════════════════════════════════

def monthly_series(key: str = "demand", value: str = "Qty",
                   df: pd.DataFrame | None = None) -> pd.Series:
    """Calendar-complete monthly series for the forecasting notebook.

    asfreq('MS') makes the DatetimeIndex regular: STL and SARIMAX both require
    an inferable frequency, and lag features built with .shift() are
    positional, so a missing month would silently misalign every lag.

    MODIFY CONDITION: key='revenue_ts' models books and services;
    key='demand' models books only.
    """
    d = pop(key, df)
    s = d.groupby("ym_ts")[value].sum().asfreq("MS")
    assert s.notna().all(), (
        f"{s.isna().sum()} calendar gaps in the {key} series: "
        "a missing month makes the seasonal period meaningless")
    return s


def decay_panel(scope: str = "all", min_months: int = 6,
                df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Months-since-first-sale panel, one row per ISBN.

    scope='all'   → every book-scoped ISBN. Use for a headline fit.
    scope='genre' → segmentable ISBNs only. Use for genre-split panels.
    """
    key = {"all": "demand", "genre": "genre"}[scope]
    d = pop(key, df).dropna(subset=["isbn_key", "Qty"]).copy()

    # Integer month index: (Period - Period) returns an offset object, not an
    # int, and breaks groupby downstream.
    d["mi"] = d["ym"].dt.year * 12 + d["ym"].dt.month
    by = d.groupby(["isbn_key", "mi"])["Qty"].sum().reset_index()
    by["m0"]  = by.groupby("isbn_key")["mi"].transform("min")
    by["msf"] = by["mi"] - by["m0"]

    # Dense 0..max grid per ISBN: a month with no sales is a real zero.
    grid = (by.set_index(["isbn_key", "msf"])["Qty"]
              .unstack("msf")
              .reindex(columns=range(0, int(by["msf"].max()) + 1))
              .fillna(0.0))

    observed = grid.notna().sum(axis=1)
    grid = grid[observed >= min_months]

    print(f"decay panel · scope={scope} · {len(grid):,} ISBNs "
          f"· horizon {grid.shape[1]} months · min_months={min_months}")
    return grid


# ═══════════════════════════════════════════════════════════════════════
# Figures
# ═══════════════════════════════════════════════════════════════════════

def save_fig(fig, name: str, dpi: int = 200, ext: str = "png", tight: bool = True):
    """Write figures/<name>.<ext> and echo the path.

    Guard: every saved figure must name the client as 'Company X' in its
    title or suptitle, so an unlabelled chart cannot reach the repository.
    """
    titles = [a.get_title() for a in fig.axes] + [a.get_title(loc="left") for a in fig.axes]
    if fig._suptitle is not None:
        titles.append(fig._suptitle.get_text())
    assert any("Company X" in t for t in titles), \
        "figure must name the client as 'Company X'"
    guard_pii_text(" ".join(titles))

    FIGURES.mkdir(parents=True, exist_ok=True)
    if tight:
        fig.tight_layout()
    path = FIGURES / f"{name}.{ext}"
    fig.savefig(path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"saved → figures/{path.name}")
    return path


def guard_pii(df: pd.DataFrame) -> None:
    """Raise if a frame bound for a figure carries a forbidden column."""
    bad = [c for c in FORBIDDEN_COLS if c in df.columns]
    assert not bad, f"forbidden columns present in a figure frame: {bad}"


def guard_pii_text(text: str) -> None:
    """Raise if figure text looks like it carries an ISBN."""
    import re
    assert not re.search(r"97[89]\d{10}", text), "an ISBN reached a figure title"


__all__ = [
    "PROJECT", "DATA", "PROCESSED", "LOOKUP", "FIGURES", "Q",
    "CONTRACT", "FILTERS", "BOOK_SCOPE", "BOOK_TYPES", "CTRL",
    "load_contract", "load_scoped", "load_master",
    "pop", "populations", "monthly_series", "decay_panel",
    "generalise_labels", "pseudonym", "mask_index", "mask_cols",
    "save_fig", "guard_pii", "guard_pii_text",
    "np", "pd",
]
