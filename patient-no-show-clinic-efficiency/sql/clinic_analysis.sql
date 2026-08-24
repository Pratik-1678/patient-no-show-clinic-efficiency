-- ============================================================
-- Patient No-Show & Clinic Efficiency Analysis
-- clinic_analysis.sql
--
-- Database: clinic_analytics
-- Table:    appointments  (one row = one scheduled appointment)
--
-- Run 00_create_table.sql first to create and load the table.
-- ============================================================

USE clinic_analytics;

-- ============================================================
-- SECTION 1: BASIC SQL
-- ============================================================

-- 1.1 Total appointments
SELECT COUNT(*) AS total_appointments
FROM appointments;

-- 1.2 Total distinct patients
SELECT COUNT(DISTINCT patient_id) AS total_patients
FROM appointments;

-- 1.3 Total no-shows and show-ups
SELECT
    SUM(no_show_flag)              AS total_no_shows,
    SUM(1 - no_show_flag)          AS total_show_ups
FROM appointments;

-- 1.4 Overall no-show rate
SELECT
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2) AS no_show_rate_pct
FROM appointments;

-- 1.5 Distinct neighbourhoods
SELECT COUNT(DISTINCT neighbourhood) AS distinct_neighbourhoods
FROM appointments;

-- 1.6 Appointment date range
SELECT
    MIN(appointment_day) AS earliest_appointment,
    MAX(appointment_day) AS latest_appointment
FROM appointments;


-- ============================================================
-- SECTION 2: BUSINESS SQL
-- ============================================================

-- 2.1 No-show rate by age group
SELECT
    age_group,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY age_group
ORDER BY no_show_rate_pct DESC;

-- 2.2 No-show rate by gender
SELECT
    gender,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY gender
ORDER BY no_show_rate_pct DESC;

-- 2.3 No-show rate by weekday
SELECT
    appointment_weekday,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY appointment_weekday
ORDER BY FIELD(appointment_weekday,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');
-- Note: no Sunday appointments exist in this dataset; Saturday volume is very small (~39) — interpret with caution.

-- 2.4 No-show rate by neighbourhood (all neighbourhoods, for reference)
SELECT
    neighbourhood,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY neighbourhood
ORDER BY no_show_rate_pct DESC;

-- 2.5 No-show rate by reminder (SMS) status
SELECT
    CASE WHEN sms_received = 1 THEN 'SMS Received' ELSE 'No SMS' END AS reminder_status,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct,
    ROUND(AVG(lead_time_days), 1)                  AS avg_lead_time_days
FROM appointments
GROUP BY reminder_status;
-- Note: SMS recipients have a much longer average lead time (see avg_lead_time_days) -
-- this is a confound (see 2.6 for the controlled comparison), not proof reminders increase no-shows.

-- 2.6 No-show rate by reminder status, CONTROLLING for lead-time bucket (resolves the confound in 2.5)
SELECT
    waiting_time_group,
    CASE WHEN sms_received = 1 THEN 'SMS Received' ELSE 'No SMS' END AS reminder_status,
    COUNT(*)                                       AS volume,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY waiting_time_group, reminder_status
ORDER BY FIELD(waiting_time_group,'Same day','1-3 days','4-7 days','8-14 days','15-30 days','31+ days'),
         reminder_status;

-- 2.7 No-show rate by lead-time bucket
SELECT
    waiting_time_group,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY waiting_time_group
ORDER BY FIELD(waiting_time_group,'Same day','1-3 days','4-7 days','8-14 days','15-30 days','31+ days');

-- 2.8 Appointment volume by month
SELECT
    appointment_year,
    appointment_month,
    COUNT(*) AS volume
FROM appointments
GROUP BY appointment_year, appointment_month
ORDER BY appointment_year, FIELD(appointment_month,'January','February','March','April','May','June',
         'July','August','September','October','November','December');

-- 2.9 No-show rate by month
SELECT
    appointment_year,
    appointment_month,
    COUNT(*)                                       AS volume,
    SUM(no_show_flag)                              AS no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY appointment_year, appointment_month
ORDER BY appointment_year, FIELD(appointment_month,'January','February','March','April','May','June',
         'July','August','September','October','November','December');

-- 2.10 Top 10 neighbourhoods by no-show rate (ALL sample sizes — for comparison with 2.11)
SELECT
    neighbourhood,
    COUNT(*)                                       AS volume,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY neighbourhood
ORDER BY no_show_rate_pct DESC
LIMIT 10;
-- Caution: some of these may be small, unreliable samples - see 2.11 for the volume-filtered version.

-- 2.11 Top 10 HIGH-VOLUME (>=100 appointments) neighbourhoods by no-show rate
--       This is the reliable version for business use (avoids ranking tiny samples).
SELECT
    neighbourhood,
    COUNT(*)                                       AS volume,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY neighbourhood
HAVING COUNT(*) >= 100
ORDER BY no_show_rate_pct DESC
LIMIT 10;

-- 2.12 Highest-volume neighbourhoods (regardless of no-show rate)
SELECT
    neighbourhood,
    COUNT(*)                                       AS volume,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY neighbourhood
ORDER BY volume DESC
LIMIT 10;

-- 2.13 High-volume AND high-no-show neighbourhoods (the real operational priority list)
--       "High volume" = top 25% by appointment count; "high no-show" = above the overall average (20.19%).
WITH neighbourhood_stats AS (
    SELECT
        neighbourhood,
        COUNT(*)                                       AS volume,
        ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
    FROM appointments
    GROUP BY neighbourhood
),
overall AS (
    SELECT ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2) AS overall_rate FROM appointments
),
volume_threshold AS (
    SELECT volume AS p75_volume
    FROM (
        SELECT volume, NTILE(4) OVER (ORDER BY volume) AS quartile
        FROM neighbourhood_stats
    ) q
    WHERE quartile = 4
    ORDER BY volume ASC
    LIMIT 1
)
SELECT
    ns.neighbourhood,
    ns.volume,
    ns.no_show_rate_pct
