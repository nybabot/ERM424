# Data dictionary: m2_claims.csv

**Corvane Mutual Insurance Company, claims extract, incidents from January 2024 through June 2025.**

One row per claim event. The file comes from the claims administration system as a flat export with 18 columns and 1,500 rows. Amounts are United States dollars. Dates are calendar dates in `YYYY-MM-DD` form. Identifiers are whole numbers assigned by the source systems; they carry no quantitative meaning.

## Columns

| # | Column | Type | Description | Values or range |
|---|---|---|---|---|
| 1 | claim_id | identifier | Claim number assigned by the claims system. Unique within the file. | 7-digit whole number |
| 2 | policy_id | identifier | Policy number of the insured. One policy can have several claims. | 6-digit whole number |
| 3 | incident_date | date | Date the loss event occurred. | 2024-01-01 to 2025-06-30 |
| 4 | report_date | date | Date the claim was reported to Corvane Mutual. | On or after incident_date |
| 5 | claim_type | categorical (nominal) | Primary coverage the claim was filed under. | Collision; Comprehensive; Property Damage Liability; Bodily Injury Liability; Personal Injury Protection; Uninsured Motorist |
| 6 | severity | categorical (ordinal) | Adjuster's severity code for the event, from least to most severe. | Minor < Moderate < Major < Total Loss |
| 7 | vehicles_involved | count | Number of vehicles involved in the event, including the insured vehicle. | 1 to 4 |
| 8 | vehicle_make | categorical (nominal) | Manufacturer of the insured vehicle as recorded at the time of the claim. | Manufacturer name |
| 9 | vehicle_year | numeric (model year) | Model year of the insured vehicle. | Four-digit year |
| 10 | vehicle_value | numeric | Actual cash value of the insured vehicle at the time of the claim, from the valuation feed. Whole dollars, rounded to the nearest 100. | Dollars |
| 11 | region | categorical (nominal) | State where the incident occurred, as a two-letter postal code. | IL, WI, IN, MI, OH, MN, MO, IA, KY, TN |
| 12 | report_channel | categorical (nominal) | How the claim was first reported. | Mobile App; Web Portal; Phone; Agent; Email |
| 13 | adjuster_id | identifier | Staff number of the adjuster assigned to the claim. | 4-digit whole number |
| 14 | injury_amount | numeric | Amount paid for bodily injury and medical costs, all parties. 0.00 when the event had no injury component. | Dollars and cents |
| 15 | property_amount | numeric | Amount paid for damage to third-party property (other vehicles, structures, fixtures). 0.00 when there was none. | Dollars and cents |
| 16 | vehicle_amount | numeric | Amount paid for damage to the insured vehicle. 0.00 when there was none. | Dollars and cents |
| 17 | total_amount | numeric | Total amount paid on the claim. | Dollars and cents |
| 18 | notes | free text | Adjuster free-text notes on the claim. | Text |

## Rules that hold in this file

1. **Consistency rule:** `total_amount` equals `injury_amount` + `property_amount` + `vehicle_amount` on every row.
2. **Date rule:** `report_date` is on or after `incident_date` on every row.

## Notes for analysts

- Load the file with pandas and check the storage type of every column against the type in this dictionary. The storage type pandas infers is not always the type the column measures.
- The file is a system export. Treat every column as it arrives and record what you find before you change anything.
