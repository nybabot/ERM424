# Data dictionary: m3_claims_extract.csv and m3_policyholders.csv

**Corvane Mutual Insurance Company, second claims extract (incidents from July 2025 through June 2026) and the policyholder reference table.**

Two files. The claims extract has one row per claim event, 20 columns. The policyholder table has one row per policyholder, 6 columns. The two tables share the `policy_id` column, which is the key for joining them: a claim's `policy_id` identifies the row of the policyholder table that describes the insured. Amounts are United States dollars; dates are calendar dates in `YYYY-MM-DD` form; identifiers are whole numbers assigned by the source systems and carry no quantitative meaning.

The extract continues the Module 2 file: the same claims system, the next twelve months of incidents, and three new columns that the policy system now supplies with each claim (`annual_income`, `prior_claims_count`, `loss_description`). The `notes` column of the Module 2 file is not part of this export.

## m3_claims_extract.csv

| # | Column | Type | Description | Values or range |
|---|---|---|---|---|
| 1 | claim_id | identifier | Claim number assigned by the claims system. | 7-digit whole number |
| 2 | policy_id | identifier | Policy number of the insured; the join key to the policyholder table. | 6-digit whole number |
| 3 | incident_date | date | Date the loss event occurred. | 2025-07-01 to 2026-06-30 |
| 4 | report_date | date | Date the claim was reported to Corvane Mutual. | On or after incident_date |
| 5 | claim_type | categorical (nominal) | Primary coverage the claim was filed under. | Collision; Comprehensive; Property Damage Liability; Bodily Injury Liability; Personal Injury Protection; Uninsured Motorist |
| 6 | severity | categorical (ordinal) | Adjuster's severity code, from least to most severe. | Minor < Moderate < Major < Total Loss |
| 7 | vehicles_involved | count | Number of vehicles involved in the event, including the insured vehicle. | 1 to 4 |
| 8 | vehicle_make | categorical (nominal) | Manufacturer of the insured vehicle. | Manufacturer name |
| 9 | vehicle_year | numeric (model year) | Model year of the insured vehicle. | Four-digit year |
| 10 | vehicle_value | numeric | Actual cash value of the insured vehicle at the time of the claim. Whole dollars, rounded to the nearest 100. | Dollars |
| 11 | region | categorical (nominal) | State where the incident occurred, two-letter postal code. | IL, WI, IN, MI, OH, MN, MO, IA, KY, TN |
| 12 | report_channel | categorical (nominal) | How the claim was first reported. | Mobile App; Web Portal; Phone; Agent; Email |
| 13 | adjuster_id | identifier | Staff number of the adjuster assigned to the claim. | 4-digit whole number |
| 14 | annual_income | numeric | Policyholder's declared annual household income at the most recent underwriting, copied from the policy system onto each claim. Whole dollars, rounded to the nearest 100. Blank when the policy system holds no declared income for the policyholder. | Dollars |
| 15 | prior_claims_count | count, with status codes | Number of claims the policyholder had filed with Corvane Mutual in the five years before the extract date, as recorded in the policy system. **Two status codes appear in this column alongside real counts:** `96` = no record available (the policy system holds no claims-history record for this policyholder); `98` = not ascertainable (a history record exists but could not be matched to the policy). The codes are values in the column, not blanks. | Whole number, or the codes 96 and 98 |
| 16 | loss_description | free text | Short description of the event entered by the intake handler. | Text |
| 17 | injury_amount | numeric | Amount paid for bodily injury and medical costs, all parties. 0.00 when none. | Dollars and cents |
| 18 | property_amount | numeric | Amount paid for damage to third-party property. 0.00 when none. | Dollars and cents |
| 19 | vehicle_amount | numeric | Amount paid for damage to the insured vehicle. 0.00 when none. | Dollars and cents |
| 20 | total_amount | numeric | Total amount paid on the claim. | Dollars and cents |

## m3_policyholders.csv

| # | Column | Type | Description | Values or range |
|---|---|---|---|---|
| 1 | policy_id | identifier | Policy number; the join key to the claims extract. | 6-digit whole number |
| 2 | customer_segment | categorical (nominal) | Underwriting segment of the policy. | Preferred; Standard; Non-standard; Commercial |
| 3 | home_region | categorical (nominal) | State where the policy is garaged, two-letter postal code. The claims extract's `region` is where the incident occurred, which is usually but not always the same state. | IL, WI, IN, MI, OH, MN, MO, IA, KY, TN |
| 4 | tenure_years | count | Whole years the policyholder has been insured with Corvane Mutual. | Whole number |
| 5 | sales_channel | categorical (nominal) | Channel through which the policy was sold. | Independent Agent; Captive Agent; Direct Online; Direct Phone; Affinity Partner |
| 6 | customer_age | numeric | Age of the named insured in whole years at the start of the current policy term. For a Commercial policy, the age of the principal on the policy. | Whole years |

## Rules that hold in these files

1. **Consistency rule:** `total_amount` equals `injury_amount` + `property_amount` + `vehicle_amount` on every row of the extract.
2. **Date rule:** `report_date` is on or after `incident_date` on every row of the extract.
3. **Join key:** `policy_id` in the extract refers to `policy_id` in the policyholder table.
4. **Status codes:** in `prior_claims_count`, the values 96 and 98 are codes with the meanings above, not counts.

## Notes for analysts

- Join the two tables before drawing conclusions about either. Check row counts and key integrity before and after the join, and record what you find.
- The policy system supplies `annual_income` and `prior_claims_count` as a snapshot per policyholder at extract time, so a policyholder with several claims carries the same values on each.
- Treat both files as they arrive. Every change you make belongs in your decision log.