FROM neighbourhood_stats ns
CROSS JOIN overall o
CROSS JOIN volume_threshold vt
WHERE ns.volume >= vt.p75_volume
  AND ns.no_show_rate_pct > o.overall_rate
ORDER BY ns.no_show_rate_pct DESC;

-- 2.14 Patient history vs attendance: does a patient's overall history predict their no-show rate?
--       (Uses a window function to count each patient's total prior appointments.)
WITH ordered_appts AS (
    SELECT
        patient_id,
        appointment_id,
        appointment_day,
        no_show_flag,
        ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY appointment_day) AS visit_number,
        LAG(no_show_flag) OVER (PARTITION BY patient_id ORDER BY appointment_day) AS prior_no_show
    FROM appointments
)
SELECT
    CASE
        WHEN prior_no_show IS NULL THEN 'No prior appointment (first visit)'
        WHEN prior_no_show = 1 THEN 'Previous appointment was a no-show'
        ELSE 'Previous appointment attended'
    END AS patient_history_segment,
    COUNT(*)                                       AS volume,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM ordered_appts
GROUP BY patient_history_segment
ORDER BY no_show_rate_pct DESC;

-- 2.15 Repeat no-show patients: patients with 2+ total no-shows, ranked by no-show count
--       (identifies which specific patients to prioritize for outreach)
SELECT
    patient_id,
    COUNT(*)                                       AS total_appointments,
    SUM(no_show_flag)                              AS total_no_shows,
    ROUND(SUM(no_show_flag) / COUNT(*) * 100, 2)   AS no_show_rate_pct
FROM appointments
GROUP BY patient_id
HAVING SUM(no_show_flag) >= 2
ORDER BY total_no_shows DESC, no_show_rate_pct DESC
LIMIT 20;

-- 2.16 Reminder coverage rate (overall, and by whether the appointment was ultimately a no-show)
SELECT
    ROUND(SUM(sms_received) / COUNT(*) * 100, 2) AS overall_reminder_coverage_pct
FROM appointments;

SELECT
    CASE WHEN no_show_flag = 1 THEN 'No-show' ELSE 'Attended' END AS outcome,
    ROUND(SUM(sms_received) / COUNT(*) * 100, 2) AS reminder_coverage_pct
FROM appointments
GROUP BY outcome;

-- 2.17 Potentially recoverable appointment capacity — scenario analysis
--       Clearly labeled as SCENARIO ESTIMATES, not actual outcomes (per project rules).
SELECT
    SUM(no_show_flag)                          AS current_lost_capacity_slots,
    ROUND(SUM(no_show_flag) * 0.10, 0)         AS scenario_recoverable_10pct_reduction,
    ROUND(SUM(no_show_flag) * 0.20, 0)         AS scenario_recoverable_20pct_reduction,
    ROUND(SUM(no_show_flag) * 0.30, 0)         AS scenario_recoverable_30pct_reduction
FROM appointments;
