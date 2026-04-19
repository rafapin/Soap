# Technical Design: SCADA Alarm Gateway

## 1. Context & Goals
The goal is to receive structured text files (CSV/JSON) containing SCADA industrial alarms. These contain expected structural inconsistencies and "dirty data". The API then serves these back normalized and filtered.

## 2. Normalization Rules applied in ETL
- **Strings/Tags:** Stripped of leading/trailing whitespaces, inside doubled spaces collapsed to one. Long values are truncated.
- **Criticality:** Unified to purely "HIGH", "MEDIUM" or "LOW". Unknown criticalities reject the row.
- **Dates:** Tried against ISO_8601, European (DD/MM), US (MM/DD) via explicit format arrays, falling back to Python `dateutil` logic. Any row without a resolvable `event_time` is rejected.
- **Logical Rules:**
  - `ack_time` cannot precede `event_time`.
  - `clear_time` cannot precede `event_time`.

## 3. Data Rejection Philosophy
Rows that cannot be logically stored are moved into an `alarm_rejections` table. This points directly back to the `ingestion_batches` entry (1:N), allowing operators to trace:
- Which file failed?
- What was the exact raw payload?
- Why did it fail? (e.g. `event_time is required; criticality INVALID not in valid catalogue`). 

No data is silently discarded.

## 4. API Design Constraints
- All responses must be wrapped consistently. All paginated lists use `PaginatedResponse[T]`.
- Enums are strictly checked via Pydantic model validation.
- Internal Database/SQL errors must not leak their stack trace to clients. Global Exception handlers remap these to structured JSON error blocks.
