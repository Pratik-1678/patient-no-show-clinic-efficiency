# Power BI Dashboard Specification — Patient No-Show & Clinic Efficiency Analysis

3 pages, built on the Phase 9 data model and Phase 10 DAX measures. All numbers referenced below are the real,
verified figures from Notebooks 01-05 and the SQL phase — used here to write the "Key Insights" text boxes so
they don't need to be retyped once the dashboard is live; just confirm they still match after you build it.

---

## Page 1 — Executive Overview

**Title:** Patient Attendance & Clinic Efficiency Overview

### KPI Cards (top row, 5 cards)
| Card | Measure |
|---|---|
| Total Appointments | `[Total Appointments]` |
| No-Show Rate | `[No-Show Rate]` |
| Show Rate | `[Show Rate]` |
| Total No-Shows | `[No-Shows]` |
| Avg Lead Time | `[Average Lead Time (Days)]` |

### Visuals
1. **Appointment Outcome (donut or bar)** — Legend: `no_show_flag` (recode 0/1 to "Attended"/"No-show" via the
   existing `no_show` text column, or use `Patient History Segment`-style SWITCH for a clean label) · Values:
   `[Total Appointments]`
2. **No-Show Trend by Month (line)** — Axis: `DimDate[year_month]` · Values: `[No-Show Rate]`. *Caveat to note
   on the visual itself: only ~6 weeks of appointment dates exist (Apr-Jun 2016), so this trend is short and
   shouldn't be read as a strong seasonal pattern.*
3. **No-Show Rate by Weekday (bar)** — Axis: `FactAppointments[appointment_weekday]` (or add via `DimDate` if
   preferred) · Values: `[No-Show Rate]` · **Filter:** exclude Saturday/Sunday or add a note — Saturday has only
   ~39 appointments (see Notebook 02)
4. **No-Show Rate by Age Group (bar)** — Axis: `age_group` · Values: `[No-Show Rate]`
5. **No-Show Rate by Reminder Status (bar)** — Axis: `sms_received` (labeled) sliced by `waiting_time_group` —
   use the controlled comparison from DAX Section 4, not the naive one
6. **Top Problematic Locations (bar)** — Axis: `DimLocation[neighbourhood]` · Values: `[No-Show Rate]` ·
   **Filters:** Top N = 10, AND `[Total Appointments] >= 100` (see DAX doc note on Top-N neighbourhoods)

### Slicers (top of page, apply to all visuals)
`DimDate[date]` (range) · `DimPatient[gender]` · `age_group` · `DimLocation[neighbourhood]` · `sms_received`

### Key Business Insights (text box, bottom of page)
> Roughly 1 in 5 appointments (20.2%) end in a no-show. No-show rate is highest among teens and young adults
> (26.1% and 23.8%) and falls steadily with age. Appointments booked 8+ days in advance are far more likely to
> be missed (30-33%) than same-day appointments (4.6%). SMS reminders, once compared within the same booking
> lead time, are associated with lower no-shows — the raw, unadjusted comparison is misleading (see Page 2).

---

## Page 2 — No-Show Drivers

**Title:** What Drives Patient No-Shows?

