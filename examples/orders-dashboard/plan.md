---
plan_version: 2
goals: monitor, answer
audience: team
cadence: weekly
review_depth: guided
success_criteria: "a store with too many returns stands out at a glance"
reconcile: false
comparison_period: order_date:week
destination: local
source: orders.parquet
data:
  - file: orders_clean.parquet
    rows: 8000
---

# Store sales, 2025

Revenue was steady all year; returns run at about 9% of orders in every store, and only East is above target.

## Assumptions
- Return-rate target: at most 9% of orders, the same for every store

## Data
- 1 row = one order · 8,000 rows · Jan–Dec 2025
- Excluded: none
- Revenue = sum of revenue per order (confirmed)
- Return rate = returned orders / all orders (confirmed)

## Story
1. KPIs: Revenue = sum(revenue) [currency]; Orders = count() [compact]; Return rate = rate(returned) [percent] target<=9%; Avg order = avg(revenue) [currency]
2. "East is the only store above a 9% return rate" | exceptions | category=store value=rate(returned) above=9% format=percent | none
3. "Weekly revenue held steady through the year" | trend | x=order_date:week y=sum(revenue) | brush
   > The last week of the year has only three days of data, so it dips.
   @ 2025-12-29: Partial week
4. "All five categories bring in about the same revenue" | bar | category=category value=sum(revenue) | click
5. "Order values spread evenly from $10 to $200" | histogram | value=revenue | brush

## Interaction
- Menus: store
- Detail table: no
- SQL on page: no
- Last updated: order_date

## Style
- register: operational
- density: balanced
- surface: status
- focus: stores above the return-rate target
- color_mode: status
- direction: down-good
- type_scale: standard
- interaction: light
- motion: transitions
- chart_set: KPIs, exceptions, trend, bar, histogram
- anomalies: spotlight
- narrative: captions
- provenance: footnote
- numbers: precise
- data_character: time-heavy, categorical, flag-driven
- accent: #2f6fde
- alert: #c2410c
- currency: USD

## Data for the executor
```sql
COPY (SELECT * FROM 'orders.parquet') TO 'orders_clean.parquet'
```
