// Authoring dependency: @oai/artifact-tool in Codex's bundled Node runtime.
// Public Python analysis does not require this authoring dependency.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const build=process.env.CASE_BUILD_DIR || path.join(root,'.build');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(root,'models'),{recursive:true});
const raw=await fs.readFile(path.join(root,'data/assumptions.csv'),'utf8');
const inputWorkbook=await Workbook.fromCSV(raw,{sheetName:'Input staging'});
const staging=inputWorkbook.worksheets.getItem('Input staging');
const inputRows=staging.getUsedRange().values.slice(1).filter(row=>row[0]).map(row=>({key:row[0],row:Number(row[1]),label:row[2],value:Number(row[3]),unit:row[4],kind:row[5],source:row[6],rationale:row[7]}));
// The original CSV remains the documented source file, separate from edited what-ifs.
const wb=Workbook.create();
const sheets={};
for(const name of ['Dashboard','Assumptions','Customer & Revenue','Operating Costs','CAPEX','Cash Flow','Investment Evaluation','Scenarios','Sensitivity'])sheets[name]=wb.worksheets.add(name);
const ink='#151515',lime='#D8FB50',paper='#FAFAF6',rule='#D2D4CB',green='#008000';
const money='"$"#,##0;("$"#,##0);"-"';
const count='#,##0;(#,##0);"-"';
const pct='0.0%;(0.0%);"-"';
const millions='"$"0.0,,"M";("$"0.0,,"M");"-"';
function base(name,last='H42'){
  const s=sheets[name];s.showGridLines=false;
  s.getRange(`A1:${last}`).format.font={name:'Arial',size:10,color:ink};
  s.getRange(`A1:${last}`).format.rowHeight=23;
  s.getRange(`A1:${last}`).format.verticalAlignment='center';
  s.getRange('A1:A60').format.columnWidth=39;
  s.getRange('B1:H60').format.columnWidth=18;
  return s;
}
function title(s,text,context){
  s.getRange('A1').values=[[text]];
  s.getRange('A1').format.font={name:'Arial',size:15,bold:true,color:ink};
  s.getRange('A1:H1').format.rowHeight=31;
  s.getRange('A1:H1').format.borders={bottom:{style:'thin',color:ink}};
  s.getRange('A2').values=[[context]];s.getRange('A2').format.font.italic=true;
}
function header(s,range,values){s.getRange(range).values=[values];s.getRange(range).format={fill:ink,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:27};}
function formula(s,cell,text){s.getRange(cell).formulas=[[text]];s.getRange(cell).format.font.color=text.includes('!')?green:'#000000';}
function row(s,r,label,values,fmt=money){s.getRange(`A${r}`).values=[[label]];if(values)s.getRange(`B${r}:${String.fromCharCode(65+values.length)}${r}`).values=[values];s.getRange(`B${r}:H${r}`).setNumberFormat(fmt);s.getRange(`B${r}:H${r}`).format.horizontalAlignment='right';}
function total(s,r,last='F'){s.getRange(`A${r}:${last}${r}`).format.font.bold=true;s.getRange(`A${r}:${last}${r}`).format.borders={top:{style:'thin',color:rule}};s.getRange(`A${r}:${last}${r}`).format.rowHeight=27;}
function context(s){s.getRange('A3').values=[['Case selected']];formula(s,'B3',"='Assumptions'!B32");s.getRange('D3').values=[['Model']];formula(s,'E3',"='Assumptions'!B31");}
function notes(s,start,rows){for(const [i,text]of rows.entries()){s.getRange(`A${start+i}`).values=[[text]];s.getRange(`A${start+i}`).format.font={name:'Arial',size:10,color:'#596052',italic:true};}}

