# Assumptions and limitations

All monetary forecasts are illustrative nominal CAD, researched and prepared as of 21 November 2026.

## What is known versus assumed

The source register contains real national coverage figures, a real BCE blended ARPU benchmark and published ISED process context. It contains no actual local subscriber survey, municipal site study, traffic model or vendor bid. The fictional serviceable market of 120,000 lines is not an estimate of a real population. A line is not necessarily a unique person or household.

The initial brief supplies 25,000 average subscribers at $65 monthly ARPU, 15% net growth, $50M network CAPEX, $8M Year 1 network OPEX, 3% OPEX growth and a 10% discount rate. Added economic assumptions are specified in `data/assumptions.csv`; they are not independently validated telecom forecasts.

## Material unresolved issues

1. **Opening adoption.** The expanded model requires approximately 23,256 opening subscribers before Year 1. Acquiring them at the assumed cost does not prove they exist. A realistic commercial ramp could reduce first-year revenue materially.
2. **Incrementality.** The 85% share is assumed. Existing customers who transfer networks do not create a full new subscription stream for the company. Retention benefits could add value, but none is monetized without evidence.
3. **Pricing.** The $65 case assumption exceeds BCE's 2025 blended $57.36 ARPU by approximately 13.3%. Product and customer mixes differ. A national blended metric does not establish a local achievable price.
4. **Cost scaling.** Network OPEX grows at 3% while average customers grow at 15%. Supplier costs, tower leases, roaming, customer support and network load need a more granular budget. Acquisition is modeled separately to avoid omitting replacement spending.
5. **Capacity.** The 60,000 closing-line ceiling is only a planning proxy, not an RF capacity study. The bull and mathematical demand break-even cases exceed it. Their finances omit any extra capacity CAPEX or OPEX.
6. **Tax.** A generic 27% rate and book depreciation proxy replace statutory tax-pool accounting. Initial acquisition costs are assumed immediately deductible with losses carried forward. No immediate tax refunds are assumed.
7. **Asset life and terminal value.** Five years is shorter than the assumed 10-year initial asset life. The zero-residual screen understates potential later benefits. Book value does not prove recoverable cash. A full-lifecycle engineering and cash-flow appraisal is required before a definitive long-term rejection.
8. **Working capital.** A 2% revenue ratio is a proxy. No release occurs at the Year 5 cutoff. Billing terms and bad debts are not separately modeled.
9. **Scope and spectrum.** $50M is treated as the entire initial network build. Existing spectrum rights, access and necessary capacity are assumed within scope. No unquoted spectrum acquisition, geographic spillover revenue, enterprise-contract upside or subsidy is credited.
10. **Execution.** The main case assumes assets are ready at Year 1 start. The separate one-year delay stress is illustrative and uses a fixed five-year cash window. No detailed site critical path is available.
11. **Uncertainty.** Sensitivity results depend on the chosen ranges. Simulation assumes independent, uncalibrated priors and excludes unmodeled capacity costs. Its output is a conditional simulation result.

## How these limits affect the decision

The recommended action is **defer / modify**, rather than claim the technology or a longer-lived network can never create value. The current case fails the stated five-year hurdle, and key commercial and engineering inputs remain unproven. A lower-cost shared design or independently supported long-term value could justify a new proposal. Neither is assumed to exist.

## File behavior

Excel's active model updates with editable inputs. Side-by-side scenario captures and published PDF/PPTX narratives are dated snapshots. Excel flags captured scenarios after assumptions change. Python reads the baseline CSV, not unsaved workbook edits, unless you explicitly export those inputs. Keep the evidence, model version and narrative aligned after any change.
