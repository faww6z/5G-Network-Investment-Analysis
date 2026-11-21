# Methodology and formula guide

## Decision and evaluation basis

Evaluate a CAD $50M initial network expansion over five annual operating periods. The default uses nominal, incremental, unlevered cash flows and a nominal 10% discount rate. No borrowing, interest, enterprise-value multiple or company equity value enters the calculation. This is a five-year capital allocation screen, not a complete estimate of the network's lifetime economic value.

The simple and expanded modes share one Excel forecast. Simple mode sets incremental revenue to 100% and acquisition cost, cash taxes, maintenance CAPEX, working capital and residual cash to zero. Expanded mode activates the documented inputs. Depreciation is displayed in both modes but only affects cash through taxes.

## Subscribers and acquisition

Let `g` be net annual growth, `A[t]` average active subscribers, `O[t]` opening subscribers, `C[t]` closing subscribers and `c` the annual cancellation intensity.

```text
A[1] = 25,000
A[t] = A[t-1] * (1 + g)
O[1] = A[1] / (1 + g/2)
O[t] = C[t-1]
C[t] = 2*A[t] - O[t]
Net additions[t] = C[t] - O[t]
Cancellations[t] = A[t] * c
Gross additions[t] = Net additions[t] + Cancellations[t]
```

Linear growth within each year makes the average equal to `(opening + closing)/2` and the closing-to-opening growth equal to `g`. It also preserves annual average growth at `g`. At 15% growth, the first year's 25,000 average subscribers require **23,255.81 opening subscribers** at the start of operations. The case assumes this base has been acquired at Year 0. Its existence is unverified and forms a central demand risk.

Acquisition spending at Year 0 is `O[1] * CAC`. Later acquisition expense is `gross additions * CAC`. Churn drives replacement acquisition spending; it is **not subtracted a second time** from net subscriber growth. The 12% annual cancellation intensity is a yearly event count divided by average subscribers. It is neither a monthly churn rate nor a literal probability that one customer leaves once.

All modeled subscribers bear acquisition cost even where part of their revenue would transfer from an existing network. This is conservative and needs a proper migration-versus-new-customer cost study. No handset financing or revenue is modeled.

## Revenue and operating spending

```text
Gross subscription revenue = Average subscribers * monthly ARPU * 12
Incremental revenue = Gross subscription revenue * incremental share
Network OPEX[t] = Year 1 network OPEX * (1 + OPEX growth)^(t-1)
Acquisition expense[t] = Gross additions[t] * CAC
EBITDA = Incremental revenue - network OPEX - acquisition expense
```

The 85% incremental share excludes transferred existing revenue. Avoid treating the excluded 15% as a measured Bell migration rate. Network OPEX includes expensed repairs, support, personnel, energy, licensing and operations, and excludes the separately modeled acquisition spending. The 3% growth rate is nominal; there is no second inflation adjustment.

The resulting Year 5 EBITDA margin is high because network OPEX grows more slowly than subscribers. That operating leverage is an assumption to investigate, not evidence of attainable efficiency.

## CAPEX, depreciation and taxes

Initial network CAPEX occurs at Year 0. Year 1 maintenance CAPEX is 2% of the initial network investment; it then grows at the OPEX growth rate. This is capitalized replacement equipment, distinct from expensed maintenance.

Initial equipment enters service at the start of Year 1 and depreciates straight-line over 10 years. Year-end maintenance additions begin depreciation in the following year. With a five-year horizon and asset life of at least five years:

```text
D&A[t] = Initial CAPEX / useful life + prior maintenance CAPEX / useful life
EBIT[t] = EBITDA[t] - D&A[t]
Losses used = MIN(opening tax losses, MAX(0, EBIT))
Taxable income = MAX(0, EBIT - losses used)
Cash taxes = Taxable income * illustrative tax rate
Closing tax losses = MAX(0, opening tax losses - EBIT)
```

Year 0 acquisition expense creates a tax loss, carried forward without an immediate refund. There is no interest tax shield. Book depreciation is a simplified proxy for tax deductions; real Canadian capital-cost-allowance classes, loss expiry, tax-group utilization and provincial differences require specialist work. The 27% rate is illustrative.

