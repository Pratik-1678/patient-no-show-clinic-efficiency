# Business Insights & Final Recommendations
## Patient No-Show & Clinic Efficiency Analysis

This document presents the 5 strongest, statistically validated findings from the analysis (Notebooks 01-05,
SQL Phase 6, Excel Phase 2), each with the evidence behind it, why it matters operationally, a concrete
recommendation, and an honest estimate of the expected benefit. Every number below was computed from the actual
dataset (110,521 cleaned appointment records) — none are illustrative or invented.

---

## Finding 1 — Lead Time Is the Strongest Predictor of No-Shows

### What happened?
No-show rate rises sharply and consistently with how far in advance an appointment is booked — from 4.6% for
same-day appointments to 33.0% for appointments booked 31+ days out, a roughly 7x increase.

### Evidence
- Notebook 02 (EDA): no-show rate by lead-time bucket — Same day 4.6%, 1-3 days ~9%, 4-7 days ~15%,
  8-14 days ~24%, 15-30 days 32.6%, 31+ days 33.0%
- Notebook 03 (statistical validation): this is the **strongest of all 11 tested factors**, with a Cramér's V
  of 0.295 (chi-square test, p < 0.001) — clearly ahead of every other driver, including patient history
- Notebook 05 (efficiency): appointments booked 8+ days ahead are only **36.0%** of total volume but account
  for **57.1%** of all lost appointment capacity (12,742 of 22,314 total no-shows)

### Business Impact
Long-lead-time bookings are a disproportionately large source of wasted clinic capacity. A slot booked a month
out is roughly seven times more likely to go unused than a same-day slot — meaning the clinic's forward-booking
practices, not just individual patient behavior, are contributing meaningfully to lost capacity.

### Recommendation
Prioritize proactive reconfirmation (a call, not just an automated text) for any appointment booked 8+ days in
advance, with escalating urgency for the 15+ day group. Consider a required reconfirmation step 48-72 hours
before the appointment specifically for this segment, rather than applying the same reminder process to every
booking regardless of lead time.

### Expected Benefit (scenario estimate, not a guarantee)
If reconfirmation calls reduced the no-show rate in the 8+ day group from ~30% down to the clinic's overall
average (20.19%), that alone would recover an estimated **3,000-4,000 appointments** across the dataset's
~6-week window — the single largest lever identified in this project.

---

## Finding 2 — A Patient's Own History Is the Second-Strongest Predictor

### What happened?
Among appointments where the patient has at least one prior visit, a previous no-show nearly doubles the
likelihood that the *next* appointment is also missed.

### Evidence
- Notebook 02/03: no-show rate is **35.15%** following a prior no-show, vs. **17.96%** following a prior
  attended appointment (48,223 appointments have a known prior visit to compare)
- Cramér's V = 0.169 (second-highest of all factors tested, p < 0.001)
- SQL query 2.15 (window functions) identifies specific repeat patients with 8+ no-shows each — some are
  effectively 100% no-show across 10+ booked appointments

### Business Impact
A small number of patients are responsible for a disproportionate share of missed appointments. Treating every
patient identically wastes outreach effort on low-risk patients while under-serving the patients who actually
need extra support (a reminder call, a check-in about barriers to attendance, or a conversation about whether
the current appointment format works for them).

### Recommendation
Flag patients with 2+ historical no-shows for a different outreach track — a personal call rather than an
automated SMS, and where appropriate, a conversation about recurring barriers (transportation, scheduling
conflicts, etc.) rather than just another reminder.

### Expected Benefit (scenario estimate)
This factor is already built into the Phase 7 risk segmentation (below), so its benefit is captured there
rather than estimated separately to avoid double-counting.

---

## Finding 3 — A Simple 3-Rule Risk Score Cleanly Separates High- and Low-Risk Appointments

### What happened?
Combining lead time, patient history, and age group into a simple 0-3 point score produces a risk segmentation
that separates cleanly: Low Risk appointments have an 11.6% no-show rate; High Risk appointments have 38.9% —
more than triple.

### Evidence
- Notebook 04: Low Risk (score 0) = 11.6% no-show rate, 46,684 appointments (42.2% of volume); Medium Risk
  (score 1) = 22.2%, 47,463 appointments; High Risk (score 2-3) = 38.9%, 16,374 appointments (14.8% of volume)
- At the extreme (score 3, all three risk factors present): **54.5%** no-show rate
- Notebook 05: the High Risk segment alone accounts for 6,370 lost appointments despite being only 14.8% of
  volume; a targeted intervention bringing this segment to the overall average would recover an estimated
  **3,064 appointments** (13.7% of all lost capacity)

### Business Impact
Reception staff have limited time for outreach calls. A simple, explainable score (not a black-box model) lets
them prioritize the ~15% of appointments that are genuinely high-risk, rather than spreading effort evenly
across all patients or relying on guesswork.

