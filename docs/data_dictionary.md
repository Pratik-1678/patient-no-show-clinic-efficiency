# Data Dictionary
## Patient No-Show & Clinic Efficiency Analysis

Source: Kaggle "Medical Appointment No Shows" dataset. Grain: **one row = one scheduled appointment**.

## Raw Columns (source file)

| Column | Meaning | Data Type | Business Relevance |
|---|---|---|---|
| PatientId | Unique patient identifier | Numeric | Enables repeat-patient / history analysis |
| AppointmentID | Unique appointment identifier | Integer | Grain of the table |
| Gender | Patient gender (F/M) | Text | Demographic driver |
| ScheduledDay | Timestamp appointment was booked | Datetime | Used to compute lead time |
| AppointmentDay | Date of the appointment (no time component) | Date | Used for weekday / monthly analysis |
| Age | Patient age in years | Integer | Age-group driver; contained 1 invalid negative value, removed during cleaning |
| Neighbourhood | Clinic/patient location | Text | Location-based no-show patterns (81 unique values) |
| Scholarship | Enrolled in Bolsa Familia welfare program (0/1) | Binary | Socio-economic proxy |
| Hipertension | Patient has hypertension (0/1) — source spelling | Binary | Medical condition driver |
| Diabetes | Patient has diabetes (0/1) | Binary | Medical condition driver |
| Alcoholism | Patient has alcoholism (0/1) | Binary | Tested — not statistically significant |
| Handcap | Degree of disability, 0-4 — source spelling, not truly binary | Ordinal | Medical condition driver |
| SMS_received | Reminder SMS sent before appointment (0/1) | Binary | Reminder-effect analysis |
| No-show | "Yes" = did NOT attend, "No" = attended | Text | Target variable |

## Engineered Columns (added during cleaning / feature engineering)

| Column | Meaning | Notes |
|---|---|---|
| no_show_flag | No-show recoded to 1/0 | 1 = no-show |
| lead_time_days | Days between scheduled_day and appointment_day | Strongest predictor found in the analysis |
| waiting_time_group | lead_time_days bucketed (Same day, 1-3, 4-7, 8-14, 15-30, 31+ days) | |
| appointment_weekday / appointment_month / appointment_year | Derived from appointment_day | |
| age_group | Age bucketed into 6 bands | |
| chronic_condition_count | Sum of hypertension + diabetes + alcoholism | |
| prior_no_show | Whether the patient's previous appointment was a no-show | Blank = first visit |
| risk_score / risk_segment | 0-3 point rule-based risk score and Low/Medium/High label | See business segmentation |

**Column not created:** appointment time-of-day (morning/afternoon/evening) — `appointment_day` has no time
component in the source data, only a date, so this was not derivable from the dataset.
