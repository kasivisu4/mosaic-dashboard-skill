# Metric definitions

> **Customize this file** with your organization's approved definitions. When a dataset has the columns a definition needs, the planner uses it and marks it `(confirmed)` without asking. Leave it empty to have the planner propose definitions from the data.

Format, one per metric:

```
## <Metric name>
- Definition: <plain words, with the denominator for rates>
- Expression: <value expression from references/plan-format.md, e.g. rate(is_churned)>
- Needs columns: <names or common aliases>
- Notes: <exclusions, e.g. exclude test accounts>
```

<!-- Example (delete or replace):
## Return rate
- Definition: returned orders / all orders
- Expression: rate(returned)
- Needs columns: returned, is_returned
- Notes: exclude orders with negative amounts (refund adjustments)
-->
