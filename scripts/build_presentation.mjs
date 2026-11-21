// Editable presentation authored with Codex's bundled @oai/artifact-tool.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
process.env.RUNTIME_NODE_MODULES ||= path.join(root,'node_modules');
const build=path.join(root,'.build/presentation');await fs.mkdir(build,{recursive:true});
const out=path.join(root,'presentation');await fs.mkdir(out,{recursive:true});
const r=JSON.parse(await fs.readFile(path.join(root,'outputs/results.json'),'utf8'));
const ink='#151515',lime='#D8FB50',paper='#FAFAF6',grey='#596052',red='#A74735',white='#FFFFFF';
const FONT='Arial';
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const template='https://www.slidescarnival.com/template/financial-management-for-small-businesses-consulting/155244';
const sources={
  crtc:'https://crtc.gc.ca/eng/publications/reports/PolicyMonitoring/2026/ctmr.htm',
  bce:'https://www.bce.ca/cs-assets/2025-bce-annual-financial-report.pdf-blt5d552f866d8a58a3',
  ised:'https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/learn-more/key-documents/procedures/client-procedures-circulars-cpc/cpc-2-0-03-radiocommunication-and-broadcasting-antenna-systems',
  update:'https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/learn-more/key-documents/consultations/consultation-amendments-tower-siting-process-and-decision-roaming-tower-sharing-and-annual-reporting',
};
function text(s,content,x,y,w,h,size=24,bold=false,color=ink,align='left'){
  const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0},text:content});
  shape.text.style={typeface:FONT,fontSize:size,bold,color,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
  return shape;
}
function rect(s,x,y,w,h,fill){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function footer(s,n,dark=false){
  text(s,'Hypothetical Canadian case. No affiliation with Bell Canada.',72,679,750,18,12,false,dark?ink:grey);
  text(s,String(n),1176,677,32,20,14,false,dark?white:grey,'right');
}
function slide(n,title){const s=deck.slides.add();s.background.fill=paper;text(s,title,72,54,1136,124,46,true);footer(s,n);return s;}
function note(s,content){s.speakerNotes.text=content+'\n\nDesign adapted from SlidesCarnival: '+template+' (CC BY 4.0). Palette and grid adapted; all case content replaced; no template photographs used.';}
function table(s,values,x,y,w,h,widths,size=22){
  const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
  t.styleOptions={headerRow:false,bandedRows:false};
  t.borders.assign({fill:'#D2D4CB',width:.6,style:'solid'});
  for(let row=0;row<values.length;row++)for(let col=0;col<values[row].length;col++){
    const cell=t.getCell(row,col);cell.fill=row===0?ink:paper;
    cell.text.style={typeface:FONT,fontSize:size,color:row===0?white:ink,bold:row===0,alignment:'left',verticalAlignment:'middle',insets:8};
  }
  return t;
}
function bar(s,categories,values,x,y,w,h,{min,max,format='0.0',colors=[ink],percent=false}={}){
  // Chart data use meaningful precision compatible with embedded Excel workbooks.
  values=values.map(value=>Number(value.toFixed(percent?3:6)));
  const c=s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},categories,
    series:[{name:percent?'5G population coverage':'NPV (CAD millions)',values,fill:ink,
      points:values.map((_,idx)=>({idx,fill:colors[idx%colors.length],line:{fill:'none',width:0,style:'solid'}}))}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:100},hasLegend:false,
    chartFill:paper,plotAreaFill:paper,chartLine:{fill:'none',width:0},
    xAxis:{textStyle:{typeface:FONT,fontSize:19,color:ink},line:{fill:'#D2D4CB',width:.6},majorGridlines:null,tickLabelPosition:'low'},
    yAxis:{min,max,numberFormatCode:format,textStyle:{typeface:FONT,fontSize:17,color:grey},majorGridlines:{fill:'#D2D4CB',width:.5,style:'solid'}},
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:FONT,fontSize:20,bold:true,color:ink}},
  });return c;
}
const fmt=x=>x<0?`(${(Math.abs(x)/1e6).toFixed(2)})`:(x/1e6).toFixed(2);

