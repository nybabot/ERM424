# Basel operational event types: the Lakefill reference sheet

One page, to keep open all term. Lakefill National Bank classifies every operational loss event by the seven Basel level-1 event types (Basel Committee on Banking Supervision, 2006, Annex 9). The examples are the kind of event each type holds in a bank like Lakefill; they are illustrations, not entries from the register.

## The seven event types

| Event type (as written in `event_type`) | What it covers | Two examples |
|---|---|---|
| Internal Fraud | Losses from acts intended to defraud, misappropriate property or get around the law or bank policy, involving at least one person inside the bank | A teller moves small amounts from dormant accounts over months; an employee approves loans to a relative's shell company |
| External Fraud | The same kinds of acts by a third party, with no one inside the bank involved | A ring opens accounts with stolen identities and draws down card credit; forged checks clear before the customer notices |
| Employment Practices and Workplace Safety | Acts inconsistent with employment, health or safety law or agreements, personal injury claims, and discrimination events | A wage-and-hour settlement with branch staff; a slip-and-fall claim at an operations center |
| Clients, Products and Business Practices | Failures, unintentional or negligent, to meet an obligation to clients, or losses from the nature or design of a product | Fees charged in breach of a disclosure rule, refunded with a penalty; an unsuitable investment recommended to a retired client |
| Damage to Physical Assets | Loss of or damage to physical assets from natural disaster or other events | A storm floods a branch basement; a fire closes a data room |
| Business Disruption and System Failures | Disruption of business or failures of systems | A core system outage delays card authorizations for a day; a vendor's network failure halts wire transfers for an afternoon |
| Execution, Delivery and Process Management | Failed transaction processing or process management, and failed relations with counterparties and vendors | A payment keyed to the wrong account and not recoverable; a trade settled late, with the counterparty's claim paid |

## The six business lines

The bank reports six business lines rather than the eight Basel business lines, deliberately: its line structure follows how it manages the business, and its centralized functions are a line of their own.

| Business line | What it does | Nearest Basel business line |
|---|---|---|
| Retail Banking | Deposit and card accounts and customer transactions for individuals | Retail Banking |
| Commercial Lending | Loans to businesses | Commercial Banking |
| Payments | Payment processing for clients | Payment and Settlement |
| Asset Management | Investment management for client accounts; acquired in 2022 | Asset Management |
| Trading and Treasury | The bank's trading positions, funding and settlements | Trading and Sales |
| Shared Services | Centralized functions: facilities, human resources and internal services | none (Basel allocates these across lines) |

Basel lines the bank does not report: Corporate Finance, Agency Services, Retail Brokerage.

## The other descriptive fields

- **Regions** (`region`): Chicago Metro, Illinois, Wisconsin, Indiana and Michigan. Centralized functions sit in Chicago Metro.
- **Reporting channels** (`reporting_channel`): Branch, Call Center, System Alert, Internal Audit, Customer Complaint.
- **Root-cause tags** (`root_cause_tags`, one per event, assigned at discovery): manual error, system defect, vendor, cyber, process gap, external event, policy breach.

The data dictionary is the authority on every field; this sheet is the vocabulary.

## Reference

Basel Committee on Banking Supervision. (2006). *International convergence of capital measurement and capital standards: A revised framework, comprehensive version* (Annexes 8 and 9). Bank for International Settlements.