const a=base('Assumptions','F47');a.tabColor='#8DA82D';
title(a,'5G expansion assumptions','Illustrative Canadian investment case. Nominal CAD. Inputs in blue on amber fill.');
// Preserve the first-stage addresses, including B2:B11.
a.getRange('A1').values=[['Assumption']];
a.getRange('B1:F1').values=[['Value','Unit',null,'Source','Rationale']];
a.getRange('A1:F1').format={fill:ink,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:27};
a.getRange('A1:A47').format.columnWidth=45;
a.getRange('C1:C47').format.columnWidth=28;
a.getRange('D1:D47').format.columnWidth=3;
a.getRange('E1:E47').format.columnWidth=29;
a.getRange('F1:F47').format.columnWidth=86;
a.getRange('A2:F2').clear({applyTo:'contents'});
for(const input of inputRows){
  a.getRange(`A${input.row}:C${input.row}`).values=[[input.label,input.value,input.unit]];
  a.getRange(`E${input.row}:F${input.row}`).values=[[input.source,input.rationale]];
  a.getRange(`B${input.row}`).format.fill='#FFF2CC';a.getRange(`B${input.row}`).format.font.color='#0000FF';
  a.getRange(`B${input.row}`).setNumberFormat(['fraction','annual rate'].includes(input.unit)||input.key==='annual_churn'?pct:count);
  if(['initial_capex','arpu','initial_opex','cac','terminal_cash'].includes(input.key))a.getRange(`B${input.row}`).setNumberFormat(money);
  a.getRange(`A${input.row}:F${input.row}`).format.rowHeight=29;
  a.getRange(`F${input.row}`).format.wrapText=true;
}
for(const [cell,hi]of [['B14',2],['B15',3]])a.dataValidations.add({range:cell,rule:{type:'whole',operator:'between',formula1:1,formula2:hi}});
a.dataValidations.add({range:'B3',rule:{type:'whole',operator:'between',formula1:5,formula2:5}});
a.dataValidations.add({range:'B20',rule:{type:'whole',operator:'between',formula1:5,formula2:40}});
for(const r of [18,19,21,22,23])a.dataValidations.add({range:`B${r}`,rule:{type:'decimal',operator:'between',formula1:0,formula2:1}});
a.getRange('A13').values=[['Model controls']];total(a,13,'F');
a.getRange('F14').values=[['1 = simplified teaching model. 2 = expanded investment model.']];
a.getRange('F15').values=[['1 = bear. 2 = base. 3 = bull. These controls drive the same forecast.']];
a.getRange('A17').values=[['Expanded-model assumptions']];total(a,17,'F');
a.getRange('A30').values=[['Active drivers used by the model']];total(a,30,'F');
const active=[
 [31,'Active model','=CHOOSE(B14,"Simplified","Expanded")'],
 [32,'Active scenario','=CHOOSE(B15,"Bear","Base","Bull")'],
 [33,'Active net subscriber growth',"=IF('Sensitivity'!B4=\"\",CHOOSE(B15,B10,B6,B11),'Sensitivity'!B4)"],
 [34,'Active monthly ARPU',"=IF('Sensitivity'!B3=\"\",B5,'Sensitivity'!B3)"],
 [35,'Active incremental revenue share','=IF(B14=1,1,B18)'],
 [36,'Active cash tax rate','=IF(B14=1,0,B19)'],
 [37,'Active maintenance CAPEX rate','=IF(B14=1,0,B21)'],
 [38,'Active working capital rate','=IF(B14=1,0,B22)'],
 [39,'Active cancellation intensity','=IF(B14=1,0,B23)'],
 [40,'Active acquisition cost','=IF(B14=1,0,B24)'],
 [41,'Active Year 5 residual cash','=IF(B14=1,0,B25)'],
];
for(const [r,label,f]of active){a.getRange(`A${r}`).values=[[label]];formula(a,`B${r}`,f);a.getRange(`B${r}`).setNumberFormat(r===34||r>=40?money:r>=33?pct:'General');}
notes(a,44,['Annual average subscribers drive revenue. Growth already includes churn.',
 'No statutory tax conclusion, local demand survey or RF engineering design is implied.',
 'Five-year workbook schedule. Assumptions CSV is the reproducible baseline.',
 'Independent hypothetical case study. No affiliation with or endorsement by Bell Canada.']);

