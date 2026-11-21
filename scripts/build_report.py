"""Render the strategy report with deliberate page layouts and source links."""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,HRFlowable
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/'outputs/results.json').read_text());B=R['base'];T=R['thresholds']
INK=colors.HexColor('#151515');LIME=colors.HexColor('#D8FB50');PAPER=colors.HexColor('#FAFAF6');GREY=colors.HexColor('#596052')
SOURCES={
 'S1':('CRTC 2026 Canadian Telecommunications Market Report','https://crtc.gc.ca/eng/publications/reports/PolicyMonitoring/2026/ctmr.htm'),
 'S2':('BCE 2025 Annual Financial Report','https://www.bce.ca/cs-assets/2025-bce-annual-financial-report.pdf-blt5d552f866d8a58a3'),
 'S3':('ISED CPC-2-0-03','https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/learn-more/key-documents/procedures/client-procedures-circulars-cpc/cpc-2-0-03-radiocommunication-and-broadcasting-antenna-systems'),
 'S4':('ISED DGSO-001-26, May 2026','https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/learn-more/key-documents/consultations/consultation-amendments-tower-siting-process-and-decision-roaming-tower-sharing-and-annual-reporting'),
 'D1':('SlidesCarnival Financial Management consulting template','https://www.slidescarnival.com/template/financial-management-for-small-businesses-consulting/155244'),
}
W,H=A4;WIDTH=W-84
styles={
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.5,leading=14,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.1,leading=11.2,textColor=GREY,spaceAfter=7),
 'h1':ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=24,leading=28,textColor=INK,spaceAfter=17),
 'h2':ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=12.5,leading=17,textColor=INK,spaceBefore=10,spaceAfter=7),
 'table':ParagraphStyle('table',fontName='Helvetica',fontSize=8.4,leading=11.4,textColor=INK),
 'th':ParagraphStyle('th',fontName='Helvetica-Bold',fontSize=8.4,leading=11.4,textColor=colors.white),
 'cover':ParagraphStyle('cover',fontName='Helvetica-Bold',fontSize=34,leading=39,textColor=INK,spaceAfter=22),
 'hero':ParagraphStyle('hero',fontName='Helvetica-Bold',fontSize=59,leading=66,textColor=INK,spaceAfter=6),
}
def p(text,style='body'):return Paragraph(text,styles[style])
def h(title):return p(title,'h1')
def link(source):
    title,url=SOURCES[source];return f'<link href="{url}" color="#596052">{source}: {title}</link>'
def money(x,dec=2):return f'({abs(x)/1e6:,.{dec}f})' if x<0 else f'{x/1e6:,.{dec}f}'
def table(rows,widths=None,small=False):
    data=[[p(escape(str(x)), 'th' if i==0 else 'table') for x in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths or [WIDTH/len(rows[0])]*len(rows[0]),hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LINEBELOW',(0,0),(-1,0),.6,INK),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#D2D4CB'))]))
    return t
def image(name,width=WIDTH):
    from PIL import Image as PILImage
    file=ROOT/f'outputs/charts/{name}.png'
    with PILImage.open(file) as im:ratio=im.height/im.width
    return Image(str(file),width=width,height=width*ratio,hAlign='LEFT')
