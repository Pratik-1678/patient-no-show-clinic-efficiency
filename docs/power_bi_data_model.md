# Power BI Data Model — Patient No-Show & Clinic Efficiency Analysis

## Overview

A star schema with **1 fact table** and **3 dimension tables**. Grain of the fact table: **one row = one
scheduled appointment** (matches the grain established in Phase 1).

```
                    ┌─────────────┐
                    │   DimDate   │
                    │  (212 rows) │
                    └──────┬──────┘
                           │ 1
                           │
                           │ *
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  DimPatient   │ 1  │ FactAppointments │  1 │ DimLocation  │
│ (62,298 rows) ├────┤   (110,521 rows) ├────┤  (81 rows)   │
└──────────────┘    *└──────────────────┘*   └──────────────┘
```

## Files (in `powerbi/data_model/`)

| File | Row Count | Purpose |
|---|---:|---|
| `FactAppointments.csv` | 110,521 | One row per appointment — measures + foreign keys |
| `DimDate.csv` | 212 | One row per calendar day, spanning both `scheduled_day` and `appointment_day` ranges (2015-11-10 to 2016-06-08) |
| `DimPatient.csv` | 62,298 | One row per distinct patient |
| `DimLocation.csv` | 81 | One row per distinct neighbourhood |

All four were built from `data/cleaned/appointments_with_risk_segments.csv` (Phase 7 output) and passed
referential-integrity checks (zero orphaned foreign keys in any direction) before export.

## Table Details

### FactAppointments
| Column | Type | Role |
|---|---|---|
| `appointment_id` | Integer | Row identifier (not a Power BI relationship key) |
| `patient_id` | Text | FK → DimPatient |
| `location_id` | Integer | FK → DimLocation |
| `appointment_date` | Date | FK → DimDate |
| `scheduled_day` | Datetime | Attribute only — **not** related to DimDate (see note below) |
| `age`, `age_group` | Number / Text | Degenerate dimension attributes |
| `lead_time_days`, `waiting_time_group` | Number / Text | Degenerate dimension attributes |
| `sms_received`, `scholarship`, `hypertension`, `diabetes`, `alcoholism`, `handicap`, `chronic_condition_count` | Number | Degenerate dimension attributes |
| `risk_score`, `risk_segment` | Number / Text | From Phase 7 segmentation |
| `prior_no_show_flag` | Number (0/1/blank) | 1 = patient's previous appointment was a no-show, 0 = attended, **blank = first visit (no prior appointment)** |
| `visit_number` | Number | This appointment's sequence number for the patient (1 = first visit) |
| `no_show_flag` | Number (0/1) | Core measure input |

### DimDate
`date`, `year`, `quarter`, `month_number`, `month_name`, `day`, `weekday_number`, `weekday_name`, `is_weekend`, `year_month`

### DimPatient
`patient_id`, `gender` — kept intentionally minimal (see design decisions below)

### DimLocation
`location_id`, `neighbourhood`

## Design Decisions (and why)

**Why age_group, waiting_time_group, risk_segment, and the medical-condition flags live in the fact table
instead of their own dimension tables:** these are all simple category labels with no additional descriptive
attributes of their own (no hierarchy, no extra columns to hang off them). Splitting each into a separate
1-column dimension table would add relationships and model complexity without adding analytical value — this
follows the project rule to only create dimensions that genuinely improve the model. They're used directly as
"degenerate dimensions" on the fact table, which is standard practice for this kind of categorical flag.

**Why DimPatient is minimal (just `patient_id` and `gender`):** it's tempting to add things like
"TotalAppointments" or "TotalNoShows" per patient directly onto DimPatient. That would be a modeling mistake —
those are aggregates that change as new appointments come in, and Power BI calculates them correctly and
efficiently as **DAX measures** against the fact table instead (Phase 10). Storing them as static dimension
columns would mean they go stale and have to be recomputed and reloaded every time the fact table changes.

**Why `scheduled_day` is NOT related to DimDate:** in a "textbook" star schema you might see a role-playing
date dimension (one relationship for `appointment_date`, a second inactive one for `scheduled_date`, activated
in DAX with `USERELATIONSHIP` when needed). Here, `lead_time_days` — the actual business-relevant derived
value — was already computed in Python during Notebook 01, so there's no need to relate `scheduled_day` to
DimDate just to recompute the same thing in DAX. It's kept in the fact table purely as a reference attribute.
This is a simplification made deliberately, not an oversight.

**Why `prior_no_show_flag` and `visit_number` are precomputed columns, not DAX measures:** these depend on
ordering each patient's appointments chronologically (a "previous row for this patient" lookup), which needs a
window-function-style calculation. This is well-supported in Python/pandas (`groupby().shift()`, as used in
Notebooks 02-04) and awkward and slow to replicate in DAX at this data volume. Precomputing it once in Python
and shipping it as a stable fact-table column is the more practical choice — DAX then just aggregates it like
any other column, which is exactly what DAX is good at.

## Relationships to Create in Power BI Desktop

| From (Dimension) | To (Fact) | Cardinality | Cross-filter direction |
|---|---|---|---|
| `DimDate[date]` | `FactAppointments[appointment_date]` | One-to-many | Single (Date → Fact) |
| `DimPatient[patient_id]` | `FactAppointments[patient_id]` | One-to-many | Single (Patient → Fact) |
| `DimLocation[location_id]` | `FactAppointments[location_id]` | One-to-many | Single (Location → Fact) |

All three relationships use **single-direction filtering** (dimension filters fact, not the reverse) — the
standard, safest star-schema pattern that avoids ambiguous filter propagation. There's no need for
bi-directional filtering anywhere in this model.

## Steps to Build This in Power BI Desktop

1. **Get Data → Text/CSV**, import all 4 files from `powerbi/data_model/`.
2. In **Model view**, mark `DimDate` as a Date Table: select the table → *Table tools* → *Mark as date table* →
   choose the `date` column.
3. Drag to create the 3 relationships listed in the table above. Power BI should auto-detect
   `patient_id`/`location_id`/`date` matches, but confirm cardinality and direction manually — don't rely on
   autodetect alone.
4. Verify each relationship is **Many-to-One** (fact side = many) and **Single** direction.
5. Rename the fact/dimension tables in the Fields pane if needed (they should already be named correctly from
   the CSV filenames: `FactAppointments`, `DimDate`, `DimPatient`, `DimLocation`).

Once the model is built, move on to **Phase 10** for the DAX measures.