const cust=base('Customer & Revenue','F29');title(cust,'Customer and revenue forecast','Annual averages reconcile to opening and closing subscribers. Nominal CAD.');context(cust);
header(cust,'A4:F4',['Forecast','Year 1','Year 2','Year 3','Year 4','Year 5']);
for(const [r,label,fmt]of [[6,'Average active subscribers',count],[7,'Net subscriber growth',pct],[8,'Opening subscribers',count],[9,'Closing subscribers',count],[10,'Net additions',count],[11,'Cancellations',count],[12,'Gross additions',count],[14,'Monthly ARPU',money],[15,'Gross subscription revenue',money],[16,'Incremental share',pct],[17,'Incremental revenue',money],[19,'Prelaunch subscribers at Year 0',count],[21,'Serviceable-line penetration',pct],[22,'End-year capacity utilization',pct]])row(cust,r,label,null,fmt);
for(const [i,col]of ['B','C','D','E','F'].entries()){
  const prev=String.fromCharCode(col.charCodeAt(0)-1);
  formula(cust,`${col}6`,i===0?"='Assumptions'!B4":`=${prev}6*(1+${col}7)`);
  formula(cust,`${col}7`,"='Assumptions'!B33");
  formula(cust,`${col}8`,i===0?`=2*${col}6/(2+${col}7)`:`=${prev}9`);
  formula(cust,`${col}9`,`=2*${col}6-${col}8`);
  formula(cust,`${col}10`,`=${col}9-${col}8`);
  formula(cust,`${col}11`,`=${col}6*'Assumptions'!B39`);
  formula(cust,`${col}12`,`=SUM(${col}10:${col}11)`);
  formula(cust,`${col}14`,"='Assumptions'!B34");
  formula(cust,`${col}15`,`=${col}6*${col}14*12`);
  formula(cust,`${col}16`,"='Assumptions'!B35");
  formula(cust,`${col}17`,`=${col}15*${col}16`);
  formula(cust,`${col}21`,`=${col}6/'Assumptions'!B26`);
  formula(cust,`${col}22`,`=${col}9/'Assumptions'!B27`);
}
formula(cust,'B19','=B8');total(cust,12);total(cust,17);cust.getRange('A17:F17').format.fill=lime;
notes(cust,25,['Linear net growth within each year: average = (opening + closing) / 2.',
 'Gross additions = net additions + cancellations. Churn is not deducted twice.',
 'Opening subscribers require acquisition spending before Year 1 operations.',
 'Capacity is a subscriber planning proxy. A flag requires an engineering redesign.',
 'Subscriber estimates retain decimals. Display rounding does not alter revenue.']);
cust.getRange('B22:F22').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:1,format:{fill:'#F9DCD4',font:{color:'#A74735',bold:true}}});

const op=base('Operating Costs','F24');title(op,'Operating cost forecast','Network costs exclude acquisition spending and capitalized equipment. Nominal CAD.');context(op);header(op,'A4:F4',['Forecast','Year 1','Year 2','Year 3','Year 4','Year 5']);
for(const [r,label,fmt]of [[6,'Network cost growth',pct],[8,'Network operating costs',money],[9,'Gross subscriber additions',count],[10,'Cost per gross acquisition',money],[11,'Acquisition expense',money],[13,'Total operating cash costs',money],[15,'Incremental revenue',money],[16,'EBITDA',money],[17,'EBITDA margin',pct]])row(op,r,label,null,fmt);
for(const [i,col]of ['B','C','D','E','F'].entries()){
  const prev=String.fromCharCode(col.charCodeAt(0)-1);
  formula(op,`${col}6`,"='Assumptions'!B8");formula(op,`${col}8`,i===0?"='Assumptions'!B7":`=${prev}8*(1+${col}6)`);
  formula(op,`${col}9`,`='Customer & Revenue'!${col}12`);formula(op,`${col}10`,"='Assumptions'!B40");
  formula(op,`${col}11`,`=${col}9*${col}10`);formula(op,`${col}13`,`=SUM(${col}8,${col}11)`);
  formula(op,`${col}15`,`='Customer & Revenue'!${col}17`);formula(op,`${col}16`,`=${col}15-${col}13`);
  formula(op,`${col}17`,`=IF(${col}15=0,"n.a.",${col}16/${col}15)`);
}
total(op,13);total(op,16);notes(op,21,['Operating costs cover expensed maintenance, personnel, energy, licensing and support.',
 'Acquisition costs cover initial and replacement customers; Year 0 is in Cash Flow.',
 'Network OPEX grows at its own nominal rate. No second inflation uplift is added.',
 'Granular supplier, staffing and energy quotes must replace the illustrative total.']);

