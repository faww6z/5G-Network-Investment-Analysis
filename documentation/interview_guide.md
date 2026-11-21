# Resume and interview preparation

Use these only after reviewing the model and being able to explain the work. Do not describe this as employment, a commissioned Bell engagement, or a realized commercial outcome.

## Two resume bullets

- Developed an Excel and Python investment analysis for a hypothetical CAD $50M Canadian 5G expansion, modeling incremental cash flows, NPV, IRR and payback across three adoption scenarios.
- Evaluated financial sensitivities and break-even conditions, reconciled 279 financial checks and 49 sensitivity combinations, and recommended a revised deployment after identifying a CAD $18.5M base-case NPV shortfall and capacity constraints.

## A 60-second explanation

"I built a hypothetical investment case asking whether a Canadian telecom provider should spend $50 million on regional 5G expansion. I started with customers, monthly revenue per user and operating costs, then expanded the model to separate new revenue from transferred revenue and include acquisition costs, taxes, maintenance capital and working capital. I calculated the financial results in Excel and independently checked them in Python. The simplified model looked attractive, but the expanded base case had an NPV of negative $18.5 million at a 10% discount rate. Even the high-growth case remained negative and exceeded the assumed network capacity. I recommended deferring the full build, validating demand and investigating infrastructure sharing. The key lesson was that growing revenue and positive operating cash flow do not necessarily justify the initial investment."

## A three-minute walkthrough

**0:00-0:30 - The decision.** Explain the $50M network investment and five-year required-return test. Establish immediately that this is an independent fictional portfolio case.

**0:30-1:10 - The economic model.** Average active subscribers drive annual revenue. A linear within-year path reconciles opening and closing balances. Growth already incorporates churn, while cancellation intensity drives replacement acquisition spending. Only 85% of gross revenue is credited as incremental. Initial network spending and prelaunch acquisition occur at Year 0.

**1:10-1:50 - The result.** The expanded base case has $111.75M incremental five-year revenue but an initial cash outflow of $53.49M. Taxes, acquisition, working capital and maintenance reduce cash available to recover the investment. NPV is -$18.50M, IRR -3.20%, and neither payback measure occurs within five years. Python and Excel match independently.

**1:50-2:25 - Uncertainty and constraints.** Growth-only scenarios produce NPVs from -$26.90M to -$8.65M. The high case needs 67,817 closing lines against a 60,000-line proxy. Break-even demand also breaches capacity, so higher demand is not a costless solution. At unchanged operations, CAPEX would need to fall to about $31.02M for NPV to reach zero.

**2:25-3:00 - The recommendation and limits.** Recommend deferring the current build and seeking sharing/reuse quotes with measured demand and an engineered capacity plan. Explain that five years is shorter than the assumed asset life: the screen does not prove lifetime value is negative. A supported lifecycle valuation could change the decision. The roadmap uses staged approvals and monitors subscriber conversion, ARPU, acquisition cost, spending, service quality and revised cash returns.

## Five technical questions and answer anchors

1. **Why does Excel NPV exclude Year 0 from its value arguments?** Excel discounts the first supplied periodic value by one period. Add the immediate initial outflow separately. Including it in the value range shifts every cash flow's timing.
2. **Why use average active subscribers rather than year-end subscribers?** Revenue accrues while subscribers are active. Year-end balances can overstate a growing year's billable base. The model explicitly reconciles the annual average to opening and closing subscribers.
3. **How do you avoid double-counting churn?** Subscriber growth is already net. Cancellations add replacement acquisition costs and gross-addition requirements; they do not reduce the net growth forecast again.
4. **How do cash ROI, IRR and payback differ?** Cash ROI is cumulative net cash divided by initial cash outflow. IRR is an annual discount rate. Payback measures cash-recovery timing and ignores value after recovery; discounted payback incorporates the hurdle rate.
5. **Could zero terminal value bias the recommendation?** Yes. A five-year screen may omit material later cash flows from infrastructure with a longer life. Approximately $29.80M of net Year 5 value would close this model's NPV gap, but it needs evidence and cannot be inferred from accounting book value. The appropriate action is a lifecycle appraisal alongside near-term cash discipline.

## Self-check before an interview

Recalculate Year 1 gross revenue by hand; explain why incremental revenue is lower; trace Year 0 acquisition into tax losses and cash flow; explain the difference between maintenance expense and maintenance CAPEX; and demonstrate that changing Excel's case selector updates the same model. Be candid about the fictional market size, assumed capacity, simplified tax treatment and uncalibrated simulation.