// 1. Executive decision. Split composition adapts the inspected reference cover.
{
 const s=deck.slides.add();s.background.fill=lime;rect(s,820,0,460,720,ink);
 text(s,'5G NETWORK EXPANSION',72,60,690,30,20,true);
 text(s,'The $50M build\nfails the five-year\ninvestment hurdle',72,156,720,236,57,true);
 text(s,'Defer the full rollout.\nValidate demand and quote a shared\nor smaller network design.',72,445,700,120,27);
 text(s,'BASE-CASE NPV (CAD)',870,165,344,32,19,true,lime);
 text(s,'($18.50M)',870,213,350,92,66,true,white);
 text(s,'10% required return\nFive-year cash-flow screen',870,325,335,83,24,false,white);
 text(s,'$53.49M initial cash outflow\nincludes prelaunch acquisition',870,455,335,92,23,false,white);
 const credit=text(s,'Design adapted from SlidesCarnival',72,636,670,22,14,false,ink);credit.hyperlink={uri:template,isExternal:true};
 footer(s,1,true);
 note(s,'Recommendation: defer / modify. Expanded base NPV CAD -18,504,240.74; IRR -3.2016%; initial network CAPEX CAD 50M plus prelaunch acquisition CAD 3,488,372.09. All operating forecasts are illustrative. Five-year horizon and zero residual are screening conventions, not a lifetime network valuation. Source: outputs/results.json and methodology.md.');
}
// 2. Market evidence, with sourced facts separated from the fictional footprint.
{
 const s=slide(2,'Rural coverage leaves room,\nbut local demand is unproven');
 text(s,'Population with 5G access in 2024',72,208,610,35,23,true);
 bar(s,['Canada','Rural','First Nations\nreserves'],[.943,.752,.522],72,262,604,306,{min:0,max:1,format:'0.0%',colors:[lime,ink,'#969E8B'],percent:true});
 text(s,'120,000 lines',750,214,455,62,43,true);
 text(s,'Fictional serviceable regional market',750,281,455,48,22);
 text(s,'25,000 average\nsubscribers in Year 1',750,356,455,90,32,true);
 text(s,'$65 monthly ARPU assumed\n$57.36 BCE blended benchmark',750,491,455,83,23);
 text(s,'Sources: CRTC 2026 CTMR, Fig. 51 (2024 data); BCE 2025 Annual Financial Report, p.52',72,580,1136,24,14,false,grey);
 text(s,'CRTC national context does not establish local demand. The footprint and forecasts are illustrative.',72,615,1136,47,19,false,grey);
 note(s,'Source S1: '+sources.crtc+'; 2026 report, page modified 2026-02-24; Figure 51 printed p.42 reports 2024 Canada 94.3%, rural 75.2%, First Nations reserves 52.2% population coverage. Categories overlap; these are not geographic coverage or adoption measures. Source S2: '+sources.bce+'; published 2026-03-05, FY2025, printed p.52: blended mobile-phone monthly ARPU CAD 57.36. Customer/product mixes differ; no direct forecast substitution. Fictional cluster: 120,000 serviceable lines. Case ARPU is about 13.3% above benchmark.');
}
// 3. Editable financial table retains all six investment periods.
{
 const s=slide(3,'Revenue growth does not close\nthe cash recovery gap');
 const f=r.forecasts.Base;
 const rows=[['CAD millions','Year 0','Year 1','Year 2','Year 3','Year 4','Year 5'],
  ['Incremental revenue',...f.map(x=>fmt(x.revenue))],
  ['Operating cash costs',...f.map(x=>fmt(x.network_opex+x.acquisition_cost))],
  ['Cash taxes',...f.map(x=>fmt(x.cash_tax))],
  ['Change in NWC',...f.map(x=>fmt(x.delta_nwc))],
  ['CAPEX',...f.map(x=>fmt(x.capex))],
  ['Free cash flow',...f.map(x=>fmt(x.fcf))]];
 const t=table(s,rows,72,219,1136,344,[260,146,146,146,146,146,146],21);
 for(let c=0;c<7;c++){t.getCell(6,c).fill=lime;t.getCell(6,c).text.style={typeface:FONT,fontSize:22,bold:true,color:ink};}
 text(s,'Year 0 includes $3.49M prelaunch acquisition. Revenue reflects 85% incrementality.',72,597,1136,38,23);
 text(s,'Net cash remains unrecovered at Year 5. Figures may differ slightly after display rounding.',72,637,1136,30,19,false,grey);
 note(s,'Sources: outputs/base_forecast.csv, results.json and methodology.md. All values are illustrative nominal CAD millions. Cost rows are displayed as positive uses of cash. FCF = revenue - operating cash costs - taxes - change in NWC - CAPEX; residual cash is zero. Year 0 cash costs are initial acquisition only; network CAPEX is separate. Operating cash costs exclude noncash depreciation. Required investment periods include Year 0 and Years 1-5.');
}
// 4. Different model scopes explain the reversal, without hiding the asset-life issue.
{
 const s=slide(4,'Economic costs reverse\nthe initial verdict');
 text(s,'Five-year NPV (CAD millions)',72,214,650,32,23,true);
 bar(s,['Simplified','Expanded'],[r.simple.npv/1e6,r.base.npv/1e6],72,261,650,310,{min:-25,max:22,format:'0.0',colors:[lime,ink]});
 text(s,'IRR  -3.20%',790,244,418,55,35,true);
 text(s,'Cash ROI  -10.51%',790,326,418,55,31,true);
 text(s,'No payback\nwithin five years',790,413,418,86,31,true);
 text(s,'Zero residual is a screening\nassumption. Later value needs\na supported lifecycle appraisal.',790,540,418,95,22);
 text(s,'The expanded case adds acquisition, cash taxes, working capital and maintenance CAPEX.',72,618,654,48,20,false,grey);
 note(s,'Sources: results.json and methodology.md. Simplified NPV CAD 15.0481M, expanded NPV CAD -18.5042M. Simple mode also assumes 100% incremental revenue; expanded uses 85%. These are intentionally different scopes. Cash ROI = cumulative net Year 0-5 FCF / initial outflow. IRR and ROI are distinct; neither payback occurs within five years. The assumed initial asset life is 10 years. Zero residual does not establish zero value after Year 5. About CAD 29.8013M supported net Year 5 cash value would close the NPV gap.');
}
// 5. High adoption alone is insufficient and can breach the capacity assumption.
{
 const s=slide(5,'Even 25% growth fails\nthe return hurdle');
 text(s,'Five-year NPV (CAD millions)',72,214,650,32,23,true);
 bar(s,['Bear 5%','Base 15%','Bull 25%'],['Bear','Base','Bull'].map(x=>r.scenarios[x].npv/1e6),72,261,650,310,{min:-32,max:1,format:'0.0',colors:['#969E8B',ink,'#91A92D']});
 text(s,'67,817 lines',790,240,418,62,45,true);
 text(s,'Bull Year 5 closing subscribers\nversus 60,000 assumed capacity',790,310,418,84,23);
 text(s,'Break-even network CAPEX',790,445,418,39,22);
 text(s,'$31.02M',790,487,418,69,48,true);
 text(s,'Other base assumptions held constant',790,562,418,50,20,false,grey);
 text(s,'Demand-only break-even also exceeds capacity. Additional capacity costs are excluded.',72,618,1136,49,23);
 note(s,'Source: scenario_summary.csv, results.json and methodology.md. Bear/base/bull change only net annual average subscriber growth to 5/15/25%. NPVs CAD -26.8953M/-18.5042M/-8.6466M. Bull closing lines 67,816.84 versus a 60,000-line commercial planning proxy, not an RF study. CAPEX break-even CAD 31,019,938.41 at other base assumptions. Mathematical Year 1 average-customer break-even 33,623.87 implies 62,911.27 closing Year 5 lines and is infeasible at the capacity proxy without new costs.');
}
// 6. Actions address specific unresolved inputs.
{
 const s=slide(6,'A cheaper build still needs\ncommercial and delivery safeguards');
 table(s,[['Risk','Case evidence','Required response'],
  ['Demand and price','Opening adoption and $65 ARPU are unverified','Price-test demand and distinguish migrated accounts'],
  ['Capacity','Bull demand exceeds the assumed line ceiling','Engineer traffic, coverage and added capacity costs'],
  ['Cost and timing','No supplier bids; delay reduces the recovery window','Quote reuse and sharing; stage commitments'],
  ['Asset life','Five-year screen omits unsupported later value','Appraise lifecycle cash flows and reinvestment']
 ],72,222,1136,365,[222,418,496],22);
 text(s,'A $27.5M network design is a modeled alternative to quote, not a demonstrated procurement outcome.',72,615,1136,55,23);
 note(s,'Source: assumptions_and_limitations.md, investment_alternatives.csv and strategy report. A modeled network CAPEX reduction to CAD 27.5M holds operating benefits and capacity constant, an optimistic assumption requiring reengineering and quotes. Source S3: '+sources.ised+'. Source S4: '+sources.update+' (May 2026; September page notes) includes proposed siting amendments, not treated here as enacted requirements. The case establishes neither permit compliance nor operational feasibility.');
}
// 7. Conditional rollout, with explicit owners and decision gates.
{
 const s=slide(7,'A staged approval can test the case\nbefore wider construction');
 table(s,[['Stage','Indicative timing','Owner and decision gate'],
  ['Feasibility','Months 0-3','Commercial / Strategy: price-tested demand'],
  ['Sharing and design','Months 3-5','Engineering / Finance: positive NPV and valid capacity'],
  ['Procurement','Months 5-7','Procurement / Regulatory: quotes and clearances'],
  ['Pilot deployment','Months 7-10','Engineering / PMO: coverage and conversion tests'],
  ['Launch and tracking','Month 10 onward','Operations / Finance: value tracking before expansion']
 ],72,213,1136,342,[240,220,676],21);
 text(s,'Approval follows positive revised NPV, verified demand and engineered capacity.',72,585,1136,50,25,true);
 text(s,'Track subscribers, ARPU, acquisition cost, CAPEX/OPEX, service quality and realized cash flow.',72,638,1136,33,20,false,grey);
 note(s,'Status: proposed conditional roadmap, not an approved rollout. Timelines are illustrative from a future diligence mandate, not fixed calendar commitments. Full stage definitions and 12 KPI formulas, sources, reporting frequencies, owners and illustrative triggers are in implementation_roadmap.md and kpi_framework.csv. No full build enters procurement under the current negative-NPV case.');
}