const cap=base('CAPEX','G23');title(cap,'Capital expenditure and depreciation','CAPEX is a cash investment. Depreciation is a noncash accounting allocation.');context(cap);header(cap,'A4:G4',['Year',0,1,2,3,4,5]);cap.getRange('B4:G4').setNumberFormat('"Year "0');
for(const [r,label]of [[6,'Initial network CAPEX'],[7,'Maintenance CAPEX'],[8,'Total CAPEX'],[10,'Initial asset depreciation'],[11,'Maintenance asset depreciation'],[12,'Total depreciation'],[14,'Closing net book value']])row(cap,r,label,null,money);
for(const [i,col]of ['B','C','D','E','F','G'].entries()){
  const prev=String.fromCharCode(col.charCodeAt(0)-1);
  formula(cap,`${col}6`,i===0?"='Assumptions'!B2":'=0');
  formula(cap,`${col}7`,i===0?'=0':i===1?"='Assumptions'!B2*'Assumptions'!B37":`=${prev}7*(1+'Assumptions'!B8)`);
  formula(cap,`${col}8`,`=SUM(${col}6:${col}7)`);
  formula(cap,`${col}10`,i===0?'=0':"='Assumptions'!B2/'Assumptions'!B20");
  formula(cap,`${col}11`,i===0?'=0':`=SUM($B$7:${prev}7)/'Assumptions'!B20`);
  formula(cap,`${col}12`,`=SUM(${col}10:${col}11)`);
  formula(cap,`${col}14`,i===0?`=${col}8`:`=${prev}14+${col}8-${col}12`);
}
total(cap,8,'G');total(cap,12,'G');total(cap,14,'G');notes(cap,18,['Initial assets enter service at the start of Year 1. Straight-line depreciation.',
 'Maintenance assets enter service at year-end and depreciate from the next year.',
 'The five-year schedule requires an asset life of at least five years.',
 'Book depreciation is a tax proxy; Canadian tax-pool rules are not modeled.',
 'Existing spectrum rights and required capacity are assumed available within scope.',
 'Net book value is not automatically credited as cash or terminal value.']);

const cf=base('Cash Flow','G37');title(cf,'Incremental unlevered free cash flow','Nominal CAD. Year 0 outflows occur immediately; annual operating cash flows at year-end.');context(cf);header(cf,'A4:G4',['Year',0,1,2,3,4,5]);cf.getRange('B4:G4').setNumberFormat('"Year "0');
const cashLabels={6:'Incremental revenue',7:'Network operating costs',8:'Acquisition expense',9:'EBITDA',10:'Depreciation',11:'EBIT',12:'Opening tax losses',13:'Tax losses utilized',14:'Taxable income',15:'Cash taxes',16:'Closing tax losses',18:'Closing working capital',19:'Change in working capital',20:'Capital expenditure',21:'Net residual cash proceeds',23:'Unlevered free cash flow',24:'Cumulative free cash flow',25:'Discount factor',26:'Discounted free cash flow',27:'Cumulative discounted cash flow',30:'Payback crossing (years)',31:'Discounted crossing (years)'};
for(const [r,label]of Object.entries(cashLabels))row(cf,Number(r),label,null,Number(r)===25?'0.0000':Number(r)>=30?'0.00':money);
for(const [i,col]of ['B','C','D','E','F','G'].entries()){
  const prev=String.fromCharCode(col.charCodeAt(0)-1),src=prev;
  formula(cf,`${col}6`,i===0?'=0':`='Customer & Revenue'!${src}17`);
  formula(cf,`${col}7`,i===0?'=0':`='Operating Costs'!${src}8`);
  formula(cf,`${col}8`,i===0?"='Customer & Revenue'!B19*'Assumptions'!B40":`='Operating Costs'!${src}11`);
  formula(cf,`${col}9`,`=${col}6-SUM(${col}7:${col}8)`);
  formula(cf,`${col}10`,`='CAPEX'!${col}12`);
  formula(cf,`${col}11`,`=${col}9-${col}10`);
  formula(cf,`${col}12`,i===0?'=0':`=${prev}16`);
  formula(cf,`${col}13`,`=MIN(${col}12,MAX(0,${col}11))`);
  formula(cf,`${col}14`,`=MAX(0,${col}11-${col}13)`);
  formula(cf,`${col}15`,`=${col}14*'Assumptions'!B36`);
  formula(cf,`${col}16`,`=MAX(0,${col}12-${col}11)`);
  formula(cf,`${col}18`,`=${col}6*'Assumptions'!B38`);
  formula(cf,`${col}19`,i===0?`=${col}18`:`=${col}18-${prev}18`);
  formula(cf,`${col}20`,`='CAPEX'!${col}8`);
  formula(cf,`${col}21`,i===5?"='Assumptions'!B41":'=0');
  formula(cf,`${col}23`,`=${col}9-${col}15-${col}19-${col}20+${col}21`);
  formula(cf,`${col}24`,i===0?`=${col}23`:`=${prev}24+${col}23`);
  formula(cf,`${col}25`,`=(1+'Assumptions'!B9)^(-${col}4)`);
  formula(cf,`${col}26`,`=${col}23*${col}25`);
  formula(cf,`${col}27`,i===0?`=${col}26`:`=${prev}27+${col}26`);
  if(i>0){formula(cf,`${col}30`,`=IF(AND(${prev}24<0,${col}24>=0,${col}23>0),${col}4-1-${prev}24/${col}23,"")`);formula(cf,`${col}31`,`=IF(AND(${prev}27<0,${col}27>=0,${col}26>0),${col}4-1-${prev}27/${col}26,"")`);}
}
for(const r of [9,11,16,23,24,26,27])total(cf,r,'G');cf.getRange('A23:G23').format.fill=lime;
notes(cf,34,['Unlevered FCF = EBITDA - cash taxes - change in working capital - CAPEX + residual cash.',
 'Year 0 acquisition spending creates tax losses carried forward, with no immediate refund.',
 'No working capital release at Year 5; continued operation is assumed after the cutoff.',
 'Fractional payback interpolates within the recovery year. No recovery is explicitly reported.']);

