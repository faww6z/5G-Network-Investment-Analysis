"""Run from the repository root: python analysis/run_analysis.py.

The workbook is a separately calculated model. Pass --validate-excel after its
build to reconcile every principal annual cash-flow item and investment metric.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".build/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns
from finance import ROOT, evaluate, find_threshold, load_assumptions

INK, LIME, PAPER, GREY, RED = "#151515", "#D8FB50", "#FAFAF6", "#777D72", "#A74735"
COLORS = {"Bear":RED,"Base":INK,"Bull":"#749C25"}


def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
        "axes.titlesize":17,"axes.titleweight":"bold","axes.labelsize":11,
        "figure.facecolor":PAPER,"axes.facecolor":PAPER,"text.color":INK,
        "axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
        "axes.spines.top":False,"axes.spines.right":False,
        "axes.spines.left":False,"axes.edgecolor":"#D2D4CB",
        "grid.color":"#E4E6DD","svg.fonttype":"none","savefig.dpi":180})


def save(fig, name):
    out=ROOT/"outputs/charts";out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/f"{name}.png",bbox_inches="tight",facecolor=PAPER)
    fig.savefig(out/f"{name}.svg",bbox_inches="tight",facecolor=PAPER)
    plt.close(fig)


def monte_carlo(a, size=5000, seed=20261121):
    """Independent illustrative triangular priors, not empirical success odds."""
    rng=np.random.default_rng(seed)
    growth=rng.triangular(.05,.15,.25,size)
    arpu=rng.triangular(55,65,70,size)
    capex=rng.triangular(45e6,50e6,60e6,size)
    cost_multiple=rng.triangular(.90,1,1.15,size)
    share=rng.triangular(.70,.85,1,size)
    opening=a["year1_customers"]/(1+growth/2)
    acquisition=opening*a["cac"]
    npv=-capex-acquisition
    nol=acquisition.copy();nwc=np.zeros(size);prior_maintenance=np.zeros(size)
    for year in range(1,6):
        average=a["year1_customers"]*(1+growth)**(year-1)
        closing=2*average-opening
        gross_adds=closing-opening+average*a["annual_churn"]
        revenue=average*arpu*12*share
        opex=a["initial_opex"]*cost_multiple*(1+a["opex_growth"])**(year-1)
        maintenance=capex*a["maintenance_rate"]*(1+a["opex_growth"])**(year-1)
        depreciation=(capex+prior_maintenance)/a["depreciation_life"]
        ebitda=revenue-opex-gross_adds*a["cac"]
        ebit=ebitda-depreciation
        taxable=np.maximum(0,ebit-np.minimum(nol,np.maximum(0,ebit)))
        tax=taxable*a["tax_rate"]
        nol=np.maximum(0,nol-ebit)
        next_nwc=revenue*a["nwc_rate"]
        cash=ebitda-tax-(next_nwc-nwc)-maintenance
        npv+=cash/(1+a["discount_rate"])**year
        opening,nwc=closing,next_nwc
        prior_maintenance+=maintenance
    return pd.DataFrame(dict(growth=growth,arpu=arpu,capex=capex,
        opex_multiplier=cost_multiple,incremental_share=share,npv=npv))


def validate_excel(a):
    capture=ROOT/"outputs/excel_validation.json"
    if not capture.exists():
        raise FileNotFoundError("Build the workbook before requesting Excel reconciliation")
    actual=json.loads(capture.read_text())
    checks=[]
    for name,g in [("Bear",a["bear_growth"]),("Base",a["base_growth"]),("Bull",a["bull_growth"])]:
        expected=evaluate(a,g)
        for key in ["npv","irr","roi","initial_outflow","tco","cumulative_revenue","cumulative_net_cash"]:
            x,y=actual[name]["metrics"][key],expected["metrics"][key]
            tolerance=1e-8 if key in ("irr","roi") else .01
            assert abs(x-y)<tolerance,(name,key,x,y)
            checks.append(dict(scenario=name,metric=key,excel=x,python=y,difference=x-y,tolerance=tolerance))
        for key in ["payback","discounted_payback"]:
            x,y=actual[name]["metrics"][key],expected["metrics"][key]
            assert (x is None and y is None) or (x is not None and y is not None and abs(x-y)<1e-8),(name,key,x,y)
            checks.append(dict(scenario=name,metric=key,excel=x,python=y,difference=0 if x is None else x-y,tolerance=1e-8))
        for key in ["average_customers","opening_customers","closing_customers","gross_additions",
                    "revenue","network_opex","acquisition_cost","depreciation","cash_tax",
                    "closing_nol","delta_nwc","capex","fcf","discounted_fcf"]:
            x=np.asarray(actual[name]["forecast"][key],dtype=float)
            y=expected["forecast"][key].to_numpy()
            np.testing.assert_allclose(x,y,rtol=0,atol=.01,err_msg=f"{name}: {key}")
            for year,(v,w) in enumerate(zip(x,y)):
                checks.append(dict(scenario=name,metric=f"{key}_year_{year}",excel=v,python=w,difference=v-w,tolerance=.01))
    grid=pd.DataFrame(actual["sensitivity"])
    for row in grid.itertuples():
        expected=evaluate(dict(a,arpu=float(row.arpu)),float(row.growth))["metrics"]["npv"]
        assert abs(row.npv-expected)<.01,("sensitivity",row,expected)
    pd.DataFrame(checks).to_csv(ROOT/"outputs/excel_python_reconciliation.csv",index=False)
    summary=dict(status="passed",principal_checks=len(checks),sensitivity_checks=len(grid),
        maximum_absolute_difference=float(max(abs(c["difference"]) for c in checks)),
        scope="Artifact Tool calculated Excel formulas independently of Python; native Excel desktop was not used")
    (ROOT/"outputs/validation_summary.json").write_text(json.dumps(summary,indent=2))
    return summary


def run(validate=False):
    out=ROOT/"outputs";out.mkdir(exist_ok=True)
    a=load_assumptions();style()
    cases={name:evaluate(a,g) for name,g in [("Bear",a["bear_growth"]),("Base",a["base_growth"]),("Bull",a["bull_growth"])]}
    simple=evaluate(a,expanded=False);base=cases["Base"];f=base["forecast"]
    scenario_rows=[]
    for name,result in cases.items():
        result["forecast"].to_csv(out/f"{name.lower()}_forecast.csv",index=False)
        row=dict(scenario=name,**result["metrics"])
        row["capacity_feasible"]=row["year5_capacity_utilization"]<=1
        row["recommendation"]="Defer / modify" if row["npv"]<=0 else "Conditional financial approval"
        scenario_rows.append(row)
    summary=pd.DataFrame(scenario_rows);summary.to_csv(out/"scenario_summary.csv",index=False)
    thresholds={key:find_threshold(a,key,*limits) for key,limits in {
        "arpu":(20,150),"year1_customers":(1000,100000),
        "initial_capex":(1e6,100e6),"incremental_share":(.1,1)}.items()}
    thresholds["terminal_cash"]=max(0,-base["metrics"]["npv"])*(1+a["discount_rate"])**5
    demand_case=evaluate(dict(a,year1_customers=thresholds["year1_customers"]))
    thresholds["demand_threshold_closing_customers"]=demand_case["metrics"]["year5_closing_customers"]
    thresholds["demand_threshold_capacity_feasible"]=demand_case["metrics"]["year5_capacity_utilization"]<=1
    growths=np.arange(0,.301,.05);arpus=np.arange(50,81,5)
    sensitivity=pd.DataFrame([[evaluate(dict(a,arpu=float(price)),float(g))["metrics"]["npv"] for price in arpus] for g in growths],index=growths,columns=arpus)
    sensitivity.to_csv(out/"npv_sensitivity.csv",index_label="net_customer_growth")
    tornado=[]
    for key,label,lo,hi in [("arpu","Monthly ARPU",58.5,71.5),
        ("initial_capex","Initial network CAPEX",45e6,55e6),
        ("initial_opex","Year 1 network OPEX",7.2e6,8.8e6),
        ("base_growth","Net subscriber growth",.10,.20),
        ("discount_rate","Discount rate",.08,.12),
        ("incremental_share","Incremental revenue share",.75,.95),
        ("annual_churn","Annual cancellation intensity",.08,.16),
        ("cac","Acquisition cost",100,200)]:
        values=[evaluate(dict(a,**{key:x}))["metrics"]["npv"] for x in [lo,hi]]
        tornado.append(dict(key=key,driver=label,low_input=lo,high_input=hi,
            low_input_npv=values[0],high_input_npv=values[1],minimum_npv=min(values),maximum_npv=max(values)))
    tornado=pd.DataFrame(tornado).sort_values("maximum_npv",ascending=False)
    tornado.to_csv(out/"tornado_sensitivity.csv",index=False)
    alternatives={
        "Network CAPEX reduced to CAD 27.5M":evaluate(dict(a,initial_capex=27.5e6))["metrics"],
        "Same design with 10% CAPEX overrun":evaluate(dict(a,initial_capex=55e6))["metrics"],
        "One-year launch delay within fixed window":evaluate(a,delay_years=1)["metrics"],
        "All subscription revenue incremental":evaluate(dict(a,incremental_share=1))["metrics"],
        "CAD 25M net cash residual in Year 5":evaluate(dict(a,terminal_cash=25e6))["metrics"],
    }
    pd.DataFrame([dict(alternative=k,**v) for k,v in alternatives.items()]).to_csv(out/"investment_alternatives.csv",index=False)
    draws=monte_carlo(a);draws.to_csv(out/"monte_carlo_draws.csv",index=False)
    simulation=dict(draws=len(draws),seed=20261121,positive_npv_share=float((draws.npv>0).mean()),
        p5=float(draws.npv.quantile(.05)),median=float(draws.npv.median()),p95=float(draws.npv.quantile(.95)),
        caveat="Conditional on independent illustrative triangular priors; not empirical success probabilities; capacity expansion costs omitted")
    results=dict(as_of="2026-11-21",assumptions=a,base=base["metrics"],simple=simple["metrics"],
        scenarios={k:v["metrics"] for k,v in cases.items()},thresholds=thresholds,
        alternatives=alternatives,simulation=simulation,
        forecasts={k:v["forecast"].to_dict(orient="records") for k,v in cases.items()})
    (out/"results.json").write_text(json.dumps(results,indent=2,allow_nan=False))

    fig,ax=plt.subplots(figsize=(9,4.4))
    for name,result in cases.items():
        d=result["forecast"].query("year>0");ax.plot(d.year,d.revenue/1e6,label=name,color=COLORS[name],lw=2.6,marker="o",ms=4)
    ax.set(title="Incremental revenue depends on adoption",xlabel="Operating year",ylabel="Annual incremental revenue (CAD millions)",xticks=range(1,6));ax.legend(frameon=False,ncol=3);ax.grid(axis="y");save(fig,"revenue_forecast")
    fig,ax=plt.subplots(figsize=(9,4.4));ax.bar(f.year,f.fcf/1e6,color=[INK]+[LIME]*5,edgecolor=INK,lw=.6)
    ax.axhline(0,color=INK,lw=.8);ax.set(title="Upfront cash outflow is CAD 53.49 million",xlabel="Year from initial investment",ylabel="Unlevered free cash flow (CAD millions)",xticks=range(6));save(fig,"annual_cash_flow")
    fig,ax=plt.subplots(figsize=(9,4.4));ax.plot(f.year,f.cumulative_fcf/1e6,lw=2.8,color=INK,marker="o",label="Undiscounted")
    ax.plot(f.year,f.cumulative_discounted_fcf/1e6,lw=2.5,color=RED,ls="--",marker="o",label="Discounted at 10%")
    ax.axhline(0,color=GREY,lw=.8);ax.set(title="The base case does not recover its cash within five years",xlabel="Year from initial investment",ylabel="Cumulative cash flow (CAD millions)",xticks=range(6));ax.legend(frameon=False);save(fig,"cumulative_cash_flow")
    fig,ax=plt.subplots(figsize=(9,5));sns.heatmap(sensitivity/1e6,annot=True,fmt=".1f",center=0,cmap="RdYlGn",linewidths=.5,
        xticklabels=[f"${x:.0f}" for x in arpus],yticklabels=[f"{g:.0%}" for g in growths],cbar_kws={"label":"NPV (CAD millions)"},ax=ax)
    ax.set(title="Price and adoption must improve together",xlabel="Monthly ARPU (CAD)",ylabel="Annual net subscriber growth");save(fig,"npv_sensitivity")
    fig,ax=plt.subplots(figsize=(9,4.4));ax.bar(summary.scenario,summary.npv/1e6,color=[COLORS[x] for x in summary.scenario]);ax.axhline(0,color=INK,lw=.8)
    for i,row in enumerate(summary.itertuples()):ax.text(i,row.npv/1e6+.7,f"${row.npv/1e6:.1f}M",ha="center",va="bottom",weight="bold")
    ax.set(title="All three adoption scenarios fail the 10% hurdle",ylabel="Five-year NPV (CAD millions)");ax.text(.99,.02,"Bull case exceeds assumed capacity",transform=ax.transAxes,ha="right",fontsize=9,color=RED);save(fig,"scenario_comparison")
    fig,ax=plt.subplots(figsize=(9,5));t=tornado.sort_values("maximum_npv");baseline=base["metrics"]["npv"]/1e6
    ax.barh(t.driver,(t.maximum_npv-t.minimum_npv)/1e6,left=t.minimum_npv/1e6,color=LIME,edgecolor=INK,lw=.7)
    ax.axvline(baseline,color=RED,ls="--",label=f"Base NPV ${baseline:.1f}M")
    ax.set(title="Revenue capture and capital spending dominate tested risks",xlabel="Five-year NPV (CAD millions)");ax.legend(frameon=False,loc="lower right");save(fig,"tornado")
    fig,ax=plt.subplots(figsize=(9,4.4));ax.hist(draws.npv/1e6,bins=45,color=LIME,edgecolor=INK,lw=.4);ax.axvline(0,color=RED,lw=1.5)
    ax.set(title="Illustrative uncertainty leaves a substantial downside",xlabel="Five-year NPV (CAD millions)",ylabel="Simulated draws")
    ax.text(.02,.96,f"5,000 draws. Positive NPV share {simulation['positive_npv_share']:.1%}\nConditional on chosen priors; not observed success odds.",transform=ax.transAxes,va="top",fontsize=9);save(fig,"monte_carlo_npv")
    fig,ax=plt.subplots(figsize=(9,4.4));ax.barh(["First Nations reserves","Rural Canada","Canada"],[52.2,75.2,94.3],color=[GREY,INK,LIME],edgecolor=INK,lw=.6)
    ax.set(xlim=(0,100),title="5G population coverage still differs across communities",xlabel="Population with access to 5G (%) in 2024")
    for i,x in enumerate([52.2,75.2,94.3]):ax.text(x-2,i,f"{x:.1f}%",va="center",ha="right",color="white" if i<2 else INK,weight="bold")
    ax.text(0,-.20,"Source: CRTC, 2026 CTMR, Figure 51. National context, not a local demand estimate.",transform=ax.transAxes,fontsize=8);save(fig,"market_coverage")
    interpretations={
        "revenue_forecast":"The base case reaches CAD 28.99M incremental revenue in Year 5. Bull demand requires added capacity.",
        "annual_cash_flow":"Year 0 includes CAD 50M network CAPEX plus prelaunch acquisition spending. Positive operating cash flows do not guarantee positive NPV.",
        "cumulative_cash_flow":"Both cumulative series remain negative after five years in the expanded base case.",
        "npv_sensitivity":"Each combination changes only ARPU and net growth. High-growth cells may exceed the 60,000-line planning capacity.",
        "scenario_comparison":"Bear, base and bull NPVs are all negative. The bull case also violates the capacity assumption.",
        "tornado":"Driver ranges differ, so bar widths rank these chosen stresses rather than universal importance. Exact endpoints are in tornado_sensitivity.csv.",
        "monte_carlo_npv":"The simulated share is conditional on independent illustrative priors, not a probability estimated from observed projects.",
        "market_coverage":"2024 coverage from a report published in 2026 indicates unequal access. Coverage does not establish commercial demand for this fictional footprint.",
    }
    (out/"chart_interpretations.json").write_text(json.dumps(interpretations,indent=2))
    if validate: print(json.dumps(validate_excel(a),indent=2))
    print(json.dumps({"base_npv":base["metrics"]["npv"],"thresholds":thresholds,"simulation":simulation},indent=2))
    return results


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--validate-excel",action="store_true")
    run(parser.parse_args().validate_excel)