## Working capital, residual value and cash flows

```text
Closing NWC[t] = Incremental revenue[t] * working capital rate
Change in NWC[t] = NWC[t] - NWC[t-1]
UFCF[t] = EBITDA[t] - cash taxes[t] - change in NWC[t] - CAPEX[t]
          + net residual cash proceeds[t]
UFCF[0] = - initial network CAPEX - prelaunch acquisition spending
```

The network continues after Year 5, so working capital is not automatically released at the cutoff. Residual proceeds default to zero. An override must represent independently supported cash value net of tax and selling costs, not accounting net book value. No disposal tax shield or working capital release is silently added to that override.

## Investment metrics

| Metric | Definition and timing |
|---|---|
| NPV | `FCF[0] + SUM(FCF[t]/(1+r)^t)` for Years 1-5. In Excel: `NPV(rate, Year1:Year5) + Year0`. |
| IRR | Annual rate making NPV of the same Year 0-5 cash flows zero. If cash flows have no sign change, report unavailable. Negative IRR is allowed. |
| Cash ROI | Sum of Year 0-5 FCF divided by the positive initial cash outflow, including prelaunch acquisition. It is cumulative, not annualized and not an accounting-profit ROI. |
| Payback | First crossing of cumulative undiscounted cash flow through zero. Fractional years interpolate within the recovery year. Otherwise report 'Not within 5 years'. |
| Discounted payback | Same crossing after discounting each year's cash flow. |
| TCO | Undiscounted initial and maintenance CAPEX plus network OPEX and acquisition costs. Income taxes, financing, working capital and residual proceeds are excluded. It measures spending, not profitability. |

## Scenarios, sensitivities and simulation

Bear/base/bull change only net subscriber growth to 5%, 15% and 25%. Each starts at the same Year 1 annual average. Consequently the implied opening customer base and initial acquisition spending differ slightly. These are adoption-isolation cases, not coordinated pessimistic/optimistic forecasts of all inputs.

The native Excel sensitivity grid varies ARPU and growth through the same active build. Python also tests CAPEX, network OPEX, discount rate, incrementality, churn and acquisition cost. Tornado bars reflect different explicit ranges, so widths depend on those ranges.

Bisection finds zero-NPV thresholds only where a bracket contains a root. No feasible incremental share between 10% and 100% reaches break-even at the other base assumptions. Demand break-even breaches capacity and is not automatically an investable solution.

The optional Monte Carlo uses 5,000 independent triangular draws with seed 20261121: growth (5%, 15%, 25%), ARPU ($55, $65, $70), initial CAPEX ($45M, $50M, $60M), network OPEX multiplier (0.90, 1.00, 1.15) and incremental share (70%, 85%, 100%). Triples are minimum, mode and maximum. Other inputs stay at base. These priors are not fitted to project observations; correlations, catastrophic events and capacity expansion spending are omitted. The positive-NPV share is conditional on those choices and must not be presented as an empirical likelihood of success.

The delay stress pays initial CAPEX and prelaunch acquisition at Year 0, incurs readiness spending equal to 5% of Year 1 network OPEX during one idle year, then starts operations. The evaluation still stops at calendar Year 5, leaving four operating years. This is a deliberately conservative fixed-window timing test, not a project scheduling estimate.

## Validation

Excel formulas and Python calculate separately. The baseline validates annual subscriber flow, revenue, OPEX, acquisition, depreciation, taxes, losses, working capital, CAPEX, FCF and discounted FCF for all three cases, plus principal investment metrics and all 49 native sensitivity combinations. The workbook also checks the NPV function against its discounted cash-flow schedule. Authoring-engine results are exported in `outputs/excel_validation.json`; Python checks appear in `outputs/excel_python_reconciliation.csv` and `outputs/validation_summary.json`.

These are independent computational checks, not an audit opinion or proof of native Excel desktop behavior. Captured validation is valid only for its associated baseline inputs.
