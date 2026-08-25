-- ============================================================
-- Patient No-Show & Clinic Efficiency Analysis
-- 00_create_table.sql
-- Creates the clinic_analytics database schema.
-- ============================================================

CREATE DATABASE IF NOT EXISTS clinic_analytics;
USE clinic_analytics;

DROP TABLE IF EXISTS appointments;

CREATE TABLE appointments (
    patient_id              VARCHAR(20)   NOT NULL,
    appointment_id          BIGINT        NOT NULL PRIMARY KEY,
    gender                  CHAR(1)       NOT NULL,
    scheduled_day           DATETIME      NOT NULL,
    appointment_day         DATE          NOT NULL,
    age                     SMALLINT      NOT NULL,
    neighbourhood           VARCHAR(60)   NOT NULL,
    scholarship             TINYINT       NOT NULL,
    hypertension            TINYINT       NOT NULL,
    diabetes                TINYINT       NOT NULL,
    alcoholism               TINYINT      NOT NULL,
    handicap                TINYINT       NOT NULL,
    sms_received            TINYINT       NOT NULL,
    no_show                 VARCHAR(3)    NOT NULL,       -- 'Yes' = did NOT attend, 'No' = attended
    no_show_flag            TINYINT       NOT NULL,       -- 1 = no-show, 0 = attended
    lead_time_days          INT           NOT NULL,
    appointment_weekday     VARCHAR(10)   NOT NULL,
    appointment_month       VARCHAR(10)   NOT NULL,
    appointment_year        SMALLINT      NOT NULL,
    age_group               VARCHAR(20)   NOT NULL,
    waiting_time_group      VARCHAR(20)   NOT NULL,
    reminder_flag           TINYINT       NOT NULL,
    scholarship_flag        TINYINT       NOT NULL,
    chronic_condition_count TINYINT       NOT NULL,

    INDEX idx_patient_id (patient_id),
    INDEX idx_neighbourhood (neighbourhood),
    INDEX idx_appointment_day (appointment_day),
    INDEX idx_no_show_flag (no_show_flag)
);
