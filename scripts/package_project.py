"""Verify final deliverable structure, record checksums, and create the review ZIP."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile,ZIP_DEFLATED
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
FILES=['models/5G_Investment_Financial_Model.xlsx','analysis/investment_analysis.ipynb',
       'documentation/strategy_report.pdf','presentation/executive_recommendation.pdf',
       'presentation/executive_recommendation.pptx']
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with ZipFile(ROOT/FILES[0]) as book:
    w=ET.fromstring(book.read('xl/workbook.xml'))
    sheets=[s.attrib['name'] for s in w.find('m:sheets',NS)]
    assert sheets==['Dashboard','Assumptions','Customer & Revenue','Operating Costs','CAPEX','Cash Flow','Investment Evaluation','Scenarios','Sensitivity']
    charts=[x for x in book.namelist() if '/charts/chart' in x and x.endswith('.xml')]
    assert len(charts)==2
    data_tables=[f.attrib for f in ET.fromstring(book.read('xl/worksheets/sheet9.xml')).findall('.//m:f',NS) if f.attrib.get('t')=='dataTable']
    assert len(data_tables)==1 and data_tables[0]['dt2D']=='1'
    for file in book.namelist():
        if file.startswith('xl/worksheets/sheet') and file.endswith('.xml'):
            assert not ET.fromstring(book.read(file)).findall('.//m:c[@t="e"]',NS),file
nb=json.loads((ROOT/FILES[1]).read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert len(code)==7 and all(c.get('execution_count') for c in code)
assert not [o for c in code for o in c.get('outputs',[]) if o['output_type']=='error']
assert len(PdfReader(ROOT/FILES[2]).pages)==9
assert len(PdfReader(ROOT/FILES[3]).pages)==7
with ZipFile(ROOT/FILES[4]) as deck:
    names=deck.namelist()
    slides=[x for x in names if x.startswith('ppt/slides/slide') and x.endswith('.xml') and '/_rels/' not in x]
    chart_parts=[x for x in names if '/charts/chart' in x and x.endswith('.xml')]
    assert len(slides)==7 and len(chart_parts)==3
    assert sum(x.startswith('ppt/embeddings/') and x.endswith('.xlsx') for x in names)==3
summary=json.loads((ROOT/'outputs/validation_summary.json').read_text())
assert summary['status']=='passed' and summary['principal_checks']==279 and summary['sensitivity_checks']==49
manifest=dict(as_of='2026-11-21',financial_validation=summary,workbook_sheets=sheets,
    native_workbook_charts=len(charts),native_two_input_data_tables=len(data_tables),
    executed_notebook_code_cells=len(code),report_pages=9,presentation_slides=7,
    native_presentation_charts=3,financial_tests=8,
    visual_review='All nine workbook sheets, nine report pages and seven final PDF slides inspected',
    native_application_limit='No Microsoft Excel or PowerPoint desktop claim; presentation PDF exported through LibreOffice',
    files=[dict(path=f,bytes=(ROOT/f).stat().st_size,sha256=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()) for f in FILES])
(ROOT/'outputs/deliverable_checks.json').write_text(json.dumps(manifest,indent=2))
target=ROOT.parent/'outputs/5G-Network-Investment-Analysis.zip';target.parent.mkdir(exist_ok=True)
excluded={'.git','.build','node_modules','__pycache__','.venv','.ipynb_checkpoints'}
with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
    for file in sorted(ROOT.rglob('*')):
        relative=file.relative_to(ROOT)
        if file.is_file() and not file.is_symlink() and not any(x in excluded or x.startswith('.chart-data-') or x=='.codex-finalizer' for x in relative.parts) and not file.name.endswith('.inspect.ndjson') and file.name!='.DS_Store':
            archive.write(file,Path(ROOT.name)/relative)
with ZipFile(target) as archive:
    assert archive.testzip() is None
    print(json.dumps({'zip':str(target),'files':len(archive.namelist()),'bytes':target.stat().st_size,'financial_validation':summary},indent=2))
