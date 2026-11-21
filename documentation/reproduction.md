# Reproduction and refresh

## Public calculation workflow

From the repository root, create a Python environment and install `requirements.txt`. Run `python analysis/run_analysis.py` to regenerate all annual forecasts, scenario summaries, break-even thresholds, sensitivity tables, simulations and PNG/SVG charts. The numerical baseline is `data/assumptions.csv`.

Run `python -m unittest discover -s tests -v` for the financial tests. Open the executed notebook in a Jupyter-capable editor. A notebook-specific run uses the same readable Python financial engine and shows outputs inline.

`python analysis/run_analysis.py --validate-excel` additionally compares Python to independently calculated workbook results captured in `outputs/excel_validation.json`. It does not evaluate workbook formula text, launch Excel or validate an edited workbook against an old capture. Changing economic inputs should fail reconciliation until the Excel model and capture are regenerated.

## Workbook interaction

Open the XLSX in Excel, leave Sensitivity B3:B4 blank, select Assumptions B14=2 and B15=2, and use automatic calculation including Data Tables. Model mode 1 displays the simplified teaching case. Scenario 1/2/3 selects bear/base/bull. Editable changes feed one forecast. The comparison captures deliberately mark themselves stale rather than claiming static values are live.

`python analysis/read_workbook_inputs.py` reads saved numeric input values from the XLSX using Python's standard ZIP/XML libraries and writes `outputs/workbook_inputs.csv`. Compare that file with `data/assumptions.csv` before intentionally promoting what-if inputs to a new baseline. It cannot read unsaved Excel changes. It does not author or recalculate the workbook.

## Optional full artifact regeneration in Codex

The included authoring scripts use `@oai/artifact-tool`, supplied by Codex's workspace runtime rather than the public Python requirements. In an environment with that library linked through `node_modules`, run:

```bash
python analysis/run_analysis.py
node scripts/build_workbook.mjs
python analysis/run_analysis.py --validate-excel
python scripts/build_notebook.py
node scripts/build_presentation.mjs
python scripts/build_report.py
```

The presentation builder also uses Codex's presentation finalizer when its skill path is available. PDF export requires LibreOffice or an equivalent presentation renderer. Report/notebook authoring needs the additional packages listed in `requirements-authoring.txt`. These authoring tools are separate from the public financial reproduction workflow.

The narrative in the README, strategy report, slides and interview guide reflects the delivered baseline dated 21 November 2026. Review its conclusions after any input change. Do not automatically publish updated numerical files alongside an old recommendation.

## Checks performed for the delivered baseline

- 279 annual/metric reconciliations and 49 sensitivity combinations, comparing separate Excel-formula and Python calculations.
- Eight financial tests covering time-zero treatment, subscriber conservation, churn costs, losses, depreciation, undefined returns, thresholds and residual-value discounting.
- Live scenario and simple/expanded selector changes, stale-capture warnings, formula error scan, exported workbook structure and native What-If formula metadata.
- Visual inspection of all workbook sheets, every presentation slide and every report page.
- Executed notebook with no error cells.

No claim is made of opening the workbook in Microsoft Excel desktop. LibreOffice conversion of the presentation is a separate export check and does not establish Excel compatibility.
