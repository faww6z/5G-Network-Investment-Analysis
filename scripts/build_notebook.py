"""Create and execute the teaching notebook using the current Python environment."""
import json
import os
from pathlib import Path
import sys
import tempfile
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook()
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
nb.cells=[
md("""# 5G network expansion: from subscribers to an investment decision

**Independent hypothetical case, prepared 21 November 2026.** All forecasts are illustrative nominal CAD. This is not a Bell engagement.

The question is whether a CAD $50M regional network build meets a 10% five-year investment hurdle. We first reproduce the simple teaching model, then add incremental revenue treatment, acquisition, maintenance capital, working capital and cash taxes. Every formula is explained in `documentation/methodology.md`; the readable Python implementation is `finance.py`.

## 1. Load the documented assumptions

The CSV is the reproducible baseline. Unsaved Excel changes are not inputs to this notebook. Real national observations live separately in `data/market_context.csv` and are used only as context, not forecasts."""),
code("""from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image

ROOT = Path.cwd()
if not (ROOT / 'data/assumptions.csv').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'analysis'))
from finance import load_assumptions, evaluate, find_threshold
from run_analysis import validate_excel, monte_carlo

pd.options.display.float_format = '{:,.2f}'.format
assumptions = pd.read_csv(ROOT / 'data/assumptions.csv')
a = load_assumptions()
display(assumptions[['label', 'value', 'unit', 'classification']])"""),
md("""## 2. Forecast subscribers, revenue and cash

Average subscribers generate revenue throughout a year. Linear within-year net growth makes the Year 1 opening base `25,000 / (1 + 15% / 2)`. The company pays acquisition costs for that opening base at Year 0. Later gross additions include net growth plus replacement cancellations. Net growth already includes churn, so we do not subtract it again.

Gross revenue is `average subscribers × monthly ARPU × 12`. The expanded case counts only 85% as incremental. FCF subtracts operating cash costs, taxes, maintenance CAPEX and changes in working capital. Depreciation is not a cash expense."""),
code("""base = evaluate(a)
forecast = base['forecast']
display(forecast[['year', 'opening_customers', 'average_customers',
                  'closing_customers', 'gross_additions', 'revenue',
                  'network_opex', 'acquisition_cost', 'cash_tax',
                  'capex', 'delta_nwc', 'fcf']])
display(Image(filename=str(ROOT / 'outputs/charts/annual_cash_flow.png'), width=850))"""),
md("""## 3. Distinguish the simplified model from the expanded case

NPV discounts the future cash flows, then adds the immediate Year 0 outflow exactly once. Cash ROI uses cumulative net cash divided by initial cash spending. IRR is an annual rate. Neither payback measure is invented if the initial cash remains unrecovered at Year 5.

The simplified model deliberately excludes important economic costs. Comparing its result with the expanded case demonstrates why model scope changes the decision."""),
code("""simple = evaluate(a, expanded=False)
metrics = pd.DataFrame({'Simplified': simple['metrics'], 'Expanded': base['metrics']})
display(metrics.loc[['initial_outflow', 'npv', 'irr', 'roi', 'payback',
                     'discounted_payback', 'tco', 'cumulative_revenue']])
display(Image(filename=str(ROOT / 'outputs/charts/cumulative_cash_flow.png'), width=850))"""),
md("""## 4. Compare adoption scenarios and the capacity constraint

Only net growth changes. The Year 1 average stays at 25,000, so higher growth implies a slightly smaller opening subscriber base. The 60,000-line ceiling is illustrative, not an engineering study. A scenario that exceeds it needs additional scope and costs before its returns can support a real decision."""),
code("""scenarios = {}
for name, key in [('Bear', 'bear_growth'), ('Base', 'base_growth'), ('Bull', 'bull_growth')]:
    scenarios[name] = evaluate(a, a[key])['metrics']
comparison = pd.DataFrame(scenarios).T
display(comparison[['npv', 'irr', 'roi', 'payback',
                    'year5_closing_customers', 'year5_capacity_utilization']])
display(Image(filename=str(ROOT / 'outputs/charts/scenario_comparison.png'), width=850))"""),
md("""## 5. Find break-even conditions instead of guessing a recommendation

Bisection searches for a zero-NPV threshold only if the specified interval contains a root. All other assumptions stay fixed. A mathematical demand threshold can still be operationally infeasible. Price and growth interact, which is why a two-input sensitivity matrix adds information beyond a single optimistic case."""),
code("""thresholds = {
    'Monthly ARPU (CAD)': find_threshold(a, 'arpu', 20, 150),
    'Year 1 average customers': find_threshold(a, 'year1_customers', 1000, 100000),
    'Initial network CAPEX (CAD)': find_threshold(a, 'initial_capex', 1e6, 100e6),
    'Incremental share in [10%,100%]': find_threshold(a, 'incremental_share', .1, 1),
}
display(pd.Series(thresholds, name='Zero-NPV threshold'))
threshold_demand = evaluate(dict(a, year1_customers=thresholds['Year 1 average customers']))
print('Closing subscribers at demand break-even:', round(threshold_demand['metrics']['year5_closing_customers']))
print('Assumed capacity:', int(a['subscriber_capacity']))
display(Image(filename=str(ROOT / 'outputs/charts/npv_sensitivity.png'), width=850))
display(Image(filename=str(ROOT / 'outputs/charts/tornado.png'), width=850))"""),
md("""## 6. Reconcile separate Excel and Python calculations

The workbook builder calculates Excel formulas using Artifact Tool and captures the same model at each scenario. Python independently recalculates subscriber flow, operating schedules and cash returns. This check compares those results; it does not ask Python to evaluate Excel formula text.

The capture belongs to the delivered baseline. If you change the CSV, reconciliation should fail until the workbook and its capture are rebuilt. This is not a fresh Microsoft Excel desktop test."""),
code("""validation = validate_excel(a)
display(pd.Series(validation))
reconciliation = pd.read_csv(ROOT / 'outputs/excel_python_reconciliation.csv')
display(reconciliation.head(12))
assert validation['status'] == 'passed'"""),
md("""## 7. Optional uncertainty simulation

The simulation uses 5,000 independent triangular priors documented in the methodology. The positive-NPV share is conditional on those assumptions. It is not an empirically estimated probability that a telecom project will succeed. Forecasts above capacity omit the cost of extra capacity, so the simulation should not justify investment approval."""),
code("""draws = monte_carlo(a, size=5000, seed=20261121)
display(draws['npv'].describe(percentiles=[.05, .5, .95]))
print(f\"Conditional positive-NPV share: {(draws['npv'] > 0).mean():.1%}\")
display(Image(filename=str(ROOT / 'outputs/charts/monte_carlo_npv.png'), width=850))"""),
md("""## 8. Investment recommendation

**Defer the full CAD $50M build and investigate a shared or smaller design.** The default expanded base case fails the five-year hurdle, and even high adoption requires added capacity without reaching positive NPV. Cost reduction is not assured; supplier quotes and engineering scope must support it.

The five-year cutoff omits later operating value from a network assumed to last longer. A supported lifecycle appraisal could change the decision. Neither book value nor an invented subsidy should be used as a cash plug.

Before an investment committee approval, validate local price-tested demand, achievable opening adoption, customer migration economics, quoted CAPEX/OPEX, spectrum and site access, and engineered capacity. The roadmap and KPI framework turn those conditions into proposed decision gates.

Sources: [CRTC 2026 CTMR](https://crtc.gc.ca/eng/publications/reports/PolicyMonitoring/2026/ctmr.htm), [BCE 2025 Annual Financial Report](https://www.bce.ca/cs-assets/2025-bce-annual-financial-report.pdf-blt5d552f866d8a58a3), and `data/sources.md`."""),
]
nb.metadata.kernelspec={"display_name":"Python 3","language":"python","name":"python3"}
nb.metadata.language_info={"name":"python","version":sys.version.split()[0]}
temporary=Path(tempfile.mkdtemp(prefix='5g-notebook-'))
kernel=temporary/'jupyter/kernels/python3';kernel.mkdir(parents=True)
(kernel/'kernel.json').write_text(json.dumps({"argv":[sys.executable,"-m","ipykernel_launcher","-f","{connection_file}"],"display_name":"Python 3","language":"python"}))
os.environ['JUPYTER_PATH']=str(temporary/'jupyter')
os.environ['JUPYTER_CONFIG_DIR']=str(temporary/'config')
os.environ['JUPYTER_RUNTIME_DIR']=str(temporary/'runtime')
os.environ['IPYTHONDIR']=str(temporary/'ipython')
client=NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT/'analysis')}})
client.execute()
target=ROOT/'analysis/investment_analysis.ipynb';nbf.write(nb,target)
assert not [output for cell in nb.cells if cell.cell_type=='code' for output in cell.outputs if output.output_type=='error']
print(f'Executed notebook saved: {target}; {sum(c.cell_type=="code" for c in nb.cells)} code cells, no errors.')