### Recommendation
Operationalize this score in the scheduling system (or even a simple daily report) so reception can see, each
morning, which of tomorrow's appointments are High Risk and call those patients first.

### Expected Benefit
An estimated 3,064 recoverable appointments if High Risk segment attendance improved to match the clinic
average — a scenario estimate, not a guaranteed outcome, since no controlled intervention has been run yet
(see Limitations).

---

## Finding 4 — SMS Reminders Likely Work, But the Naive Comparison Says the Opposite

### What happened?
A surface-level comparison suggests SMS reminders are associated with a *higher* no-show rate (27.6% vs.
16.7%) — which would suggest reminders don't work or even backfire. This is misleading: reminders are sent far
more often to patients with long lead times, who are independently more likely to no-show for unrelated
reasons. Once lead time is controlled for, the pattern reverses.

### Evidence
- Notebook 02: naive comparison shows SMS-received no-show rate of 27.6% vs. 16.7% without SMS
- Same notebook: average lead time is **19.0 days** for SMS recipients vs. only **6.0 days** for non-recipients
   — a clear confound
- Controlled comparison (within the same lead-time bucket): SMS recipients show a **lower** no-show rate than
  non-recipients in every bucket tested (e.g. 15-30 day bucket: 29.8% with SMS vs. 36.9% without)
- SQL query 2.6 and DAX Section 4 reproduce this controlled comparison independently, with matching results

### Business Impact
If the clinic looked only at the naive number, a reasonable but incorrect conclusion would be to cut the SMS
reminder program as ineffective — which the deeper analysis shows would likely make attendance worse, not
better, especially for long-lead-time bookings where reminders appear to help most.

### Recommendation
Continue the SMS reminder program. Consider specifically ensuring reminder coverage is high for long-lead-time
bookings (Finding 1), since that's both where reminders show the clearest benefit and where the most capacity
is being lost.

### Expected Benefit
Not separately quantified as a standalone recovery number, since this finding is about *not cutting* an
existing beneficial program rather than adding a new intervention — but avoiding this mistake protects an
estimated 6,000+ SMS-covered appointments per the current coverage rate from a worse outcome.

---

## Finding 5 — Lost Capacity Is Concentrated in a Small Number of Neighbourhoods

### What happened?
No-show rates vary meaningfully by neighbourhood, and the highest-volume neighbourhood is *not* the worst
performer — meaning "biggest" and "most problematic" are different places, which matters for where outreach
effort should go.

### Evidence
- Notebook 02/05: the highest-volume neighbourhood (JARDIM CAMBURI, 7,717 appointments) has a below-average
  no-show rate (18.9%)
- **11 neighbourhoods** are both in the top volume quartile AND above the overall average no-show rate —
  led by ITARARÉ (26.3% no-show rate, 3,514 appointments), followed by JESUS DE NAZARETH (24.4%), ILHA DO
  PRÍNCIPE (23.5%), CARATOÍRA, and ANDORINHAS
- SQL query 2.13 (CTE + `NTILE`) and Notebook 05 independently reproduce this same list

### Business Impact
Location-based outreach (e.g. community partnerships, local transportation support, neighbourhood-specific
reminder campaigns) is most efficient when targeted at neighbourhoods that are both high-volume and high-risk —
spreading the same effort evenly across all 81 neighbourhoods would waste resources on places that don't need
it and under-serve the ones that do.

### Recommendation
Direct any location-specific intervention (extra reminder calls, community outreach, transportation partnerships)
at the 11 identified neighbourhoods first, starting with ITARARÉ, JESUS DE NAZARETH, and ILHA DO PRÍNCIPE — the
three highest-volume members of that list.

### Expected Benefit
These 11 neighbourhoods together account for an estimated several thousand no-shows; bringing their combined
rate down to the clinic average would be a meaningful, geographically-targeted contribution to the broader
capacity-recovery goal — though this hasn't been isolated as a standalone number to avoid overlapping with
Finding 1 and Finding 3's recovery estimates (all three findings share some of the same underlying appointments).

---

## Cross-Cutting Notes

- **Ruled out, not just unmentioned:** gender and alcoholism showed no statistically significant relationship
  with no-shows (Notebook 03, p = 0.17 and p = 0.97) and are deliberately excluded from every recommendation
  above — building interventions around them would not be evidence-based.
- **Association, not causation, throughout.** Every finding above describes an observed statistical pattern in
  historical data, not a proven causal mechanism. No randomized intervention has been run. See the full
  discussion in Notebook 03, Section 5.
- **Scenario estimates are estimates.** Every "expected benefit" figure assumes an intervention achieves its
  target improvement — none of these are guaranteed outcomes, and actual results should be measured against a
  baseline once any recommendation is implemented (see Phase 20 / limitations discussion).
