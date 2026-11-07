# Lakefill National Bank: operational loss event data dictionary

**Files covered:** `lakefill_losses_raw.csv` (the history, 2021 to 2025, issued at the week 5 sync), `lakefill_checkpoint1.csv` (the reference-prepared history, Monday of week 6), `lakefill_2026Q1_slice.csv` (week 9), `lakefill_2026Q2_extract.csv` (week 10), and the companion exposure tables `lakefill_exposure_monthly.csv`, `lakefill_exposure_monthly_2026Q1.csv`, `lakefill_exposure_monthly_2026Q2.csv`. All event files share the 26 columns in section 2; all exposure tables share the 8 columns in section 3. Generator version 1.0.0.

Lakefill National Bank is a fictional mid-size commercial bank headquartered in Chicago. This is its operational loss event register: one row per operational loss event, as extracted from the bank's operational risk management system (ORMS) by the Chief Risk Officer's (CRO) office. Dollar amounts are in US dollars. Dates are `YYYY-MM-DD`. Blank means the value is not recorded.

## 1. What you need to know about how this data was collected

| Date | Fact |
|---|---|
| 2021-01-01 | Start of the history. Events before this date are not in the file. |
| 2023-01-01 | ORMS went live. Before this date, events were loaded from the legacy general-ledger loss feed, which did not carry a recovery field for trading and treasury (see `recoveries`) and in which some retail banking events were never assigned an event type (see `event_type`). |
| 2023-01-01 | Shared services' collection threshold changed. Every line's events are recorded when the gross loss is at or above the bank's **collection threshold of 10,000**, with one exception: shared services events were collected at **20,000** before 2023-01-01 and at 10,000 from that date (its losses were captured through the facilities and human-resources expense process before ORMS). `threshold_era` marks the two periods. Counts and averages across the two eras are not directly comparable for shared services. |
| 2023-04-01 | Payment verification control went live in retail banking (`post_verification`). |
| 2023-07-01 | Payments moved to a new processing platform (`post_migration`). Straight-through processing on the new platform is reflected in `automation_flag` for payments from this date. |
| 2023-07-01 | Asset Management (acquired in 2022) was onboarded to ORMS. It has no events before this date. |
| 2024-01-01 | Straight-through processing went live in trading and treasury (`automation_flag`). |
| 2026-03-31 | As-of date of the history file and of the 2026 Q1 slice. Events not yet closed on that date are `Open` (section 2, `status`). |
| 2026-06-30 | As-of date of the Q2 refreshed extract. |

Business lines (six; the bank reports these rather than the eight Basel business lines): Retail Banking, Commercial Lending, Payments, Asset Management, Trading and Treasury, Shared Services. Event types: the seven Basel level-1 operational event types. Regions: Chicago Metro, Illinois, Wisconsin, Indiana and Michigan (centralized functions sit in Chicago Metro).

## 2. Event files: columns

**Availability mark**: **D** = known at discovery (the value exists when the event is first recorded, so it can be a feature of a model that predicts at discovery). **C** = known at close (the value is set after the event has run its course; it is never available at discovery). **R** = reference: taken from the exposure table for the line and the month of discovery (known at discovery; also in the exposure table).

