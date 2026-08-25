# Power BI DAX Measures — Patient No-Show & Clinic Efficiency Analysis

**Note on verification:** I don't have Power BI Desktop available to actually run these, so unlike every
notebook/SQL/Excel deliverable so far, these formulas are **not execution-tested**. They're written carefully
against the exact table and column names from the Phase 9 data model (`FactAppointments`, `DimDate`,
`DimPatient`, `DimLocation`). If any formula throws an error when you paste it in, send me the exact error
message and I'll troubleshoot the specific table/column reference rather than guessing — this matches the
project rule to fix the exact problem, not hand you generic DAX.

## Measures vs. Calculated Columns — and why almost everything below is a measure

- A **calculated column** computes a value **per row**, stored physically in the table, evaluated at refresh time.
- A **measure** computes a value **dynamically**, based on whatever filter context a visual/slicer applies —
  never stored, always recalculated on the fly.

Nearly every KPI in this project (rates, sums, averages) should be a **measure** — that's what makes them
correctly recalculate when someone filters the dashboard by date, location, or age group. The only
**calculated column** in this project is `Patient History Segment` (Section 6) — it needs to inspect each row
individually (is *this row's* `prior_no_show_flag` blank, 0, or 1) to produce a label to filter or chart by,
which is what calculated columns are for.

---

## 1. Volume Measures

```dax
Total Appointments = COUNTROWS(FactAppointments)

Total Patients = DISTINCTCOUNT(FactAppointments[patient_id])

Show-Ups = CALCULATE([Total Appointments], FactAppointments[no_show_flag] = 0)

No-Shows = SUM(FactAppointments[no_show_flag])
```

## 2. Attendance Rate Measures

```dax
No-Show Rate = DIVIDE([No-Shows], [Total Appointments], 0)

Show Rate = DIVIDE([Show-Ups], [Total Appointments], 0)
```

*Using `DIVIDE(..., 0)` instead of `/` avoids divide-by-zero errors when a filter combination returns no rows
(e.g. a neighbourhood + date-range slicer combination with zero appointments) — this matters once slicers are
added on the dashboard pages.*

## 3. Lead Time Measures

```dax
Average Lead Time (Days) = AVERAGE(FactAppointments[lead_time_days])
```

*Note: `lead_time_days` was already computed in Python (Notebook 01) — this measure just averages the
precomputed column, consistent with the Phase 9 decision not to relate `scheduled_day` to `DimDate`.*

## 4. Reminder (SMS) Measures

```dax
Reminder Coverage % = DIVIDE(SUM(FactAppointments[sms_received]), [Total Appointments], 0)

No-Show Rate - SMS Received =
CALCULATE([No-Show Rate], FactAppointments[sms_received] = 1)

No-Show Rate - No SMS =
CALCULATE([No-Show Rate], FactAppointments[sms_received] = 0)
```

**Reminder these are set up to be sliced by `waiting_time_group`** (put `waiting_time_group` on an axis, these
two measures as values) — that reproduces the *controlled* comparison from Notebook 02/03 that resolves the SMS
confound, rather than the naive comparison. Don't present the naive (unsliced) version as the headline number —
see the caveat notes in Notebooks 02, 03, and SQL query 2.5/2.6.

## 5. Capacity & Scenario Measures

```dax
Lost Capacity (Slots) = [No-Shows]

Scenario Recoverable - 10% Reduction = [Lost Capacity (Slots)] * 0.1

Scenario Recoverable - 20% Reduction = [Lost Capacity (Slots)] * 0.2

Scenario Recoverable - 30% Reduction = [Lost Capacity (Slots)] * 0.3
```

**Targeted scenario (High Risk segment brought down to the overall average rate)** — matches the Notebook 05
calculation:

```dax
Overall No-Show Rate (Unfiltered) =
CALCULATE([No-Show Rate], ALL(FactAppointments[risk_segment]))

High Risk Volume =
CALCULATE([Total Appointments], FactAppointments[risk_segment] = "High Risk")

High Risk No-Shows =
CALCULATE([No-Shows], FactAppointments[risk_segment] = "High Risk")

Targeted Recoverable (High Risk to Avg) =
[High Risk No-Shows] - ([High Risk Volume] * [Overall No-Show Rate (Unfiltered)])
```

*`ALL(FactAppointments[risk_segment])` is used deliberately so this measure still reflects the true overall
average even if the visual it's used in has a risk-segment slicer or filter applied to it — without `ALL`, the
measure would use whatever segment filter is active, which isn't what "overall average" should mean.*

## 6. Segmentation Measures (Phase 7)

```dax
% Appointments - High Risk =
DIVIDE(
    CALCULATE([Total Appointments], FactAppointments[risk_segment] = "High Risk"),
    [Total Appointments], 0
)

No-Show Rate - High Risk =
CALCULATE([No-Show Rate], FactAppointments[risk_segment] = "High Risk")

No-Show Rate - Medium Risk =
CALCULATE([No-Show Rate], FactAppointments[risk_segment] = "Medium Risk")

No-Show Rate - Low Risk =
CALCULATE([No-Show Rate], FactAppointments[risk_segment] = "Low Risk")
```

## 7. Patient History Measures (+ 1 Calculated Column)

**Calculated column** (needed because it inspects each row's own `prior_no_show_flag` value to build a label —
this is the one column in the whole model that should NOT be a measure):

```dax
Patient History Segment =
SWITCH(
    TRUE(),
    ISBLANK(FactAppointments[prior_no_show_flag]), "No prior appointment (first visit)",
    FactAppointments[prior_no_show_flag] = 1, "Previous appointment was a no-show",
    "Previous appointment attended"
)
```

Once that column exists, put it on a chart axis with `[No-Show Rate]` as the value — no extra measures needed,
it aggregates automatically by whichever category is on the axis.

## 8. Date Intelligence

```dax
Appointments - Prior Month =
CALCULATE([Total Appointments], DATEADD(DimDate[date], -1, MONTH))

No-Show Rate - Prior Month =
CALCULATE([No-Show Rate], DATEADD(DimDate[date], -1, MONTH))
```

*These require `DimDate` to be marked as a Date Table (Phase 9, Step 2) to work correctly. Given the dataset
only spans ~6 weeks of actual appointment dates (late April to early June 2016), month-over-month comparisons
will have limited statistical value here — included for completeness/technique demonstration, with that caveat
noted on the dashboard itself rather than presented as a robust trend.*

---

## A Note on Top-N Neighbourhood Rankings

Rather than writing complex DAX to replicate the "top 10 high-volume, high-no-show neighbourhoods" logic from
SQL query 2.13 (which used `NTILE`), the simpler and more robust approach in Power BI is to build the bar chart
with `neighbourhood` on the axis and `[No-Show Rate]` as the value, then use the visual's built-in **Filter →
Top N** pane, combined with a separate visual-level filter of `[Total Appointments] >= 100`. This reproduces the
same "don't rank tiny samples" logic without a fragile DAX formula trying to compute quartiles across filter
context — a good example of choosing the simpler, more maintainable tool for the job rather than DAX for its
own sake.