for(const [i,s]of deck.slides.items.entries()){
 const png=await deck.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
 const layout=await s.export({format:'layout'});await fs.writeFile(path.join(build,`slide-${i+1}.layout.json`),await layout.text());
}
const candidate=path.join(build,'candidate.pptx');await(await PresentationFile.exportPptx(deck)).save(candidate);
const skill=process.env.PRESENTATION_SKILL_DIR || path.join(os.homedir(),'.codex/plugins/cache/openai-primary-runtime/presentations/26.1119.11507/skills/presentations');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const final=path.join(out,'executive_recommendation.pptx');
// The finalizer does not overwrite previous revisions. Keep revisions private.
try{await fs.rename(final,path.join(build,`previous-${Date.now()}.pptx`));}catch(error){if(error.code!=='ENOENT')throw error;}
try{await fs.rename(path.join(build,'validation.json'),path.join(build,`previous-validation-${Date.now()}.json`));}catch(error){if(error.code!=='ENOENT')throw error;}
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:process.env.CODEX_RUNTIME_PYTHON || path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',
   '--require-native-table-slide','3','--require-native-table-slide','6','--require-native-table-slide','7'],
 explicitTotalSlideCount:7,requiredNativeTableOwnerSlides:[3,6,7],requiredNativeChartOwnerSlides:[2,4,5],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},
 verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
for(const entry of await fs.readdir(root))if(entry.startsWith('.chart-data-'))await fs.rename(path.join(root,entry),path.join(build,entry));
console.log(JSON.stringify(result));