| # | Column | Type | Mark | Definition and values |
|---|---|---|---|---|
| 1 | event_id | identifier | D | `OL` followed by seven digits. Unique in the register. Not sequential. |
| 2 | business_line | nominal | D | One of the six business lines above. |
| 3 | event_type | nominal | D | One of the seven Basel level-1 event types: Internal Fraud; External Fraud; Employment Practices and Workplace Safety; Clients, Products and Business Practices; Damage to Physical Assets; Business Disruption and System Failures; Execution, Delivery and Process Management. Blank where the legacy feed carried no event type (retail banking, before 2023). |
| 4 | region | nominal | D | One of the four regions above. |
| 5 | reporting_channel | nominal | D | How the event reached the loss team: Branch, Call Center, System Alert, Internal Audit, Customer Complaint. |
| 6 | occurrence_date | date | D | The date the event began (the first day of the loss-causing activity), as recorded when the event was logged. On or before `discovery_date`. |
| 7 | discovery_date | date | D | The date the bank became aware of the event. Use this date for every count by period. |
| 8 | reporting_date | date | D | The date the event was logged in the loss system. On or after `discovery_date`; the difference is the reporting lag. |
| 9 | status | nominal | D | `Closed` or `Open` at the file's as-of date. An open event has a provisional `gross_loss` (the current estimate) and blank `close_date`, `days_open`, `final_reserve`, `recoveries`, `net_loss`. |
| 10 | close_date | date | C | The date the event was closed in the loss system. Blank while open. |
| 11 | days_open | integer | C | `close_date` minus `discovery_date`, in days. Blank while open. |
| 12 | initial_estimate | dollars | D | The first loss estimate, recorded at discovery and never revised in this field. Rounded to 100. |
| 13 | final_reserve | dollars | C | The provision on file for this event at closure. Provisions are set once a loss is identified and revised as the case develops; this field holds the last value before closure. It is an event-level operational loss provision, not a credit-loss allowance. Blank while open. |
| 14 | gross_loss | dollars | C (provisional while open) | The gross loss before any recovery. For a closed event, the final figure. For an open event, the current estimate, which will change. |
| 15 | recoveries | dollars | C | Amounts recovered through insurance, restitution, reversal or other means, as recorded at closure. 0 where nothing was recovered. Blank while open. Blank for trading and treasury events discovered before 2023-01-01, where the source feed carried no recovery field. |
| 16 | net_loss | dollars | C | `gross_loss` minus `recoveries`. Blank wherever `recoveries` is blank or the event is open. |
| 17 | threshold_era | nominal | D | `before 2023` or `2023 onward`, by `discovery_date`. See section 1 for what changed on 2023-01-01. |
| 18 | post_verification | integer | D | 1 if `discovery_date` is on or after 2023-04-01 (payment verification live), else 0. Carried on every row. |
| 19 | post_migration | integer | D | 1 if `discovery_date` is on or after 2023-07-01 (payments platform migration), else 0. Carried on every row, including rows of other lines. |
| 20 | transaction_volume | number | R | The business line's activity measure in the month of discovery (section 3). |
| 21 | account_count | number | R | The business line's account or position count in the month of discovery (section 3). |
| 22 | control_maturity_score | number, 1.0 to 5.0 | R | The business line's control maturity rating in the quarter of discovery (section 3). |
| 23 | staffing_ratio | number | R | The business line's staffing against plan in the month of discovery; 1.00 is at plan (section 3). |
| 24 | system_age | number, years | R | Years since the business line's core processing system was last replaced, in the quarter of discovery (section 3). |
| 25 | automation_flag | integer | R | 1 when straight-through processing is live for the business line in the quarter of discovery, else 0 (section 3). |
| 26 | root_cause_tags | nominal | D | One tag assigned at discovery: manual error, system defect, vendor, cyber, process gap, external event, policy breach. |

Rows are ordered by `discovery_date`, then `event_id`. The Checkpoint 1 file, the Q1 slice and the Q2 extract have the same columns as the raw file.

## 3. Exposure tables: columns

One row per business line per month. The history table covers 2021-01 to 2025-12 (Asset Management from 2023-07); the Q1 and Q2 tables extend it to 2026-03 and 2026-06. Values at a quarterly grain are repeated across the quarter's three months.

| # | Column | Type | Grain | Definition |
|---|---|---|---|---|
| 1 | month | `YYYY-MM` | monthly | |
| 2 | business_line | nominal | | |
| 3 | transaction_volume | number | monthly | The line's activity measure: retail banking, customer transactions processed; payments, payment items processed; commercial lending, loans outstanding; asset management, client accounts; trading and treasury, settlements processed; shared services, internal service requests completed. Units differ by line; compare within a line, not across lines. |
| 4 | account_count | number | monthly | A second size measure: retail banking, deposit and card accounts; payments, client payment accounts; commercial lending, borrowers; asset management, client accounts; trading and treasury, open positions at month end; shared services, employees served. |
| 5 | control_maturity_score | number, 1.0 to 5.0 | quarterly | The internal control assessment's rating of the line's control environment: 1 initial, 2 developing, 3 defined, 4 managed, 5 optimized. |
| 6 | staffing_ratio | number | monthly | Filled positions divided by planned positions; 1.00 is at plan. |
| 7 | system_age | number, years | quarterly | Years since the line's core processing system was last replaced. |
| 8 | automation_flag | integer | quarterly | 1 when straight-through processing is live for the line, else 0. |

## 4. Reading notes

- Every count by period should use `discovery_date`. Every severity or recovery analysis should use `Closed` rows, because an open event's `gross_loss` is an estimate and its close-side fields are blank.
- The collection threshold means the file holds no event below 10,000 (20,000 for shared services before 2023). Averages and counts describe recorded events, not all events.
- The exposure table is the source for any analysis at the line-by-month grain, including months in which a line recorded no events. The R-marked columns on the event rows repeat the exposure table's values for convenience.
- The dictionary is accurate about when each field becomes known. Read the marks before choosing features for any model that is meant to predict at discovery.
