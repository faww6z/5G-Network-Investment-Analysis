"""Transparent annual investment model. All amounts are nominal CAD.

This module calculates independently of Excel. No workbook formulas are evaluated
or copied into Python. See documentation/methodology.md for timing conventions.
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import numpy_financial as nf
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_assumptions(path: Path | None = None) -> dict[str, float]:
    frame = pd.read_csv(path or ROOT / "data/assumptions.csv")
    return dict(zip(frame.key, frame.value.astype(float)))


def payback(flows: np.ndarray, discount: float = 0) -> float | None:
    values = flows / (1 + discount) ** np.arange(len(flows))
    cumulative = np.cumsum(values)
    for year in range(1, len(flows)):
        if cumulative[year - 1] < 0 <= cumulative[year] and values[year] > 0:
            return float(year - 1 - cumulative[year - 1] / values[year])
    return None


def evaluate(a: dict[str, float], growth: float | None = None,
             expanded: bool = True, horizon: int | None = None,
             delay_years: int = 0) -> dict:
    """A five-year screen, with explicit average/opening/closing subscriber flows.

    Linear within-year net growth makes opening = average / (1 + g/2).
    Cancellations = average * annual cancellation intensity. Gross additions
    replace cancellations as well as delivering net growth.
    """
    g = a["base_growth"] if growth is None else growth
    n = int(a["horizon"]) if horizon is None else horizon
    if not 0 <= g <= 1 or n < 1 or not 0 <= delay_years < n:
        raise ValueError("Growth must be in [0,1] and delay shorter than horizon")
    if a["discount_rate"] <= -1 or a["depreciation_life"] < n:
        raise ValueError("Discount rate must exceed -100%; asset life must cover horizon")
    if any(a[key] < 0 for key in ("initial_capex", "year1_customers", "arpu", "initial_opex", "cac")):
        raise ValueError("CAPEX, subscribers, ARPU, OPEX and CAC must be nonnegative")
    share = a["incremental_share"] if expanded else 1.0
    tax_rate = a["tax_rate"] if expanded else 0.0
    cac = a["cac"] if expanded else 0.0
    churn = a["annual_churn"] if expanded else 0.0
    nwc_rate = a["nwc_rate"] if expanded else 0.0
    maint_rate = a["maintenance_rate"] if expanded else 0.0
    opening = a["year1_customers"] / (1 + g / 2)
    initial_acquisition = opening * cac
    records = [dict(year=0, average_customers=0, opening_customers=0,
                    closing_customers=opening, net_additions=opening,
                    cancellations=0, gross_additions=opening,
                    gross_revenue=0, revenue=0, network_opex=0,
                    acquisition_cost=initial_acquisition,
                    ebitda=-initial_acquisition, depreciation=0,
                    ebit=-initial_acquisition, opening_nol=0, nol_used=0,
                    taxable_income=0, cash_tax=0, closing_nol=initial_acquisition,
                    nwc=0, delta_nwc=0, maintenance_capex=0,
                    capex=a["initial_capex"], residual_cash=0,
                    fcf=-a["initial_capex"]-initial_acquisition)]
    previous_nwc = 0.0
    nol = initial_acquisition
    prior_maintenance = 0.0
    for year in range(1, n + 1):
        operating_year = year - delay_years
        if operating_year <= 0:
            # Illustrative readiness expense while the project waits. Capital and
            # initial acquisition have already been paid, a conservative stress.
            idle_cost = a["initial_opex"] * 0.05
            records.append(dict(year=year, average_customers=0, opening_customers=opening,
                closing_customers=opening, net_additions=0, cancellations=0,
                gross_additions=0, gross_revenue=0, revenue=0, network_opex=idle_cost,
                acquisition_cost=0, ebitda=-idle_cost, depreciation=0, ebit=-idle_cost,
                opening_nol=nol, nol_used=0, taxable_income=0, cash_tax=0,
                closing_nol=nol+idle_cost, nwc=0, delta_nwc=0,
                maintenance_capex=0, capex=0, residual_cash=0, fcf=-idle_cost))
            nol += idle_cost
            continue
        average = a["year1_customers"] * (1 + g) ** (operating_year - 1)
        closing = 2 * average - opening
        net_additions = closing - opening
        cancellations = average * churn
        gross_additions = net_additions + cancellations
        gross_revenue = average * a["arpu"] * 12
        revenue = gross_revenue * share
        network_opex = a["initial_opex"] * (1 + a["opex_growth"]) ** (operating_year - 1)
        acquisition = gross_additions * cac
        ebitda = revenue - network_opex - acquisition
        maintenance = a["initial_capex"] * maint_rate * (1 + a["opex_growth"]) ** (operating_year - 1)
        depreciation = a["initial_capex"] / a["depreciation_life"] + prior_maintenance / a["depreciation_life"]
        ebit = ebitda - depreciation
        nol_used = min(nol, max(0.0, ebit))
        taxable = max(0.0, ebit - nol_used)
        tax = taxable * tax_rate
        closing_nol = max(0.0, nol - ebit)
        nwc = revenue * nwc_rate
        delta_nwc = nwc - previous_nwc
        residual = a["terminal_cash"] if expanded and year == n else 0.0
        fcf = ebitda - tax - delta_nwc - maintenance + residual
        records.append(dict(year=year, average_customers=average, opening_customers=opening,
            closing_customers=closing, net_additions=net_additions,
            cancellations=cancellations, gross_additions=gross_additions,
            gross_revenue=gross_revenue, revenue=revenue, network_opex=network_opex,
            acquisition_cost=acquisition, ebitda=ebitda, depreciation=depreciation,
            ebit=ebit, opening_nol=nol, nol_used=nol_used, taxable_income=taxable,
            cash_tax=tax, closing_nol=closing_nol, nwc=nwc, delta_nwc=delta_nwc,
            maintenance_capex=maintenance, capex=maintenance,
            residual_cash=residual, fcf=fcf))
        opening, previous_nwc, nol = closing, nwc, closing_nol
        prior_maintenance += maintenance
    frame = pd.DataFrame(records)
    frame["discount_factor"] = (1 + a["discount_rate"]) ** (-frame.year)
    frame["discounted_fcf"] = frame.fcf * frame.discount_factor
    frame["cumulative_fcf"] = frame.fcf.cumsum()
    frame["cumulative_discounted_fcf"] = frame.discounted_fcf.cumsum()
    flows = frame.fcf.to_numpy()
    irr = float(nf.irr(flows)) if np.min(flows) < 0 < np.max(flows) else float("nan")
    initial_outflow = -flows[0]
    metrics = dict(npv=float(frame.discounted_fcf.sum()),
        irr=irr if math.isfinite(irr) else None,
        roi=float(flows.sum()/initial_outflow) if initial_outflow else None,
        payback=payback(flows), discounted_payback=payback(flows,a["discount_rate"]),
        tco=float(frame.capex.sum()+frame.network_opex.sum()+frame.acquisition_cost.sum()),
        initial_outflow=float(initial_outflow), cumulative_revenue=float(frame.revenue.sum()),
        cumulative_gross_revenue=float(frame.gross_revenue.sum()),
        cumulative_net_cash=float(flows.sum()), year5_customers=float(frame.iloc[-1].average_customers),
        year5_closing_customers=float(frame.iloc[-1].closing_customers),
        year5_revenue=float(frame.iloc[-1].revenue),
        year5_capacity_utilization=float(frame.iloc[-1].closing_customers/a["subscriber_capacity"]))
    return {"metrics": metrics, "forecast": frame}


def find_threshold(a: dict[str,float], key: str, low: float, high: float) -> float | None:
    """Bisection on NPV with an explicit bracket, no implied existence of a root."""
    def value(x):
        return evaluate(dict(a,**{key:x}))["metrics"]["npv"]
    left, right = value(low), value(high)
    if left * right > 0:
        return None
    for _ in range(90):
        mid = (low + high) / 2
        fm = value(mid)
        if abs(fm) < 0.001:
            return mid
        if left * fm <= 0:
            high = mid
        else:
            low, left = mid, fm
    return (low + high) / 2