def footer(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(LIME if doc.page==1 else PAPER);canvas.rect(0,0,W,H,fill=1,stroke=0)
    canvas.setFillColor(INK);canvas.setFont('Helvetica-Bold',8)
    canvas.drawString(42,H-34,'5G NETWORK EXPANSION  /  INVESTMENT REVIEW')
    canvas.setFont('Helvetica',8);canvas.drawRightString(W-42,H-34,'21 NOVEMBER 2026')
    canvas.setStrokeColor(INK);canvas.setLineWidth(.5);canvas.line(42,38,W-42,38)
    canvas.setFont('Helvetica',7);canvas.drawString(42,25,'Independent hypothetical case. No affiliation with Bell Canada.')
    canvas.drawRightString(W-42,25,f'{doc.page:02d}')
    canvas.restoreState()

story=[]
story += [Spacer(1,20),p('A $50M build needs<br/>a different<br/>investment case','cover'),
 p('DEFER THE FULL BUILD','h2'),p(f'CAD ({abs(B["npv"])/1e6:.2f}M)','hero'),
 p('Five-year NPV at a 10% required return. Expanded base case.','body'),
 HRFlowable(width='100%',thickness=1,color=INK),Spacer(1,18),
 p('The initial forecast grows revenue, but it does not recover the required investment within five years. Customer acquisition, transferred revenue, taxes and ongoing capital needs reverse the simplified model\'s positive result.'),
 table([['Investment committee decision','Evidence'],['Defer / modify the current $50M scope','Base NPV negative; IRR -3.20%; no five-year payback'],['Investigate sharing or a smaller cluster','CAPEX break-even is about $31.02M before a safety margin'],['Validate opening demand and capacity','23,256 opening subscribers assumed; bull capacity exceeds design']],[WIDTH*.43,WIDTH*.57]),
 Spacer(1,12),p('This is a fictional regional case for a Canadian telecom provider. All operating forecasts are illustrative. The analysis distinguishes the five-year screen from the network\'s unresolved lifetime value.','small'),
 p(f'Design adapted from {link("D1")}. CC BY 4.0. Original content and financial evidence replace the template assets.','small'),PageBreak()]

story += [h('Coverage gaps create a question,<br/>not proof of demand'),
 p('National evidence supports investigating underserved regions. It does not establish that a particular cluster can attract the assumed subscribers at the assumed price.'),
 image('market_coverage'),p(f'{link("S1")}. 2024 observations; report page modified 24 February 2026. Coverage categories overlap.','small'),
 table([['Fictional regional commercial case','Required validation'],['120,000 serviceable subscriber lines','Map actual eligible lines, coverage gaps and competitor offers'],['25,000 Year 1 average active subscribers','About 20.8% line penetration and 23,256 opening subscribers'],['CAD $65 gross monthly ARPU','Price-test local demand; BCE 2025 blended ARPU was $57.36'],['Consumer, SME and anchor-account demand','Separate new accounts, migrated accounts and enterprise contracts']],[WIDTH*.43,WIDTH*.57]),
 p('Coverage reliability, home connectivity substitution and SME service needs are hypotheses to investigate. Enterprise and digital-service upside is not included without contracted evidence. Bell, Rogers and TELUS are relevant national competitors; regional and wholesale alternatives depend on the selected footprint.'),
 p(f'{link("S2")}, printed p.52. Different customer and product mixes limit direct comparability. The $65 case assumption is approximately 13.3% higher.','small'),PageBreak()]

f=R['forecasts']['Base']
forecast_rows=[['CAD millions','Year 0','Year 1','Year 2','Year 3','Year 4','Year 5']]
for label,key in [('Incremental revenue','revenue'),('Network OPEX','network_opex'),('Acquisition spending','acquisition_cost'),('Cash taxes','cash_tax'),('Change in NWC','delta_nwc'),('CAPEX','capex'),('Free cash flow','fcf')]:forecast_rows.append([label]+[money(row[key]) for row in f])
story += [h('Revenue is not the cash<br/>available to recover CAPEX'),
 p('The same subscriber forecast produces CAD $131.48M of gross revenue and CAD $111.75M of incremental revenue over five years. The difference represents the assumed transfer of existing company revenue.'),
 table(forecast_rows,[132]+[(WIDTH-132)/6]*6),Spacer(1,12),
 p('The annual customer average reconciles to opening and closing balances. At 15% growth, 25,000 average customers imply 23,256 at opening and 26,744 at the end of Year 1. Acquisition at $150 per gross addition therefore starts before operations.'),
 p('Customer and revenue formulas','h2'),
 p('Opening subscribers = annual average / (1 + net growth / 2).<br/>Gross additions = closing - opening + cancellations.<br/>Incremental revenue = average subscribers x monthly ARPU x 12 x 85%.'),
 p('Cash-flow formula','h2'),p('Unlevered FCF = EBITDA - cash taxes - change in working capital - CAPEX + supported residual cash proceeds. Depreciation reduces taxable income but is not itself a cash outflow.'),
 p('Year 0 includes $50.00M network CAPEX and $3.49M initial acquisition. No working capital release or unsupported terminal cash is credited at Year 5. Columns may not sum exactly after display rounding.','small'),PageBreak()]

story += [h('Economic costs reverse<br/>the simplified verdict'),
 table([['Five-year metric','Simplified','Expanded'],['Initial cash outflow','$50.00M','$53.49M'],['NPV at 10%','$15.05M','$(18.50)M'],['IRR','19.70%','-3.20%'],['Cash ROI','78.01%','-10.51%'],['Payback','3.34 years','Not within 5 years'],['Discounted payback','4.03 years','Not within 5 years'],['Undiscounted TCO','$92.47M','$107.83M']],[WIDTH*.46,WIDTH*.27,WIDTH*.27]),
 Spacer(1,12),p('The simplified case assumes all subscription revenue is new to the company, excludes acquisition and replacement spending, and omits cash taxes, maintenance capital and working capital. It is a teaching baseline, not the investment recommendation.'),
 p('A five-year cutoff is not an asset-life conclusion','h2'),
 p('The model assumes a 10-year initial asset life. A zero Year 5 residual omits possible later value. Approximately <b>CAD $29.80M of net Year 5 cash value</b> would close the base NPV gap, holding other assumptions constant. A modeled $25M net residual still leaves NPV negative.'),
 p('Accounting book value is about $29.28M at Year 5, but that is not evidence of sale proceeds or discounted continuation cash. A full-lifecycle forecast must include capacity reinvestment, tax treatment and justified demand.'),
 p('Metric conventions','h2'),p('Cash ROI is cumulative net project cash divided by the initial cash outflow, including prelaunch acquisition. TCO is undiscounted network CAPEX, maintenance CAPEX, network OPEX and acquisition spending; it excludes taxes, financing, working capital and residual proceeds.'),PageBreak()]

scenario_rows=[['Scenario','Net growth','NPV','Year 5 closing lines']]
for name in ['Bear','Base','Bull']:
    m=R['scenarios'][name];scenario_rows.append([name,f'{R["assumptions"][name.lower()+"_growth"]:.0%}',f'CAD ({abs(m["npv"])/1e6:.2f}M)',f'{m["year5_closing_customers"]:,.0f}'])
story += [h('High adoption still needs<br/>a stronger investment case'),table(scenario_rows,[WIDTH*.18,WIDTH*.20,WIDTH*.29,WIDTH*.33]),
 image('npv_sensitivity'),
 p('The bull case needs 67,817 closing subscribers, exceeding the 60,000-line planning capacity. Green sensitivity cells can also require added capacity; the grid does not include its additional costs.'),
 table([['Zero-NPV threshold','Result','Interpretation'],['Initial network CAPEX','$31.02M','38% below the original network budget'],['Monthly ARPU','$85.11','31% above the $65 starting price'],['Year 1 average customers','33,624','Implies 62,911 Year 5 closing lines, over capacity']],[WIDTH*.36,WIDTH*.18,WIDTH*.46]),
 p('Each threshold holds other base inputs constant. No incremental revenue share at or below 100% alone produces positive NPV. Mathematical break-even is not a management safety margin.','small'),PageBreak()]

alt=R['alternatives']
story += [h('A revised scope must survive<br/>commercial and delivery risk'),
 table([['Risk','Evidence or assumption','Response'],['Demand and opening base','23,256 opening subscribers assumed before Year 1','Price-test demand and conversion before committing the full build'],['Price and migration','$65 ARPU and 85% incrementality unverified','Separate migrated accounts; test offers against current competitors'],['Capacity','Bull case reaches 113% of assumed capacity','Engineer coverage, traffic, backhaul and expansion costs'],['Delivery and costs','CAPEX and OPEX lack supplier bids','Quote site reuse/sharing; include contingency and stop gates'],['Five-year cutoff','No supported residual or lifecycle forecast','Appraise later cash flows with reinvestment and tax treatment']],[WIDTH*.23,WIDTH*.36,WIDTH*.41]),
 p('Alternatives are tests, not approved projects','h2'),
 table([['Modeled alternative','Five-year NPV'],
 ['Same benefits with network CAPEX reduced to $27.5M',f'CAD {money(alt["Network CAPEX reduced to CAD 27.5M"]["npv"])}M'],
 ['10% network CAPEX overrun',f'CAD {money(alt["Same design with 10% CAPEX overrun"]["npv"])}M'],
 ['One-year launch delay in the fixed five-year window',f'CAD {money(alt["One-year launch delay within fixed window"]["npv"])}M'],
 ['All gross subscription revenue assumed incremental',f'CAD {money(alt["All subscription revenue incremental"]["npv"])}M']],[WIDTH*.73,WIDTH*.27]),
 p('The cheaper build assumes unchanged benefits, network OPEX and capacity. Actual sharing or a smaller footprint could change all three. Do not claim that reducing cost alone is operationally achievable.'),
 p('The delay stress retains Year 0 spending, adds $0.40M readiness cost in the idle year and leaves only four operating years before the fixed cutoff.','small'),PageBreak()]

story += [h('Approval can follow<br/>measured evidence in stages'),
 table([['Stage','Indicative window','Accountable function and gate'],['Feasibility','Months 0-3','Strategy / Commercial: verify local lines, pricing and an achievable opening base'],['Sharing and design','Months 3-5','Engineering / Finance: quoted scope with positive revised NPV and valid capacity'],['Procurement','Months 5-7','Procurement / Regulatory: executable quotes and applicable preconstruction clearances'],['Pilot deployment','Months 7-10','Engineering / PMO: pass coverage, quality, spend and conversion tests'],['Launch and value tracking','Months 10-18 onward','Operations / Finance: expand only against measured demand and updated returns']],[WIDTH*.26,WIDTH*.22,WIDTH*.52]),
 p('These windows start from a future diligence mandate. They are planning assumptions, not a construction commitment or a claim that approvals are complete.'),
 p('Conditions for a new investment committee proposal','h2'),
 p('A revised proposal needs positive base NPV after all economic costs, credible downside, a capacity plan supported by engineering, price-tested demand, executable scope and cost evidence, and a defensible lifecycle valuation. A break-even CAPEX ceiling is not an acceptable approved price without a safety margin.'),
 p('Proposed management triggers','h2'),
 p('Reforecast when subscriber averages or realized ARPU fall below 90% of the approved plan for two reporting periods, network OPEX exceeds plan by more than 10%, or committed spending plus estimate-to-complete exceeds the approved CAPEX envelope. Hold the next discretionary tranche until Finance and Engineering explain the effect on NPV.'),
 p(f'Infrastructure reuse, siting and consultation diligence follow the applicable published framework. {link("S3")}; {link("S4")}. Proposed 2026 amendments are not treated as enacted requirements.','small'),PageBreak()]

with (ROOT/'documentation/kpi_framework.csv').open() as stream:kpis=list(csv.DictReader(stream))
kpirows=[['KPI','Definition','Source / reporting','Owner']]
for k in kpis:kpirows.append([k['kpi'],k['formula'],k['data_source']+'; '+k['frequency'],k['accountable_function']])
story += [h('Value tracking connects<br/>operations to cash returns'),
 p('Targets and triggers are case assumptions or proposed controls. The companion CSV gives the full specification and illustrative threshold for each KPI.'),
 table(kpirows,[WIDTH*.20,WIDTH*.37,WIDTH*.25,WIDTH*.18]),
 Spacer(1,8),p('Subscriber capacity utilization is a commercial planning ratio. Real engineering measures must include traffic loading, spectrum, coverage and service quality. Cancellation intensity uses a trailing annual event count, distinct from a monthly churn measure.','small'),PageBreak()]

story += [h('Assumptions and evidence<br/>bound the recommendation'),
 p('The financial inputs are illustrative. Local demand, vendor costs, spectrum rights and RF capacity have not been established. The 27% tax proxy uses book depreciation rather than statutory tax pools. Network OPEX scales independently of subscriber growth and produces substantial assumed operating leverage.'),
 p('Simulation is conditional, not a success forecast','h2'),
 p(f'The optional 5,000-draw simulation uses independent triangular priors for growth, ARPU, CAPEX, OPEX and incrementality. Its positive-NPV share is {R["simulation"]["positive_npv_share"]:.1%}, conditional on those choices. The median NPV is CAD ({abs(R["simulation"]["median"])/1e6:.2f}M). No empirical project probabilities or correlations were estimated; capacity expansion costs remain omitted.'),
 p('Source register','h2'),
 p(f'{link("S1")}. Report edition 2026, page modified 24 February 2026. Coverage observations are from 2024; Figure 51, printed p.42. Coverage is not adoption.','small'),
 p(f'{link("S2")}. Published 5 March 2026; FY2025. Printed p.52 reports blended monthly mobile-phone ARPU of $57.36. Product mix differs from the hypothetical case.','small'),
 p(f'{link("S3")}. Issue 6, July 2022. {link("S4")}. May 2026, with September 2026 page notes. Applicable requirements need rechecking for a real design.','small'),
 p(f'{link("D1")}. Design adapted under <link href="https://creativecommons.org/licenses/by/4.0/" color="#596052">CC BY 4.0</link>. Lime/black palette and editorial grid adapted; typography, charts and all case content changed. No template photographs redistributed.','small'),
 p('Computational evidence','h2'),
 p('Excel and Python reconcile across 279 principal checks and 49 sensitivity combinations. Eight financial tests pass, and the teaching notebook executes without error. Formula-engine validation does not establish Microsoft Excel desktop behavior. All forecasts and narratives represent the dated delivered baseline.'),
 p('Reproduction and full definitions: README.md, documentation/methodology.md, documentation/assumptions_and_limitations.md, data/sources.md and the executed analysis notebook. The interview guide provides a plain-language explanation without claiming a commissioned or realized commercial result.','small')]

target=ROOT/'documentation/strategy_report.pdf'
doc=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=64,bottomMargin=53,title='5G Network Expansion Investment Review',author='Independent portfolio case study')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
pages=len(PdfReader(target).pages)
print(f'Saved strategy report: {pages} pages. Target 9.')
assert pages==9,f'Unexpected pagination: {pages}; inspect and refine layout'