const ev=base('Investment Evaluation','F25');title(ev,'Investment evaluation','Five-year cash-flow screen. Figures include Year 0 acquisition spending in expanded mode.');context(ev);header(ev,'A4:D4',['Metric','Result',null,'Definition']);
const metrics=[
 [5,'NPV',"=NPV('Assumptions'!B9,'Cash Flow'!C23:G23)+'Cash Flow'!B23",money,'Year 0 plus discounted Year 1-5 cash flows'],
 [6,'IRR',"=IF(AND(MIN('Cash Flow'!B23:G23)<0,MAX('Cash Flow'!B23:G23)>0),IRR('Cash Flow'!B23:G23),\"n.a.\")",pct,'Annual return solving NPV = 0'],
 [7,'Cash ROI',"=IF('Cash Flow'!B23=0,\"n.a.\",SUM('Cash Flow'!B23:G23)/(-'Cash Flow'!B23))",pct,'Cumulative net FCF / initial cash outflow'],
 [8,'Payback',"=IF(COUNT('Cash Flow'!C30:G30)=0,\"Not within 5 years\",MIN('Cash Flow'!C30:G30))",'0.00','Years to undiscounted cash recovery'],
 [9,'Discounted payback',"=IF(COUNT('Cash Flow'!C31:G31)=0,\"Not within 5 years\",MIN('Cash Flow'!C31:G31))",'0.00','Years to recovery at the discount rate'],
 [10,'Initial cash outflow',"=-'Cash Flow'!B23",money,'Network CAPEX plus prelaunch acquisition'],
 [11,'Total cost of ownership',"=SUM('Cash Flow'!B7:G8)+SUM('Cash Flow'!B20:G20)",money,'Undiscounted CAPEX + network OPEX + acquisition'],
 [12,'Five-year incremental revenue',"=SUM('Cash Flow'!C6:G6)",money,'Revenue attributable to this investment'],
 [13,'Five-year gross revenue',"=SUM('Customer & Revenue'!B15:F15)",money,'Before removing transferred existing revenue'],
 [14,'Cumulative net cash flow',"=SUM('Cash Flow'!B23:G23)",money,'Includes the initial investment'],
 [15,'NPV reconciliation difference',"=B5-SUM('Cash Flow'!B26:G26)",'0.00','NPV function versus discounted schedule'],
 [16,'Year 5 closing subscribers',"='Customer & Revenue'!F9",count,'End-year subscriber capacity test'],
 [17,'Year 5 capacity utilization',"='Customer & Revenue'!F22",pct,'Closing subscribers / assumed line capacity'],
 [18,'Financial decision','=IF(B5>0,"Conditional financial approval","Defer / modify")','General','Approval still requires demand and engineering evidence'],
 [19,'Capacity decision','=IF(B17<=1,"Within assumed capacity","Exceeds assumed capacity")','General','Excess capacity requires new scope and costs'],
];
for(const [r,label,f,fmt,definition]of metrics){row(ev,r,label,null,fmt);formula(ev,`B${r}`,f);ev.getRange(`D${r}`).values=[[definition]];}
ev.getRange('B1:B25').format.columnWidth=28;ev.getRange('C1:C25').format.columnWidth=3;ev.getRange('D1:D25').format.columnWidth=66;ev.getRange('D5:D19').format.wrapText=true;ev.getRange('D5:D19').format.horizontalAlignment='left';ev.getRange('B5:B19').format.font.color=ink;ev.getRange('A5:D19').format.rowHeight=30;total(ev,5,'D');ev.getRange('A5:D5').format.fill=lime;
ev.getRange('E3').clear({applyTo:'contents'});formula(ev,'D3',`="Model: "&'Assumptions'!B31`);
notes(ev,22,['TCO excludes income taxes, financing and working capital; it measures ownership spending.',
 'IRR and cash ROI use consistent incremental cash flows. ROI is not an annual return.',
 'Zero residual value is a five-year screening assumption, not a claim that the network expires.',
 'A positive financial result does not resolve unvalidated demand, spectrum or engineering risks.']);

