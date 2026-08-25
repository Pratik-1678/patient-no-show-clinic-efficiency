# Executive Summary
## Patient No-Show & Clinic Efficiency Analysis

### Business Problem
Clinics lose staff time, appointment slots, and revenue every time a scheduled patient fails to attend without
warning. Unlike a cancellation, a no-show gives no advance notice, so the slot usually cannot be backfilled.
This project asks: how large is this problem, which factors actually predict a no-show, how much appointment
capacity is being lost, and what specific, evidence-based actions could a clinic take to reduce it?

### Dataset
The public Kaggle "Medical Appointment No Shows" dataset — 110,527 real appointment records from a Brazilian
public healthcare system (2015-2016), covering patient demographics, scheduling details, medical conditions,
and whether an SMS reminder was sent. After cleaning (removing 6 records with invalid ages or impossible
negative lead times), the working dataset is **110,521 appointments** across **62,298 unique patients**.

### Methodology
Excel was used for an initial structural audit; Python (pandas) for cleaning, feature engineering, exploratory
analysis, and statistical validation (chi-square tests + Cramér's V effect sizes); MySQL for business-facing
queries using CTEs and window functions; Power BI for an executive dashboard (data model, DAX measures, and
3-page layout spec); and a working Streamlit app for an interactive, code-based alternative dashboard. Every
number in this project was computed from the actual data and cross-checked across at least two tools — nothing
was estimated or assumed.

### Key Findings
- **Overall no-show rate: 20.19%** — roughly 1 in 5 booked appointments goes unused.
- **Lead time is the strongest predictor.** No-show rate rises from 4.6% (same-day) to 33.0% (31+ days ahead) —
  a ~7x increase. Appointments booked 8+ days out are 36% of volume but **57.1% of all lost capacity**.
- **Patient history is the second-strongest predictor.** A prior no-show nearly doubles the odds of the next
  appointment also being missed (35.2% vs. 18.0%).
- **A simple 3-rule risk score cleanly separates risk levels:** 11.6% (Low Risk) vs. 38.9% (High Risk) no-show
  rate — no machine learning required.
- **SMS reminders likely help, but a naive comparison says the opposite.** Reminders are sent disproportionately
  to long-lead-time patients, who are already higher-risk; once that's controlled for, reminders show a real,
  consistent benefit. Cutting the program based on the naive number would have been the wrong call.
- **Lost capacity is geographically concentrated** in 11 specific neighbourhoods that are both high-volume and
  above-average no-show rate, led by ITARARÉ (26.3%).
- **Gender and alcoholism were formally ruled out** as drivers (no statistically significant relationship) —
  recommendations avoid targeting these factors.

### Business Recommendations
1. Add proactive reconfirmation calls for appointments booked 8+ days in advance.
2. Flag patients with 2+ prior no-shows for personal outreach rather than automated reminders alone.
3. Operationalize the 3-rule risk score so reception can prioritize daily outreach.
4. Continue and expand SMS reminders specifically for long-lead-time bookings.
5. Target location-based outreach at the 11 identified high-volume, high-no-show neighbourhoods.

### Expected Impact
Scenario modeling (not a guarantee — no controlled intervention has been run yet) suggests a targeted
intervention on the High Risk segment alone could recover an estimated **3,064 appointments**; a broader 20%
reduction in no-shows across the board would recover **4,463 appointments**. These are directional estimates
meant to size the opportunity, not promises of a specific outcome.

### Technology Stack
Excel · Python (pandas, matplotlib, seaborn, scipy) · MySQL · Power BI (data model + DAX) · Streamlit (plotly) · Jupyter · Git/GitHub
