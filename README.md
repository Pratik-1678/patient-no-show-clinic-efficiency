# Patient No-Show & Clinic Efficiency Analysis

End-to-end analytics project identifying why patients miss scheduled clinic appointments, how much appointment
capacity is lost as a result, and what operational actions could recover it — built with Excel, Python, MySQL,
Power BI, and Streamlit.

## Business Problem

Clinics lose staff time, appointment slots, and revenue every time a scheduled patient fails to show up.
Unlike a cancellation, a no-show gives no advance warning, so the slot usually can't be backfilled. This
project answers: how large is the problem, which factors actually predict a no-show, how much capacity is
being lost, and what specific, evidence-based actions could reduce it?

## Objective

Move beyond a simple "% of no-shows" report to a full diagnostic: validate which factors genuinely predict
attendance (not just correlate with it), build a usable risk-prioritization tool, and quantify the operational
impact in terms clinic management can act on.

## Dataset

[Kaggle — Medical Appointment No Shows](https://www.kaggle.com/datasets/joniarroba/noshowappointments):
110,527 real appointment records from a Brazilian public healthcare system (Nov 2015 – Jun 2016). One row =
one scheduled appointment. After cleaning (6 records removed — 1 invalid age, 5 impossible negative lead
times), the working dataset is **110,521 appointments across 62,298 patients**.

## Key Questions

- How large is the no-show problem, and which patient/scheduling factors actually predict it (not just
  correlate with it)?
- How much appointment capacity is lost, and where does it concentrate?
- Can a simple, explainable rule (not a black-box model) reliably flag high-risk appointments?
- Do SMS reminders work, and is the obvious answer to that question actually correct?

## Tools Used

| Tool | Purpose |
|---|---|
| Excel | Initial data audit, validation checks, formula-driven KPI summary |
| Python (pandas, matplotlib, seaborn, scipy) | Cleaning, feature engineering, EDA, statistical validation |
| MySQL | Business queries — `GROUP BY`/`HAVING`, CTEs, window functions |
| Power BI | Star-schema data model, DAX measures, 3-page executive dashboard |
| Streamlit + Plotly | Interactive, filterable alternative dashboard |

## Data Cleaning

- Standardized column names, fixed source typos (`Hipertension` → `hypertension`, `Handcap` → `handicap`)
- Removed 1 record with an invalid age (`-1`) and 5 records with a negative lead time (scheduled after the
  appointment date — a logical impossibility)
- Verified zero duplicate rows and zero missing values
- Engineered `lead_time_days`, `waiting_time_group`, `age_group`, `appointment_weekday`, `prior_no_show`,
  `chronic_condition_count`, and a rule-based `risk_score` / `risk_segment`
- Deliberately did **not** create an appointment time-of-day feature — the source data has no time component
  for the appointment date, only for the booking timestamp

Full detail: `notebooks/01_data_cleaning.ipynb`, `docs/data_dictionary.md`

## SQL Analysis

`sql/clinic_analysis.sql` — 23 queries against a live MySQL `clinic_analytics` database, including:
- No-show rate broken down by age, gender, weekday, neighbourhood, lead-time bucket, and reminder status
- A CTE + window functions (`ROW_NUMBER`, `LAG`) query linking each appointment to whether the *same patient's*
  previous appointment was a no-show
- A CTE + `NTILE` query identifying neighbourhoods that are both high-volume and above-average no-show rate
- Scenario-based recoverable-capacity queries (10% / 20% / 30% no-show reduction)

## Python Analysis

Five notebooks, each with a specific job:

| Notebook | Purpose |
|---|---|
| `01_data_cleaning.ipynb` | Structural cleaning + feature engineering |
| `02_exploratory_analysis.ipynb` | EDA across 9 business dimensions (age, gender, lead time, reminders, weekday, location, patient history, medical conditions) |
| `03_statistical_validation.ipynb` | Chi-square tests + Cramér's V effect sizes to separate real drivers from noise |
| `04_business_segmentation.ipynb` | 3-rule risk score (Low / Medium / High) |
| `05_clinic_efficiency.ipynb` | Utilization, lost capacity, recovery scenarios, impact/priority ranking |

## Power BI Dashboard

Star schema (`FactAppointments` + `DimDate` / `DimPatient` / `DimLocation`), documented in
`docs/power_bi_data_model.md`, with DAX measures in `docs/power_bi_dax_measures.md` and the full 3-page layout
spec in `docs/power_bi_dashboard_spec.md`:

1. **Executive Overview** — top-line KPIs, attendance trend, weekday/age breakdowns
2. **No-Show Drivers** — lead time, the controlled (deconfounded) reminder comparison, patient history
3. **Clinic Efficiency & Action Plan** — lost capacity, recovery scenarios, impact/priority table

*(See `outputs/screenshots/` for dashboard screenshots.)*

## Key KPIs

| KPI | Value |
|---|---:|
| Total appointments | 110,521 |
| Total patients | 62,298 |
| No-show rate | 20.19% |
| Show rate | 79.81% |
| Average lead time | 10.2 days |
| Lost appointment capacity | 22,314 slots |

## Key Findings

1. **Lead time is the strongest predictor of no-shows** (Cramér's V = 0.295) — no-show rate rises from 4.6%
   (same-day) to 33.0% (31+ days). Appointments booked 8+ days out are 36% of volume but **57.1% of all lost
   capacity**.
2. **Patient history is the second-strongest predictor** (Cramér's V = 0.169) — a prior no-show nearly doubles
   the odds of the next appointment also being missed (35.2% vs. 18.0%).
3. **A simple 3-rule risk score cleanly separates risk**: 11.6% (Low Risk) vs. 38.9% (High Risk) no-show rate
   — no machine learning required.
4. **SMS reminders likely help — but the naive comparison says the opposite.** Reminders are sent
   disproportionately to long-lead-time patients, who are already higher-risk. Once controlled for, reminders
   show a consistent, real benefit.
5. **Lost capacity is geographically concentrated** in 11 specific neighbourhoods that are both high-volume
   and above-average no-show rate, led by ITARARÉ (26.3%).
6. **Gender and alcoholism were formally ruled out** as drivers (p = 0.17 and 0.97) — not used in any
   recommendation.

Full detail: `docs/business_insights.md`

## Business Recommendations

1. Add proactive reconfirmation calls for appointments booked 8+ days in advance.
2. Flag patients with 2+ prior no-shows for personal outreach, not just automated reminders.
3. Operationalize the risk score so reception can prioritize daily outreach.
4. Continue and expand SMS reminders specifically for long-lead-time bookings.
5. Target location-based outreach at the 11 identified high-volume, high-no-show neighbourhoods.

## Dashboard Screenshots

*(Add your Power BI screenshots to `outputs/screenshots/`.)*

## Project Structure

```
patient-no-show-clinic-efficiency/
├── data/
│   ├── raw/                   # Original Kaggle CSV
│   └── cleaned/                # Cleaned + segmented datasets (regenerated by notebooks 01, 04)
├── notebooks/                  # 01-05, run in order
├── sql/                         # Schema + business queries
├── powerbi/
│   ├── data_model/             # Fact/dimension CSVs for import
│   └── (your .pbix file here)
├── streamlit/                  # app.py + requirements.txt
├── excel/                       # Phase 2 audit workbook
├── outputs/
│   ├── charts/                 # Notebook-generated PNGs
│   └── screenshots/            # Your Power BI screenshots
├── docs/                        # Data dictionary, business insights, executive summary, Power BI docs
├── requirements.txt
└── .gitignore
```

## How to Run

```bash
pip install -r requirements.txt

# Notebooks (run in order)
jupyter notebook notebooks/01_data_cleaning.ipynb

# MySQL
mysql -u root < sql/00_create_table.sql
# then LOAD DATA the cleaned CSV and run sql/clinic_analysis.sql

# Streamlit
cd streamlit
streamlit run app.py
```

## Skills Demonstrated

Data cleaning & validation · feature engineering · exploratory data analysis · hypothesis testing (chi-square,
effect sizes) · rule-based segmentation (as an alternative to ML) · SQL (CTEs, window functions, `HAVING`) ·
dimensional/star-schema data modeling · DAX · interactive dashboard development (Power BI + Streamlit) ·
business communication (translating statistical findings into operational recommendations)