const sen=base('Sensitivity','H22');title(sen,'NPV sensitivity to pricing and adoption','Native two-input Excel What-If Data Table. Expanded or simplified mode follows the model control.');
sen.getRange('A3').values=[['ARPU override (leave blank)']];sen.getRange('A4').values=[['Growth override (leave blank)']];
sen.getRange('B3:B4').values=[[null],[null]];sen.getRange('B3:B4').format.fill='#FFF2CC';sen.getRange('B3:B4').format.font.color='#0000FF';sen.getRange('B3').setNumberFormat(money);sen.getRange('B4').setNumberFormat(pct);
sen.getRange('A6').values=[['Rows: annual net growth. Columns: monthly ARPU in CAD. Outputs: five-year NPV in CAD.']];
const arpus=[50,55,60,65,70,75,80],growths=[0,.05,.10,.15,.20,.25,.30];
formula(sen,'A8',"='Investment Evaluation'!B5");sen.getRange('A8').setNumberFormat(';;;');
sen.getRange('B8:H8').values=[arpus];sen.getRange('A9:A15').values=growths.map(x=>[x]);
sen.getRange('B8:H8').setNumberFormat(money);sen.getRange('A9:A15').setNumberFormat(pct);
sen.getRange('A8:H8').format.fill=ink;sen.getRange('A8:H8').format.font.color='#FFFFFF';sen.getRange('A9:A15').format.font.bold=true;
sen.dataTables.add('A8:H15',{rowInput:'B3',columnInput:'B4'});
sen.getRange('B9:H15').setNumberFormat(millions);sen.getRange('B9:H15').conditionalFormats.add('colorScale',{colors:['#F0BCAC','#FAFAF6','#D8FB50'],thresholds:['min',0,'max']});
notes(sen,18,['The blank override cells drive the model only while the What-If table substitutes values.',
 'Data Table calculation must be enabled in Excel. Each cell evaluates the same live forecast.',
 'High-growth combinations can exceed line capacity. Extra capacity CAPEX is not assumed.',
 'Other drivers, exact stress ranges and break-even thresholds are in the Python analysis.',
 'Annual cash flows remain at year-end. NPV includes the initial outflow exactly once.']);

// Calculate each named case through this same build, then capture a labeled comparison.
function value(s,cell){return sheets[s].getRange(cell).values[0][0];}
const captures={};
for(const [name,selector]of [['Bear',1],['Base',2],['Bull',3]]){
  a.getRange('B15').values=[[selector]];
  const m={};for(const [key,r]of [['npv',5],['irr',6],['roi',7],['payback',8],['discounted_payback',9],['initial_outflow',10],['tco',11],['cumulative_revenue',12],['cumulative_net_cash',14]]){const v=value('Investment Evaluation',`B${r}`);m[key]=typeof v==='number'?v:null;}
  const forecast={};
  const cashKeys={revenue:6,network_opex:7,acquisition_cost:8,depreciation:10,cash_tax:15,closing_nol:16,delta_nwc:19,capex:20,fcf:23,discounted_fcf:26};
  for(const [key,r]of Object.entries(cashKeys))forecast[key]=cf.getRange(`B${r}:G${r}`).values[0];
  for(const [key,r,zero]of [['average_customers',6,0],['opening_customers',8,0],['closing_customers',9,value('Customer & Revenue','B8')],['gross_additions',12,value('Customer & Revenue','B8')]])forecast[key]=[zero,...cust.getRange(`B${r}:F${r}`).values[0]];
  captures[name]={metrics:m,forecast,growth:value('Assumptions','B33'),year5_customers:value('Customer & Revenue','F6'),year5_closing:value('Customer & Revenue','F9'),capacity:value('Investment Evaluation','B17')};
}
a.getRange('B15').values=[[2]];
const sc=base('Scenarios','F51');title(sc,'Captured scenario comparison','Same forecast recalculated for each case at the baseline assumptions. Captures are not live scenario formulas.');
sc.getRange('A3').values=[['Capture status']];sc.getRange('E3').values=[['21 Nov 2026']];
header(sc,'A5:D5',['Metric','Bear','Base','Bull']);
const scenarioMetrics=[
 [6,'Net subscriber growth','growth',pct],[7,'Year 5 average subscribers','year5_customers',count],
 [8,'Five-year incremental revenue','cumulative_revenue',money],[9,'Initial cash outflow','initial_outflow',money],
 [10,'NPV','npv',money],[11,'IRR','irr',pct],[12,'Cash ROI','roi',pct],
 [13,'Payback (years)','payback','0.00'],[14,'Discounted payback (years)','discounted_payback','0.00'],
 [15,'Total cost of ownership','tco',money],[16,'Cumulative net cash flow','cumulative_net_cash',money],
 [17,'Year 5 closing subscribers','year5_closing',count],[18,'Capacity utilization','capacity',pct],
];
for(const [r,label,key,fmt]of scenarioMetrics){row(sc,r,label,null,fmt);for(const [i,name]of ['Bear','Base','Bull'].entries()){const cap=captures[name];const v=key in cap?cap[key]:cap.metrics[key];sc.getRange(`${String.fromCharCode(66+i)}${r}`).values=[[v===null?(key.includes('payback')?'Not within 5 years':'n.a.'):v]];}}
sc.getRange('A19:D19').values=[['Recommendation',...['Bear','Base','Bull'].map(name=>captures[name].metrics.npv>0?'Conditional approval':'Defer / modify')]];
sc.getRange('A20:D20').values=[['Capacity screen',...['Bear','Base','Bull'].map(name=>captures[name].capacity<=1?'Within design':'Requires extra capacity')]];
sc.getRange('B1:D51').format.columnWidth=25;total(sc,10,'D');sc.getRange('A10:D10').format.fill=lime;
notes(sc,22,['Use Assumptions B15 to inspect live case results in the Dashboard and Investment Evaluation.',
 'Editing a driver marks captures stale. Rebuild the workbook to refresh these captured results.']);
