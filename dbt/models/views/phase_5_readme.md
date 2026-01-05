# Phase 5: Governance Views and Analytics Schema Alignment

## Objective

Phase 5 introduces a **governance and access control layer** on top of the Silver models.

The goal is to:
- protect sensitive data
- clearly separate administrative access from analytical access
- expose only safe, intentional schemas to analysts
- avoid duplicating or transforming data unnecessarily

This phase formalizes **who can see what**, without changing **what the data is**.

---

## Architectural Position

The views introduced in this phase sit **directly on top of the Silver layer**.

- Silver remains the **source of truth**
- Views act as a **controlled interface**
- No business logic or aggregation is introduced here

This keeps correctness in Silver and access control in Views.

---

## Admin Views

Admin views are created under the `admin` schema.

### Purpose
- debugging
- audits
- development validation
- full visibility into Silver data

### Characteristics
- direct `select *` from Silver models
- no column filtering
- no masking
- no transformations

### Admin Models
- `admin_customers`
- `admin_accounts`
- `admin_transactions`
- `admin_payments`
- `admin_subscriptions`
- `admin_refunds`

These views are intended for **restricted access only**.

---

## Analytics Views

Analytics views are created under the `analytics` schema.

### Purpose
- analyst consumption
- reporting
- downstream exploration
- safe access for BI tools

### Characteristics
- explicit column selection
- PII fields are masked or excluded
- stable schema contracts
- no joins or derived metrics

These views are **analyst safe by design**.

### Analytics Models
- `analytics_customers`
- `analytics_accounts`
- `analytics_transactions`
- `analytics_payments`
- `analytics_subscriptions`
- `analytics_refunds`

---

## Schema Alignment Strategy

All views:
- reference only Silver models
- preserve Silver naming conventions
- avoid renaming or retyping columns
- remain thin and declarative

This ensures:
- minimal blast radius from upstream changes
- clear ownership of logic
- predictable downstream behavior

---

## Documentation and Discoverability

All views are documented in `schema.yml` with clear intent:
- analyst safe vs admin only
- debugging vs consumption
- governance boundaries

This makes the platform:
- easier to onboard onto
- safer to query
- harder to misuse accidentally

---

## Why This Matters

This phase demonstrates:
- separation of correctness and access control
- governance without data duplication
- intentional exposure of sensitive data
- production grade analytics design patterns

Phase 5 turns the platform from **technically correct** into **operationally safe**.
