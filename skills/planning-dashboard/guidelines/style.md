# Style guideline

> **Customize this file** with your organization's brand. The method (how goal, audience and data choose a Style Profile) is in `references/style-system.md` and shouldn't need editing. Here you map its color roles to your colors, pick fonts, and tighten audience limits. You can tighten limits, never loosen them.

## Color roles

Every color on a dashboard comes from one of these roles. Executors read this table; plans name roles, not colors.

| Role | Light | Dark | Notes |
|---|---|---|---|
| `ink` | #1f2933 | #e4e7eb | text, axes, default marks |
| `ink-muted` | #9aa5b1 | #616e7c | context series, gridlines, "Other" |
| `focus` | #2f6fde | #6ea2ff | the subject named in the profile's `focus` |
| `selected` | #7c5cd6 | #a78bfa | what the reader clicked or brushed |
| `good` | #1f7a4d | #4cc38a | only with a declared direction, always with a sign |
| `bad` | #c2410c | #fb923c | only with a declared direction, always with a sign |
| `breach` | #b42318 | #f97066 | a value past its limit, on that element only |
| `category-1` | #2f6fde | #6ea2ff | categories keep their color on every chart |
| `category-2` | #d97706 | #fbbf24 | |
| `category-3` | #0f766e | #2dd4bf | |
| `category-4` | #be185d | #f472b6 | |
| `category-5` | #4d7c0f | #a3e635 | |
| `category-6` | #6d28d9 | #a78bfa | |
| `sequential` | #dbe7fb → #1e4fa8 | #1c2a44 → #9cc0ff | one hue, light to dark |
| `diverging` | #c2410c ↔ #e5e7eb ↔ #2f6fde | #fb923c ↔ #374151 ↔ #6ea2ff | midpoint must mean something |

## Plan tokens

Copied into every plan's `## Style` alongside the profile, for executors that only read these three:

- accent: #2f6fde
- alert: #c2410c
- currency: USD

## Fonts

| Use | Font |
|---|---|
| Everything by default | the platform's sans (system-ui) |
| Editorial headline and hero number (only `register: editorial`) | a serif, e.g. Georgia |
| Numbers | tabular figures, always |

## Audience limits (tighten only)

The defaults are in `references/style-system.md` (Audience overrides). Add stricter rules for your organization here, e.g.:

- leadership: at most 4 KPI tiles (default 5)
- clients: always show the organization's logo and a confidentiality footer

## House rules

- Never ask the person about chart library or styling; the Style Profile decides.
- Number formats: thousands as 412K, millions as 2.1M; currency with the symbol; percentages with one decimal unless `numbers: exact`.