header(sc,'A25:D25',['Captured input','Current input','Captured input','Changed']);
const captureInputs=inputRows.filter(x=>x.key!=='scenario');
for(const [i,input]of captureInputs.entries()){
  const r=26+i;sc.getRange(`A${r}`).values=[[input.label]];formula(sc,`B${r}`,`='Assumptions'!B${input.row}`);sc.getRange(`C${r}`).values=[[input.value]];formula(sc,`D${r}`,`=IF(B${r}=C${r},0,1)`);
  const fmt=['fraction','annual rate'].includes(input.unit)||input.key==='annual_churn'?pct:count;sc.getRange(`B${r}:C${r}`).setNumberFormat(fmt);
}
formula(sc,'B3',`=IF(OR('Sensitivity'!B3<>"",'Sensitivity'!B4<>""),"Refresh required",IF(SUM(D26:D${25+captureInputs.length})=0,"Current capture","Refresh required"))`);
sc.getRange('B3').conditionalFormats.add('containsText',{text:'Refresh required',format:{fill:'#F9DCD4',font:{color:'#A74735',bold:true}}});

const dash=base('Dashboard','L38');dash.tabColor=ink;title(dash,'5G network expansion investment review','Fictional Canadian regional cluster. Five-year investment screen. Nominal CAD.');
dash.getRange('A3').values=[['Case selected']];formula(dash,'B3',"='Assumptions'!B32");dash.getRange('E3').values=[['Model']];formula(dash,'F3',"='Assumptions'!B31");
dash.getRange('A1:A38').format.columnWidth=33;dash.getRange('B1:B38').format.columnWidth=25;dash.getRange('C1:C38').format.columnWidth=3;dash.getRange('D1:L38').format.columnWidth=12;
for(const [r,label,target,fmt]of [[6,'Five-year NPV',5,money],[7,'IRR',6,pct],[8,'Cash ROI',7,pct],[9,'Payback (years)',8,'0.00'],[11,'Initial cash outflow',10,money],[12,'Five-year incremental revenue',12,money],[14,'Financial decision',18,'General'],[15,'Capacity screen',19,'General']]){dash.getRange(`A${r}`).values=[[label]];formula(dash,`B${r}`,`='Investment Evaluation'!B${target}`);dash.getRange(`B${r}`).setNumberFormat(fmt);dash.getRange(`B${r}`).format.font.color=ink;}
dash.getRange('A6:B6').format.fill=lime;dash.getRange('A6:B6').format.font.bold=true;dash.getRange('A6:B6').format.rowHeight=35;
dash.getRange('A17').values=[['Captured comparison status']];formula(dash,'B17',"='Scenarios'!B3");dash.getRange('B17').format.font.color=ink;
header(dash,'A20:B20',['Year','Incremental revenue']);
for(const [i,col]of ['B','C','D','E','F'].entries()){dash.getRange(`A${21+i}`).values=[[`Year ${i+1}`]];formula(dash,`B${21+i}`,`='Customer & Revenue'!${col}17`);dash.getRange(`B${21+i}`).setNumberFormat(money);dash.getRange(`B${21+i}`).format.font.color=ink;}
header(dash,'A28:B28',['Year','Free cash flow']);
for(const [i,col]of ['B','C','D','E','F','G'].entries()){dash.getRange(`A${29+i}`).values=[[`Year ${i}`]];formula(dash,`B${29+i}`,`='Cash Flow'!${col}23`);dash.getRange(`B${29+i}`).setNumberFormat(money);dash.getRange(`B${29+i}`).format.font.color=ink;}
const rchart=dash.charts.add('line',dash.getRange('A20:B25'));rchart.setPosition('D5','L18');rchart.title='Incremental revenue (CAD millions)';rchart.hasLegend=false;
rchart.series.items[0].line={fill:ink,style:'solid',width:2.5};
const cchart=dash.charts.add('bar',dash.getRange('A28:B34'));cchart.setPosition('D21','L35');cchart.title='Unlevered free cash flow (CAD millions)';cchart.hasLegend=false;cchart.series.items[0].fill='#8DA82D';
for(const chart of [rchart,cchart]){chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=13;chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};chart.yAxis={numberFormatCode:'"$"0,,"M"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};}
notes(dash,37,['Sources and definitions are on Assumptions. Financial results follow the live model controls.',
 'Independent hypothetical case study. No affiliation with or endorsement by Bell Canada.']);

// Freeze period headings on longer working schedules only.
for(const s of [cust,op,cap,cf])s.freezePanes.freezeRows(4);
for(const name of ['Customer & Revenue','Operating Costs'])sheets[name].getRange('B1:F40').format.horizontalAlignment='right';
// Preserve left alignment of notes and text controls after numeric formatting.
for(const s of [cust,op]){s.getRange('B3').format.horizontalAlignment='left';s.getRange('E3').format.horizontalAlignment='left';}
wb.recalculate();

const baseExpected=JSON.parse(await fs.readFile(path.join(root,'outputs/results.json'),'utf8'));
for(const name of ['Bear','Base','Bull'])for(const key of ['npv','irr','roi','initial_outflow','tco','cumulative_revenue','cumulative_net_cash'])assert.ok(Math.abs(captures[name].metrics[key]-baseExpected.scenarios[name][key])<(key==='irr'||key==='roi'?1e-7:.01),`${name} ${key}: Excel ${captures[name].metrics[key]} Python ${baseExpected.scenarios[name][key]}`);
const sensitivity=[];
for(const [i,g]of growths.entries())for(const [j,arpu]of arpus.entries()){
  const npv=sen.getRangeByIndexes(8+i,1+j,1,1).values[0][0];assert.equal(typeof npv,'number');sensitivity.push({growth:g,arpu,npv});
}
// Control-change checks exercise the one live build and the stale-capture warning.
a.getRange('B14').values=[[1]];assert.ok(Math.abs(value('Investment Evaluation','B5')-baseExpected.simple.npv)<.01);assert.equal(value('Scenarios','B3'),'Refresh required');
a.getRange('B14').values=[[2]];a.getRange('B15').values=[[1]];assert.ok(Math.abs(value('Investment Evaluation','B5')-captures.Bear.metrics.npv)<.01);
a.getRange('B15').values=[[2]];a.getRange('B5').values=[[70]];assert.equal(value('Assumptions','B34'),70);assert.equal(value('Scenarios','B3'),'Refresh required');a.getRange('B5').values=[[65]];
assert.equal(value('Scenarios','B3'),'Current capture');
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'Investment Evaluation'!A4:D19",include:'values,formulas',tableMaxRows:16,tableMaxCols:4,maxChars:5000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula error scan',maxChars:2000})).ndjson);
await fs.writeFile(path.join(root,'outputs/excel_validation.json'),JSON.stringify({...captures,sensitivity},null,2));
const filename=path.join(root,'models/5G_Investment_Financial_Model.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(filename);
const renderRanges={'Dashboard':'A1:L38','Assumptions':'A1:F47','Customer & Revenue':'A1:F29','Operating Costs':'A1:F24','CAPEX':'A1:G23','Cash Flow':'A1:G37','Investment Evaluation':'A1:D25','Scenarios':'A1:D23','Sensitivity':'A1:H22'};
for(const [name,range]of Object.entries(renderRanges)){
  const blob=await wb.render({sheetName:name,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(build,`${name.replaceAll(' ','_').replaceAll('&','and')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log(`Saved ${filename}. Live cases, simple/expanded controls, captures and sensitivity computed.`);