### Visuals
1. **No-show rate by lead-time bucket (bar or line)** — Axis: `waiting_time_group`, sorted `Same day → 31+
   days` (set a sort-by column if the alphabetical default sorts it wrong) · Values: `[No-Show Rate]`.
   **This should be the most visually prominent chart on the page** — it's the strongest validated driver
   (Cramér's V = 0.295, Notebook 03).
2. **No-show rate by age group (bar)** — same as Page 1, repeated here for the "drivers" narrative
3. **No-show rate by reminder status, sliced by lead-time bucket (clustered bar)** — Axis: `waiting_time_group`
   · Legend: SMS Received / No SMS · Values: `[No-Show Rate]`. This is the controlled comparison that resolves
   the confound — make sure this version is what's shown, not the naive unsliced one.
4. **No-show rate by weekday (bar)** — same as Page 1
5. **No-show rate by patient history (bar)** — Axis: `Patient History Segment` (the calculated column from DAX
   Section 6) · Values: `[No-Show Rate]`. Second-strongest validated driver (Cramér's V = 0.169).
6. **Location comparison (bar or map if lat/long is added later)** — Axis: `neighbourhood` · Values:
   `[No-Show Rate]` and `[Total Appointments]` · Filter: `[Total Appointments] >= 100`

### Slicers
Same as Page 1, plus `risk_segment` (from Phase 7)

### Page framing text
> Which factors are most associated with missed appointments? Lead time and patient history are the two
> strongest, statistically validated drivers (Notebook 03) — both should anchor any operational response.
> Gender and alcoholism showed no statistically significant relationship with attendance and are not included
> here as drivers.

---

## Page 3 — Clinic Efficiency & Action Plan

**Title:** Clinic Efficiency & Improvement Opportunities

### KPI Cards (top row)
| Card | Measure |
|---|---|
| Lost Capacity (Slots) | `[Lost Capacity (Slots)]` |
| Utilization Rate | `[Show Rate]` (framed as "booked-capacity utilization" — see Notebook 05 limitation note) |
| Scenario Recovery (20%) | `[Scenario Recoverable - 20% Reduction]` |
| Targeted Recovery (High Risk → Avg) | `[Targeted Recoverable (High Risk to Avg)]` |

### Visuals
1. **Lost capacity by lead-time bucket (bar)** — Axis: `waiting_time_group` · Values: `[No-Shows]`. Add a data
   label or secondary measure showing % of total lost capacity — this is where the "36% of volume but 57.1% of
   lost capacity" insight from Notebook 05 lives.
2. **Scenario recovery comparison (bar)** — Categories: "10% reduction", "20% reduction", "30% reduction",
   "Targeted: High Risk → avg" · Values: the four scenario measures from DAX Section 5. Clearly label this
   visual "Scenario estimates, not guaranteed outcomes" (small caption, per project rules).
3. **High-volume / high-no-show neighbourhoods (bar)** — same as Page 2's location visual, but filtered to just
   the 11 neighbourhoods identified in Notebook 05 (top-quartile volume AND above-average no-show rate)
4. **Impact vs Priority table** — a table visual, columns: Segment, Volume, No-Show Rate, Business Impact (lost
   appointments), Priority. Populate directly from the Notebook 05 "Section 5" table (Medium Risk / High Risk /
   Low Risk / lead-time buckets) — this can be built as a table visual with `risk_segment` and `waiting_time_group`
   both on rows (or two separate small tables if mixing grains gets awkward in Power BI).

### Recommended Actions (text box, bottom of page)
> - Prioritize reconfirmation calls for appointments booked 8+ days in advance — this group is 36% of volume
>   but 57% of lost capacity.
> - Use the risk segmentation (Phase 7) to target outreach: High Risk appointments (14.8% of volume) have a
>   38.9% no-show rate, nearly 2x the overall average.
> - Focus location-based effort on the 11 neighbourhoods that are both high-volume and above-average no-show
>   rate, led by ITARARÉ (26.3%).
> - Continue and consider expanding SMS reminders for long-lead-time bookings specifically — the controlled
>   comparison shows a real benefit once lead time is accounted for.
> - Even the Low Risk segment contributes real lost capacity (5,423 appointments) purely due to its size —
>   a baseline reminder program still has value clinic-wide, not just for flagged high-risk patients.

---

## General Notes for All Pages
- Use consistent colors: keep the same color for "No-show" (e.g. a warm/red tone) and "Attended"/"Show" (e.g. a
  cool/green tone) across every visual on every page, so the eye doesn't have to re-learn the legend per chart.
- Every "No-Show Rate" visual should use `DIVIDE`-based measures (already built this way in Phase 10) so blank
  filter combinations don't throw divide-by-zero errors when slicers narrow the data heavily.
- Small-sample caveats (Saturday weekday, low-volume neighbourhoods) should be visible on the page itself
  (a caption or filtered out), not just mentioned once in a notebook nobody sees again.
